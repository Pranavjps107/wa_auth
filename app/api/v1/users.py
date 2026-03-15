# auth-service/app/api/v1/users.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.db import get_db
from app.services.auth import verify_token
from app.schemas.auth import UserContext

router = APIRouter(prefix="/users", tags=["users"])

# ============================================================================
# MODELS
# ============================================================================

class AvatarUploadResponse(BaseModel):
    success: bool
    avatar_url: str

class NotificationPreferences(BaseModel):
    email_enabled: bool
    new_conversations: bool
    unread_messages: bool
    weekly_reports: bool

class UserProfileResponse(BaseModel):
    id: str
    email: str
    full_name: str
    avatar_url: Optional[str]
    role: str
    status: str
    created_at: str
    notification_settings: Optional[dict]

# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/me", response_model=UserProfileResponse)
async def get_current_user(
    user: UserContext = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Get current user profile.
    Used by: Settings page - Profile section
    """
    from app.models import User
    
    user_record = db.query(User).filter(User.id == user.user_id).first()
    
    if not user_record:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserProfileResponse(
        id=str(user_record.id),
        email=user_record.email,
        full_name=user_record.full_name or "",
        avatar_url=getattr(user_record, "avatar_url", None),
        role=user_record.role,
        status=getattr(user_record, "status", "active"),
        created_at=user_record.created_at.isoformat(),
        notification_settings=getattr(user_record, "notification_settings", {})
    )


@router.post("/me/avatar", response_model=AvatarUploadResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    user: UserContext = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Upload user profile picture.
    Used by: Settings page - Profile section
    """
    from app.models import User
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # For now, store path in database
    # In production, you'd upload to S3 or similar
    avatar_url = f"/uploads/avatars/{user.user_id}.jpg"
    
    user_record = db.query(User).filter(User.id == user.user_id).first()
    if not user_record:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_record.avatar_url = avatar_url
    user_record.updated_at = datetime.utcnow()
    db.commit()
    
    return AvatarUploadResponse(
        success=True,
        avatar_url=avatar_url
    )


@router.patch("/me/profile")
async def update_user_profile(
    full_name: Optional[str] = None,
    user: UserContext = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Update user profile information.
    Used by: Settings page - Profile section
    """
    from app.models import User
    
    user_record = db.query(User).filter(User.id == user.user_id).first()
    if not user_record:
        raise HTTPException(status_code=404, detail="User not found")
    
    if full_name:
        user_record.full_name = full_name
    
    user_record.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "success": True,
        "message": "Profile updated successfully"
    }


@router.get("/me/notifications", response_model=NotificationPreferences)
async def get_notification_preferences(
    user: UserContext = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Get user notification preferences.
    Used by: Settings page - Notifications section
    """
    from app.models import User
    
    user_record = db.query(User).filter(User.id == user.user_id).first()
    
    if not user_record:
        raise HTTPException(status_code=404, detail="User not found")
    
    settings = getattr(user_record, "notification_settings", None)
    
    if not settings:
        # Return defaults
        return NotificationPreferences(
            email_enabled=True,
            new_conversations=True,
            unread_messages=False,
            weekly_reports=True
        )
    
    return NotificationPreferences(**settings)


@router.patch("/me/notifications", response_model=NotificationPreferences)
async def update_notification_preferences(
    preferences: NotificationPreferences,
    user: UserContext = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Update user notification preferences.
    Used by: Settings page - Notifications section
    """
    from app.models import User
    
    user_record = db.query(User).filter(User.id == user.user_id).first()
    if not user_record:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_record.notification_settings = preferences.dict()
    user_record.updated_at = datetime.utcnow()
    db.commit()
    
    return preferences


@router.post("/me/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    user: UserContext = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Change user password.
    Used by: Settings page - Security section
    """
    from app.models import User
    from app.services.auth import AuthService
    
    user_record = db.query(User).filter(User.id == user.user_id).first()
    if not user_record:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify current password
    if not AuthService.verify_password(current_password, user_record.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Update password
    user_record.password_hash = AuthService.hash_password(new_password)
    user_record.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "success": True,
        "message": "Password changed successfully"
    }


@router.delete("/me")
async def delete_account(
    password: str,
    user: UserContext = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Delete user account (soft delete).
    Used by: Settings page - Account deletion
    """
    from app.models import User
    from app.services.auth import AuthService
    
    user_record = db.query(User).filter(User.id == user.user_id).first()
    if not user_record:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify password
    if not AuthService.verify_password(password, user_record.password_hash):
        raise HTTPException(status_code=400, detail="Password is incorrect")
    
    # Soft delete
    user_record.deleted_at = datetime.utcnow()
    db.commit()
    
    return {
        "success": True,
        "message": "Account deleted successfully"
    }
