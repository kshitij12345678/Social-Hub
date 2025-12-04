# Fix: Railway Building Frontend Instead of Backend

## Problem

Railway is trying to build your **frontend** (using `bun`) instead of your **backend** (using Python).

**Error:**
```
bun install --frozen-lockfile
error: lockfile had changes, but lockfile is frozen
```

This happens because Railway detects `package.json` and `bun.lockb` in the root directory.

---

## Solution: Set Root Directory

### Step 1: Go to Railway Dashboard

1. Open your Railway project
2. Click on your **backend service** (the one that's failing)
3. Go to **Settings** tab

### Step 2: Set Root Directory

1. Find **"Root Directory"** setting
2. Set it to: `backend`
3. Click **Save**

**This tells Railway:** "Only look in the `backend/` folder, ignore the root directory"

### Step 3: Redeploy

1. Go to **Deployments** tab
2. Click **"Redeploy"** or push new code
3. Railway will now build from `backend/` directory

---

## Alternative: Use Railway.json in Root

If setting Root Directory doesn't work, you can create a `railway.json` in the **root** directory that points to backend:

**Create `/Users/ankushchhabra/Downloads/Social-Hub/railway.json`:**

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "cd backend && pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT"
  }
}
```

But **Root Directory method is better** - use that first!

---

## Verification

After setting Root Directory, the build should:

1. ✅ Detect Python (not Node.js/bun)
2. ✅ Run: `pip install -r requirements.txt`
3. ✅ Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. ✅ Create database tables on startup

**You should see in logs:**
```
Installing Python dependencies...
Installing from requirements.txt...
Starting uvicorn...
🔨 Creating database tables...
✅ Database tables created/verified successfully!
```

---

## Quick Fix Checklist

- [ ] Go to Railway Dashboard → Your Backend Service
- [ ] Settings → Root Directory → Set to: `backend`
- [ ] Save changes
- [ ] Redeploy service
- [ ] Check logs - should see Python build, not bun

---

## Why This Happens

Railway auto-detects project type by looking for:
- `package.json` → Detects Node.js/JavaScript
- `requirements.txt` → Detects Python
- `bun.lockb` → Detects Bun/JavaScript

Since your root has `package.json` and `bun.lockb`, Railway thinks it's a JavaScript project.

**Solution:** Tell Railway to only look in `backend/` folder where `requirements.txt` is.

---

## Files Created

I've also created:
- `backend/nixpacks.toml` - Explicit build configuration
- Updated `backend/railway.json` - Better configuration

But the **Root Directory setting** is the main fix!

