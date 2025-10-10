"""
Authentication Endpoints
Phase 3: Appwrite integration endpoints for user authentication
"""

from fastapi import APIRouter, HTTPException, status, Response, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
import logging

from appwrite_config import appwrite_config
from user_sync import user_sync_service
from auth_middleware import get_current_user, appwrite_auth
from database import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Pydantic models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class SessionResponse(BaseModel):
    message: str
    user: Dict[str, Any]
    session_expires: str

class UserProfileResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    profile_picture: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    is_verified: bool
    user_type: str

@router.post("/login", response_model=SessionResponse)
async def login(
    login_data: LoginRequest, 
    response: Response, 
    request: Request
):
    """
    Create email/password session with Appwrite and sync user to local database
    """
    try:
        # Use CLIENT-SIDE approach exactly like frontend
        from appwrite.client import Client
        from appwrite.services.account import Account
        
        client_side_client = Client()
        client_side_client.set_endpoint(appwrite_config.endpoint)
        client_side_client.set_project(appwrite_config.project_id)
        # NO API KEY - client-side authentication
        
        account_service = Account(client_side_client)
        
        # Create email/password session (exactly like frontend)
        session = account_service.create_email_password_session(
            email=login_data.email,
            password=login_data.password
        )
        
        logger.info(f"Created session for user: {login_data.email}")
        
        # Extract session details
        session_secret = session.get('secret')
        user_id = session.get('userId')
        expires = session.get('expire')
        
        if not session_secret or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid login credentials"
            )
        
        # Sync user to local database
        user = await user_sync_service.ensure_user_exists(user_id, session_secret)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to sync user data"
            )
        
        # Set session cookie
        project_id = appwrite_config.project_id
        cookie_name = f"a_session_{project_id}"
        
        response.set_cookie(
            key=cookie_name,
            value=session_secret,
            max_age=60 * 60 * 24 * 7,  # 7 days
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax"
        )
        
        return SessionResponse(
            message="Login successful",
            user={
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "profile_picture_url": user.profile_picture_url,
                "bio": user.bio,
                "location": user.location
            },
            session_expires=expires
        )
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login credentials"
        )

@router.post("/register")
async def register(
    register_data: RegisterRequest
):
    """
    Backend registration endpoint - Frontend should handle Appwrite auth directly
    This endpoint is for demonstration only - use frontend Appwrite client for real auth
    """
    return {
        "message": "Registration should be handled by frontend Appwrite client",
        "instructions": {
            "step1": "Use frontend: account.create(ID.unique(), email, password, name)",
            "step2": "Use frontend: account.createEmailPasswordSession(email, password)", 
            "step3": "Backend will auto-sync user when accessing protected endpoints",
            "note": "This avoids rate limits and follows proper client-side auth pattern"
        },
        "frontend_example": {
            "register": "await account.create(ID.unique(), email, password, name)",
            "login": "await account.createEmailPasswordSession(email, password)",
            "getUser": "await account.get()"
        }
    }

@router.post("/logout")
async def logout(response: Response, request: Request):
    """
    Logout user by clearing session cookie and invalidating Appwrite session
    """
    try:
        # Get current session
        project_id = appwrite_config.project_id
        cookie_name = f"a_session_{project_id}"
        session_secret = request.cookies.get(cookie_name)
        
        if session_secret:
            # Invalidate session with Appwrite
            try:
                session_client = appwrite_config.create_session_client(session_secret)
                account_service = appwrite_config.get_account_service(session_client)
                account_service.delete_session('current')
                logger.info("Session invalidated with Appwrite")
            except Exception as e:
                logger.warning(f"Could not invalidate Appwrite session: {e}")
        
        # Clear session cookie
        response.delete_cookie(key=cookie_name)
        
        return {"message": "Logout successful"}
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return {"message": "Logout completed"}  # Always return success for logout

@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    request: Request,
    current_user: User = Depends(appwrite_auth)
):
    """
    Get current authenticated user profile
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    return UserProfileResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        profile_picture=current_user.profile_picture,
        bio=current_user.bio,
        location=current_user.location,
        is_verified=current_user.is_verified,
        user_type=current_user.user_type
    )

@router.post("/sync-user")
async def sync_user_from_frontend(
    request: Request,
    current_user: User = Depends(appwrite_auth)
):
    """
    Sync authenticated Appwrite user to local database
    Called by frontend after successful Appwrite authentication
    """
    try:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated"
            )
        
        return {
            "message": "User synced successfully",
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "full_name": current_user.full_name,
                "profile_picture_url": current_user.profile_picture_url,
                "bio": current_user.bio,
                "location": current_user.location,
                "is_active": current_user.is_active
            }
        }
        
    except Exception as e:
        logger.error(f"User sync error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync user data"
        )

@router.get("/session/verify")
async def verify_session(request: Request):
    """
    Verify if user has valid session (works with middleware)
    """
    try:
        # Check if middleware set user
        current_user = get_current_user(request)
        
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No valid session found"
            )
        
        return {
            "valid": True,
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "full_name": current_user.full_name,
                "profile_picture_url": current_user.profile_picture_url,
                "bio": current_user.bio,
                "location": current_user.location
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session verification failed"
        )