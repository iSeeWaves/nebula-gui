"""Authentication endpoints with signup and enhanced logging."""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, validator
from sqlalchemy.orm import Session

from core.database import get_db, User
from core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    validate_password_strength,
    check_permission,
    Role,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from core.logger import log_action

router = APIRouter(prefix="/auth", tags=["authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[str] = "user"
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Username must be between 3 and 50 characters')
        return v
    
    @validator('role')
    def validate_role(cls, v):
        if v not in [Role.VIEWER, Role.USER, Role.ADMIN]:
            raise ValueError(f'Role must be one of: {Role.VIEWER}, {Role.USER}, {Role.ADMIN}')
        return v


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


class Token(BaseModel):
    access_token: str
    token_type: str


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current admin user."""
    if not check_permission(current_user.role, Role.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required."
        )
    return current_user


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Register a new user with password validation."""
    # Check if username exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password strength
    is_valid, error_msg = validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role,
        is_admin=(user_data.role == Role.ADMIN)
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Log action
    log_action(
        db=db,
        user_id=db_user.id,
        action="user_signup",
        resource_type="user",
        resource_id=str(db_user.id),
        resource_name=db_user.username,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return db_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Login and get access token with enhanced logging."""
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        # Log failed login
        if user:
            log_action(
                db=db,
                user_id=user.id,
                action="login_failed",
                resource_type="auth",
                status="failed",
                error_message="Invalid password",
                ip_address=request.client.host if request else None,
                user_agent=request.headers.get("user-agent") if request else None
            )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    # Log successful login
    log_action(
        db=db,
        user_id=user.id,
        action="login_success",
        resource_type="auth",
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Logout with logging."""
    log_action(
        db=db,
        user_id=current_user.id,
        action="logout",
        resource_type="auth",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return {"message": "Successfully logged out"}
