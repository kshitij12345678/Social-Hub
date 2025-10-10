"""
User Synchronization Service
Phase 3: Appwrite to Backend Database Sync
Maps Appwrite users to existing database schema
"""

from typing import Optional, Dict, Any, Tuple
from datetime import datetime
import logging
import json

try:
    from appwrite.exception import AppwriteException
    from appwrite.services.users import Users
    from appwrite.services.account import Account
except ImportError:
    # Handle case where appwrite is not yet installed
    class AppwriteException(Exception):
        pass

from sqlalchemy.orm import Session
from database import User, SessionLocal, AuthProvider
from appwrite_config import appwrite_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserSyncService:
    """
    Service to synchronize Appwrite authenticated users with existing database schema
    Maps Appwrite data to: full_name, email, google_id, profile_picture_url, etc.
    """
    
    def __init__(self):
        try:
            self.users_service = appwrite_config.get_users_service()
        except:
            self.users_service = None
            logger.warning("Appwrite service not available - check installation")
        
    async def sync_user_from_appwrite(
        self, 
        appwrite_user_id: str, 
        session_secret: Optional[str] = None
    ) -> Tuple[Optional[User], bool]:
        """
        Sync a user from Appwrite to existing local database schema
        Uses google_id field to store appwrite_user_id for identification
        
        Args:
            appwrite_user_id: Appwrite user ID
            session_secret: Optional session secret for user-specific operations
            
        Returns:
            Tuple of (User object, was_created_flag)
        """
        if not self.users_service:
            logger.error("Appwrite service not available")
            return None, False
            
        db = SessionLocal()
        try:
            # Check if user already exists (using google_id field to store appwrite_user_id)
            existing_user = db.query(User).filter(
                User.google_id == appwrite_user_id
            ).first()
            
            if existing_user:
                logger.info(f"User {appwrite_user_id} already exists in database")
                return existing_user, False
                
            # Fetch user details from Appwrite
            try:
                appwrite_user = self.users_service.get(appwrite_user_id)
                logger.info(f"Fetched user from Appwrite: {appwrite_user.get('email', 'no-email')}")
                
                # Extract user preferences if session is available
                preferences = {}
                if session_secret:
                    preferences = await self._get_user_preferences(session_secret)
                
                # Create new user mapping to existing database schema
                new_user = User(
                    full_name=appwrite_user.get('name', ''),
                    email=appwrite_user.get('email', ''),
                    google_id=appwrite_user_id,  # Store Appwrite user ID here
                    auth_provider=AuthProvider.GOOGLE,  # Mark as external auth
                    hashed_password=None,  # No password for Appwrite users
                    profile_picture_url=preferences.get('profile_picture', '') or appwrite_user.get('prefs', {}).get('avatar', ''),
                    bio=preferences.get('bio', '') or appwrite_user.get('prefs', {}).get('bio', ''),
                    location=preferences.get('location', '') or appwrite_user.get('prefs', {}).get('location', ''),
                    phone=appwrite_user.get('phone', ''),
                    education_school=preferences.get('education_school', ''),
                    education_degree=preferences.get('education_degree', ''),
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
                
                logger.info(f"Created new user in database: {new_user.email}")
                return new_user, True
                
            except AppwriteException as e:
                logger.error(f"Failed to fetch user from Appwrite: {e}")
                return None, False
                
        except Exception as e:
            logger.error(f"Error syncing user: {e}")
            db.rollback()
            return None, False
        finally:
            db.close()
    
    async def _get_user_preferences(self, session_secret: str) -> Dict[str, Any]:
        """
        Get user preferences using session client
        """
        try:
            session_client = appwrite_config.create_session_client(session_secret)
            account_service = appwrite_config.get_account_service(session_client)
            
            preferences = account_service.get_prefs()
            return preferences if isinstance(preferences, dict) else {}
            
        except Exception as e:
            logger.warning(f"Could not fetch user preferences: {e}")
            return {}
    
    async def ensure_user_exists(
        self, 
        appwrite_user_id: str, 
        session_secret: Optional[str] = None
    ) -> Optional[User]:
        """
        Ensure user exists in local database, sync from Appwrite if needed
        This is the main method to call from middleware
        """
        user, was_created = await self.sync_user_from_appwrite(
            appwrite_user_id, session_secret
        )
        
        if user and was_created:
            logger.info(f"Successfully synced new user: {user.email}")
        elif user:
            logger.info(f"User already exists: {user.email}")
        else:
            logger.warning(f"Could not sync user with ID: {appwrite_user_id}")
            
        return user
    
    async def update_user_from_appwrite(
        self, 
        appwrite_user_id: str, 
        session_secret: Optional[str] = None
    ) -> Optional[User]:
        """
        Update existing user data from Appwrite
        """
        if not self.users_service:
            return None
            
        db = SessionLocal()
        try:
            # Find user by google_id (where we store appwrite_user_id)
            user = db.query(User).filter(
                User.google_id == appwrite_user_id
            ).first()
            
            if not user:
                logger.warning(f"User {appwrite_user_id} not found for update")
                return None
                
            # Fetch latest data from Appwrite
            try:
                appwrite_user = self.users_service.get(appwrite_user_id)
                preferences = {}
                if session_secret:
                    preferences = await self._get_user_preferences(session_secret)
                
                # Update user fields mapping to existing schema
                user.email = appwrite_user.get('email', user.email)
                user.full_name = appwrite_user.get('name', user.full_name)
                user.phone = appwrite_user.get('phone', user.phone)
                user.updated_at = datetime.utcnow()
                
                # Update preferences if available
                if preferences:
                    user.profile_picture_url = preferences.get('profile_picture', user.profile_picture_url)
                    user.bio = preferences.get('bio', user.bio)
                    user.location = preferences.get('location', user.location)
                    user.education_school = preferences.get('education_school', user.education_school)
                    user.education_degree = preferences.get('education_degree', user.education_degree)
                
                db.commit()
                db.refresh(user)
                
                logger.info(f"Updated user: {user.email}")
                return user
                
            except Exception as e:
                logger.error(f"Failed to update user from Appwrite: {e}")
                return user  # Return existing user without updates
                
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            db.rollback()
            return None
        finally:
            db.close()

# Global instance
user_sync_service = UserSyncService()