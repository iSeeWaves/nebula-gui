"""User management endpoints."""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, EmailStr, validator
from sqlalchemy.orm import Session

from core.database import get_db, User
from core.security import get_password_hash, validate_password_strength, Role, check_permission
from api.auth import get_current_admin_user, get_current_active_user
from core.logger import log_action

router = APIRouter(prefix="/users", tags=["users"])


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True

class EmailChangeRequest(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    
    @validator('role')
    def validate_role(cls, v):
        if v and v not in [Role.VIEWER, Role.USER, Role.ADMIN]:
            raise ValueError(f'Role must be one of: {Role.VIEWER}, {Role.USER}, {Role.ADMIN}')
        return v


class PasswordChange(BaseModel):
    old_password: str
    new_password: str


class UserStats(BaseModel):
    total_users: int
    active_users: int
    admin_users: int
    recent_signups: int


@router.get("/", response_model=List[UserResponse])
async def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """List all users (admin only)."""
    users = db.query(User).all()
    return users


@router.get("/stats", response_model=UserStats)
async def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get user statistics (admin only)."""
    from datetime import timedelta
    
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    admin_users = db.query(User).filter(User.is_admin == True).count()
    
    # Recent signups (last 30 days)
    recent_cutoff = datetime.utcnow() - timedelta(days=30)
    recent_signups = db.query(User).filter(User.created_at >= recent_cutoff).count()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "admin_users": admin_users,
        "recent_signups": recent_signups
    }


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get specific user (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update user (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Don't allow demoting yourself from admin
    if user.id == current_user.id and user_data.role and user_data.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own admin role"
        )
    
    # Update fields
    if user_data.email:
        user.email = user_data.email
    
    if user_data.role:
        user.role = user_data.role
        user.is_admin = (user_data.role == Role.ADMIN)
    
    if user_data.is_active is not None:
        # Don't allow deactivating yourself
        if user.id == current_user.id and not user_data.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate yourself"
            )
        user.is_active = user_data.is_active
    
    user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    
    # Log action
    log_action(
        db=db,
        user_id=current_user.id,
        action="user_update",
        resource_type="user",
        resource_id=str(user.id),
        resource_name=user.username,
        details=f"Updated user: role={user.role}, active={user.is_active}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return user



@router.post("/{user_id}/toggle-active")
async def toggle_user_active(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Toggle user active status (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Don't allow deactivating yourself
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot toggle your own active status"
        )
    
    user.is_active = not user.is_active
    user.updated_at = datetime.utcnow()
    
    db.commit()
    
    # Log action
    log_action(
        db=db,
        user_id=current_user.id,
        action="user_toggle_active",
        resource_type="user",
        resource_id=str(user.id),
        resource_name=user.username,
        details=f"Set active status to {user.is_active}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return {"message": f"User {'activated' if user.is_active else 'deactivated'}", "is_active": user.is_active}


@router.post("/me/change-password")
async def change_my_password(
    password_data: PasswordChange,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Change current user's password."""
    from core.security import verify_password
    
    # Verify old password
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect"
        )
    
    # Validate new password
    is_valid, error_msg = validate_password_strength(password_data.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    
    db.commit()
    
    # Log action
    log_action(
        db=db,
        user_id=current_user.id,
        action="password_change",
        resource_type="user",
        resource_id=str(current_user.id),
        resource_name=current_user.username,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return {"message": "Password changed successfully"}


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete user (admin only)."""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    username = user.username
    
    # Log action before deleting
    log_action(
        db=db,
        user_id=current_user.id,
        action="user_delete",
        resource_type="user",
        resource_id=str(user.id),
        resource_name=username,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    db.delete(user)
    db.commit()
    
    return None

@router.put("/me/email", response_model=UserResponse)
async def change_my_email(
    request: Request,
    email_data: EmailChangeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change current user's email."""
    from core.security import verify_password
    
    # Verify password
    if not verify_password(email_data.password, current_user.hashed_password):
        log_action(
            db=db,
            user_id=current_user.id,
            action="email_change_failed",
            resource_type="user",
            resource_id=str(current_user.id),
            status="failed",
            error_message="Invalid password",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    # Check if email already exists
    existing_user = db.query(User).filter(
        User.email == email_data.email,
        User.id != current_user.id
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already in use by another account"
        )
    
    # Update email
    old_email = current_user.email
    current_user.email = email_data.email
    db.commit()
    db.refresh(current_user)
    
    # Log action
    log_action(
        db=db,
        user_id=current_user.id,
        action="email_changed",
        resource_type="user",
        resource_id=str(current_user.id),
        resource_name=current_user.username,
        details=f"Email changed from {old_email} to {email_data.email}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return current_user