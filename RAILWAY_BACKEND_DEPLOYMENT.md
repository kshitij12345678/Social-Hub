# Deploy Backend to Railway - Complete Guide

This guide will walk you through deploying your FastAPI backend to Railway.

## Prerequisites

- ✅ Railway account (you have this)
- ✅ PostgreSQL database on Railway (you have this)
- ✅ Backend code ready (you have this)
- ✅ GitHub repository (recommended) or code ready to deploy

---

## Method 1: Deploy from GitHub (Recommended)

### Step 1: Push Code to GitHub

If your code isn't on GitHub yet:

```bash
# Initialize git if not already done
cd /Users/ankushchhabra/Downloads/Social-Hub
git init  # if not already initialized
git add .
git commit -m "Initial commit - ready for Railway deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/Social-Hub.git
git branch -M main
git push -u origin main
```

**Important:** Make sure `.env` is in `.gitignore` (don't commit secrets!)

---

### Step 2: Create Backend Service on Railway

1. **Go to Railway Dashboard**
   - Visit: https://railway.app
   - Open your project: `motivated-spontaneity`

2. **Create New Service**
   - Click **"+ New"** button (top right)
   - Select **"GitHub Repo"**
   - Authorize Railway to access GitHub (if first time)
   - Select your repository: `Social-Hub`
   - Railway will create a new service

3. **Configure Service**
   - Railway will detect it's a Python project
   - It will automatically find `requirements.txt` in the `backend/` folder
   - **Set Root Directory:**
     - Go to **Settings** tab
     - Find **"Root Directory"** setting
     - Set it to: `backend`
     - This tells Railway where your Python code is

---

### Step 3: Configure Environment Variables

Railway will automatically set `DATABASE_URL`, but you need to set other variables:

1. **Go to Variables Tab**
   - Click on your backend service
   - Go to **"Variables"** tab
   - Click **"+ New Variable"**

2. **Add These Variables:**

```env
# JWT Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Rocket.Chat Configuration
ROCKET_CHAT_URL=http://10.68.0.49:30082
ROCKET_CHAT_USER_ID=K8MHCfESxc7zJrdg3
ROCKET_CHAT_AUTH_TOKEN=S4j_j25SJLVeQmwySRVc1-O-S7QIa6yK7zuKDgO1L9_

# Google OAuth (if using)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

**Important:**
- `DATABASE_URL` is **automatically set** by Railway (don't add it manually)
- Railway will use the internal URL: `postgres.railway.internal:5432`
- Generate a strong `SECRET_KEY` for production (use a random string generator)

---

### Step 4: Configure Build Settings

1. **Go to Settings Tab**
2. **Build Command:** (usually auto-detected, but verify)
   ```
   pip install -r requirements.txt
   ```
3. **Start Command:** (set this)
   ```
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
   Railway sets `$PORT` automatically.

4. **Root Directory:** (important!)
   ```
   backend
   ```

---

### Step 5: Deploy

1. **Railway will automatically deploy** when you:
   - Push code to GitHub (if connected)
   - Or click **"Deploy"** button

2. **Watch the Logs**
   - Go to **"Deployments"** tab
   - Click on the latest deployment
   - Watch the build logs
   - You should see:
     ```
     Installing dependencies...
     Building...
     Starting...
     🔨 Creating database tables...
     ✅ Database tables created/verified successfully!
     ```

3. **Check Service URL**
   - Railway will generate a URL like: `your-service.railway.app`
   - You can find it in the **"Settings"** tab → **"Domains"**

---

## Method 2: Deploy from Local Code (Alternative)

If you don't want to use GitHub:

1. **Install Railway CLI** (if not already installed)
   ```bash
   npm install -g @railway/cli
   ```

2. **Login and Link**
   ```bash
   railway login
   cd /Users/ankushchhabra/Downloads/Social-Hub
   railway link
   ```

3. **Deploy**
   ```bash
   cd backend
   railway up
   ```

---

## Verification Steps

### 1. Check Deployment Logs

```bash
railway logs
```

Look for:
- ✅ "Installing dependencies"
- ✅ "Starting uvicorn"
- ✅ "Creating database tables..."
- ✅ "Application startup complete"

### 2. Test Health Endpoint

```bash
curl https://your-service.railway.app/health
```

Expected response:
```json
{"message": "API is healthy and running!"}
```

### 3. Test Root Endpoint

```bash
curl https://your-service.railway.app/
```

Expected response:
```json
{"message": "Welcome to Social Hub API"}
```

### 4. Check Database Connection

The logs should show:
```
✅ Database tables created/verified successfully!
```

If you see errors, check:
- `DATABASE_URL` is set (Railway sets this automatically)
- Database service is running
- Network connectivity

---

## Troubleshooting

### Issue: "Module not found"

**Solution:**
- Check `requirements.txt` has all dependencies
- Verify Root Directory is set to `backend`
- Check build logs for installation errors

### Issue: "Port already in use"

**Solution:**
- Railway sets `$PORT` automatically
- Make sure start command uses: `--port $PORT`
- Don't hardcode port numbers

### Issue: "Database connection failed"

**Solution:**
- Railway automatically sets `DATABASE_URL`
- Check database service is running
- Verify both services are in same project/environment

### Issue: "Tables not created"

**Solution:**
- Check startup logs for errors
- Verify `create_tables()` is called in `main.py`
- Check database permissions

### Issue: "Build fails"

**Solution:**
- Check Python version (Railway uses Python 3.11+ by default)
- Verify `requirements.txt` is in `backend/` folder
- Check build logs for specific errors

---

## Setting Up Custom Domain (Optional)

1. **Go to Settings → Domains**
2. **Click "Generate Domain"** or **"Add Custom Domain"**
3. **Configure DNS** (if custom domain)
4. **SSL is automatic** (Railway handles it)

---

## Monitoring and Logs

### View Logs in Dashboard
- Go to your service → **"Logs"** tab
- Real-time logs are shown

### View Logs via CLI
```bash
railway logs
```

### View Specific Service Logs
```bash
railway logs --service your-service-name
```

---

## Environment Variables Reference

### Automatically Set by Railway:
- `DATABASE_URL` - PostgreSQL connection (internal URL)
- `PORT` - Port to run the app
- `RAILWAY_ENVIRONMENT` - Environment name
- `RAILWAY_PROJECT_ID` - Project identifier

### You Need to Set:
- `SECRET_KEY` - JWT secret key
- `ROCKET_CHAT_URL` - Rocket.Chat server URL
- `ROCKET_CHAT_USER_ID` - Rocket.Chat user ID
- `ROCKET_CHAT_AUTH_TOKEN` - Rocket.Chat auth token
- `GOOGLE_CLIENT_ID` - (if using Google OAuth)
- `GOOGLE_CLIENT_SECRET` - (if using Google OAuth)

---

## Next Steps After Deployment

1. ✅ **Test API endpoints**
   ```bash
   curl https://your-service.railway.app/health
   ```

2. ✅ **Update Frontend**
   - Update frontend API URL to point to Railway backend
   - Deploy frontend (Vercel, Netlify, etc.)

3. ✅ **Monitor Performance**
   - Check Railway dashboard for metrics
   - Monitor logs for errors

4. ✅ **Set Up Backups** (if needed)
   - Railway handles database backups automatically
   - Check database service → Backups tab

---

## Quick Reference

**Railway Dashboard:** https://railway.app  
**CLI Commands:**
```bash
railway login          # Login to Railway
railway link           # Link project
railway up             # Deploy from current directory
railway logs           # View logs
railway variables      # View environment variables
```

**Service URL Format:**
```
https://your-service-name.railway.app
```

**Database Connection:**
- Automatically configured
- Uses internal URL: `postgres.railway.internal:5432`
- No manual setup needed!

---

## Summary

✅ **What Railway Does Automatically:**
- Detects Python project
- Installs dependencies from `requirements.txt`
- Sets `DATABASE_URL` with internal connection
- Provides public URL for your API
- Handles SSL certificates

✅ **What You Need to Do:**
- Set Root Directory to `backend`
- Set Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Add environment variables (SECRET_KEY, etc.)
- Deploy!

Your backend will automatically:
- Connect to PostgreSQL
- Create database tables on startup
- Start serving API requests

**Ready to deploy!** 🚀

