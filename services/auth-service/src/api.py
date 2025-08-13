"""
Authentication Service API - Complete Implementation
FastAPI application for user authentication, authorization, and session management.
"""

from fastapi import FastAPI, Depends, HTTPException, Path, Query, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import logging
import uuid
from datetime import datetime, timedelta

from .models import User, Role, UserRole, UserSession
from .database import get_session as get_db_session
from .auth_manager import AuthManager
from .service_client import ServiceClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Authentication Service API",
    description="OpenPolicy Platform - User Authentication and Authorization Service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
auth_manager = AuthManager()
service_client = ServiceClient()
security = HTTPBearer()

# Pydantic models for API requests/responses
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any

class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=8, description="Password")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    phone: Optional[str] = Field(None, description="Phone number")
    is_active: bool = Field(True, description="Whether user is active")
    roles: Optional[List[str]] = Field(None, description="User roles")

class UserUpdateRequest(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Username")
    email: Optional[EmailStr] = Field(None, description="Email address")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    phone: Optional[str] = Field(None, description="Phone number")
    is_active: Optional[bool] = Field(None, description="Whether user is active")
    roles: Optional[List[str]] = Field(None, description="User roles")

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    first_name: str
    last_name: str
    phone: Optional[str]
    is_active: bool
    roles: List[str]
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]

class UserLoginRequest(BaseModel):
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")
    remember_me: bool = Field(False, description="Remember login session")

class UserLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: UserResponse

class UserRefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh token")

class UserRefreshResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")

class ResetPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="Email address")

class ResetPasswordConfirmRequest(BaseModel):
    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., min_length=8, description="New password")

class RoleCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Role name")
    description: str = Field(..., description="Role description")
    permissions: List[str] = Field(..., description="Role permissions")
    is_active: bool = Field(True, description="Whether role is active")

class RoleUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50, description="Role name")
    description: Optional[str] = Field(None, description="Role description")
    permissions: Optional[List[str]] = Field(None, description="Role permissions")
    is_active: Optional[bool] = Field(None, description="Whether role is active")

class RoleResponse(BaseModel):
    id: str
    name: str
    description: str
    permissions: List[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

class UserSessionResponse(BaseModel):
    id: str
    user_id: str
    session_token: str
    ip_address: str
    user_agent: str
    created_at: datetime
    expires_at: datetime
    is_active: bool

class UserProfileResponse(BaseModel):
    id: str
    username: str
    email: str
    first_name: str
    last_name: str
    phone: Optional[str]
    is_active: bool
    roles: List[str]
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    session_count: int

# Dependency functions
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db_session: Session = Depends(get_db_session)
) -> Dict[str, Any]:
    """Get current authenticated user from JWT token."""
    try:
        token = credentials.credentials
        user_data = auth_manager.verify_token(token, db_session)
        if not user_data:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        return user_data
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get current active user."""
    if not current_user.get("is_active"):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def require_role(required_role: str):
    """Dependency to require a specific role."""
    async def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        if required_role not in current_user.get("roles", []):
            raise HTTPException(
                status_code=403,
                detail=f"Role '{required_role}' required"
            )
        return current_user
    return role_checker

def get_db_session():
    """Get database session."""
    return next(get_db_session())

# Health and readiness endpoints
@app.get("/healthz", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    try:
        # Check database connection
        db = get_db_session()
        db.execute("SELECT 1")
        
        # Check auth manager
        auth_health = auth_manager.health_check()
        
        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "service": "auth-service",
            "version": "1.0.0",
            "database": "connected",
            "auth_manager": auth_health
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/readyz", tags=["Health"])
async def readiness_check():
    """Readiness check endpoint."""
    try:
        # Check database connection
        db = get_db_session()
        db.execute("SELECT 1")
        
        # Check if auth manager is ready
        if not auth_manager.is_ready():
            raise HTTPException(status_code=503, detail="Auth manager not ready")
        
        return {
            "status": "ready",
            "timestamp": datetime.now().isoformat(),
            "service": "auth-service"
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

# Authentication endpoints
@app.post("/auth/register", response_model=UserResponse, status_code=201, tags=["Authentication"])
async def register_user(
    request: UserCreateRequest,
    db_session: Session = Depends(get_db_session)
):
    """Register a new user."""
    try:
        # Check if username already exists
        existing_user = db_session.query(User).filter(
            User.username == request.username
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Check if email already exists
        existing_email = db_session.query(User).filter(
            User.email == request.email
        ).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")
        
        # Create user
        user = auth_manager.create_user(
            username=request.username,
            email=request.email,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name,
            phone=request.phone,
            is_active=request.is_active,
            db_session=db_session
        )
        
        # Assign roles if provided
        if request.roles:
            for role_name in request.roles:
                role = db_session.query(Role).filter(Role.name == role_name).first()
                if role:
                    user_role = UserRole(
                        id=str(uuid.uuid4()),
                        user_id=user.id,
                        role_id=role.id,
                        assigned_at=datetime.now(),
                        assigned_by="system"
                    )
                    db_session.add(user_role)
        
        db_session.commit()
        db_session.refresh(user)
        
        # Get user with roles
        user_with_roles = auth_manager.get_user_by_id(user.id, db_session)
        
        logger.info(f"User registered: {user.id}")
        
        # Record metrics
        await service_client.record_metric(
            "auth_users_registered_total", 1,
            {"username": request.username}
        )
        
        return UserResponse(
            id=user_with_roles["id"],
            username=user_with_roles["username"],
            email=user_with_roles["email"],
            first_name=user_with_roles["first_name"],
            last_name=user_with_roles["last_name"],
            phone=user_with_roles["phone"],
            is_active=user_with_roles["is_active"],
            roles=user_with_roles["roles"],
            created_at=user_with_roles["created_at"],
            updated_at=user_with_roles["updated_at"],
            last_login=user_with_roles.get("last_login")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to register user: {e}")
        db_session.rollback()
        raise HTTPException(status_code=500, detail="Failed to register user")

@app.post("/auth/login", response_model=UserLoginResponse, tags=["Authentication"])
async def login_user(
    request: UserLoginRequest,
    db_session: Session = Depends(get_db_session),
    user_agent: Optional[str] = Header(None),
    x_forwarded_for: Optional[str] = Header(None)
):
    """Authenticate user and create session."""
    try:
        # Authenticate user
        user = auth_manager.authenticate_user(
            username=request.username,
            password=request.password,
            db_session=db_session
        )
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not user["is_active"]:
            raise HTTPException(status_code=400, detail="User account is inactive")
        
        # Create access token
        access_token = auth_manager.create_access_token(
            data={"sub": user["id"], "username": user["username"]},
            expires_delta=timedelta(hours=1)
        )
        
        # Create refresh token
        refresh_token = auth_manager.create_refresh_token(
            data={"sub": user["id"]},
            expires_delta=timedelta(days=30 if request.remember_me else 7)
        )
        
        # Create user session
        ip_address = x_forwarded_for.split(",")[0].strip() if x_forwarded_for else "unknown"
        session = UserSession(
            id=str(uuid.uuid4()),
            user_id=user["id"],
            session_token=refresh_token,
            ip_address=ip_address,
            user_agent=user_agent or "unknown",
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=30 if request.remember_me else 7),
            is_active=True
        )
        
        db_session.add(session)
        
        # Update last login
        user_obj = db_session.query(User).filter(User.id == user["id"]).first()
        user_obj.last_login = datetime.now()
        
        db_session.commit()
        
        logger.info(f"User logged in: {user['id']}")
        
        # Record metrics
        await service_client.record_metric(
            "auth_logins_total", 1,
            {"username": user["username"], "success": True}
        )
        
        return UserLoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=3600,  # 1 hour
            user=UserResponse(
                id=user["id"],
                username=user["username"],
                email=user["email"],
                first_name=user["first_name"],
                last_name=user["last_name"],
                phone=user["phone"],
                is_active=user["is_active"],
                roles=user["roles"],
                created_at=user["created_at"],
                updated_at=user["updated_at"],
                last_login=user.get("last_login")
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.post("/auth/refresh", response_model=UserRefreshResponse, tags=["Authentication"])
async def refresh_token(
    request: UserRefreshRequest,
    db_session: Session = Depends(get_db_session)
):
    """Refresh access token using refresh token."""
    try:
        # Verify refresh token
        user_data = auth_manager.verify_refresh_token(request.refresh_token, db_session)
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        # Check if session is still active
        session = db_session.query(UserSession).filter(
            UserSession.session_token == request.refresh_token,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.now()
        ).first()
        
        if not session:
            raise HTTPException(status_code=401, detail="Session expired or invalid")
        
        # Create new access token
        access_token = auth_manager.create_access_token(
            data={"sub": user_data["id"], "username": user_data["username"]},
            expires_delta=timedelta(hours=1)
        )
        
        logger.info(f"Token refreshed for user: {user_data['id']}")
        
        return UserRefreshResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=3600  # 1 hour
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(status_code=500, detail="Token refresh failed")

@app.post("/auth/logout", status_code=204, tags=["Authentication"])
async def logout_user(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """Logout user and invalidate session."""
    try:
        # Invalidate all active sessions for the user
        sessions = db_session.query(UserSession).filter(
            UserSession.user_id == current_user["id"],
            UserSession.is_active == True
        ).all()
        
        for session in sessions:
            session.is_active = False
            session.updated_at = datetime.now()
        
        db_session.commit()
        
        logger.info(f"User logged out: {current_user['id']}")
        
        # Record metrics
        await service_client.record_metric(
            "auth_logouts_total", 1,
            {"username": current_user["username"]}
        )
        
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(status_code=500, detail="Logout failed")

@app.post("/auth/logout/all", status_code=204, tags=["Authentication"])
async def logout_all_sessions(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """Logout user from all sessions."""
    try:
        # Invalidate all active sessions for the user
        sessions = db_session.query(UserSession).filter(
            UserSession.user_id == current_user["id"],
            UserSession.is_active == True
        ).all()
        
        for session in sessions:
            session.is_active = False
            session.updated_at = datetime.now()
        
        db_session.commit()
        
        logger.info(f"User logged out from all sessions: {current_user['id']}")
        
    except Exception as e:
        logger.error(f"Logout all sessions failed: {e}")
        raise HTTPException(status_code=500, detail="Logout all sessions failed")

# User management endpoints
@app.get("/users/me", response_model=UserProfileResponse, tags=["User Management"])
async def get_current_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db_session: Session = Depends(get_db_session)
):
    """Get current user profile."""
    try:
        user = auth_manager.get_user_by_id(current_user["id"], db_session)
        
        # Get active session count
        session_count = db_session.query(UserSession).filter(
            UserSession.user_id == current_user["id"],
            UserSession.is_active == True,
            UserSession.expires_at > datetime.now()
        ).count()
        
        return UserProfileResponse(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            first_name=user["first_name"],
            last_name=user["last_name"],
            phone=user["phone"],
            is_active=user["is_active"],
            roles=user["roles"],
            created_at=user["created_at"],
            updated_at=user["updated_at"],
            last_login=user.get("last_login"),
            session_count=session_count
        )
        
    except Exception as e:
        logger.error(f"Failed to get user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user profile")

@app.put("/users/me", response_model=UserResponse, tags=["User Management"])
async def update_current_user_profile(
    request: UserUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db_session: Session = Depends(get_db_session)
):
    """Update current user profile."""
    try:
        user_obj = db_session.query(User).filter(User.id == current_user["id"]).first()
        
        # Update fields if provided
        if request.username is not None:
            # Check if username is already taken
            existing = db_session.query(User).filter(
                User.username == request.username,
                User.id != current_user["id"]
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail="Username already exists")
            user_obj.username = request.username
        
        if request.email is not None:
            # Check if email is already taken
            existing = db_session.query(User).filter(
                User.email == request.email,
                User.id != current_user["id"]
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail="Email already exists")
            user_obj.email = request.email
        
        if request.first_name is not None:
            user_obj.first_name = request.first_name
        if request.last_name is not None:
            user_obj.last_name = request.last_name
        if request.phone is not None:
            user_obj.phone = request.phone
        
        user_obj.updated_at = datetime.now()
        
        # Update roles if provided
        if request.roles is not None:
            # Remove existing roles
            existing_roles = db_session.query(UserRole).filter(
                UserRole.user_id == current_user["id"]
            ).all()
            for role in existing_roles:
                db_session.delete(role)
            
            # Add new roles
            for role_name in request.roles:
                role = db_session.query(Role).filter(Role.name == role_name).first()
                if role:
                    user_role = UserRole(
                        id=str(uuid.uuid4()),
                        user_id=current_user["id"],
                        role_id=role.id,
                        assigned_at=datetime.now(),
                        assigned_by=current_user["id"]
                    )
                    db_session.add(user_role)
        
        db_session.commit()
        db_session.refresh(user_obj)
        
        # Get updated user with roles
        updated_user = auth_manager.get_user_by_id(current_user["id"], db_session)
        
        logger.info(f"User profile updated: {current_user['id']}")
        
        return UserResponse(
            id=updated_user["id"],
            username=updated_user["username"],
            email=updated_user["email"],
            first_name=updated_user["first_name"],
            last_name=updated_user["last_name"],
            phone=updated_user["phone"],
            is_active=updated_user["is_active"],
            roles=updated_user["roles"],
            created_at=updated_user["created_at"],
            updated_at=updated_user["updated_at"],
            last_login=updated_user.get("last_login")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user profile: {e}")
        db_session.rollback()
        raise HTTPException(status_code=500, detail="Failed to update user profile")

@app.post("/users/me/change-password", status_code=204, tags=["User Management"])
async def change_password(
    request: ChangePasswordRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db_session: Session = Depends(get_db_session)
):
    """Change current user password."""
    try:
        # Verify current password
        if not auth_manager.verify_password(request.current_password, current_user["password_hash"]):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        # Update password
        auth_manager.change_password(
            user_id=current_user["id"],
            new_password=request.new_password,
            db_session=db_session
        )
        
        logger.info(f"Password changed for user: {current_user['id']}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to change password: {e}")
        raise HTTPException(status_code=500, detail="Failed to change password")

@app.post("/auth/forgot-password", status_code=200, tags=["Authentication"])
async def forgot_password(
    request: ResetPasswordRequest,
    db_session: Session = Depends(get_db_session)
):
    """Send password reset email."""
    try:
        user = db_session.query(User).filter(User.email == request.email).first()
        if not user:
            # Don't reveal if email exists or not
            return {"message": "If the email exists, a reset link has been sent"}
        
        # Generate reset token
        reset_token = auth_manager.create_reset_token(user.id)
        
        # Send reset email (placeholder)
        # TODO: Implement actual email sending
        logger.info(f"Password reset token generated for user: {user.id}")
        
        return {"message": "If the email exists, a reset link has been sent"}
        
    except Exception as e:
        logger.error(f"Failed to process password reset: {e}")
        return {"message": "If the email exists, a reset link has been sent"}

@app.post("/auth/reset-password", status_code=200, tags=["Authentication"])
async def reset_password(
    request: ResetPasswordConfirmRequest,
    db_session: Session = Depends(get_db_session)
):
    """Reset password using reset token."""
    try:
        # Verify reset token
        user_id = auth_manager.verify_reset_token(request.token)
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        
        # Update password
        auth_manager.change_password(
            user_id=user_id,
            new_password=request.new_password,
            db_session=db_session
        )
        
        # Invalidate all sessions for the user
        sessions = db_session.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True
        ).all()
        
        for session in sessions:
            session.is_active = False
            session.updated_at = datetime.now()
        
        db_session.commit()
        
        logger.info(f"Password reset for user: {user_id}")
        
        return {"message": "Password reset successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reset password: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset password")

# User management (admin only)
@app.get("/users", response_model=List[UserResponse], tags=["User Management"])
async def list_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of users to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    role: Optional[str] = Query(None, description="Filter by role"),
    search: Optional[str] = Query(None, description="Search in username, email, first_name, last_name"),
    current_user: Dict[str, Any] = Depends(require_role("admin")),
    db_session: Session = Depends(get_db_session)
):
    """List users with optional filtering (admin only)."""
    try:
        query = db_session.query(User)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (User.username.ilike(search_term)) |
                (User.email.ilike(search_term)) |
                (User.first_name.ilike(search_term)) |
                (User.last_name.ilike(search_term))
            )
        
        users = query.offset(skip).limit(limit).all()
        
        # Get users with roles
        user_responses = []
        for user in users:
            user_with_roles = auth_manager.get_user_by_id(user.id, db_session)
            if role is None or role in user_with_roles["roles"]:
                user_responses.append(UserResponse(
                    id=user_with_roles["id"],
                    username=user_with_roles["username"],
                    email=user_with_roles["email"],
                    first_name=user_with_roles["first_name"],
                    last_name=user_with_roles["last_name"],
                    phone=user_with_roles["phone"],
                    is_active=user_with_roles["is_active"],
                    roles=user_with_roles["roles"],
                    created_at=user_with_roles["created_at"],
                    updated_at=user_with_roles["updated_at"],
                    last_login=user_with_roles.get("last_login")
                ))
        
        return user_responses
        
    except Exception as e:
        logger.error(f"Failed to list users: {e}")
        raise HTTPException(status_code=500, detail="Failed to list users")

@app.get("/users/{user_id}", response_model=UserResponse, tags=["User Management"])
async def get_user(
    user_id: str = Path(..., description="User ID"),
    current_user: Dict[str, Any] = Depends(require_role("admin")),
    db_session: Session = Depends(get_db_session)
):
    """Get a specific user by ID (admin only)."""
    try:
        user = auth_manager.get_user_by_id(user_id, db_session)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            first_name=user["first_name"],
            last_name=user["last_name"],
            phone=user["phone"],
            is_active=user["is_active"],
            roles=user["roles"],
            created_at=user["created_at"],
            updated_at=user["updated_at"],
            last_login=user.get("last_login")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user")

@app.put("/users/{user_id}", response_model=UserResponse, tags=["User Management"])
async def update_user(
    user_id: str = Path(..., description="User ID"),
    request: UserUpdateRequest = None,
    current_user: Dict[str, Any] = Depends(require_role("admin")),
    db_session: Session = Depends(get_db_session)
):
    """Update a user (admin only)."""
    try:
        user_obj = db_session.query(User).filter(User.id == user_id).first()
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update fields if provided
        if request.username is not None:
            existing = db_session.query(User).filter(
                User.username == request.username,
                User.id != user_id
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail="Username already exists")
            user_obj.username = request.username
        
        if request.email is not None:
            existing = db_session.query(User).filter(
                User.email == request.email,
                User.id != user_id
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail="Email already exists")
            user_obj.email = request.email
        
        if request.first_name is not None:
            user_obj.first_name = request.first_name
        if request.last_name is not None:
            user_obj.last_name = request.last_name
        if request.phone is not None:
            user_obj.phone = request.phone
        if request.is_active is not None:
            user_obj.is_active = request.is_active
        
        user_obj.updated_at = datetime.now()
        user_obj.updated_by = current_user["id"]
        
        # Update roles if provided
        if request.roles is not None:
            # Remove existing roles
            existing_roles = db_session.query(UserRole).filter(
                UserRole.user_id == user_id
            ).all()
            for role in existing_roles:
                db_session.delete(role)
            
            # Add new roles
            for role_name in request.roles:
                role = db_session.query(Role).filter(Role.name == role_name).first()
                if role:
                    user_role = UserRole(
                        id=str(uuid.uuid4()),
                        user_id=user_id,
                        role_id=role.id,
                        assigned_at=datetime.now(),
                        assigned_by=current_user["id"]
                    )
                    db_session.add(user_role)
        
        db_session.commit()
        db_session.refresh(user_obj)
        
        # Get updated user with roles
        updated_user = auth_manager.get_user_by_id(user_id, db_session)
        
        logger.info(f"User updated by admin: {user_id}")
        
        return UserResponse(
            id=updated_user["id"],
            username=updated_user["username"],
            email=updated_user["email"],
            first_name=updated_user["first_name"],
            last_name=updated_user["last_name"],
            phone=updated_user["phone"],
            is_active=updated_user["is_active"],
            roles=updated_user["roles"],
            created_at=updated_user["created_at"],
            updated_at=updated_user["updated_at"],
            last_login=updated_user.get("last_login")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user {user_id}: {e}")
        db_session.rollback()
        raise HTTPException(status_code=500, detail="Failed to update user")

# Role management endpoints
@app.post("/roles", response_model=RoleResponse, status_code=201, tags=["Role Management"])
async def create_role(
    request: RoleCreateRequest,
    current_user: Dict[str, Any] = Depends(require_role("admin")),
    db_session: Session = Depends(get_db_session)
):
    """Create a new role (admin only)."""
    try:
        # Check if role already exists
        existing_role = db_session.query(Role).filter(Role.name == request.name).first()
        if existing_role:
            raise HTTPException(status_code=400, detail="Role already exists")
        
        # Create role
        role = Role(
            id=str(uuid.uuid4()),
            name=request.name,
            description=request.description,
            permissions=request.permissions,
            is_active=request.is_active,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=current_user["id"]
        )
        
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)
        
        logger.info(f"Role created: {role.id}")
        
        return RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            permissions=role.permissions,
            is_active=role.is_active,
            created_at=role.created_at,
            updated_at=role.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create role: {e}")
        db_session.rollback()
        raise HTTPException(status_code=500, detail="Failed to create role")

@app.get("/roles", response_model=List[RoleResponse], tags=["Role Management"])
async def list_roles(
    skip: int = Query(0, ge=0, description="Number of roles to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of roles to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db_session: Session = Depends(get_db_session)
):
    """List roles with optional filtering."""
    try:
        query = db_session.query(Role)
        
        if is_active is not None:
            query = query.filter(Role.is_active == is_active)
        
        roles = query.offset(skip).limit(limit).all()
        
        return [
            RoleResponse(
                id=role.id,
                name=role.name,
                description=role.description,
                permissions=role.permissions,
                is_active=role.is_active,
                created_at=role.created_at,
                updated_at=role.updated_at
            )
            for role in roles
        ]
        
    except Exception as e:
        logger.error(f"Failed to list roles: {e}")
        raise HTTPException(status_code=500, detail="Failed to list roles")

# Session management endpoints
@app.get("/sessions", response_model=List[UserSessionResponse], tags=["Session Management"])
async def list_user_sessions(
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db_session: Session = Depends(get_db_session)
):
    """List current user's active sessions."""
    try:
        sessions = db_session.query(UserSession).filter(
            UserSession.user_id == current_user["id"],
            UserSession.is_active == True,
            UserSession.expires_at > datetime.now()
        ).order_by(UserSession.created_at.desc()).all()
        
        return [
            UserSessionResponse(
                id=session.id,
                user_id=session.user_id,
                session_token=session.session_token,
                ip_address=session.ip_address,
                user_agent=session.user_agent,
                created_at=session.created_at,
                expires_at=session.expires_at,
                is_active=session.is_active
            )
            for session in sessions
        ]
        
    except Exception as e:
        logger.error(f"Failed to list user sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to list user sessions")

@app.delete("/sessions/{session_id}", status_code=204, tags=["Session Management"])
async def revoke_session(
    session_id: str = Path(..., description="Session ID"),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db_session: Session = Depends(get_db_session)
):
    """Revoke a specific session."""
    try:
        session = db_session.query(UserSession).filter(
            UserSession.id == session_id,
            UserSession.user_id == current_user["id"]
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session.is_active = False
        session.updated_at = datetime.now()
        
        db_session.commit()
        
        logger.info(f"Session revoked: {session_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to revoke session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to revoke session")

# Statistics and analytics endpoints
@app.get("/stats", tags=["Analytics"])
async def get_auth_statistics(
    current_user: Dict[str, Any] = Depends(require_role("admin")),
    db_session: Session = Depends(get_db_session)
):
    """Get authentication service statistics (admin only)."""
    try:
        total_users = db_session.query(User).count()
        active_users = db_session.query(User).filter(User.is_active == True).count()
        total_roles = db_session.query(Role).count()
        active_sessions = db_session.query(UserSession).filter(
            UserSession.is_active == True,
            UserSession.expires_at > datetime.now()
        ).count()
        
        # Recent registrations
        recent_registrations = db_session.query(User).filter(
            User.created_at >= datetime.now() - timedelta(days=7)
        ).count()
        
        # Recent logins
        recent_logins = db_session.query(User).filter(
            User.last_login >= datetime.now() - timedelta(days=7)
        ).count()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users,
            "total_roles": total_roles,
            "active_sessions": active_sessions,
            "recent_registrations_7d": recent_registrations,
            "recent_logins_7d": recent_logins,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get auth statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get auth statistics")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now().isoformat(),
            "path": request.url.path
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat(),
            "path": request.url.path
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
