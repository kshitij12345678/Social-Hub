# Social Hub - Rocket.Chat Integration Architecture

**Project**: Social Hub with Rocket.Chat Integration  
**Date**: November 2025  
**Focus**: Rocket.Chat Integration & SSO Only

---

## Table of Contents

1. [Software Architecture](#1-software-architecture)
2. [Backend Architecture](#2-backend-architecture)
3. [Infrastructure & Tech Stack](#3-infrastructure--tech-stack)

---

## 1. Software Architecture

### 1.1 System Overview

Social Hub is a React frontend that integrates with **Rocket.Chat** as the messaging backbone. The backend fetches conversations, messages, and user data from Rocket.Chat via REST API and displays them through a custom UI. Users are provisioned in Rocket.Chat via SSO when they register in Social Hub.

```
┌──────────────────────────────────────────────────────────┐
│           Social Hub Frontend (React)                    │
│  • Display Rocket.Chat conversations                     │
│  • Pin message management (local DB)                     │
│  • User search and directory                             │
└────────────────┬─────────────────────────────────────────┘
                 │ HTTP/REST Calls (Polling)
                 │
    ┌────────────┴─────────────┐
    │                          │
┌───▼──────────────┐   ┌──────▼──────────┐
│  Social Hub API  │   │  Social Hub DB  │
│  (FastAPI)       │   │  (SQLite)       │
│                  │   │                 │
│ • Rocket.Chat    │   │ • Users         │
│   proxies        │   │ • Pinned Msgs   │
│ • Message fetch  │   │ • SSO Creds     │
│ • Room list      │   │ • User Profiles │
│ • User directory │   │                 │
└────────┬─────────┘   └─────────────────┘
         │
         │ REST API Calls with Auth Headers
         │
┌────────▼─────────────────────────────┐
│   Rocket.Chat Server (External)       │
│   http://10.68.0.49:30082            │
│                                       │
│ • Message Storage                     │
│ • Room/Channel Management             │
│ • User Accounts                       │
│ • Thread Storage                      │
│ • DM Management                       │
└───────────────────────────────────────┘
```

### 1.2 Integration Patterns

#### **Rocket.Chat as External Service**
- Social Hub acts as a client to Rocket.Chat
- RocketChatClient wraps all Rocket.Chat REST API calls
- Backend fetches data and proxies to frontend
- No direct frontend-to-Rocket.Chat connections

#### **SSO Integration**
- User registers in Social Hub → account created in Rocket.Chat
- Credentials stored in Social Hub database
- Backend uses stored credentials for authenticated Rocket.Chat API calls
- Single username/password for both platforms

#### **HTTP REST API (Direct Calls)**
- Frontend polls backend for conversations and messages
- Backend calls Rocket.Chat REST API **on every request** (no caching currently)
- Fresh data retrieved from Rocket.Chat each time
- **Note**: Message caching infrastructure defined but not implemented yet

#### **Message Pinning (Rocket.Chat Integration)**
- Pinned messages synced with Rocket.Chat
- Composite room_id format for DMs: `dm:username`
- Social Hub maintains local cache in SQLite for performance
- Pin/unpin operations sent to Rocket.Chat REST API
- Local database mirrors Rocket.Chat pinned state

### 1.3 Data Flow Diagrams

#### **Fetching Messages from Rocket.Chat**
```
Frontend              Backend              Rocket.Chat
   │                    │                      │
   ├─ GET /chat/messages                       │
   │  (room_id, limit)  │                      │
   ├───────────────────→│                      │
   │                    ├─ Check cache (30s)  │
   │                    │                      │
   │                    ├─ If expired:         │
   │                    ├─ Call Rocket API ──→
   │                    │  /api/v1/channels.  │
   │                    │  messages?roomId=X  │
   │                    │                      │
   │                    │  ← Messages array    │
   │                    │                      │
   │                    ├─ Cache response     │
   │                    │                      │
   │  ← Message array   │                      │
   │←───────────────────┤                      │
   │                    │                      │
   ├─ Render in UI     │                      │
   │                    │                      │
```

#### **User Directory Sync**
```
Frontend              Backend              Rocket.Chat
   │                    │                      │
   ├─ GET /chat/users   │                      │
   │  ?search=query    │                      │
   ├───────────────────→│                      │
   │                    ├─ Call Rocket API ──→
   │                    │ /api/v1/users.list  │
   │                    │  ?query=search_term │
   │                    │                      │
   │                    │  ← Users list        │
   │                    │                      │
   │  ← User list       │                      │
   │←───────────────────┤                      │
   │                    │                      │
   ├─ Search/Filter    │                      │
   │                    │                      │
```

#### **Direct Messages (DMs) Fetching**
```
Frontend              Backend              Rocket.Chat
   │                    │                      │
   ├─ GET /chat/dm-list │                      │
   ├───────────────────→│                      │
   │                    ├─ Call Rocket API ──→
   │                    │ /api/v1/subscriptions.
   │                    │ getOne?roomName=@user│
   │                    │                      │
   │                    │  ← DM room data      │
   │                    │                      │
   │  ← DM list         │                      │
   │←───────────────────┤                      │
   │                    │                      │
   ├─ Select DM        │                      │
   ├─ Fetch messages   │                      │
   │  (room_id:username)                      │
   │                    │                      │
```

#### **Message Pinning (Rocket.Chat Sync)**
```
Frontend (DM)         Backend              Local DB      Rocket.Chat
   │                    │                    │                 │
   ├─ Click pin         │                    │                 │
   │ (room_id:username) │                    │                 │
   ├─ POST /pin-msg ───→│                    │                 │
   │                    ├─ Send to RC API ────────────────────→
   │                    │  /api/v1/chat.pinMessage            │
   │                    │                    │                 │
   │                    │  ← Pin confirmed   │                 │
   │                    │← ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│
   │                    │                    │                 │
   │                    │                 │
   │                    ├───────────────────→                 │
   │                    │                    │                 │
   │  ← Success        │                    │                 │
   │←───────────────────┤                    │                 │
   │                    │                    │                 │
   ├─ GET /pinned-msgs  │                    │                 │
   ├─ ?room_id=username │                    │                 │
   ├───────────────────→│                    │                 │
   │                    ├─ Query RC API     │                 │
   │                    ├────────────────────────────────────→
   │                    │  /api/v1/channels.getPinnedMessages │
   │                    │                    │                 │
   │                    │  ← Pinned msgs    │                 │
   │                    │← ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│
   │                    │                    │                 │
   │                      │                 │
   │                    ├───────────────────→                 │
    │                    │                    │                 │
   │  ← Pinned msgs    │                    │                 │
   │←───────────────────┤                    │                 │
   │                    │                    │                 │
   ├─ Display header   │                    │                 │
   │ with RC pins      │                    │                 │
   │                    │                    │                 │
```

#### **SSO User Creation**
```
Frontend              Backend              Social Hub DB    Rocket.Chat
   │                    │                      │                 │
   ├─ POST /register    │                      │                 │
   │ {email, password}  │                      │                 │
   ├───────────────────→│                      │                 │
   │                    ├─ Create user ──────→                 │
   │                    │                      │                 │
   │                    ├─ Call Rocket API ──────────────────→ │
   │                    │ /api/v1/users.create                 │
   │                    │ {username, password} │                 │
   │                    │                      │                 │
   │                    │                      │  ← User created  │
   │                    │                      │← Confirmation   │
   │                    │                      │                 │
   │                    ├─ Store credentials ──→                 │
   │                    │ in User model        │                 │
   │                    │                      │                 │
   │  ← Success         │                      │                 │
   │←───────────────────┤                      │                 │
   │                    │                      │                 │
```

### 1.4 Key Design Decisions

| Decision | Why | Status |
|----------|-----|--------|
| **Rocket.Chat as External Service** | Offload messaging complexity, use existing platform | ✅ Implemented |
| **REST API Integration** | Standard HTTP, reliable, no WebSocket overhead | ✅ Implemented | | ✅ Implemented |
| **Local SQLite for Pins** | Independent pin storage, not dependent on Rocket.Chat | ✅ Implemented |
| **Composite Room IDs** | `dm:username` format enables consistent querying | ✅ Implemented |
| **SSO Integration** | Single credential for both platforms | ✅ Implemented |
| **Credentials in DB** | Store for making authenticated API calls | ✅ Implemented |

---

## 2. Backend Architecture

### 2.1 Backend Structure

```
backend/
├── main.py                    # FastAPI app, Rocket.Chat endpoints
├── rocket_chat_local.py       # RocketChatClient wrapper class
├── database.py                # SQLAlchemy ORM models
├── crud.py                    # Database CRUD operations
├── schemas.py                 # Pydantic request/response models
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
└── uploads/
    └── profile_pictures/      # User profile images
```

### 2.2 Data Models

#### **User Model (SSO)**
```python
class User:
    id: int                          # Primary key
    full_name: str
    email: str                       # Unique identifier
    hashed_password: str
    
    # Rocket.Chat SSO Fields
    rocket_chat_username: str        # Username in Rocket.Chat
    rocket_chat_password: str        # Password for Rocket.Chat API calls
    
    # User Profile
    bio: str
    education_school: str
    education_degree: str
    location: str
    phone: str
    profile_picture_url: str
    
    created_at: datetime
    updated_at: datetime
```

#### **PinnedMessage Model**
```python
class PinnedMessage:
    id: int                          # Primary key
    message_id: str                  # From Rocket.Chat
    room_id: str                     # Channel ID or "dm:username"
    room_name: str                   # Channel/DM name
    room_type: str                   # 'channel', 'group', or 'dm'
    pinned_by: int (FK)              # User who pinned
    message_text: str                # Cached message text
    rocket_chat_pin_id: str          # Reference to Rocket.Chat pin ID
    pinned_at: datetime
    # Synced with Rocket.Chat - backend calls RC API to pin/unpin
```

#### **Group Model**
```python
class Group:
    id: int                          # Primary key
    name: str
    description: str
    created_by: int (FK)
    rocket_chat_group_id: str        # Reference to Rocket.Chat group
    created_at: datetime
    updated_at: datetime
```

### 2.3 Rocket.Chat API Integration

#### **Endpoints Calling Rocket.Chat**

| Social Hub Endpoint | Rocket.Chat API | Purpose |
|---|---|---|
| `GET /api/rocket-chat/channels` | `/api/v1/channels.list` | List public channels |
| `GET /api/rocket-chat/groups` | `/api/v1/groups.list` | List private groups |
| `GET /api/rocket-chat/user-rooms` | `/api/v1/subscriptions.get` | List user's rooms |
| `GET /chat/channel-messages?room_id=X` | `/api/v1/channels.messages?roomId=X` | Fetch channel messages |
| `GET /chat/group-messages?room_id=X` | `/api/v1/groups.messages?roomId=X` | Fetch group messages |
| `GET /chat/dm-messages?username=X` | `/api/v1/subscriptions.getOne?roomName=@X` | Fetch DM messages |
| `GET /chat/thread-messages?room_id=X&thread_id=Y` | `/api/v1/channels.messages?roomId=X&threadId=Y` | Fetch threaded messages |
| `GET /api/rocket-chat/users?search=X` | `/api/v1/users.list?query=X` | Search user directory |
| `POST /chat/pin-message` | `/api/v1/chat.pinMessage` | Pin message in Rocket.Chat |
| `POST /chat/unpin-message` | `/api/v1/chat.unpin` | Unpin message from Rocket.Chat |
| `GET /chat/pinned-messages?room_id=X` | `/api/v1/channels.getPinnedMessages` | Get pinned messages from Rocket.Chat |

### 2.4 RocketChatClient Service

Main class that wraps Rocket.Chat REST API:

```python
class RocketChatClient:
    """Wrapper for Rocket.Chat REST API"""
    
    # Connection
    async def test_connection() → bool
        # Verify Rocket.Chat server is reachable
    
    async def get_user_headers() → Dict
        # Get authenticated headers for API calls
        # Uses stored credentials from User model
    
    # Conversations/Rooms
    async def get_all_user_rooms() → List[Room]
        # GET /api/v1/subscriptions.get
        # Returns: channels, groups, and DMs for user
    
    async def get_channel_list() → List[Channel]
        # GET /api/v1/channels.list
        # Returns all public channels
    
    async def get_direct_message_list() → List[DM]
        # GET /api/v1/subscriptions.getOne?roomName=@username
        # Returns user's direct message rooms
    
    # Messages
    async def get_channel_messages(room_id, limit) → List[Message]
        # GET /api/v1/channels.messages?roomId=<id>
        # Fetch messages from Rocket.Chat channel
    
    async def get_direct_messages(username, limit) → List[Message]
        # GET /api/v1/subscriptions.getOne?roomName=@<username>
        # Fetch messages from DM conversation
    
    async def get_thread_messages(room_id, thread_id) → List[Message]
        # GET /api/v1/channels.messages?roomId=<id>&threadId=<id>
        # Fetch messages in a thread
    
    async def send_message(room_id, text) → Message
        # POST /api/v1/chat.postMessage
        # Send message to Rocket.Chat room
    
    # Users
    async def create_user_account(email, name, password) → bool
        # POST /api/v1/users.create
        # Create user in Rocket.Chat during SSO
    
    async def search_users(query) → List[User]
        # GET /api/v1/users.list?query=<query>
        # Search Rocket.Chat user directory
    
    async def get_user_info(username) → User
        # GET /api/v1/users.info?username=<username>
        # Get user profile from Rocket.Chat
    
    # Reactions
    async def add_reaction(message_id, reaction) → bool
        # POST /api/v1/chat.react
        # Add emoji reaction to message
    
    async def remove_reaction(message_id, reaction) → bool
        # POST /api/v1/chat.deleteReaction
        # Remove emoji reaction from message
```

### 2.5 Message Pinning (Rocket.Chat Synced)

Pinned messages are synced with Rocket.Chat via REST API:

```python
# Pin a message (sends to Rocket.Chat)
POST /chat/pin-message
{
    "message_id": "from_rocket_chat",
    "room_id": "dm:username or channel_id",
    "room_name": "channel_name",
    "room_type": "dm|channel|group",
    "message_text": "cached message content"
}
# Backend: calls RC API /api/v1/chat.pinMessage
# Then caches in local SQLite for performance

# Unpin a message (removes from Rocket.Chat)
POST /chat/unpin-message
{
    "message_id": "from_rocket_chat",
    "room_id": "dm:username or channel_id"
}
# Backend: calls RC API /api/v1/chat.unpin
# Then removes from local SQLite cache

# Get pinned messages for a room (from Rocket.Chat)
GET /chat/pinned-messages?room_id=dm:username

# Backend: calls RC API /api/v1/channels.getPinnedMessages
# Then caches response (30 sec TTL)

Response: [
    {
        "id": "message_uuid",
        "message_id": "rocket_chat_id",
        "room_id": "dm:username",
        "message_text": "pinned message content",
        "pinned_at": "2025-11-16T10:30:00"
    }
]
```

**Flow**:
1. User clicks pin → Frontend sends to backend
2. Backend calls Rocket.Chat API to pin message
3. Rocket.Chat confirms pin
4. Backend caches in local SQLite
5. Frontend fetches pinned messages from backend
6. Backend queries Rocket.Chat for pinned messages
7. Results displayed in UI header

### 2.6 SSO User Creation

During registration, users are provisioned in both systems:

```python
@app.post("/auth/register")
async def register(user: UserRegistration, db: Session):
    # 1. Create user in Social Hub database
    social_hub_user = create_user(
        email=user.email,
        full_name=user.full_name,
        password=user.password
    )
    
    # 2. Create user in Rocket.Chat
    rocket_chat_success = await rocket_client.create_user_account(
        email=user.email,
        name=user.full_name,
        password=user.password
    )
    
    # 3. Store Rocket.Chat credentials in Social Hub
    if rocket_chat_success:
        social_hub_user.rocket_chat_username = user.email
        social_hub_user.rocket_chat_password = user.password
        db.commit()
    
    # 4. Return token for frontend
    return {"access_token": token, "user": user_data}
```

---

## 3. Infrastructure & Tech Stack

### 3.1 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | React 18.3 | UI framework |
| | TypeScript 5.8 | Type safety |
| | Vite 5.4 | Build tool |
| | Tailwind CSS 3.4 | Styling |
| | Shadcn/UI | Component library |
| | React Router 6.30 | Routing |
| | Fetch API | HTTP calls |
| **Backend** | FastAPI | Web framework |
| | Python 3.9+ | Runtime |
| | SQLAlchemy 2.0+ | ORM |
| | Pydantic 2.0+ | Validation |
| | httpx | Async HTTP client |
| | bcrypt | Password hashing |
| **Database** | SQLite 3 | Local storage |
| **External** | Rocket.Chat 6.0+ | Message platform |
| | Google OAuth 2.0 | Authentication |
| **DevOps** | Docker | Containerization |
| | Docker Compose | Orchestration |

### 3.2 API Communication

#### **HTTP REST (Direct Calls)**
- All communication via HTTP GET/POST/PUT/DELETE
- Frontend initiates requests (no server push)
- Backend makes direct calls to Rocket.Chat (no caching currently)

#### **Frontend → Backend**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json

GET /api/rocket-chat/channels
GET /chat/channel-messages?room_id=X
GET /chat/pinned-messages?room_id=X
POST /chat/pin-message
POST /chat/unpin-message
```

#### **Backend → Rocket.Chat**
```
X-Auth-Token: <admin_token>
X-User-Id: <admin_user_id>
Content-Type: application/json

GET /api/v1/channels.list
GET /api/v1/channels.messages?roomId=X
POST /api/v1/users.create
POST /api/v1/chat.postMessage
```

### 3.3 Configuration

#### **.env File**
```env
# Database
DATABASE_URL=sqlite:///./social_hub.db

# Rocket.Chat Connection
ROCKET_CHAT_URL=http://10.68.0.49:30082
ROCKET_CHAT_USER_ID=<admin_user_id>
ROCKET_CHAT_AUTH_TOKEN=<admin_auth_token>

# Google OAuth (if used)
GOOGLE_CLIENT_ID=your_google_client_id
```

### 3.5 Deployment Architecture

#### **Development Setup**
```
Local Machine:
├── Frontend: npm run dev (http://localhost:5173)
├── Backend: python main.py (http://localhost:8000)
└── Database: social_hub.db (local file)

Remote Services:
└── Rocket.Chat: http://10.68.0.49:30082
```
## Appendix

### A. Rocket.Chat API Reference

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/api/v1/channels.list` | Admin | List public channels |
| GET | `/api/v1/channels.messages?roomId=X` | Admin | Fetch channel messages |
| GET | `/api/v1/groups.list` | Admin | List private groups |
| GET | `/api/v1/groups.messages?roomId=X` | Admin | Fetch group messages |
| GET | `/api/v1/subscriptions.get` | User | List user's rooms |
| GET | `/api/v1/subscriptions.getOne?roomName=@X` | User | Get specific room/DM |
| GET | `/api/v1/users.list?query=X` | Admin | Search users |
| GET | `/api/v1/users.info?username=X` | Admin | Get user profile |
| POST | `/api/v1/users.create` | Admin | Create user (SSO) |
| POST | `/api/v1/chat.postMessage` | User | Send message |
| POST | `/api/v1/chat.react?emoji=X` | User | Add reaction |
| DELETE | `/api/v1/chat.deleteReaction` | User | Remove reaction |
| GET | `/api/v1/channels.threads?roomId=X` | User | Get threads |

### B. DM Room ID Format

For consistency across room types, DM room IDs use format: `dm:username`

Examples:
- `dm:john.doe@example.com` - DM with john.doe
- `dm:admin` - DM with admin user
- `channel_id_123` - Regular channel (no prefix)
- `group_id_456` - Private group (no prefix)

### C. Future Enhancements

1. **WebSocket** - Real-time message push instead of polling
2. **Audio/Video Calls** - Backend integration for calling
3. **Message Search** - Full-text search in Rocket.Chat
4. **Push Notifications** - Real-time notification support
5. **File Sharing** - Document and media upload to Rocket.Chat
6. **Message Encryption** - End-to-end encryption
7. **Offline Support** - Service worker for offline functionality
8. **Typing Indicators** - Show when users are typing

---

**Document Version**: 1.0  
**Last Updated**: November 2025  
**Status**: Rocket.Chat Integration Focused
