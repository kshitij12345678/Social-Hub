"""
Simple test for Appwrite configuration
"""

import os
import sys
sys.path.append('/home/kshitij/Downloads/Social Hub/Social-Hub/backend')

try:
    from appwrite_config import appwrite_config
    print("✅ Appwrite config loaded successfully")
    print(f"Endpoint: {appwrite_config.endpoint}")
    print(f"Project ID: {appwrite_config.project_id}")
    print(f"API Key configured: {'Yes' if appwrite_config.api_key else 'No'}")
    
    # Test client creation
    admin_client = appwrite_config.admin_client
    print("✅ Admin client created successfully")
    
    session_client = appwrite_config.create_session_client()
    print("✅ Session client created successfully")
    
    print("\n🎉 Phase 3 Appwrite integration setup complete!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()