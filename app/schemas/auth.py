


# ----------------------------------------------------------------------------
# FILE: auth-service/app/schemas/auth.py
# ----------------------------------------------------------------------------
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginRequest(BaseModel):
    """Login credentials"""
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """User registration"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    tenant_name: str


class VerifyTokenRequest(BaseModel):
    """Token verification request"""
    token: str


class UserContext(BaseModel):
    """User context returned to other services"""
    user_id: str
    tenant_id: str
    email: str
    role: str
    scopes: List[str] = []


class APIKeyCreateRequest(BaseModel):
    """Create API key"""
    name: str
    scopes: Optional[List[str]] = []
    expires_in_days: Optional[int] = None


class APIKeyResponse(BaseModel):
    """API key response"""
    id: str
    name: str
    key: Optional[str] = None  # Only on creation
    scopes: List[str]
    created_at: datetime
    expires_at: Optional[datetime]
    revoked: bool

