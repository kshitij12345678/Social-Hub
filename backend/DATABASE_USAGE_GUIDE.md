# PostgreSQL Database Usage Guide

## Quick Start

Your PostgreSQL database is now configured and running. Here's how to use it in your FastAPI backend:

---

## 1. **Connection Details**

All connection details are automatically managed via environment variables in `.env`:

```
DATABASE_URL=postgresql+psycopg://socialhub:socialhub_pass@localhost:5432/socialhub_db
```

The connection is automatically established in `database.py` with connection pooling enabled.

---

## 2. **Available Models**

Your database has 5 tables with the following models:

### **User** (`users` table)
```python
User(
    id,                           # Primary key
    email,                        # Unique email (required)
    full_name,                    # User's full name
    hashed_password,              # Hashed password (nullable for Google users)
    google_id,                    # Google OAuth ID (nullable)
    auth_provider,                # 'local' or 'google'
    bio,                          # User bio/description
    profile_picture_url,          # URL to profile picture
    rocket_chat_username,         # Rocket.Chat integration
    rocket_chat_password,         # Rocket.Chat password
    education_school,             # School name
    education_degree,             # Degree info
    location,                     # User location
    phone,                        # Phone number
    is_active,                    # Account status
    created_at,                   # Timestamp
    updated_at                    # Timestamp
)
```

### **ChatMessage** (`chat_messages` table)
```python
ChatMessage(
    id,                           # UUID primary key
    user_id,                      # Foreign key to User
    message,                      # Message text
    created_at                    # Timestamp
)
```

### **Group** (`groups` table)
```python
Group(
    id,                           # Primary key
    name,                         # Group name
    description,                  # Group description
    created_by,                   # FK to User (creator)
    rocket_chat_group_id,         # Rocket.Chat group ID
    created_at,                   # Timestamp
    updated_at                    # Timestamp
)
```

### **GroupMember** (`group_members` table)
```python
GroupMember(
    id,                           # Primary key
    group_id,                     # FK to Group
    user_id,                      # FK to User
    joined_at                     # Timestamp
)
```

### **PinnedMessage** (`pinned_messages` table)
```python
PinnedMessage(
    id,                           # Primary key
    message_id,                   # Rocket.Chat message ID
    room_id,                      # Rocket.Chat room ID
    room_name,                    # Room name
    room_type,                    # 'channel', 'group', or 'dm'
    pinned_by,                    # FK to User (who pinned)
    message_text,                 # Message content
    pinned_at                     # Timestamp
)
```

---

## 3. **Using the Database in Your Endpoints**

### **Getting a Database Session**

Use the `get_db` dependency in any endpoint:

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db, User

@app.get("/example")
async def example_endpoint(db: Session = Depends(get_db)):
    # Now you have access to db
    return {"message": "OK"}
```

### **Query Examples**

#### **Create a User**
```python
from database import User, SessionLocal
from sqlalchemy.orm import Session

def create_user(db: Session, email: str, full_name: str, hashed_password: str):
    user = User(
        email=email,
        full_name=full_name,
        hashed_password=hashed_password,
        auth_provider="local"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
```

#### **Query a User by Email**
```python
def get_user(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()
```

#### **Update a User**
```python
def update_user(db: Session, user_id: int, bio: str, location: str):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.bio = bio
        user.location = location
        db.commit()
        db.refresh(user)
    return user
```

#### **Delete a User**
```python
def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return True
    return False
```

---

## 4. **Using CRUD Functions**

The `crud.py` file contains pre-built functions. Import them:

```python
from crud import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    authenticate_user,
    create_chat_message,
    get_recent_chat_messages,
    create_group,
    get_group_by_id,
    add_member_to_group,
    get_group_members,
    search_users
)
```

Example usage in endpoints:
```python
@app.post("/auth/register")
async def register(user: UserRegistration, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    db_user = create_user(db, user)
    return db_user
```

---

## 5. **Working with Relationships**

### **Access Related Objects**

```python
# Get a user and their groups
user = db.query(User).filter(User.id == user_id).first()
user_groups = user.groups  # Relationship defined in model

# Get a group and its members
group = db.query(Group).filter(Group.id == group_id).first()
members = group.members  # Relationship defined in model

# Access member's user info
for member in members:
    print(f"Member: {member.user.full_name}")
```

### **Create a Group with Members**

```python
from database import Group, GroupMember

# Create group
group = Group(
    name="Python Developers",
    description="Group for Python devs",
    created_by=user_id
)
db.add(group)
db.commit()
db.refresh(group)

# Add members
for user_id in [1, 2, 3]:
    member = GroupMember(group_id=group.id, user_id=user_id)
    db.add(member)
db.commit()
```

---

## 6. **Common Patterns**

### **Transaction with Rollback**
```python
try:
    user = User(email="new@email.com", full_name="New User")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
except Exception as e:
    db.rollback()
    raise HTTPException(status_code=500, detail=str(e))
```

### **Bulk Queries**
```python
# Get all active users
active_users = db.query(User).filter(User.is_active == True).all()

# Get users with email domain
gmail_users = db.query(User).filter(User.email.endswith("@gmail.com")).all()

# Count records
user_count = db.query(User).count()
```

### **Ordering and Limiting**
```python
from sqlalchemy import desc

# Get 10 most recent messages
recent_messages = db.query(ChatMessage)\
    .order_by(desc(ChatMessage.created_at))\
    .limit(10)\
    .all()
```

---

## 7. **Verifying Your Database**

### **Check Tables**
```bash
psql -U socialhub -d socialhub_db -c "\dt"
```

### **Check User Count**
```bash
psql -U socialhub -d socialhub_db -c "SELECT COUNT(*) FROM users;"
```

### **View Sample Data**
```bash
psql -U socialhub -d socialhub_db -c "SELECT email, full_name, created_at FROM users LIMIT 5;"
```

---

## 8. **Important Notes**

✅ **Connection pooling is enabled** - automatically handles multiple concurrent requests
✅ **Timestamps are automatic** - `created_at` and `updated_at` are handled by SQLAlchemy
✅ **Foreign keys are enforced** - PostgreSQL will prevent orphaned records
✅ **Indexes are created** - email, user_id, google_id are indexed for fast queries
✅ **Environment-based config** - Change `DATABASE_URL` in `.env` for different databases

---

## 9. **Next Steps**

1. **Update `main.py`** - Ensure all endpoints use the new database models
2. **Test endpoints** - Use PostMan or curl to test API endpoints
3. **Verify data** - Check PostgreSQL directly to confirm data is persisting
4. **Check `crud.py`** - Review CRUD functions to see if they match your schema

---

## 10. **Troubleshooting**

### **Connection Error?**
```bash
# Check if PostgreSQL is running
psql -U socialhub -d socialhub_db -c "SELECT 1;"
```

### **Table Not Found?**
```python
# Recreate tables from Python
from database import create_tables
create_tables()
```

### **Specific Query Help?**
See `crud.py` for 30+ pre-built query functions
