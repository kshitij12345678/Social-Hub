"""
Test utility to understand Appwrite session structure
"""

import sys
import os
sys.path.append('/home/kshitij/Downloads/Social Hub/Social-Hub/backend')

from appwrite.client import Client
from appwrite.services.account import Account

def test_session_structure():
    """
    Test what fields are actually returned in Appwrite session
    """
    print("🔍 Testing Appwrite Session Structure")
    print("="*50)
    
    # Create client like the frontend does
    client = Client()
    client.set_endpoint('http://localhost/v1')
    client.set_project('social-hub')
    
    account = Account(client)
    
    # Let's check what methods are available
    print("Available Account methods:")
    methods = [method for method in dir(account) if not method.startswith('_')]
    for method in methods:
        print(f"  - {method}")
    
    print("\n" + "="*50)
    
    # Let's test with a simple login to an existing user
    # (This will fail due to rate limit, but we can see the expected structure)
    try:
        print("Attempting to understand session response structure...")
        print("(This may fail due to rate limit, but we can see the error details)")
        
        # Try to login with a test user
        session = account.create_email_password_session(
            email="test@example.com",
            password="password123"
        )
        
        print(f"✅ Session created successfully!")
        print(f"Session type: {type(session)}")
        print(f"Session keys: {list(session.keys()) if hasattr(session, 'keys') else 'No keys method'}")
        print(f"Session content: {session}")
        
        # Check specific fields we're looking for
        if hasattr(session, 'get'):
            print(f"secret: {session.get('secret')}")
            print(f"userId: {session.get('userId')}")
            print(f"expire: {session.get('expire')}")
        elif hasattr(session, '__dict__'):
            print(f"Session attributes: {session.__dict__}")
        
    except Exception as e:
        print(f"❌ Session creation failed: {e}")
        print(f"Error type: {type(e)}")
        
        # Let's see if we can understand the expected structure from docs or error
        print("\n🔍 Let's check the session object structure from Appwrite docs...")
        print("Expected session fields based on Appwrite documentation:")
        print("  - $id: Session ID")
        print("  - $createdAt: Creation timestamp") 
        print("  - $updatedAt: Update timestamp")
        print("  - userId: User ID")
        print("  - expire: Expiration timestamp")
        print("  - provider: Auth provider")
        print("  - providerUid: Provider user ID")
        print("  - providerAccessToken: Provider access token")
        print("  - providerAccessTokenExpiry: Token expiry")
        print("  - providerRefreshToken: Refresh token")
        print("  - ip: Client IP")
        print("  - osCode: OS code")
        print("  - osName: OS name")
        print("  - osVersion: OS version")
        print("  - clientType: Client type")
        print("  - clientCode: Client code")
        print("  - clientName: Client name")
        print("  - clientVersion: Client version")
        print("  - clientEngine: Client engine")
        print("  - clientEngineVersion: Engine version")
        print("  - deviceName: Device name")
        print("  - deviceBrand: Device brand")
        print("  - deviceModel: Device model")
        print("  - countryCode: Country code")
        print("  - countryName: Country name")
        print("  - secret: Session secret (for cookies)")

if __name__ == "__main__":
    test_session_structure()