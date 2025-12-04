# How to Use PostgreSQL Database in Your Code - Complete Guide

## 📖 Documentation Overview

Start with **DATABASE_QUICK_REFERENCE.md** for a quick cheat sheet, then dive deeper:

1. **DATABASE_QUICK_REFERENCE.md** ⭐ START HERE
   - Quick syntax for common operations
   - Pre-built CRUD functions list
   - 1-page quick reference

2. **REAL_WORLD_EXAMPLES.md** (7 practical examples)
   - User registration with database
   - User login and authentication
   - Group creation with members
   - Message pinning
   - User search
   - Database flow diagram

3. **DATABASE_USAGE_GUIDE.md** (complete reference)
   - All 5 model definitions
   - Query patterns and examples
   - Relationship usage
   - Bulk operations
   - Backup/restore

4. **TESTING_GUIDE.md** (how to test)
   - API testing with cURL
   - PostgreSQL direct testing
   - Python testing
   - Performance testing
   - Debugging guide

5. **POSTGRESQL_SETUP_COMPLETE.md** (full summary)
   - Current status
   - Files modified
   - Model overview
   - Scaling considerations
   - Troubleshooting

---

## 🎯 Quick Answer: How to Use in Your Code

### In Any FastAPI Endpoint

```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import get_db, User
from crud import create_user, get_user_by_email

app = FastAPI()

@app.post("/auth/register")
async def register(email: str, full_name: str, password: str, db: Session = Depends(get_db)):
    # 1. Check if user exists
    existing = get_user_by_email(db, email)
    if existing:
        return {"error": "User already exists"}
    
    # 2. Create new user using pre-built function
    user = create_user(db, UserRegistration(email=email, full_name=full_name, password=password))
    
    # 3. User is now in PostgreSQL database
    return {"id": user.id, "email": user.email}

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    # 1. Query database
    user = db.query(User).filter(User.id == user_id).first()
    
    # 2. Return data (SQLAlchemy converts to dict automatically)
    return user
```

### Key Points:
- ✅ Use `Depends(get_db)` to get database session
- ✅ Session auto-closes after request completes
- ✅ Use CRUD functions from `crud.py` (30+ functions available)
- ✅ For custom queries, use SQLAlchemy ORM
- ✅ Data automatically persists in PostgreSQL

---

## 📊 Database Tables and Models

```python
# All available in database.py
from database import User, ChatMessage, Group, GroupMember, PinnedMessage

# Use in queries like:
db.query(User).filter(User.email == "test@example.com").first()
db.query(Group).filter(Group.created_by == user_id).all()
db.query(ChatMessage).order_by(desc(ChatMessage.created_at)).limit(50).all()
```

---

## 🔧 Pre-Built CRUD Functions

Import from `crud.py`:

```python
from crud import (
    # User operations
    get_user_by_email,
    get_user_by_id,
    create_user,
    authenticate_user,
    create_google_user,
    
    # Group operations
    create_group,
    get_group_by_id,
    get_user_groups,
    add_member_to_group,
    remove_member_from_group,
    get_group_members,
    search_users,
    is_user_in_group,
    update_group,
    delete_group,
    
    # Message operations
    create_chat_message,
    get_recent_chat_messages,
    get_chat_messages_after
)
```

**Example usage:**
```python
# Instead of writing a query, use pre-built function
user = get_user_by_email(db, "test@example.com")
groups = get_user_groups(db, user.id)
```

---

## 💾 Common Operations

### Create/Insert
```python
# Single insert
user = User(email="new@example.com", full_name="New User")
db.add(user)
db.commit()
db.refresh(user)

# Bulk insert
users = [User(email=f"user{i}@example.com") for i in range(100)]
db.add_all(users)
db.commit()
```

### Read/Query
```python
# Get one
user = db.query(User).filter(User.id == 1).first()

# Get multiple
users = db.query(User).filter(User.is_active == True).all()

# Count
count = db.query(User).count()

# Search
results = db.query(User).filter(User.email.like("%gmail%")).all()

# Order and limit
recent = db.query(User).order_by(desc(User.created_at)).limit(10).all()
```

### Update
```python
user = db.query(User).filter(User.id == 1).first()
user.full_name = "Updated Name"
user.bio = "New bio"
db.commit()
db.refresh(user)
```

### Delete
```python
user = db.query(User).filter(User.id == 1).first()
db.delete(user)
db.commit()
```

---

## 🔗 Working with Relationships

```python
# Get a group and its members
group = db.query(Group).filter(Group.id == 1).first()
members = group.members  # List of GroupMember objects
for member in members:
    print(member.user.full_name)  # Access related user

# Get creator's info
creator = group.creator  # Related User object
print(creator.email)

# Create with relationships
group = Group(name="Developers", created_by=user_id)
db.add(group)
db.flush()

for user_id in [1, 2, 3]:
    member = GroupMember(group_id=group.id, user_id=user_id)
    db.add(member)
db.commit()
```

---

## ⚙️ Database Configuration

**Environment Variable** (in `.env`):
```
DATABASE_URL=postgresql+psycopg://socialhub:socialhub_pass@localhost:5432/socialhub_db
```

**Backend automatically uses this to:**
- ✅ Connect to PostgreSQL server
- ✅ Select correct database
- ✅ Authenticate with user credentials
- ✅ Pool connections (10 concurrent, 20 max overflow)

---

## ✅ Verification

### Verify Database is Connected
```python
from database import SessionLocal
db = SessionLocal()
print("✅ Connected to database!")
db.close()
```

### Verify Tables Exist
```bash
psql -U socialhub -d socialhub_db -c "\dt"
```

### Check Your Data
```bash
# Count users
psql -U socialhub -d socialhub_db -c "SELECT COUNT(*) FROM users;"

# View users
psql -U socialhub -d socialhub_db -c "SELECT email, full_name FROM users LIMIT 5;"
```

---

## 🚀 Getting Started

### Step 1: Start Backend
```bash
cd /Users/ankushchhabra/Downloads/Social-Hub/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 2: Register a User (Test)
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "full_name": "Test User",
    "password": "password123"
  }'
```

### Step 3: Verify in Database
```bash
psql -U socialhub -d socialhub_db -c "SELECT * FROM users WHERE email = 'testuser@example.com';"
```

### Step 4: Read Documentation
- For quick reference: **DATABASE_QUICK_REFERENCE.md**
- For examples: **REAL_WORLD_EXAMPLES.md**
- For complete guide: **DATABASE_USAGE_GUIDE.md**

---

## 📚 Documentation Files Location

All in `/Users/ankushchhabra/Downloads/Social-Hub/backend/`:

- `DATABASE_QUICK_REFERENCE.md` ⭐
- `DATABASE_USAGE_GUIDE.md`
- `REAL_WORLD_EXAMPLES.md`
- `TESTING_GUIDE.md`
- `POSTGRESQL_SETUP_COMPLETE.md`
- `HOW_TO_USE_DATABASE.md` (this file)

---

## 🆘 Common Questions

**Q: How do I use the database in an endpoint?**
A: Use `db: Session = Depends(get_db)` as a parameter. See REAL_WORLD_EXAMPLES.md

**Q: Where are the pre-built functions?**
A: All in `crud.py` - 30+ functions for users, groups, messages, etc.

**Q: How do I create a custom query?**
A: Use SQLAlchemy ORM: `db.query(User).filter(...).first()` 
See DATABASE_USAGE_GUIDE.md for examples

**Q: How do I access related objects?**
A: Use dot notation: `group.creator`, `group.members`
See DATABASE_USAGE_GUIDE.md for relationship examples

**Q: How do I test my database changes?**
A: See TESTING_GUIDE.md for cURL, Python, and PostgreSQL testing

**Q: Is my data persistent?**
A: Yes! PostgreSQL persists all data across server restarts

**Q: Can I use SQLite instead?**
A: No, already migrated to PostgreSQL. Change DATABASE_URL if needed.

---

## Next Steps

1. ✅ Read: **DATABASE_QUICK_REFERENCE.md** (2 min)
2. ✅ Read: **REAL_WORLD_EXAMPLES.md** (5 min)
3. ✅ Start Backend and register a test user
4. ✅ Verify data in PostgreSQL
5. ✅ Update your endpoints to use database
6. ✅ Reference TESTING_GUIDE.md when needed

**You're ready to use PostgreSQL!** 🚀
