

# ----------------------------------------------------------------------------
# FILE: auth-service/app/services/auth.py
# ----------------------------------------------------------------------------
import logging
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Tuple
from jose import jwt, JWTError
import bcrypt
from sqlalchemy.orm import Session

from app.config import settings
from app.models import User, APIKey
from app.schemas.auth import UserContext

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Base auth error"""
    pass


class InvalidCredentialsError(AuthenticationError):
    pass


class AccountLockedError(AuthenticationError):
    pass


class AuthService:
    """Core authentication service"""
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify password"""
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    
    @staticmethod
    def generate_jwt(user: User) -> Tuple[str, str]:
        """Generate access and refresh tokens"""
        now = datetime.utcnow()
        
        # Access token
        access_payload = {
            "user_id": str(user.id),
            "tenant_id": str(user.tenant_id),
            "email": user.email,
            "role": user.role,
            "type": "access",
            "iat": now,
            "exp": now + timedelta(seconds=settings.JWT_EXPIRY_SECONDS)
        }
        access_token = jwt.encode(
            access_payload,
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM
        )
        
        # Refresh token
        refresh_payload = {
            "user_id": str(user.id),
            "type": "refresh",
            "iat": now,
            "exp": now + timedelta(seconds=settings.JWT_REFRESH_EXPIRY_SECONDS)
        }
        refresh_token = jwt.encode(
            refresh_payload,
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM
        )
        
        return access_token, refresh_token
    
    @staticmethod
    def verify_jwt(token: str) -> UserContext:
        """Verify JWT and return user context"""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            if payload.get("type") != "access":
                raise AuthenticationError("Invalid token type")
            
            return UserContext(
                user_id=payload["user_id"],
                tenant_id=payload["tenant_id"],
                email=payload["email"],
                role=payload["role"],
                scopes=[]
            )
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            raise AuthenticationError("Invalid or expired token")
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate random API key"""
        random_part = secrets.token_urlsafe(settings.API_KEY_LENGTH)
        return f"{settings.API_KEY_PREFIX}{random_part}"
    
    @staticmethod
    def hash_api_key(key: str) -> str:
        """Hash API key for storage"""
        return hashlib.sha256(key.encode()).hexdigest()

    @classmethod
    def authenticate_user(cls, db: Session, email: str, password: str) -> User:
        """Authenticate user with email and password"""
        user = db.query(User).filter(User.email == email.lower()).first()

        if not user:
            raise InvalidCredentialsError("Invalid email or password")

        # Check account status
        if getattr(user, "status", None) and user.status != "active":
            raise AccountLockedError(f"Account is {user.status}")

        # Check if account is locked by time
        if getattr(user, "locked_until", None) and user.locked_until and user.locked_until > datetime.utcnow():
            raise AccountLockedError(f"Account locked until {user.locked_until.isoformat()}")

        # Verify password
        if not cls.verify_password(password, user.password_hash):
            # Increment failed attempts if field exists
            if hasattr(user, "failed_login_attempts"):
                user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
                # Lock account if threshold reached
                if user.failed_login_attempts >= cls.MAX_FAILED_ATTEMPTS:
                    user.locked_until = datetime.utcnow() + timedelta(minutes=cls.LOCKOUT_DURATION_MINUTES)
                    db.commit()
                    raise AccountLockedError(f"Account locked for {cls.LOCKOUT_DURATION_MINUTES} minutes")
                db.commit()

            raise InvalidCredentialsError("Invalid email or password")

        # Successful login: reset counters, update last_login
        if hasattr(user, "failed_login_attempts"):
            user.failed_login_attempts = 0
        if hasattr(user, "locked_until"):
            user.locked_until = None
        if hasattr(user, "last_login_at"):
            user.last_login_at = datetime.utcnow()
        db.commit()

        return user


# Public function for other services to import
def verify_token(token: str) -> UserContext:
    """Verify JWT token (used by AI service)"""
    return AuthService.verify_jwt(token)
