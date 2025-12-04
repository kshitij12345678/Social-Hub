# Architecture Document Updates - November 16, 2025

## Summary of Changes

The `ARCHITECTURE.md` document has been updated to reflect **ONLY what is actually implemented and working** in the Social Hub project. Previously, it included conceptual features that are not yet functional.

---

## Key Changes Made


### 1. **Authentication**
- ✅ Tokens stored in localStorage
- ✅ Bearer token authentication on all protected endpoints
- ✅ Google OAuth 2.0 integration working
- Removed misleading SSO description (replaced with actual JWT flow)

### 2. **Communication: HTTP REST Polling **
- ✅ All endpoints use HTTP REST (GET/POST/PUT/DELETE)
- Clarified polling-based message fetching
- Frontend triggers requests on-demand (not real-time)
- Marked WebSocket as future enhancement

### 3. **Updated Diagrams**
- System architecture diagram updated to show JWT/REST emphasis
- Authentication flow diagram updated to show actual JWT process
- Message loading flow diagram added (shows polling, not events)
- Removed WebSocket references from diagrams

### 4. **Technology Stack Accuracy**
- Fetch API is the HTTP client (not additional library)
- Removed false claims about WebSocket/real-time
- Added "Notes" column for implementation details
- Clarified Rocket.Chat is remote (not local)

### 5. **API Endpoints Documentation**
- Listed all actually implemented endpoints
- Marked protected endpoints that require JWT
- Removed planned features from current API list

### 6. **Future Enhancements Expanded**
- WebSocket moved to #1 recommended enhancement
- Added clear description of why WebSocket is needed
- Listed 10 concrete future improvement areas
- Realistic prioritization of features

### 7. **Authentication Section Rewritten**
- JWT Token Strategy section now shows actual implementation
- Step-by-step flow of token generation/validation
- Google OAuth flow documented
- Removed outdated SSO information

---

## What Is ACTUALLY Working

### Frontend
- ✅ React + TypeScript + Tailwind CSS
- ✅ JWT authentication (login/register/Google OAuth)
- ✅ Message pinning UI in DMs, channels, groups
- ✅ Audio call button (UI, no backend)
- ✅ Profile management and uploads
- ✅ Responsive design
- ✅ HTTP API calls via Fetch API

### Backend
- ✅ FastAPI REST endpoints
- ✅ SQLite database (users, messages, pinned_messages)
- ✅ Rocket.Chat API integration (fetching messages, users)
- ✅ Message pinning/unpinning to database
- ✅ User registration and authentication
- ✅ Google OAuth verification
- ✅ Profile picture uploads

### Communication
- ✅ HTTP REST API (GET/POST/PUT/DELETE)
- ✅ Bearer token authentication header
- ✅ JSON request/response bodies
- ✅ Polling-based message fetching

### Database
- ✅ SQLite local database
- ✅ SQLAlchemy ORM models
- ✅ Relationships (users → messages, users → groups)
- ✅ Indexing on key fields

### External Integration
- ✅ Rocket.Chat REST API calls
- ✅ Google OAuth 2.0 ID token verification
- ✅ Message fetching from Rocket.Chat
- ✅ User listing from Rocket.Chat

---