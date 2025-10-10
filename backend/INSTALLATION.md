# Social Hub Backend - Installation Guide

## Quick Setup (Recommended)

### Prerequisites
- Python 3.8+ (tested with Python 3.12)
- pip package manager

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd Social-Hub/backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment
**Linux/Mac:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 4. Install Dependencies
**Option A - Minimal Install (Recommended for first-time):**
```bash
pip install -r requirements-minimal.txt
```

**Option B - Full Install (Exact versions):**
```bash
pip install -r requirements.txt
```

### 5. Test Installation
```bash
python test_setup.py
```

### 6. Start Server
```bash
python main.py
```

## Verification

### Check Server Status
- Server should start on: `http://localhost:8001`
- API Documentation: `http://localhost:8001/docs`
- Health check: `http://localhost:8001/health`

### Database Tables Created
The following tables should be created automatically:
- `users` - User profiles and authentication
- `posts` - Social media posts
- `likes` - Post likes
- `comments` - Post comments  
- `shares` - Post shares
- `locations` - Travel destinations
- `follows` - User relationships
- `user_interests` - Recommendation data
- `post_tags` - Post categories

## Troubleshooting

### Common Issues

**1. Import Errors:**
```bash
# Ensure you're in the virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

**2. Package Installation Failures:**
```bash
# Upgrade pip first
pip install --upgrade pip setuptools wheel

# Then install requirements
pip install -r requirements-minimal.txt
```

**3. Database Issues:**
```bash
# Delete and recreate database
rm social_hub.db
python test_setup.py
```

**4. Port Already in Use:**
```bash
# Kill process on port 8001
lsof -ti:8001 | xargs kill -9  # Linux/Mac
# or change port in main.py
```

## Development Mode

### Enable Hot Reload
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### Test Endpoints
```bash
# Test authentication
curl -X POST "http://localhost:8001/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"full_name": "Test User", "email": "test@example.com", "password": "password123"}'

# Test health
curl http://localhost:8001/health
```

## Next Steps

1. ✅ **Phase 1 Complete**: Backend foundation ready
2. 🎯 **Phase 2**: Generate synthetic data for demo
3. 🚀 **Phase 3**: Connect to frontend
4. 📱 **Phase 4**: Build Instagram-like UI

## File Structure
```
backend/
├── main.py                 # FastAPI application
├── database.py            # Database models
├── schemas.py             # Request/response schemas
├── social_crud.py         # CRUD operations
├── blob_storage.py        # File storage
├── test_setup.py          # Setup validation
├── requirements.txt       # Full dependencies
├── requirements-minimal.txt # Essential dependencies
├── recommender/           # AI recommendation system
└── uploads/               # File storage
```

## Production Deployment

For production deployment, see [DEPLOYMENT.md](DEPLOYMENT.md) (coming soon).

## Support

If you encounter any issues:
1. Check this README
2. Run `python test_setup.py` for diagnostics
3. Check server logs for detailed error messages
4. Ensure all dependencies are properly installed