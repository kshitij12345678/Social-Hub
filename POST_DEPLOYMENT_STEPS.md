# Post-Deployment Steps - What to Do Now

## ✅ Deployment Successful!

Your backend is now live on Railway. Here's what to do next:

---

## Step 1: Get Your API URL

1. **Go to Railway Dashboard**
2. **Click your backend service**
3. **Go to "Settings" tab**
4. **Find "Domains" section**
5. **Copy the Railway-provided URL** (e.g., `your-service.railway.app`)

Or check the **"Deployments"** tab - the URL is usually shown there.

---

## Step 2: Test Your API

### Test Health Endpoint

```bash
curl https://your-service.railway.app/health
```

**Expected response:**
```json
{"message": "API is healthy and running!"}
```

### Test Root Endpoint

```bash
curl https://your-service.railway.app/
```

**Expected response:**
```json
{"message": "Welcome to Social Hub API"}
```

### Test API Docs

Open in browser:
```
https://your-service.railway.app/docs
```

You should see FastAPI's interactive documentation!

---

## Step 3: Verify Database Connection

### Check Logs

1. **Railway Dashboard** → Your Backend Service
2. **Logs** tab
3. Look for:
   ```
   🔨 Creating database tables...
   ✅ Database tables created/verified successfully!
   ```

If you see this, your database is connected and tables are created!

### Test Database Endpoint

Try registering a test user:

```bash
curl -X POST https://your-service.railway.app/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "full_name": "Test User",
    "password": "testpass123"
  }'
```

**Expected:** Should return a JWT token if successful.

---

## Step 4: Update Frontend to Use Railway Backend

### Find Your Frontend API Configuration

Your frontend likely has an API base URL configured. Update it to point to Railway.

**Check these files:**
- `src/services/api.ts` or similar
- `src/config/` directory
- `.env` or `.env.local` files

### Update API URL

**Example in `src/services/api.ts`:**

```typescript
// Before (local):
const API_BASE_URL = 'http://localhost:8000';

// After (Railway):
const API_BASE_URL = 'https://your-service.railway.app';
```

Or use environment variable:

```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

**Create/Update `.env` or `.env.production`:**
```env
VITE_API_URL=https://your-service.railway.app
```

---

## Step 5: Update CORS Settings (If Needed)

If your frontend is on a different domain, update CORS in your backend:

**In `backend/main.py`:**

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local dev
        "https://your-frontend-domain.com",  # Production frontend
        "https://your-frontend.vercel.app",  # If using Vercel
        # Add your frontend URL here
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

Then redeploy the backend.

---

## Step 6: Deploy Frontend

### Option 1: Deploy to Vercel (Recommended)

1. **Go to** https://vercel.com
2. **Import your GitHub repository**
3. **Set build settings:**
   - Framework: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`
4. **Add environment variable:**
   - `VITE_API_URL` = `https://your-service.railway.app`
5. **Deploy**

### Option 2: Deploy to Netlify

1. **Go to** https://netlify.com
2. **Import your GitHub repository**
3. **Set build settings:**
   - Build command: `npm run build`
   - Publish directory: `dist`
4. **Add environment variable:**
   - `VITE_API_URL` = `https://your-service.railway.app`
5. **Deploy**

### Option 3: Deploy to Railway (Same Platform)

1. **Railway Dashboard** → **"+ New"** → **"GitHub Repo"**
2. **Select your repository**
3. **Set Root Directory:** (leave empty or set to root)
4. **Set Build Command:** `npm run build`
5. **Set Start Command:** (for static site, Railway handles this)
6. **Add environment variable:**
   - `VITE_API_URL` = `https://your-service.railway.app`

---

## Step 7: Test Everything End-to-End

1. **Open your deployed frontend**
2. **Try to register a new user**
3. **Try to login**
4. **Test other features**

---

## Step 8: Monitor Your Backend

### Check Logs Regularly

```bash
railway logs
```

Or in Railway Dashboard → Logs tab

### Monitor Metrics

- Railway Dashboard → **Metrics** tab
- Check CPU, Memory, Network usage

### Set Up Alerts (Optional)

- Railway Dashboard → Settings → Notifications
- Get alerts for deployment failures, errors, etc.

---

## Quick Reference

### Your Backend URL
```
https://your-service.railway.app
```

### API Endpoints
- Health: `GET /health`
- Docs: `GET /docs`
- Register: `POST /auth/register`
- Login: `POST /auth/login`

### Environment Variables on Railway
- `DATABASE_URL` - Auto-set by Railway ✅
- `SECRET_KEY` - You set this
- `ROCKET_CHAT_URL` - You set this
- Other variables you configured

---

## Troubleshooting

### API Not Responding?

1. **Check service is running:**
   - Railway Dashboard → Service status should be "Active"

2. **Check logs:**
   - Look for errors in deployment logs

3. **Test locally:**
   - Make sure your code works locally first

### Database Connection Issues?

1. **Check DATABASE_URL:**
   - Railway automatically sets this
   - Should use internal URL: `postgres.railway.internal:5432`

2. **Check database service:**
   - Make sure PostgreSQL service is running

3. **Check logs:**
   - Look for database connection errors

### Frontend Can't Connect?

1. **Check CORS settings:**
   - Add your frontend URL to allowed origins

2. **Check API URL:**
   - Make sure frontend is using correct Railway URL

3. **Check network:**
   - Open browser console for errors

---

## Next Steps Summary

1. ✅ **Get API URL** from Railway
2. ✅ **Test API** endpoints
3. ✅ **Verify database** connection
4. ⏭️ **Update frontend** API URL
5. ⏭️ **Deploy frontend**
6. ⏭️ **Test end-to-end**

---

## Congratulations! 🎉

Your backend is now:
- ✅ Deployed on Railway
- ✅ Connected to PostgreSQL
- ✅ Database tables created
- ✅ API is live and accessible

**Ready for production!** 🚀

