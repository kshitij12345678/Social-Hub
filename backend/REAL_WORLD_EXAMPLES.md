# Real-World Database Usage Examples

## Example 1: User Registration with PostgreSQL

```python
from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from database import get_db, User
from crud import create_user, get_user_by_email
from schemas import UserRegistration

app = FastAPI()

@app.post("/auth/register")
async def register(user: UserRegistration, db: Session = Depends(get_db)):
    """
    1. Get database session via dependency injection
    2. Check if user already exists in PostgreSQL
    3. Create new user in PostgreSQL
    4. Return token with user data
    """
    # Check if user already exists in database
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user in PostgreSQL (from crud.py)
    db_user = create_user(db, user)
    
    # Create JWT token
    access_token = create_access_token(
        data={"sub": db_user.email}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "email": db_user.email,
            "full_name": db_user.full_name
        }
    }
```

**Database operations happening:**
- ✅ Query `users` table to check if email exists
- ✅ Insert new row into `users` table with hashed password
- ✅ PostgreSQL generates auto-increment `id`
- ✅ PostgreSQL sets `created_at` and `updated_at` timestamps

---

## Example 2: User Login with Authentication

```python
from datetime import timedelta

@app.post("/auth/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    1. Query user from PostgreSQL by email
    2. Verify password hash
    3. Generate JWT token with user ID
    """
    # Query users table
    db_user = authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # User found in database, create token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": db_user.email},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(db_user)
    }
```

**Database operations:**
- ✅ SELECT * FROM users WHERE email = 'user@email.com'
- ✅ Verify hashed_password with bcrypt
- ✅ Return user object with all fields

---

## Example 3: Update User Profile

```python
@app.put("/auth/profile")
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    1. Get current authenticated user (from token)
    2. Update user fields in PostgreSQL
    3. Return updated user data
    """
    # Update fields
    current_user.full_name = profile_data.full_name
    current_user.bio = profile_data.bio
    current_user.location = profile_data.location
    current_user.phone = profile_data.phone
    
    # Commit changes to database
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.from_orm(current_user)
```

**Database operations:**
- ✅ UPDATE users SET full_name=?, bio=?, location=?, phone=? WHERE id=?
- ✅ PostgreSQL automatically updates `updated_at` timestamp
- ✅ Return refreshed user object from database

---

## Example 4: Create a Group with Members

```python
from database import Group, GroupMember

@app.post("/groups/create")
async def create_group(
    group_data: GroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    1. Create group record in PostgreSQL
    2. Add creator as first member
    3. Add invited members to group
    """
    # Create group in groups table
    db_group = Group(
        name=group_data.name,
        description=group_data.description,
        created_by=current_user.id  # Foreign key to users table
    )
    db.add(db_group)
    db.flush()  # Get the generated ID
    
    # Add creator as member
    creator_member = GroupMember(
        group_id=db_group.id,  # Foreign key to groups
        user_id=current_user.id  # Foreign key to users
    )
    db.add(creator_member)
    
    # Add invited members
    for user_id in group_data.invited_user_ids:
        member = GroupMember(
            group_id=db_group.id,
            user_id=user_id
        )
        db.add(member)
    
    # Commit all at once
    db.commit()
    db.refresh(db_group)
    
    return {"group_id": db_group.id, "name": db_group.name}
```

**Database operations:**
- ✅ INSERT INTO groups (name, description, created_by) VALUES (?, ?, ?)
- ✅ INSERT INTO group_members (group_id, user_id) VALUES (?, ?) [multiple rows]
- ✅ PostgreSQL maintains referential integrity (foreign keys)

---

## Example 5: Get User's Groups

```python
@app.get("/groups/my-groups")
async def get_my_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    1. Query groups table with JOIN on group_members
    2. Filter by current user
    3. Return all groups user is member of
    """
    # Query with relationship
    user_groups = (db.query(Group)
                   .join(GroupMember)
                   .filter(GroupMember.user_id == current_user.id)
                   .order_by(desc(Group.created_at))
                   .all())
    
    return [
        {
            "id": group.id,
            "name": group.name,
            "description": group.description,
            "creator": group.creator.full_name,
            "member_count": len(group.members),
            "created_at": group.created_at
        }
        for group in user_groups
    ]
```

**Database operations:**
- ✅ SELECT groups.* FROM groups JOIN group_members ON groups.id = group_members.group_id WHERE group_members.user_id = ?
- ✅ Access related User via group.creator (lazy loading)
- ✅ Access related GroupMembers via group.members (lazy loading)

---

## Example 6: Pin a Message

```python
from database import PinnedMessage

@app.post("/chat/pin-message")
async def pin_message(
    message_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    1. Insert pinned message record into PostgreSQL
    2. Store message metadata (room_id, room_name, message_text)
    3. Track who pinned it (pinned_by foreign key)
    """
    message_id = message_data.get("message_id")
    room_id = message_data.get("room_id")
    
    # Check if already pinned
    existing_pin = db.query(PinnedMessage).filter(
        PinnedMessage.message_id == message_id,
        PinnedMessage.room_id == room_id
    ).first()
    
    if not existing_pin:
        # Create pinned message record
        pinned_message = PinnedMessage(
            message_id=message_id,
            room_id=room_id,
            room_name=message_data.get("room_name"),
            room_type=message_data.get("room_type", "channel"),
            pinned_by=current_user.id,  # Foreign key to users
            message_text=message_data.get("message_text")
        )
        db.add(pinned_message)
        db.commit()
    
    return {"success": True, "message": "Message pinned"}
```

**Database operations:**
- ✅ INSERT INTO pinned_messages (...) VALUES (?, ?, ?, ?, ?, ?)
- ✅ Foreign key constraint: pinned_by REFERENCES users(id)
- ✅ PostgreSQL sets pinned_at timestamp automatically

---

## Example 7: Search Users

```python
@app.get("/users/search")
async def search_users(
    q: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    1. Query users table with LIKE search on name or email
    2. Filter for active users only
    3. Return limited results (10)
    """
    search_term = f"%{q}%"
    results = (db.query(User)
               .filter(
                   (User.full_name.ilike(search_term)) |
                   (User.email.ilike(search_term))
               )
               .filter(User.is_active == True)
               .limit(10)
               .all())
    
    return [
        {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "profile_picture_url": user.profile_picture_url
        }
        for user in results
    ]
```

**Database operations:**
- ✅ SELECT * FROM users WHERE (full_name ILIKE ? OR email ILIKE ?) AND is_active = TRUE LIMIT 10
- ✅ Uses PostgreSQL ILIKE for case-insensitive search
- ✅ Uses indexes on email and id for fast queries

---

## Database Connection Flow

```
FastAPI Endpoint
       ↓
Depends(get_db) → SessionLocal() → PostgreSQL Connection
       ↓
SQLAlchemy ORM builds SQL query
       ↓
PostgreSQL executes query
       ↓
Results converted to Python objects
       ↓
Response returned to client
       ↓
Session closes (connection returned to pool)
```

---

## Key Points

1. **Always use `Depends(get_db)`** - Provides auto-closing database session
2. **Use ORM models** - Don't write raw SQL
3. **Foreign keys work** - PostgreSQL enforces referential integrity
4. **Relationships automatic** - Access related objects with dot notation
5. **Timestamps automatic** - created_at and updated_at updated automatically
6. **Connection pooling** - 10 connections available for concurrent requests
7. **No data loss** - PostgreSQL persists all data across server restarts

---

## Testing Your Database

```bash
# Start your backend
cd /Users/ankushchhabra/Downloads/Social-Hub/backend
uvicorn main:app --reload

# In another terminal, test the API
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "full_name": "Test User", "password": "password123"}'

# Check data in PostgreSQL
psql -U socialhub -d socialhub_db -c "SELECT id, email, full_name FROM users;"
```
