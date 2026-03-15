# ----------------------------------------------------------------------------
# FILE: auth-service/app/api/v1/auth.py
# ----------------------------------------------------------------------------
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
from app.config import settings
from app.db import get_db
from app.schemas.auth import (
    RegisterRequest, LoginRequest, TokenResponse,
    VerifyTokenRequest, UserContext, APIKeyCreateRequest, APIKeyResponse
)
from app.services.auth import AuthService
from app.models import User, Tenant, APIKey
from datetime import datetime, timedelta

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register new user and tenant"""
    try:
        # Check if user exists
        existing = db.query(User).filter(User.email == request.email.lower()).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create tenant
        tenant = Tenant(name=request.tenant_name)
        db.add(tenant)
        db.flush()
        
        # Create user
        user = User(
            tenant_id=tenant.id,
            email=request.email.lower(),
            password_hash=AuthService.hash_password(request.password),
            full_name=request.full_name,
            role="admin"
        )
        db.add(user)
        db.commit()
        
        logger.info(f"User registered: {user.email}")
        return {"status": "success", "user_id": str(user.id)}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Registration failed")


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password"""
    user = db.query(User).filter(User.email == request.email.lower()).first()

    if not user or not AuthService.verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check account lock
    locked_until = getattr(user, "locked_until", None)
    if locked_until and locked_until > datetime.utcnow():
        raise HTTPException(status_code=423, detail="Account locked")
    
    # Generate tokens
    access_token, refresh_token = AuthService.generate_jwt(user)
    
    # Update last login
    if hasattr(user, "last_login_at"):
        user.last_login_at = datetime.utcnow()
    if hasattr(user, "failed_login_attempts"):
        user.failed_login_attempts = 0
    db.commit()
    
    logger.info(f"User logged in: {user.email}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRY_SECONDS
    )


@router.post("/verify", response_model=UserContext)
async def verify_token_endpoint(request: VerifyTokenRequest):
    """Verify JWT token (called by other services)"""
    try:
        context = AuthService.verify_jwt(request.token)
        return context
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/api-keys", response_model=APIKeyResponse, status_code=201)
async def create_api_key(
    request: APIKeyCreateRequest,
    db: Session = Depends(get_db)
):
    """Create API key"""
    # In production, extract user from JWT
    # For now, simplified
    raw_key = AuthService.generate_api_key()
    key_hash = AuthService.hash_api_key(raw_key)
    
    expires_at = None
    if request.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=request.expires_in_days)
    
    # Mock tenant_id - in production get from JWT
    from uuid import uuid4
    tenant_id = uuid4()
    
    api_key = APIKey(
        tenant_id=tenant_id,
        key_hash=key_hash,
        name=request.name,
        scopes=request.scopes or [],
        expires_at=expires_at
    )
    db.add(api_key)
    db.commit()
    
    return APIKeyResponse(
        id=str(api_key.id),
        name=api_key.name,
        key=raw_key,
        scopes=api_key.scopes,
        created_at=api_key.created_at,
        expires_at=api_key.expires_at,
        revoked=api_key.revoked
    )

