# Social Hub - Rocket.Chat Integration Architecture Document

**Project**: Social Hub with Rocket.Chat Integration  
**Date**: November 2025  
**Author**: Ankush Chhabra  
**Status**: Active Development

---

## ⚡ Rocket.Chat Integration - Current Implementation Status

### ✅ FULLY IMPLEMENTED & WORKING
- **Rocket.Chat Server Integration**: Connected to external Rocket.Chat server (10.68.0.49:30082)
- **Message Fetching**: Retrieve messages from Rocket.Chat channels, groups, and DMs
- **Conversation Management**: List all channels, private groups, and direct messages
- **User Directory**: Fetch and search users from Rocket.Chat
- **Message Pinning**: Pin/unpin messages in DMs, channels, and groups with local database backup
- **Thread Support**: Fetch and display threaded messages from Rocket.Chat
- **User SSO**: Single Sign-On integration (users created in Social Hub sync with Rocket.Chat)
- **REST API Polling**: All Rocket.Chat data fetched via REST API calls
- **API Caching**: 30-second cache for conversations to reduce API load

### ⏳ NOT IMPLEMENTED (Future Enhancements)
- **WebSocket**: Currently using HTTP polling only (no real-time push from Rocket.Chat)
- **Audio/Video Calling**: Audio call button in DMs (UI only, needs RTC backend)
- **Push Notifications**: No real-time notifications from Rocket.Chat
- **Message Search**: No full-text search in Rocket.Chat
- **Offline Message Sync**: No offline support

---

## Table of Contents

1. [Software Architecture (SW Arch)](#1-software-architecture-sw-arch)
2. [Application Architecture - Backend (BE)](#2-application-architecture---backend-be)
3. [Infrastructure Architecture - Tech Stack](#3-infrastructure-architecture---tech-stack)

---

## 1. Software Architecture (SW Arch)

### 1.1 System Overview

The Social Hub is a full-stack social media platform that **integrates with Rocket.Chat as the messaging backbone**. The architecture fetches messages, conversations, and user data from Rocket.Chat and displays them in a custom React frontend. Communication with Rocket.Chat is through HTTP/REST API polling (no WebSocket).

```
┌─────────────────────────────────────────────────────────────────┐
│                  Social Hub Frontend (React)                    │
│              - EnhancedMessagesWidget (Chat UI)                 │
│              - Display Rocket.Chat conversations               │
│              - Pin message management (local DB)               │
└────────────────────┬────────────────────────────────────────────┘
                     │
      ┌──────────────┴──────────────┐
      │                             │
      │ HTTP/REST Calls             │ Manage Local Data
      │ (Polling)                   │ (SQLite)
      │                             │
┌─────▼──────────────┐      ┌──────▼──────────┐
│  Social Hub API    │      │  Social Hub DB  │
│  (FastAPI)         │      │  (SQLite)       │
│                    │      │                 │
│ • Message Fetch    │      │ • Users         │
│ • Room/Conv List   │      │ • Pinned Msgs   │
│ • User Directory   │      │ • SSO Creds     │
│ • Thread Support   │      │ • User Data     │
└────────┬───────────┘      └─────────────────┘
         │
         │ REST API Calls
         │ (Authentication via headers)
         │
┌────────▼──────────────────────────────┐
│   Rocket.Chat Server (External)        │
│   10.68.0.49:30082                    │
│                                        │
│ • Message Storage                      │
│ • Room/Channel Management              │
│ • User Accounts                        │
│ • Thread Storage                       │
│ • DM Management                        │
└────────────────────────────────────────┘
```

### 1.2 Architectural Patterns

#### **Rocket.Chat Integration Pattern**
- **External Service Integration**: Social Hub acts as a client to Rocket.Chat
- **REST API Wrapper**: RocketChatClient wraps Rocket.Chat REST API
- **Data Aggregation**: Fetches from Rocket.Chat and displays in Social Hub UI
- **Local Persistence**: Stores pinned messages and user data locally in SQLite

#### **SSO (Single Sign-On) Pattern**
- Users authenticate with Social Hub (email/password or Google OAuth)
- User credentials synced to Rocket.Chat on registration
- Backend maintains credentials in database for future API calls
- User sessions managed separately in both systems

#### **API Communication Pattern - HTTP Polling (REST)**
- Frontend polls backend for conversations and messages
- No WebSocket or real-time subscriptions
- Backend caches Rocket.Chat responses (30-second TTL)
- Reduces API calls to remote Rocket.Chat server
- Frontend triggers refreshes on user action or interval

#### **Message Pinning Strategy**
- Local database stores pinned messages metadata
- Composite room_id format (`dm:username`) for DMs
- Distinguishes between DMs, channels, and groups
- Enables consistent querying across room types

### 1.3 Data Flow Diagrams

#### **Message Loading Flow (REST Polling)**
```
Frontend                Backend              Rocket.Chat           Local DB
   │                        │                      │                  │
   ├─ GET /chat/channel-msg │                      │                  │
   │   (room_id, limit)     │                      │                  │
   │──────────────────────────→                      │                  │
   │ (triggered by UI reload/│                      │                  │
   │  user scroll, not event)│                      │                  │
   │                        ├─ Check Cache         │                  │
   │                        │ (30 sec TTL)          │                  │
   │                        │                      │                  │
   │                        ├─ If expired:         │                  │
   │                        ├─ Fetch from Rocket──→                   │
   │                        │  (REST API call)      ├─ /api/messages  │
   │                        │                      ←─────────────────┤
   │                        │                      │                  │
   │                        ├─ Cache Response      │                  │
   │                        │                      │                  │
   │        Array of        │                      │                  │
   │        Messages        │                      │                  │
   │←──────────────────────────                      │                  │
   │                        │                      │                  │
   ├─ Render Messages      │                      │                  │
   │ in Chat Window        │                      │                  │
   │                        │                      │                  │
   ├─ [Poll every N sec]   │                      │                  │
   │ or on user action     │                      │                  │
   │                        │                      │                  │

Note: All data fetched from Rocket.Chat via REST API
- Uses HTTP polling (frontend-initiated)
- Messages not immediately synced
- Depends on polling interval or user refresh
```

#### **Rocket.Chat API Caching Strategy**
```
Request Timeline:

First Request:
  Frontend → Backend (GET /chat/messages?room_id=X)
  Backend → Rocket.Chat (GET /api/v1/channels.messages?roomId=X)
  Rocket.Chat returns messages
  Backend caches response (30-second TTL)
  Backend returns to Frontend

Second Request (within 30 seconds):
  Frontend → Backend (GET /chat/messages?room_id=X)
  Backend checks cache (HIT!)
  Backend returns cached response immediately
  NO call to Rocket.Chat

Third Request (after 30 seconds):
  Frontend → Backend (GET /chat/messages?room_id=X)
  Backend checks cache (EXPIRED!)
  Backend → Rocket.Chat (new API call)
  Backend updates cache and returns

Benefits:
- Reduces API calls to Rocket.Chat
- Faster response times (cache hit)
- Less network traffic
- Improves frontend responsiveness
```

#### **SSO (Single Sign-On) Flow with Rocket.Chat**
```
Frontend                API Layer              Database           Rocket.Chat
   │                        │                      │                  │
   ├─ POST /auth/register   │                      │                  │
   │─ {email, password}     │                      │                  │
   │─────────────────────────→                      │                  │
   │                        ├─ Hash Password       │                  │
   │                        ├─ Create Local User   │                  │
   │                        │─────────────────────→                   │
   │                        │                      │                  │
   │                        ├─ Generate JWT Token  │                  │
   │                        │ (user_id, email, exp)│                  │
   │                        │                      │                  │
   │        JWT Token       │                      │                  │
   │        + User Data     │                      │                  │
   │←─────────────────────────                      │                  │
   │                        │                      │                  │
   ├─ Store token in       │                      │                  │
   │  localStorage          │                      │                  │
   │                        │                      │                  │

Subsequent Protected Requests:
   │                        │                      │                  │
   ├─ GET /auth/me         │                      │                  │
   │ Header: Authorization: │                      │                  │
   │ Bearer <JWT_TOKEN>    │                      │                  │
   │─────────────────────────→                      │                  │
   │                        ├─ Verify JWT Signature│                  │
   │                        ├─ Extract user_id    │                  │
   │                        ├─ Query User Data    │                  │
   │                        │←─────────────────────┤                  │
   │                        │                      │                  │
   │        User Profile    │                      │                  │
   │←─────────────────────────                      │                  │
   │                        │                      │                  │
```

#### **Message Pinning Flow (DMs)**
```
Frontend (DM Section)              API Layer              DB            Rocket.Chat
   │                                   │                   │                 │
   ├─ Click Pin Icon                  │                   │                 │
   │─ room_id: dm:username            │                   │                 │
   ├─ POST /chat/pin-message──────────→                   │                 │
   │ Header: Authorization: Bearer JWT │                   │                 │
   │                                   │                   │                 │
   │                                   ├─ JWT Validation   │                 │
   │                                   ├─ Extract room_id  │                 │
   │                                   ├─ Save to DB      │                 │
   │                                   │────────────────────→                │
   │                                   │                   │                 │
   │                                   ├─ (Optional) Call Rocket.Chat        │
   │                                   │──────────────────────────────────→ │
   │                                   │                   │                 │
   │                    Success Response (JSON)            │                 │
   │←──────────────────────────────────┤                   │                 │
   │                                   │                   │                 │
   ├─ GET /chat/pinned-messages       │                   │                 │
   ├─ ?room_id=dm:username            │                   │                 │
   │─────────────────────────────────→                   │                 │
   │ Header: Authorization: Bearer JWT │                   │                 │
   │                                   ├─ JWT Validation   │                 │
   │                                   ├─ Query by room_id │                 │
   │                                   │←────────────────┤                 │
   │                                   │                   │                 │
   │         Pinned Messages Array      │                   │                 │
   │←─────────────────────────────────┤                   │                 │
   │                                   │                   │                 │
   ├─ Display in Header Section        │                   │                 │
   │                                   │                   │                 │
```

### 1.4 Key Design Decisions for Rocket.Chat Integration

| Decision | Rationale | Status |
|----------|-----------|--------|
| **Rocket.Chat as External Service** | Offloads messaging complexity, leverages existing platform features | ✅ Implemented |
| **REST API Integration** | Standard HTTP calls, easier than WebSocket, works reliably | ✅ Implemented |
| **30-Second API Caching** | Balances freshness with reducing load on Rocket.Chat server | ✅ Implemented |
| **Local SQLite for Pins** | Pin messages in Social Hub DB, independent from Rocket.Chat | ✅ Implemented |
| **Composite DM Room IDs** | Format `dm:username` enables consistent querying across room types | ✅ Implemented |
| **SSO Integration** | Single username/password for both Social Hub and Rocket.Chat | ✅ Implemented |
| **User Credentials in DB** | Store credentials to make authenticated Rocket.Chat API calls | ✅ Implemented |
| **No WebSocket** | HTTP polling sufficient for non-real-time chat requirements | ⏳ Future Enhancement |

---

## 2. Application Architecture - Backend (BE)

### 2.1 Backend Structure

```
backend/
├── main.py                      # FastAPI app, route definitions
├── database.py                  # SQLAlchemy models, DB session
├── crud.py                      # Database operations (Create, Read, Update, Delete)
├── auth.py                      # JWT token generation/verification
├── schemas.py                   # Pydantic models (request/response validation)
├── rocket_chat_local.py         # Rocket.Chat API wrapper
├── requirements.txt             # Python dependencies
├── .env                         # Environment configuration
└── uploads/
    └── profile_pictures/        # User profile images
```

### 2.2 Data Models for Rocket.Chat Integration

#### **User Model (SSO Integration)**
```python
class User:
    id: int (primary key)
    full_name: str
    email: str (unique)
    hashed_password: str
    google_id: str (for Google OAuth)
    auth_provider: enum (LOCAL | GOOGLE)
    profile_picture_url: str
    
    # Rocket.Chat SSO Credentials
    rocket_chat_username: str    # Synced username in Rocket.Chat
    rocket_chat_password: str    # Encrypted password for API calls
    
    # User Profile
    bio: str
    education_school: str
    education_degree: str
    location: str
    phone: str
    
    is_active: bool
    created_at: datetime
    updated_at: datetime
```
**Purpose**: Stores Social Hub user data + Rocket.Chat credentials for SSO

#### **PinnedMessage Model (Local Storage)**
```python
class PinnedMessage:
    id: int (primary key)
    message_id: str           # Rocket.Chat message ID
    room_id: str              # From Rocket.Chat or composite "dm:username"
    room_name: str            # Channel/Group name or DM username
    room_type: enum           # 'channel', 'group', or 'dm'
    pinned_by: int (FK)       # User who pinned (FK → User)
    message_text: str         # Cached message text for quick display
    pinned_at: datetime       # When pinned
```
**Purpose**: Local database backup for pinned messages (independent from Rocket.Chat)

#### **Group Model (Social Hub Groups)**
```python
class Group:
    id: int (primary key)
    name: str
    description: str
    created_by: int (FK → User)
    rocket_chat_group_id: str  # Reference to Rocket.Chat private group
    created_at: datetime
    updated_at: datetime
```
**Purpose**: Links Social Hub private groups to Rocket.Chat groups

### 2.3 Rocket.Chat Integration Endpoints

#### **Rocket.Chat Conversation Endpoints**
| Method | Endpoint | Purpose | Backend Call to Rocket.Chat |
|--------|----------|---------|-----|
| GET | `/api/rocket-chat/channels` | List all Rocket.Chat public channels | `/api/v1/channels.list` |
| GET | `/api/rocket-chat/groups` | List Rocket.Chat private groups | `/api/v1/groups.list` |
| GET | `/api/rocket-chat/user-rooms` | List user's joined rooms (channels + groups) | `/api/v1/subscriptions.get` |
| GET | `/api/rocket-chat/dm-list` | List user's direct messages | `/api/v1/subscriptions.getOne?roomName=@user` |

#### **Rocket.Chat Message Endpoints**
| Method | Endpoint | Purpose | Backend Call to Rocket.Chat |
|--------|----------|---------|-----|
| GET | `/chat/channel-messages?room_id=X` | Fetch messages from Rocket.Chat channel | `/api/v1/channels.messages?roomId=X` |
| GET | `/chat/group-messages?room_id=X` | Fetch messages from Rocket.Chat group | `/api/v1/groups.messages?roomId=X` |
| GET | `/chat/dm-messages?room_name=@user` | Fetch messages from DM conversation | `/api/v1/subscriptions.getOne?roomName=@user` |
| GET | `/chat/thread-messages?room_id=X&thread_id=Y` | Fetch threaded messages | `/api/v1/channels.messages?roomId=X&threadId=Y` |

#### **Rocket.Chat User Directory**
| Method | Endpoint | Purpose | Backend Call to Rocket.Chat |
|--------|----------|---------|-----|
| GET | `/api/rocket-chat/users?search=query` | Search Rocket.Chat user directory | `/api/v1/users.list?query=X` |
| GET | `/api/rocket-chat/users/info?username=user` | Get user profile from Rocket.Chat | `/api/v1/users.info?username=user` |

#### **Message Pinning (Local Storage)**
| Method | Endpoint | Purpose | Storage |
|--------|----------|---------|---------|
| POST | `/chat/pin-message` | Pin message (room_id: dm:username for DMs) | Social Hub SQLite DB |
| POST | `/chat/unpin-message` | Unpin message from local DB | Social Hub SQLite DB |
| GET | `/chat/pinned-messages?room_id=X` | Get pinned messages for room | Social Hub SQLite DB |

### 2.4 Rocket.Chat Client (Backend Service)

#### **RocketChatClient Class - Main Integration Point**
The `RocketChatClient` wraps all Rocket.Chat REST API calls:

```python
class RocketChatClient:
    def __init__(self):
        self.base_url = os.getenv("ROCKET_CHAT_URL")  # 10.68.0.49:30082
        self.user_id = os.getenv("ROCKET_CHAT_USER_ID")  # Admin ID
        self.auth_token = os.getenv("ROCKET_CHAT_AUTH_TOKEN")  # Admin token
        
        # Caching
        self._conversations_cache = None
        self._cache_duration = 30  # seconds
        
        # SSO cache
        self._sso_cache = {}
```

#### **Key Rocket.Chat Operations**
```python
# Connection & Authentication
async def test_connection() → bool
    # Test if Rocket.Chat server is reachable

async def get_user_headers() → Dict
    # Get user-specific headers for Rocket.Chat API calls
    # Uses stored credentials from Social Hub User model

# Conversations/Rooms
async def get_all_user_rooms() → List[Room]
    # Fetch channels, groups, DMs for current user
    # Returns: [{"_id": "...", "name": "...", "type": "..."}]

async def get_channel_list() → List[Channel]
    # List all public channels from Rocket.Chat

async def get_direct_message_list() → List[DM]
    # List all user's DMs with room names

# Messages
async def get_channel_messages(room_id, limit) → List[Message]
    # Fetch messages from Rocket.Chat channel
    # GET /api/v1/channels.messages?roomId=<room_id>

async def get_direct_messages(username, limit) → List[Message]
    # Fetch DM messages with a specific user
    # GET /api/v1/subscriptions.getOne?roomName=@<username>

async def send_message(room_id, text) → Message
    # Send message to Rocket.Chat room
    # POST /api/v1/chat.postMessage

# Users
async def create_user_account(email, name, password) → bool
    # Create user in Rocket.Chat during Social Hub registration
    # POST /api/v1/users.create

async def search_users(query) → List[User]
    # Search Rocket.Chat user directory
    # GET /api/v1/users.list?query=<query>

# Threads
async def get_thread_messages(room_id, thread_id) → List[Message]
    # Fetch messages in a thread

# Reactions
async def add_reaction(message_id, reaction) → bool
    # Add emoji reaction to message

async def remove_reaction(message_id, reaction) → bool
    # Remove emoji reaction from message
```

#### **CRUD Operations for Social Hub DB**
```python
# These operate on Social Hub local SQLite database

- create_user()              # Create user in Social Hub + Rocket.Chat
- authenticate_user()        # Verify credentials
- create_group()            # Create Social Hub group
- add_member_to_group()     # Add user to Social Hub group
- get_pinned_messages()     # Query pinned messages from local DB
```
- `get_recent_chat_messages()` - Fetch messages
- `create_group()` - Group creation
- `add_member_to_group()` - Membership management

### 2.5 Authentication Flow

#### **JWT Token Strategy (IMPLEMENTED & WORKING)**
```
1. User sends credentials (email + password)
   ↓
2. Backend validates:
   - Check if user exists in database
   - Verify password using bcrypt/argon2
   ↓
3. Backend generates JWT token:
   - Payload: {"sub": email, "exp": expiry_time}
   - Algorithm: HS256
   - Secret: Signing key from environment variable
   ↓
4. Token sent to frontend in response:
   {
     "access_token": "eyJhbGc...",
     "token_type": "bearer",
     "user": {...}
   }
   ↓
5. Frontend stores token in localStorage:
   localStorage.setItem('access_token', token)
   ↓
6. Frontend includes token in subsequent requests:
   Authorization: Bearer <token>
   ↓
7. Backend middleware verifies token:
   - Extract token from header
   - Verify signature using secret
   - Decode payload to get email
   - Look up user in database
   - Attach user to request context
   ↓
8. Protected endpoints use verified user
```

#### **JWT Implementation Details**
- **Secret Key**: Stored in environment variable `SECRET_KEY`
- **Algorithm**: HMAC-SHA256 (HS256)
- **Token Lifetime**: 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Storage**: localStorage on frontend (no HttpOnly cookies)
- **Validation**: Happens on every protected endpoint request
- **Error Handling**: 401 Unauthorized if token invalid/expired

#### **Token Verification Middleware**
```python
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    email = verify_token(token)  # Decodes and validates JWT
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = get_user_by_email(db, email)
    return user
```

#### **Google OAuth Flow**
```
1. Frontend initiates Google OAuth
   ↓
2. User authenticates with Google
   ↓
3. Frontend receives ID token from Google
   ↓
4. Frontend sends ID token to backend: POST /auth/google
   ↓
5. Backend verifies token signature with Google's public key
   ↓
6. Backend extracts user info (email, name, google_id)
   ↓
7. Backend checks if user exists:
   - If yes: Load existing user
   - If no: Create new user in database
   ↓
8. Backend generates JWT token
   ↓
9. Frontend receives JWT and stores in localStorage
```

### 2.6 Business Logic Implementation

#### **Message Pinning Logic**

**Pin Operation**:
```python
@app.post("/chat/pin-message")
async def pin_message(
    message_id: str,
    room_id: str,
    room_name: str,
    room_type: str,
    current_user: User
):
    # 1. Validate inputs
    # 2. Check user has access to room
    # 3. Create PinnedMessage record
    #    - For DMs: room_id format is "dm:username"
    #    - For channels/groups: room_id is Rocket.Chat ID
    # 4. Optional: Call Rocket.Chat API
    # 5. Return success response
```

**Unpin Operation**:
```python
@app.post("/chat/unpin-message")
async def unpin_message(
    message_id: str,
    room_id: str,
    current_user: User
):
    # 1. Validate inputs
    # 2. Find and delete PinnedMessage record
    #    - Match by message_id AND room_id (composite key)
    # 3. Optional: Call Rocket.Chat API
    # 4. Return success response
```

**Load Pinned Messages**:
```python
@app.get("/chat/pinned-messages")
async def get_pinned_messages(
    room_id: str,
    current_user: User
):
    # 1. Query PinnedMessage table
    #    - Filter by room_id
    #    - For DMs: room_id is in format "dm:username"
    # 2. Return as array of pinned messages
    # 3. Frontend displays in header section
```

#### **DM Room ID Format**
- **Purpose**: Distinguish DMs from channels/groups in database
- **Format**: `dm:{username}` where username is Rocket.Chat username
- **Example**: `dm:john.doe@email.com` for DM with john.doe
- **Used in**: Pin/unpin operations, message queries

---

## 3. Infrastructure Architecture - Tech Stack

### 3.1 Technology Stack Summary

| Layer | Technology | Purpose | Notes |
|-------|-----------|---------|-------|
| **Frontend** | React 18.3 | UI Framework | Functional Components, Hooks |
| | TypeScript 5.8 | Type Safety | Strict mode enabled |
| | Vite 5.4 | Build Tool | Dev server + production build |
| | Tailwind CSS 3.4 | Styling | Utility-first CSS |
| | Shadcn/UI | Component Library | Radix UI + Tailwind |
| | React Router 6.30 | Routing | Client-side navigation |
| | React Hook Form 7.61 | Form Management | Validation included |
| | Lucide React 0.462 | Icons | SVG icons library |
| | Fetch API | HTTP Client | Built-in, no third-party lib |
| **Backend** | FastAPI 0.104+ | Web Framework | Async Python framework |
| | Python 3.9+ | Runtime | Async/await support |
| | SQLAlchemy 2.0+ | ORM | Database abstraction layer |
| | Pydantic 2.0+ | Data Validation | Request/response schemas |
| | httpx 0.24+ | HTTP Client | Async HTTP for Rocket.Chat calls |
| | PyJWT | JWT Authentication | Token signing/verification |
| | bcrypt/argon2 | Password Hashing | Secure password storage |
| | python-dotenv | Environment Config | Load .env variables |
| | google-auth | Google OAuth | Verify ID tokens |
| **Database** | SQLite 3 | Local Data Store | File-based, no server needed |
| **External Services** | Rocket.Chat 6.0+ | Messaging Platform | Remote server at 10.68.0.49:30082 |
| | Google OAuth 2.0 | Authentication | ID token verification |
| **Communication** | HTTP/REST | API Protocol | Polling-based (no WebSocket) |
| | JWT Bearer | Auth Mechanism | Stateless token-based |
| **DevOps** | Docker | Containerization | Optional deployment |
| | Docker Compose | Orchestration | Multi-container setup |
| **Version Control** | Git | Source Control | GitHub repository |

### 3.2 Frontend Architecture

#### **Component Structure**
```
src/
├── components/
│   ├── chat/
│   │   ├── EnhancedMessagesWidget.tsx (Main chat UI)
│   │   ├── UserSearch.tsx
│   │   └── MessageThread.tsx
│   ├── layout/
│   │   └── responsive-layout.tsx
│   ├── forms/
│   │   ├── login-form.tsx
│   │   └── signup-form.tsx
│   └── ui/ (Shadcn components)
│
├── pages/
│   ├── Feed.tsx
│   ├── Messages.tsx
│   ├── Profile.tsx
│   ├── Notifications.tsx
│   └── Login.tsx
│
├── contexts/
│   └── AuthContext.tsx (Global auth state)
│
├── services/
│   ├── api.ts (HTTP requests)
│   ├── chat.ts (Chat service)
│   └── chat-service.ts
│
├── hooks/
│   ├── use-toast.ts
│   └── use-mobile.tsx
│
├── types/
│   └── user.ts
│
├── lib/
│   ├── utils.ts
│   └── mockData.ts
│
└── main.tsx
```

#### **State Management**
- **React Context**: AuthContext for global authentication state (JWT token)
- **React Hooks**: useState, useEffect for component state
- **Local Storage**: Persist JWT tokens and user data
- **HTTP Polling**: Manual fetch calls to backend (no automatic subscription)

#### **Communication Pattern**
- **REST API**: All requests are HTTP GET/POST
- **Request-Response**: Frontend sends request, waits for response
- **No WebSocket**: No real-time server push (future enhancement)
- **Polling Strategy**: Frontend triggers data fetches on:
  - Component mount
  - User interaction (button clicks, navigation)
  - Manual refresh (pull-to-refresh pattern)

#### **Key Components**

**EnhancedMessagesWidget**:
- Main chat interface
- Supports DMs, private groups, channels
- Pin/unpin message functionality
- Message threading
- User search integration

**AuthContext**:
- Manages user authentication state
- Stores JWT token
- Provides user information
- Handles login/logout

### 3.3 Backend Architecture (Detailed)

#### **Framework: FastAPI**
- **Async Support**: Non-blocking I/O for scalability
- **Auto Documentation**: OpenAPI/Swagger UI at `/docs`
- **Validation**: Pydantic for request/response validation
- **Security**: Built-in JWT, CORS, HTTPS support
- **Middleware**: CORS, authentication, error handling

#### **Database Layer**

**SQLAlchemy ORM**:
- Object-relational mapping
- Database agnostic (SQLite now, PostgreSQL later)
- Relationship management (one-to-many, many-to-many)
- Query builder for complex queries
- Transaction support

**SQLite Database**:
```
social_hub.db
├── users table (accounts)
├── chat_messages table (local messages)
├── groups table (social groups)
├── group_members table (membership)
└── pinned_messages table (pinned chat messages)
```

#### **External Integration**

**Rocket.Chat Client**:
- REST API wrapper around Rocket.Chat server
- Handles authentication (admin + user credentials)
- Implements caching for frequently accessed data
- Manages SSO integration
- Error handling and retries

**Google OAuth**:
- Server-side verification of ID tokens
- User creation if new
- Profile picture extraction
- Email-based account matching

### 3.4 Deployment Architecture

#### **Current Setup**
```
┌─────────────────────────────────────────────────────────────┐
│                     Development Environment                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Local Machine                                                │
│  ├── Frontend: npm run dev                                   │
│  │   └── http://localhost:5173                              │
│  │                                                            │
│  ├── Backend: python main.py                                │
│  │   └── http://localhost:8000                              │
│  │                                                            │
│  └── Database: social_hub.db (local)                         │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│                    External Services                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Rocket.Chat Server (Remote)                                 │
│  └── http://10.68.0.49:30082                                │
│                                                               │
│  Google OAuth                                                │
│  └── https://accounts.google.com                            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

#### **Docker Stack** (Optional)
```yaml
services:
  backend:
    image: python:3.11
    build: ./backend
    ports: [8000:8000]
    env: .env
    volumes: [./backend:/app]
    depends_on: [db]

  frontend:
    image: node:18
    build: ./
    ports: [5173:5173]
    volumes: [./src:/app/src]

  db: # Optional PostgreSQL
    image: postgres:15
    env:
      POSTGRES_DB: social_hub
      POSTGRES_PASSWORD: ${DB_PASSWORD}

  rocket-chat:
    # External - not locally managed
```

### 3.5 Security Architecture

#### **Authentication & Authorization**
```
Request Flow:
1. User provides credentials
   ↓
2. Backend validates against database
   ↓
3. Generate JWT token (contains user_id, email, exp)
   ↓
4. Frontend stores token in localStorage
   ↓
5. Frontend includes token in all API requests:
   Authorization: Bearer <JWT_TOKEN>
   ↓
6. Backend validates token signature
   ↓
7. Extract user_id from token
   ↓
8. Verify user has access to resource
```

#### **Data Security**
| Data Type | Security Measure |
|-----------|------------------|
| Passwords | bcrypt hashing (salt rounds: 12) |
| JWT Tokens | HMAC-SHA256 signing |
| Sensitive Data | Environment variables (.env) |
| API Keys | Not exposed in frontend code |
| CORS | Whitelist specific origins |

#### **API Security**
- **CORS**: Whitelist frontend origins
- **Rate Limiting**: Consider adding for production
- **Input Validation**: Pydantic models enforce schema
- **SQL Injection**: Prevented by SQLAlchemy ORM
- **XSS Protection**: React auto-escapes values

### 3.6 Performance Optimization

#### **Caching Strategy**
```
Level 1: Backend Cache (30 seconds)
├── Rocket.Chat API responses
├── Conversation lists
└── Channel/Group information

Level 2: Frontend Storage (localStorage)
├── JWT tokens
├── User profile data
└── Last viewed conversations

Level 3: Database Indexes
├── User email (unique)
├── Message timestamps
└── Room IDs for pinned messages
```

#### **Frontend Optimization**
- Code splitting with Vite dynamic imports
- Lazy loading of routes with React Router
- Image optimization for profile pictures
- CSS minification (Tailwind production build)
- JavaScript minification and bundling
- Component memoization to prevent unnecessary re-renders

#### **Backend Optimization**
- Async I/O with FastAPI (non-blocking requests)
- Connection pooling for database
- Query optimization with SQLAlchemy indexing
- API caching to reduce Rocket.Chat calls (30-second TTL)
- Response compression with gzip

#### **HTTP Polling Strategy** (No WebSocket)
- Frontend calls backend endpoints on-demand
- Manual polling on button clicks or UI navigation
- Reduces server load (no persistent connections)
- Trade-off: Messages not immediately synced (polling interval delay)
- Suitable for non-real-time chat requirements

### 3.7 Monitoring & Logging

#### **Backend Logging**
```python
# Key events logged:
- Authentication attempts
- API requests/responses
- Rocket.Chat API calls
- Database operations
- Errors and exceptions
- Performance metrics
```

#### **Console Output Indicators**
```
🎯 Component lifecycle events
📌 Pinned message operations
📞 Audio call initiation
❌ Error conditions
✅ Success operations
⚠️  Warnings
🔐 Authentication events
```

### 3.8 Configuration Management

#### **Environment Variables** (.env)
```env
# Frontend (.env)
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=xxxxx

# Backend (.env)
DATABASE_URL=sqlite:///./social_hub.db
JWT_SECRET_KEY=your_secret_key
ROCKET_CHAT_URL=http://10.68.0.49:30082
ROCKET_CHAT_USER_ID=admin_id
ROCKET_CHAT_AUTH_TOKEN=admin_token
GOOGLE_CLIENT_ID=xxxxx
```

---

## Appendix

### A. Key Algorithms

#### **DM Room ID Generation**
```
Input: selectedConversation object
  - type: 'direct_message'
  - name: Rocket.Chat username
  - other_user: Display name

Process:
  if (type === 'direct_message'):
    room_id = 'dm:' + (name || other_user)
  else if (type === 'private_group'):
    room_id = rocket_chat_group_id
  else:
    room_id = conversation_id

Output: room_id for database/API queries
```

#### **Token Validation**
```
Input: JWT token from request header

Process:
  1. Extract token from Authorization header
  2. Verify signature using secret key
  3. Decode payload
  4. Check expiry time
  5. Extract user_id

Output: user_id if valid, error if invalid
```

### B. Error Handling

| Error Type | Status Code | Response |
|-----------|------------|----------|
| Invalid credentials | 401 | "Invalid email or password" |
| Unauthorized access | 403 | "You don't have permission" |
| Resource not found | 404 | "Resource not found" |
| Validation error | 400 | "Invalid input: {details}" |
| Server error | 500 | "Internal server error" |
| Rocket.Chat unavailable | 503 | "Chat service unavailable" |

### C. Future Enhancements

1. **WebSocket Support** (RECOMMENDED NEXT):
   - Real-time message delivery
   - Replace HTTP polling with server push
   - Reduced latency for chat interactions
   - Tools: Socket.IO or native WebSocket

2. **Audio/Video Calling**:
   - Integrate audio call button in DMs
   - Use WebRTC for peer-to-peer calls
   - STUN/TURN servers for NAT traversal

3. **Message Encryption**:
   - End-to-end encryption for DMs
   - Optional group encryption

4. **Offline Support**:
   - Service Worker implementation
   - Local caching of messages
   - Sync on reconnection

5. **Push Notifications**:
   - Backend push notifications on new messages
   - Mobile notifications support

6. **Message Search**:
   - Full-text search across messages
   - Search filters by date, sender, room

7. **Scalability**:
   - Migration to PostgreSQL (from SQLite)
   - Redis for caching/sessions
   - Horizontal scaling of backend

8. **Microservices**:
   - Separate services for chat, auth, groups
   - Message queue for async operations

9. **Analytics**:
   - User activity tracking
   - Engagement metrics

10. **Admin Dashboard**:
    - User management
    - System health monitoring
    - Message moderation tools

---

## Document Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Nov 2025 | Ankush Chhabra | Initial architecture documentation |

---

**End of Document**
