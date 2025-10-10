"""
Phase 3 Authentication Integration Test Suite
Tests all components of the Appwrite authentication system
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8001"

class Phase3AuthTester:
    def __init__(self):
        self.results = []
        
    def log_result(self, test_name: str, success: bool, details: str = ""):
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({
            "test": test_name,
            "status": status,
            "details": details
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
    
    def test_server_health(self):
        """Test if the server is running"""
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                self.log_result("Server Health Check", True, f"Status: {response.status_code}")
                return True
            else:
                self.log_result("Server Health Check", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Server Health Check", False, f"Error: {str(e)}")
            return False
    
    def test_registration_endpoint_response(self):
        """Test that registration endpoint returns proper guidance"""
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/register",
                headers={"Content-Type": "application/json"},
                json={"email": "test@example.com", "password": "password123", "name": "Test User"},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "frontend" in data.get("message", ""):
                    self.log_result("Registration Guidance", True, "Returns proper frontend guidance")
                    return True
                else:
                    self.log_result("Registration Guidance", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_result("Registration Guidance", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_result("Registration Guidance", False, f"Error: {str(e)}")
            return False
    
    def test_protected_endpoints_require_auth(self):
        """Test that protected endpoints require authentication"""
        protected_endpoints = [
            "/api/posts",
            "/api/feed", 
            "/api/profile",
            "/api/user"
        ]
        
        all_protected = True
        for endpoint in protected_endpoints:
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
                if response.status_code == 401:
                    self.log_result(f"Protected: {endpoint}", True, "Correctly requires auth")
                else:
                    self.log_result(f"Protected: {endpoint}", False, f"Status: {response.status_code}")
                    all_protected = False
            except Exception as e:
                self.log_result(f"Protected: {endpoint}", False, f"Error: {str(e)}")
                all_protected = False
        
        return all_protected
    
    def test_public_endpoints_accessible(self):
        """Test that public endpoints are accessible"""
        public_endpoints = [
            "/",
            "/health",
            "/docs"
        ]
        
        all_public = True
        for endpoint in public_endpoints:
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
                if response.status_code == 200:
                    self.log_result(f"Public: {endpoint}", True, "Accessible without auth")
                else:
                    self.log_result(f"Public: {endpoint}", False, f"Status: {response.status_code}")
                    all_public = False
            except Exception as e:
                self.log_result(f"Public: {endpoint}", False, f"Error: {str(e)}")
                all_public = False
        
        return all_public
    
    def test_auth_middleware_integration(self):
        """Test that auth middleware is properly integrated"""
        try:
            # Test with invalid bearer token
            response = requests.get(
                f"{BASE_URL}/api/posts",
                headers={"Authorization": "Bearer invalid-token"},
                timeout=5
            )
            
            if response.status_code == 401:
                self.log_result("Auth Middleware", True, "Correctly rejects invalid tokens")
                return True
            else:
                self.log_result("Auth Middleware", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Auth Middleware", False, f"Error: {str(e)}")
            return False
    
    def test_appwrite_config(self):
        """Test Appwrite configuration"""
        try:
            # Import and test configuration
            import sys
            import os
            sys.path.append('/home/kshitij/Downloads/Social Hub/Social-Hub/backend')
            
            from appwrite_config import appwrite_config
            
            # Check configuration values
            if appwrite_config.endpoint == "http://localhost/v1":
                self.log_result("Appwrite Endpoint", True, f"Endpoint: {appwrite_config.endpoint}")
            else:
                self.log_result("Appwrite Endpoint", False, f"Unexpected endpoint: {appwrite_config.endpoint}")
                return False
            
            if appwrite_config.project_id == "social-hub":
                self.log_result("Appwrite Project ID", True, f"Project ID: {appwrite_config.project_id}")
            else:
                self.log_result("Appwrite Project ID", False, f"Unexpected project ID: {appwrite_config.project_id}")
                return False
            
            # Test client creation
            client = appwrite_config.create_session_client()
            if client:
                self.log_result("Appwrite Client Creation", True, "Session client created successfully")
                return True
            else:
                self.log_result("Appwrite Client Creation", False, "Failed to create session client")
                return False
                
        except Exception as e:
            self.log_result("Appwrite Config", False, f"Error: {str(e)}")
            return False
    
    def test_user_sync_service(self):
        """Test user sync service availability"""
        try:
            import sys
            sys.path.append('/home/kshitij/Downloads/Social Hub/Social-Hub/backend')
            
            from user_sync import user_sync_service
            
            if user_sync_service:
                self.log_result("User Sync Service", True, "Service initialized successfully")
                return True
            else:
                self.log_result("User Sync Service", False, "Service not initialized")
                return False
                
        except Exception as e:
            self.log_result("User Sync Service", False, f"Error: {str(e)}")
            return False
    
    def test_database_integration(self):
        """Test database models and connection"""
        try:
            import sys
            sys.path.append('/home/kshitij/Downloads/Social Hub/Social-Hub/backend')
            
            from database import User, SessionLocal
            
            # Test database connection
            db = SessionLocal()
            user_count = db.query(User).count()
            db.close()
            
            self.log_result("Database Connection", True, f"Connected, {user_count} users in database")
            return True
                
        except Exception as e:
            self.log_result("Database Connection", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests and provide summary"""
        print("🚀 Phase 3 Authentication Integration Test Suite")
        print("=" * 60)
        
        # Run tests in order
        tests = [
            self.test_server_health,
            self.test_appwrite_config,
            self.test_user_sync_service,
            self.test_database_integration,
            self.test_public_endpoints_accessible,
            self.test_protected_endpoints_require_auth,
            self.test_auth_middleware_integration,
            self.test_registration_endpoint_response
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                result = test()
                if result:
                    passed += 1
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
        
        print("\n" + "=" * 60)
        print(f"📊 TEST SUMMARY: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Phase 3 integration is working correctly!")
            print("\n✅ Ready for frontend integration:")
            print("   • Authentication middleware: Working")
            print("   • User sync service: Ready") 
            print("   • Protected endpoints: Secured")
            print("   • Appwrite configuration: Correct")
            print("   • Database integration: Connected")
        else:
            print("⚠️  Some tests failed. Check the details above.")
        
        return passed == total

if __name__ == "__main__":
    tester = Phase3AuthTester()
    tester.run_all_tests()