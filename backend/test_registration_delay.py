"""
Simple registration test with delay to avoid rate limits
"""

import time
import requests
import json

def test_registration_with_delay():
    """Test registration with proper delays"""
    
    print("⏱️  Waiting 60 seconds for rate limit to reset...")
    time.sleep(60)
    
    url = "http://localhost:8001/api/auth/register"
    headers = {"Content-Type": "application/json"}
    
    # Use unique timestamp-based email
    timestamp = int(time.time())
    data = {
        "email": f"user{timestamp}@example.com",
        "password": "password123",
        "name": f"User {timestamp}"
    }
    
    print(f"🚀 Testing registration with email: {data['email']}")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Registration successful!")
        elif response.status_code == 429:
            print("❌ Still rate limited - need to wait longer")
        else:
            print(f"❌ Registration failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_registration_with_delay()