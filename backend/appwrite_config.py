"""
Appwrite Configuration and Client Setup
Phase 3: User Data Sync & Authentication Integration
"""

import os
from appwrite.client import Client
from appwrite.services.users import Users
from appwrite.services.account import Account
from appwrite.exception import AppwriteException
from typing import Optional

class AppwriteConfig:
    """
    Centralized Appwrite configuration management
    """
    
    def __init__(self):
        # Appwrite Configuration from environment variables
        self.endpoint = os.getenv("APPWRITE_ENDPOINT", "http://localhost/v1")
        self.project_id = os.getenv("APPWRITE_PROJECT_ID", "social-hub")
        self.api_key = os.getenv("APPWRITE_API_KEY", "your-appwrite-api-key-here")
        
        # Initialize admin client for server-side operations
        self.admin_client = self._create_admin_client()
        
    def _create_admin_client(self) -> Client:
        """
        Create admin client with API key for server-side operations
        This bypasses rate limits and can perform admin actions
        """
        client = Client()
        client.set_endpoint(self.endpoint)
        client.set_project(self.project_id)
        client.set_key(self.api_key)
        return client
        
    def create_session_client(self, session_secret: Optional[str] = None) -> Client:
        """
        Create session client for user-specific operations
        Each request should have its own session client
        """
        client = Client()
        client.set_endpoint(self.endpoint)
        client.set_project(self.project_id)
        
        if session_secret:
            client.set_session(session_secret)
            
        return client
        
    def get_users_service(self, client: Optional[Client] = None) -> Users:
        """
        Get Users service instance
        """
        return Users(client or self.admin_client)
        
    def get_account_service(self, client: Client) -> Account:
        """
        Get Account service instance for session-based operations
        """
        return Account(client)

# Global instance
appwrite_config = AppwriteConfig()