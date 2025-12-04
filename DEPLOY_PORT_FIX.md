# Deploy PORT Fix - Step by Step

## Current Status

Backend is still showing **502 error** because the PORT fix hasn't been deployed yet.

## Step 1: Commit and Push the Fix

The PORT fix is ready, but needs to be committed and pushed:

```bash
cd /Users/ankushchhabra/Downloads/Social-Hub

# Check what changed
git status

# Add the fixed files
git add backend/Dockerfile railway.json

# Commit
git commit -m "Fix PORT environment variable for Railway deployment"

# Push to trigger redeploy
git push
```

## Step 2: Watch Railway Deploy

1. **Go to Railway Dashboard**
2. **Click your backend service**
3. **Go to "Deployments" tab**
4. **Watch the new deployment**

You should see:
- Building Docker image...
- Starting container...
- Application starting...

## Step 3: Check Logs

After deployment, check logs:

1. **Railway Dashboard** → Backend Service → **"Logs" tab**
2. **Look for:**

✅ **Success:**
```
Starting uvicorn...
Uvicorn running on http://0.0.0.0:XXXX
🔨 Creating database tables...
✅ Database tables created/verified successfully!
```

❌ **Still failing:**
```
Error: Invalid value for '--port': '$PORT'
```

If you still see the PORT error, the fix didn't deploy. Check:
- Did you commit and push?
- Is Railway building from the latest code?
- Check the deployment logs

## Step 4: Verify Environment Variables

While checking logs, also verify:

1. **Railway Dashboard** → Backend Service → **"Variables" tab**
2. **Make sure these are set:**
   - `DATABASE_URL` (Railway sets automatically)
   - `SECRET_KEY` (you need to set this)
   - `ROCKET_CHAT_URL`
   - `ROCKET_CHAT_USER_ID`
   - `ROCKET_CHAT_AUTH_TOKEN`

**Missing `SECRET_KEY` is a common cause of startup failures!**

## Step 5: Test After Deployment

Once deployment completes:

```bash
# Test health endpoint
curl https://social-hub-production-f278.up.railway.app/health

# Should return:
# {"message": "API is healthy and running!"}
```

## If Still Failing After Fix

### Check 1: Railway Logs
- What error messages do you see?
- Is the application starting?
- Any database connection errors?

### Check 2: Environment Variables
- Is `SECRET_KEY` set?
- Are all required variables present?

### Check 3: Service Status
- Is the service showing "Active"?
- Try restarting the service

### Check 4: Database Connection
- Is PostgreSQL service running?
- Check `DATABASE_URL` is set correctly

## Quick Checklist

- [ ] Committed `backend/Dockerfile` with PORT fix
- [ ] Committed `railway.json` with startCommand
- [ ] Pushed to GitHub
- [ ] Railway redeployed
- [ ] Checked logs - no PORT error
- [ ] Verified environment variables
- [ ] Tested API endpoint

## Summary

**Action Required:**
1. Commit and push the PORT fix
2. Wait for Railway to redeploy
3. Check logs for success
4. Test the API

**After fix deploys:** Backend should respond with 200 OK instead of 502!

