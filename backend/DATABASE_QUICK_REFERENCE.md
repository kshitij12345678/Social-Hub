# PostgreSQL Quick Reference Card

## Connection Info
```
Host:     localhost
Port:     5432
Database: socialhub_db
User:     socialhub
Password: socialhub_pass
```

## Using Database in Code

### Get Session in Endpoint
```python
from database import get_db
from sqlalchemy.orm import Session

@app.get("/example")
async def example(db: Session = Depends(get_db)):
    # Use db for queries
    return {"status": "ok"}
```

### Create Records
```python
from database import User
user = User(email="test@example.com", full_name="Test")
db.add(user)
db.commit()
db.refresh(user)
```

### Query Records
```python
# Single record
user = db.query(User).filter(User.email == "test@example.com").first()

# Multiple records
users = db.query(User).filter(User.is_active == True).all()

# Count
count = db.query(User).count()

# Order and limit
recent = db.query(User).order_by(desc(User.created_at)).limit(10).all()
```

### Update Records
```python
user = db.query(User).filter(User.id == 1).first()
user.full_name = "New Name"
db.commit()
db.refresh(user)
```

### Delete Records
```python
user = db.query(User).filter(User.id == 1).first()
db.delete(user)
db.commit()
```

## Database Tables

| Table | Purpose | Key Fields |
|-------|---------|-----------|
| users | User accounts | id, email, full_name, hashed_password |
| groups | Group/channels | id, name, created_by |
| group_members | Group membership | group_id, user_id, joined_at |
| chat_messages | Messages | id, user_id, message, created_at |
| pinned_messages | Pinned messages | id, message_id, pinned_by, room_id |

## Pre-built CRUD Functions

```python
from crud import *

# User operations
get_user_by_email(db, email)
get_user_by_id(db, user_id)
create_user(db, user)
authenticate_user(db, email, password)

# Group operations
create_group(db, group_data, creator_id)
get_group_by_id(db, group_id)
get_user_groups(db, user_id)
add_member_to_group(db, group_id, user_id)
get_group_members(db, group_id)

# Message operations
create_chat_message(db, user_id, message_data)
get_recent_chat_messages(db, limit=50)

# Search
search_users(db, query, limit=10)
```

## Common Patterns

### Check if Record Exists
```python
exists = db.query(User).filter(User.email == "test@example.com").first() is not None
```

### Get or Create
```python
user = db.query(User).filter(User.email == email).first()
if not user:
    user = User(email=email, full_name=full_name)
    db.add(user)
    db.commit()
```

### Batch Operations
```python
users = [User(email=f"user{i}@example.com") for i in range(100)]
db.add_all(users)
db.commit()
```

### Relationships
```python
# Get related objects
group = db.query(Group).filter(Group.id == 1).first()
members = group.members  # Access related GroupMembers
creator = group.creator  # Access related User
```

## PostgreSQL Commands

### Connect
```bash
psql -U socialhub -d socialhub_db
```

### List Tables
```bash
psql -U socialhub -d socialhub_db -c "\dt"
```

### View Records
```bash
psql -U socialhub -d socialhub_db -c "SELECT * FROM users LIMIT 5;"
```

### Count Records
```bash
psql -U socialhub -d socialhub_db -c "SELECT COUNT(*) FROM users;"
```

### View Schema
```bash
psql -U socialhub -d socialhub_db -c "\d users"
```

### Query
```bash
psql -U socialhub -d socialhub_db -c "
  SELECT email, full_name, created_at FROM users ORDER BY created_at DESC;
"
```

### Backup
```bash
pg_dump -U socialhub -d socialhub_db > backup.sql
```

### Restore
```bash
psql -U socialhub -d socialhub_db < backup.sql
```

## Environment Variable

```
DATABASE_URL=postgresql+psycopg://socialhub:socialhub_pass@localhost:5432/socialhub_db
```

Location: `backend/.env`

## Test Database Connection

### Python
```python
from database import SessionLocal
db = SessionLocal()
result = db.execute("SELECT 1")
print("✅ Connected!")
db.close()
```

### Terminal
```bash
psql -U socialhub -d socialhub_db -c "SELECT 1;"
```

## Start Backend
```bash
cd /Users/ankushchhabra/Downloads/Social-Hub/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Test API
```bash
# Register user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "full_name": "Test User",
    "password": "password123"
  }'

# Check database
psql -U socialhub -d socialhub_db -c "SELECT * FROM users;"
```

## Performance Tips

- ✅ Indexes on: email, user_id, google_id, created_at
- ✅ Connection pooling: 10 connections
- ✅ Use .all() for multiple, .first() for single
- ✅ Filter early, join efficiently
- ✅ Use relationships instead of multiple queries

## Common Errors & Fixes

| Error | Fix |
|-------|-----|
| `table does not exist` | Run `create_tables()` |
| `connection refused` | Start PostgreSQL: `brew services start postgresql@15` |
| `permission denied` | Check user credentials in `.env` |
| `too many connections` | Reduce pool_size in database.py |
| `foreign key violation` | Ensure referenced record exists first |

## Documentation Files

- `DATABASE_USAGE_GUIDE.md` - Full reference
- `REAL_WORLD_EXAMPLES.md` - 7 code examples
- `TESTING_GUIDE.md` - How to test
- `POSTGRESQL_SETUP_COMPLETE.md` - Complete summary
- `DATABASE_QUICK_REFERENCE.md` - This file

---

**Setup Complete! Ready to use PostgreSQL in your FastAPI backend.** 🚀
