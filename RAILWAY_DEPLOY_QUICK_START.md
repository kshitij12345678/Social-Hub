# Railway Backend Deployment - Quick Start

## 🚀 5-Minute Deployment Guide

### Step 1: Prepare Your Code (2 minutes)

✅ **Files Created:**
- `backend/Procfile` - Tells Railway how to start your app
- `backend/runtime.txt` - Specifies Python version
- `backend/railway.json` - Railway configuration

✅ **Your code is ready!** These files are already created.

---

### Step 2: Push to GitHub (if not already)

```bash
cd /Users/ankushchhabra/Downloads/Social-Hub
git add .
git commit -m "Add Railway deployment config"
git push
```

---

### Step 3: Deploy on Railway (3 minutes)

1. **Go to Railway Dashboard**
   - https://railway.app
   - Open project: `motivated-spontaneity`

2. **Create New Service**
   - Click **"+ New"** → **"GitHub Repo"**
   - Select: `Social-Hub` repository
   - Railway creates service automatically

3. **Configure Service**
   - Go to **Settings** tab
   - **Root Directory:** Set to `backend`
   - **Start Command:** (already in Procfile, but verify)
     ```
     uvicorn main:app --host 0.0.0.0 --port $PORT
     ```

4. **Add Environment Variables**
   - Go to **Variables** tab
   - Click **"+ New Variable"**
   - Add these (Railway auto-sets `DATABASE_URL`):

   ```
   SECRET_KEY=your-super-secret-key-here
   ROCKET_CHAT_URL=http://10.68.0.49:30082
   ROCKET_CHAT_USER_ID=K8MHCfESxc7zJrdg3
   ROCKET_CHAT_AUTH_TOKEN=S4j_j25SJLVeQmwySRVc1-O-S7QIa6yK7zuKDgO1L9_
   ```

5. **Deploy**
   - Railway auto-deploys when you connect GitHub
   - Or click **"Deploy"** button
   - Watch logs in **Deployments** tab

---

### Step 4: Verify (1 minute)

1. **Check Logs**
   - Look for: `✅ Database tables created/verified successfully!`

2. **Test API**
   ```bash
   curl https://your-service.railway.app/health
   ```
   Should return: `{"message": "API is healthy and running!"}`

3. **Get Your API URL**
   - Settings → Domains
   - Copy the Railway-provided URL

---

## ✅ That's It!

Your backend is now:
- ✅ Deployed on Railway
- ✅ Connected to PostgreSQL (automatic)
- ✅ Tables created (automatic)
- ✅ Ready to accept requests

---

## 🔧 Quick Troubleshooting

**Build fails?**
- Check Root Directory is `backend`
- Verify `requirements.txt` exists in `backend/`

**Database connection fails?**
- Railway sets `DATABASE_URL` automatically
- Check database service is running
- Both services must be in same project

**Tables not created?**
- Check startup logs
- Look for `create_tables()` execution

---

## 📋 What Happens Automatically

✅ Railway detects Python project  
✅ Installs from `requirements.txt`  
✅ Sets `DATABASE_URL` (internal connection)  
✅ Runs `create_tables()` on startup  
✅ Provides public URL  
✅ Handles SSL  

**You just need to:**
- Set Root Directory: `backend`
- Add environment variables
- Deploy!

---

## 🎯 Next Steps

1. **Get your API URL** from Railway dashboard
2. **Update frontend** to use Railway backend URL
3. **Deploy frontend** (Vercel, Netlify, etc.)
4. **Test everything** end-to-end

---

**Full guide:** See `RAILWAY_BACKEND_DEPLOYMENT.md` for detailed instructions.

