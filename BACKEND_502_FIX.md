# Fix 502 Error - Backend Not Responding

## Current Issue

Your backend URL `https://social-hub-production-f278.up.railway.app` is returning:
```
502 - Application failed to respond
```

This means the backend service isn't responding. Let's fix it!

---

## Step 1: Check Railway Logs

1. **Go to Railway Dashboard**
2. **Click your backend service**
3. **Go to "Logs" tab**
4. **Look for errors**

Common issues to look for:
- ❌ Database connection errors
- ❌ Missing environment variables
- ❌ Application crashes on startup
- ❌ Port binding issues

---

## Step 2: Common Fixes

### Fix 1: Check Environment Variables

Make sure all required variables are set:

1. **Railway Dashboard** → Backend Service → **Variables** tab
2. **Verify these are set:**
   - `DATABASE_URL` (Railway sets this automatically)
   - `SECRET_KEY` (you need to set this)
   - `ROCKET_CHAT_URL`
   - `ROCKET_CHAT_USER_ID`
   - `ROCKET_CHAT_AUTH_TOKEN`

### Fix 2: Check Service Status

1. **Railway Dashboard** → Backend Service
2. **Check status** - should be "Active" (green)
3. **If not active**, try restarting:
   - Click "..." menu → "Restart"

### Fix 3: Check Port Configuration

The Dockerfile uses `${PORT:-8000}` which should work, but verify:

1. **Settings** → Check if PORT is set
2. Railway automatically sets PORT, so this should be fine

### Fix 4: Check Database Connection

If database connection fails, the app won't start:

1. **Check logs** for database errors
2. **Verify PostgreSQL service** is running
3. **Check DATABASE_URL** is set correctly

---

## Step 3: Check Specific Errors in Logs

Look for these in the logs:

### Error: "Module not found"
**Fix:** Check `requirements.txt` has all dependencies

### Error: "DATABASE_URL not set"
**Fix:** Railway should set this automatically, but verify in Variables

### Error: "Connection refused" (database)
**Fix:** Check PostgreSQL service is running

### Error: "Port already in use"
**Fix:** Railway handles ports automatically, but check settings

### Error: "Tables creation failed"
**Fix:** Check database permissions and connection

---

## Step 4: Restart Service

1. **Railway Dashboard** → Backend Service
2. **Click "..." menu** → **"Restart"**
3. **Watch logs** to see if it starts successfully

---

## Step 5: Verify Startup

After restart, logs should show:

```
Starting uvicorn...
🔨 Creating database tables...
✅ Database tables created/verified successfully!
Application startup complete.
```

---

## Quick Debugging Commands

### Check if service is running:
```bash
railway status
```

### View logs:
```bash
railway logs
```

### Check variables:
```bash
railway variables
```

---

## If Still Failing

1. **Share the error logs** from Railway
2. **Check all environment variables** are set
3. **Verify database service** is running
4. **Try redeploying** from scratch

---

## After Fix: Test Backend

Once fixed, test:

```bash
# Health check
curl https://social-hub-production-f278.up.railway.app/health

# Should return:
# {"message": "API is healthy and running!"}
```

---

## Next Steps After Fix

1. ✅ Backend responds correctly
2. ⏭️ Update frontend with API URL
3. ⏭️ Deploy frontend
4. ⏭️ Test end-to-end

---

**Action:** Check Railway logs and share any errors you see!

