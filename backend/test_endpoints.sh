#!/bin/bash

# Test script for post update and delete endpoints

BASE_URL="http://localhost:8001"

echo "Testing Social Hub API endpoints..."

# First, let's try to register a user
echo -e "\n1. Registering test user..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test User",
    "email": "test@example.com",
    "password": "testpass123"
  }')

echo "Register response: $REGISTER_RESPONSE"

# Login to get token
echo -e "\n2. Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }')

echo "Login response: $LOGIN_RESPONSE"

# Extract token
TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | grep -o '[^"]*$')
echo "Token: $TOKEN"

if [ -z "$TOKEN" ]; then
    echo "Failed to get token. Exiting."
    exit 1
fi

# Create a test post first
echo -e "\n3. Creating test post..."
CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/posts" \
  -H "Authorization: Bearer $TOKEN" \
  -F 'post={"caption":"Test post for editing","post_type":"photo"}')

echo "Create response: $CREATE_RESPONSE"

# Extract post ID
POST_ID=$(echo $CREATE_RESPONSE | grep -o '"id":[^,]*' | grep -o '[0-9]*')
echo "Post ID: $POST_ID"

if [ -z "$POST_ID" ]; then
    echo "Failed to create post. Exiting."
    exit 1
fi

# Test update endpoint
echo -e "\n4. Testing UPDATE endpoint..."
UPDATE_RESPONSE=$(curl -s -X PUT "$BASE_URL/posts/$POST_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "caption": "Updated caption via curl"
  }')

echo "Update response: $UPDATE_RESPONSE"

# Test delete endpoint
echo -e "\n5. Testing DELETE endpoint..."
DELETE_RESPONSE=$(curl -s -X DELETE "$BASE_URL/posts/$POST_ID" \
  -H "Authorization: Bearer $TOKEN")

echo "Delete response: $DELETE_RESPONSE"

echo -e "\nTest completed!"