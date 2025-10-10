"""
Fixed Appwrite Authentication Middleware
Phase 5: Properly handles frontend Appwrite client authentication
"""

from fastapi import Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
import logging
from typing import Optional, Dict, Any

from appwrite_config import appwrite_config
from appwrite.exception import AppwriteException
from user_sync import UserSyncService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FixedAppwriteAuthMiddleware(BaseHTTPMiddleware):
    """
    Fixed middleware that properly handles frontend Appwrite authentication
    """
    
    def __init__(self, app, protected_paths: list = None):
        super().__init__(app)
        self.protected_paths = protected_paths or ["/api/"]
        self.user_sync_service = UserSyncService()
        self.security = HTTPBearer(auto_error=False)
        
    async def dispatch(self, request: Request, call_next):
        """
        Process request - check authentication for protected paths
        """
        
        # Skip authentication for non-protected paths
        if not self._is_protected_path(request.url.path):
            return await call_next(request)
            
        # Skip OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
            
        try:
            # Extract and validate authentication
            user_data = await self._authenticate_request(request)
            
            if not user_data:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Authentication required - please login"}
                )
            
            # Add user data to request state for use in endpoints
            request.state.user = user_data
            
            return await call_next(request)
            
        except Exception as e:
            logger.error(f"Authentication middleware error: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Authentication service error"}
            )
    
    def _is_protected_path(self, path: str) -> bool:
        """Check if path requires authentication"""
        # Allow public endpoints
        public_paths = [
            "/docs", "/redoc", "/openapi.json",
            "/", "/health", "/api/auth/login", "/api/auth/register",
            "/api/public", "/uploads"
        ]
        
        if any(path.startswith(public) for public in public_paths):
            return False
            
        return any(path.startswith(protected) for protected in self.protected_paths)
    
    async def _authenticate_request(self, request: Request) -> Optional[Dict[str, Any]]:
        """
        Extract and validate authentication from request
        Returns user data if authentication successful
        """
        
        try:
            # Method 1: Try Authorization header (Bearer token)
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[7:]  # Remove "Bearer " prefix
                logger.info(f"Found Authorization header with token: {token[:20]}...")
                user_data = await self._validate_bearer_token(token)
                if user_data:
                    return user_data
            
            # Method 2: Try session cookies
            session_cookies = self._extract_session_from_cookies(request)
            if session_cookies:
                logger.info(f"Found session cookies: {list(session_cookies.keys())}")
                user_data = await self._validate_session_cookies(session_cookies)
                if user_data:
                    return user_data
            
            # Method 3: Try query parameters
            session_query = request.query_params.get('session')
            if session_query:
                logger.info("Found session in query parameters")
                user_data = await self._validate_session_string(session_query)
                if user_data:
                    return user_data
                    
            logger.warning("No valid authentication credentials found in request")
            return None
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return None
    
    async def _validate_bearer_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate Bearer token (JWT or session secret)
        """
        try:
            # Create session client with the token
            session_client = appwrite_config.create_session_client(token)
            account_service = appwrite_config.get_account_service(session_client)
            
            # Get current user from Appwrite
            appwrite_user = account_service.get()
            
            logger.info(f"Successfully authenticated user: {appwrite_user.get('email', 'unknown')}")
            
            # Sync user to our database
            db_user, created = await self.user_sync_service.sync_user_from_appwrite(
                appwrite_user.get('$id'), token
            )
            
            return {
                'appwrite_user': appwrite_user,
                'db_user': db_user,
                'user_id': db_user.id if db_user else None,
                'appwrite_user_id': appwrite_user.get('$id')
            }
            
        except AppwriteException as e:
            logger.error(f"Appwrite authentication failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return None
    
    async def _validate_session_cookies(self, cookies: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        Validate session from cookies
        """
        try:
            # Appwrite typically stores session in cookies like:
            # a_session_<project_id> = session_secret
            session_secret = None
            
            for key, value in cookies.items():
                if key.startswith('a_session_') or key == 'appwrite-session':
                    session_secret = value
                    break
            
            if session_secret:
                return await self._validate_session_string(session_secret)
                
            return None
            
        except Exception as e:
            logger.error(f"Cookie validation error: {e}")
            return None
    
    async def _validate_session_string(self, session_secret: str) -> Optional[Dict[str, Any]]:
        """
        Validate session secret string
        """
        try:
            session_client = appwrite_config.create_session_client(session_secret)
            account_service = appwrite_config.get_account_service(session_client)
            
            appwrite_user = account_service.get()
            db_user, created = await self.user_sync_service.sync_user_from_appwrite(
                appwrite_user.get('$id'), session_secret
            )
            
            return {
                'appwrite_user': appwrite_user,
                'db_user': db_user,
                'user_id': db_user.id if db_user else None,
                'appwrite_user_id': appwrite_user.get('$id')
            }
            
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return None
    
    def _extract_session_from_cookies(self, request: Request) -> Dict[str, str]:
        """
        Extract potential session cookies from request
        """
        cookies = {}
        if hasattr(request, 'cookies'):
            for key, value in request.cookies.items():
                if 'session' in key.lower() or 'appwrite' in key.lower():
                    cookies[key] = value
        return cookies

# Dependency function for getting current user in endpoints
async def get_current_user_fixed(request: Request) -> Dict[str, Any]:
    """
    FastAPI dependency to get current authenticated user
    """
    if not hasattr(request.state, 'user') or not request.state.user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required - please login"
        )
    
    return request.state.user

# Optional authentication dependency
async def get_current_user_optional_fixed(request: Request) -> Optional[Dict[str, Any]]:
    """
    FastAPI dependency to get current user (optional)
    Returns None if not authenticated
    """
    if hasattr(request.state, 'user'):
        return request.state.user
    return None