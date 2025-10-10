"""
Authentication Middleware
Phase 3: FastAPI middleware for Appwrite session verification and user sync
"""

import logging
from typing import Optional, Tuple
from datetime import datetime, timezone
import json

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from appwrite_config import appwrite_config
from user_sync import user_sync_service
from database import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AppwriteAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle Appwrite authentication and user synchronization
    
    This middleware:
    1. Extracts Appwrite session from cookies or Authorization header
    2. Verifies session with Appwrite
    3. Syncs user data to local database
    4. Adds user info to request state
    """
    
    def __init__(self, app, protected_paths: Optional[list] = None):
        super().__init__(app)
        self.protected_paths = protected_paths or [
            "/api/posts",
            "/api/profile",
            "/api/feed",
            "/api/messages",
            "/api/notifications"
        ]
        
    async def dispatch(self, request: Request, call_next):
        # Skip authentication for non-protected paths
        if not self._is_protected_path(request.url.path):
            return await call_next(request)
            
        # Extract session information
        session_info = self._extract_session(request)
        
        if not session_info:
            # No session found - return 401 for protected paths
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authentication required"}
            )
            
        session_secret, user_id = session_info
        
        # Verify session and sync user
        try:
            user = await self._verify_and_sync_user(session_secret, user_id)
            
            if not user:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Invalid session or user not found"}
                )
                
            # Add user info to request state
            request.state.current_user = user
            request.state.session_secret = session_secret
            request.state.is_authenticated = True
            
            logger.info(f"Authenticated user: {user.username}")
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Authentication service error"}
            )
            
        return await call_next(request)
    
    def _is_protected_path(self, path: str) -> bool:
        """
        Check if the path requires authentication
        """
        # Allow public endpoints
        public_paths = [
            "/docs", "/redoc", "/openapi.json",
            "/", "/health", "/api/auth/login", "/api/auth/register",
            "/api/public"
        ]
        
        if path in public_paths or path.startswith("/static"):
            return False
            
        # Check if path matches protected patterns
        for protected_path in self.protected_paths:
            if path.startswith(protected_path):
                return True
                
        return False
    
    def _extract_session(self, request: Request) -> Optional[Tuple[str, str]]:
        """
        Extract session from cookies or Authorization header
        
        Returns:
            Tuple of (session_secret, user_id) or None
        """
        # Method 1: From cookie (SSR style)
        project_id = appwrite_config.project_id
        cookie_name = f"a_session_{project_id}"
        session_secret = request.cookies.get(cookie_name)
        
        if session_secret:
            # For cookie-based sessions, we need to verify to get user ID
            user_id = self._get_user_id_from_session(session_secret)
            if user_id:
                return session_secret, user_id
        
        # Method 2: From Authorization header (JWT style)
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split("Bearer ")[1]
            
            # Check if it's a JWT token
            user_id = self._extract_user_id_from_jwt(token)
            if user_id:
                return token, user_id
                
            # Or treat as session secret
            user_id = self._get_user_id_from_session(token)
            if user_id:
                return token, user_id
        
        # Method 3: From custom header
        session_header = request.headers.get("X-Appwrite-Session")
        if session_header:
            user_id = self._get_user_id_from_session(session_header)
            if user_id:
                return session_header, user_id
        
        return None
    
    def _get_user_id_from_session(self, session_secret: str) -> Optional[str]:
        """
        Get user ID from session secret by making request to Appwrite
        """
        try:
            session_client = appwrite_config.create_session_client(session_secret)
            account_service = appwrite_config.get_account_service(session_client)
            
            account = account_service.get()
            return account.get('$id')
            
        except Exception as e:
            logger.warning(f"Could not get user ID from session: {e}")
            return None
    
    def _extract_user_id_from_jwt(self, jwt_token: str) -> Optional[str]:
        """
        Extract user ID from JWT token
        Note: This is a simplified version. In production, you should properly validate JWT
        """
        try:
            import base64
            import json
            
            # Split JWT and decode payload
            parts = jwt_token.split('.')
            if len(parts) != 3:
                return None
                
            # Add padding if necessary
            payload = parts[1]
            padding = len(payload) % 4
            if padding:
                payload += '=' * (4 - padding)
                
            decoded = base64.urlsafe_b64decode(payload)
            payload_data = json.loads(decoded)
            
            return payload_data.get('userId')
            
        except Exception as e:
            logger.warning(f"Could not extract user ID from JWT: {e}")
            return None
    
    async def _verify_and_sync_user(
        self, 
        session_secret: str, 
        user_id: str
    ) -> Optional[User]:
        """
        Verify session and sync user to local database
        """
        try:
            # Verify session is still valid by making account request
            session_client = appwrite_config.create_session_client(session_secret)
            account_service = appwrite_config.get_account_service(session_client)
            
            account = account_service.get()
            if not account or account.get('$id') != user_id:
                logger.warning("Session verification failed")
                return None
            
            # Sync user to local database
            user = await user_sync_service.ensure_user_exists(user_id, session_secret)
            return user
            
        except Exception as e:
            logger.error(f"Session verification failed: {e}")
            return None

class AppwriteBearerAuth(HTTPBearer):
    """
    Simplified bearer token authentication for API endpoints
    """
    
    async def __call__(self, request: Request) -> Optional[User]:
        try:
            credentials: HTTPAuthorizationCredentials = await super().__call__(request)
            
            if not credentials:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication credentials missing"
                )
            
            # Extract user ID from token
            user_id = self._extract_user_id_from_token(credentials.credentials)
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token format"
                )
            
            # Verify session and sync user
            user = await self._verify_and_sync_user(credentials.credentials, user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid session or user not found"
                )
            
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Bearer auth error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service error"
            )
    
    def _extract_user_id_from_token(self, token: str) -> Optional[str]:
        """
        Extract user ID from token (session secret or JWT)
        """
        # Try JWT first
        try:
            import base64
            import json
            
            parts = token.split('.')
            if len(parts) == 3:
                payload = parts[1]
                padding = len(payload) % 4
                if padding:
                    payload += '=' * (4 - padding)
                    
                decoded = base64.urlsafe_b64decode(payload)
                payload_data = json.loads(decoded)
                return payload_data.get('userId')
        except:
            pass
        
        # Try session verification
        try:
            session_client = appwrite_config.create_session_client(token)
            account_service = appwrite_config.get_account_service(session_client)
            account = account_service.get()
            return account.get('$id')
        except:
            pass
            
        return None
    
    async def _verify_and_sync_user(
        self, 
        session_secret: str, 
        user_id: str
    ) -> Optional[User]:
        """
        Verify session and sync user to local database
        """
        try:
            session_client = appwrite_config.create_session_client(session_secret)
            account_service = appwrite_config.get_account_service(session_client)
            
            account = account_service.get()
            if not account or account.get('$id') != user_id:
                return None
            
            user = await user_sync_service.ensure_user_exists(user_id, session_secret)
            return user
            
        except Exception as e:
            logger.error(f"Session verification failed: {e}")
            return None

# Create global instances
appwrite_auth = AppwriteBearerAuth()

def get_current_user(request: Request) -> Optional[User]:
    """
    Helper function to get current user from request state
    """
    return getattr(request.state, 'current_user', None)

def is_authenticated(request: Request) -> bool:
    """
    Helper function to check if request is authenticated
    """
    return getattr(request.state, 'is_authenticated', False)