# Testing Your PostgreSQL Integration

## Quick Start

### 1. Start the Backend Server

```bash
cd /Users/ankushchhabra/Downloads/Social-Hub/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
✓ Database tables created successfully
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## API Testing with cURL

### Test 1: Health Check
```bash
curl http://localhost:8000/health
```
Expected response:
```json
{"message": "API is healthy and running!"}
```

### Test 2: Register a New User
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "full_name": "Test User",
    "password": "password123"
  }'
```

Expected response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "testuser@example.com",
    "full_name": "Test User",
    ...
  }
}
```

✅ **This means:**
- User created in `users` table
- Password hashed and stored
- JWT token generated
- All data persisted in PostgreSQL

---

### Test 3: Login User
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "password123"
  }'
```

✅ **This queries the database and verifies credentials**

---

### Test 4: Get Current User Profile
```bash
# Replace TOKEN with actual token from register response
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

✅ **This queries user by email from JWT token**

---

### Test 5: Update User Profile
```bash
curl -X PUT http://localhost:8000/auth/profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "full_name": "Updated Name",
    "bio": "Software Engineer",
    "location": "San Francisco",
    "phone": "+1-555-0123"
  }'
```

✅ **This updates user fields in PostgreSQL**

---

## PostgreSQL Direct Testing

### Check Tables Were Created
```bash
psql -U socialhub -d socialhub_db -c "\dt"
```

Output:
```
              List of relations
 Schema |      Name       | Type  |   Owner   
--------+-----------------+-------+-----------
 public | chat_messages   | table | socialhub
 public | group_members   | table | socialhub
 public | groups          | table | socialhub
 public | pinned_messages | table | socialhub
 public | users           | table | socialhub
(5 rows)
```

### View Users in Database
```bash
psql -U socialhub -d socialhub_db -c "SELECT id, email, full_name, created_at FROM users;"
```

### View User Details
```bash
psql -U socialhub -d socialhub_db -c "SELECT * FROM users WHERE email = 'testuser@example.com';"
```

### Count Total Users
```bash
psql -U socialhub -d socialhub_db -c "SELECT COUNT(*) as total_users FROM users;"
```

### View Table Schema
```bash
psql -U socialhub -d socialhub_db -c "\d users"
```

Shows all columns, types, constraints, and indexes

---

## Testing Database Relationships

### Create a Test Group

```bash
# First, get a valid token from a user
TOKEN="your_jwt_token"

# Create a group (assuming endpoint exists)
curl -X POST http://localhost:8000/groups/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Python Developers",
    "description": "A group for Python developers",
    "invited_user_ids": [2, 3]
  }'
```

### Verify in PostgreSQL

```bash
# See all groups
psql -U socialhub -d socialhub_db -c "SELECT id, name, created_by, created_at FROM groups;"

# See group members
psql -U socialhub -d socialhub_db -c "
  SELECT 
    g.name as group_name, 
    u.full_name as member_name, 
    gm.joined_at 
  FROM groups g
  JOIN group_members gm ON g.id = gm.group_id
  JOIN users u ON gm.user_id = u.id;
"
```

---

## Python Testing

Create a file `test_db.py`:

```python
from backend.database import SessionLocal, User, Group, GroupMember
from backend.crud import get_user_by_email, create_user, get_user_groups
from backend.schemas import UserRegistration

# Get database session
db = SessionLocal()

# Test 1: Get total users
user_count = db.query(User).count()
print(f"✅ Total users in database: {user_count}")

# Test 2: Find a specific user
user = get_user_by_email(db, "testuser@example.com")
if user:
    print(f"✅ Found user: {user.email} (ID: {user.id})")
else:
    print("❌ User not found")

# Test 3: Get user's groups
if user:
    groups = get_user_groups(db, user.id)
    print(f"✅ User is member of {len(groups)} groups")
    for group in groups:
        print(f"   - {group.name} (created by {group.creator.full_name})")

# Test 4: Count groups
group_count = db.query(Group).count()
print(f"✅ Total groups: {group_count}")

# Test 5: List all active users
active_users = db.query(User).filter(User.is_active == True).all()
print(f"✅ Active users:")
for user in active_users:
    print(f"   - {user.full_name} ({user.email})")

db.close()
```

Run it:
```bash
cd /Users/ankushchhabra/Downloads/Social-Hub/backend
python test_db.py
```

---

## Automated Testing

Create `test_api.py`:

```python
import requests
import json

BASE_URL = "http://localhost:8000"

def test_registration():
    """Test user registration"""
    response = requests.post(f"{BASE_URL}/auth/register", json={
        "email": f"test{int(time.time())}@example.com",
        "full_name": "Test User",
        "password": "testpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    print("✅ Registration test passed")
    return data["access_token"]

def test_get_profile(token):
    """Test getting user profile"""
    response = requests.get(
        f"{BASE_URL}/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    print("✅ Get profile test passed")

def test_update_profile(token):
    """Test updating profile"""
    response = requests.put(
        f"{BASE_URL}/auth/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "full_name": "Updated Name",
            "bio": "Test bio",
            "location": "Test City",
            "phone": "+1234567890"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"
    print("✅ Update profile test passed")

if __name__ == "__main__":
    import time
    token = test_registration()
    test_get_profile(token)
    test_update_profile(token)
    print("\n✅ All tests passed!")
```

Run it:
```bash
cd /Users/ankushchhabra/Downloads/Social-Hub/backend
pip install requests
python test_api.py
```

---

## Debugging Database Issues

### Problem: "No such table"
```python
# Recreate tables
from database import create_tables
create_tables()
```

### Problem: Connection Error
```bash
# Check if PostgreSQL is running
psql -U socialhub -d socialhub_db -c "SELECT 1;"
```

### Problem: Foreign Key Error
```bash
# Check if referenced record exists
psql -U socialhub -d socialhub_db -c "
  SELECT * FROM group_members 
  WHERE group_id = 999 OR user_id = 999;
"
```

### Problem: Out of Memory
```bash
# Check connection pool status
psql -U socialhub -d socialhub_db -c "
  SELECT datname, count(*) FROM pg_stat_activity 
  GROUP BY datname;
"
```

---

## Performance Testing

### Load Test: Create 100 Users

```python
import time
from backend.database import SessionLocal
from backend.schemas import UserRegistration
from backend.crud import create_user

db = SessionLocal()
start_time = time.time()

for i in range(100):
    user_data = UserRegistration(
        email=f"user{i}@example.com",
        full_name=f"User {i}",
        password="testpass123"
    )
    create_user(db, user_data)
    if (i + 1) % 10 == 0:
        print(f"Created {i + 1} users...")

elapsed = time.time() - start_time
print(f"✅ Created 100 users in {elapsed:.2f} seconds ({100/elapsed:.0f} users/sec)")

db.close()
```

---

## Monitoring

### View Active Connections
```bash
psql -U socialhub -d socialhub_db -c "
  SELECT pid, usename, application_name, state 
  FROM pg_stat_activity;
"
```

### View Slow Queries
```bash
psql -U socialhub -d socialhub_db -c "
  SELECT query, calls, mean_exec_time 
  FROM pg_stat_statements 
  ORDER BY mean_exec_time DESC 
  LIMIT 10;
"
```

---

## Summary Checklist

- ✅ PostgreSQL running: `psql -U socialhub -d socialhub_db -c "SELECT 1;"`
- ✅ All 5 tables created: `psql -U socialhub -d socialhub_db -c "\dt"`
- ✅ Backend can connect: `python -c "from database import SessionLocal; SessionLocal()"`
- ✅ API responds: `curl http://localhost:8000/health`
- ✅ Users stored in DB: `psql -U socialhub -d socialhub_db -c "SELECT COUNT(*) FROM users;"`
- ✅ Relationships work: `psql -U socialhub -d socialhub_db -c "SELECT g.name FROM groups g JOIN group_members gm ON g.id = gm.group_id LIMIT 1;"`

**Everything working? You're ready to scale! 🚀**
