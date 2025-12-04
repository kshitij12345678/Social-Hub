# Fix Railway Build Error - Step by Step

## Current Error
```
bun install --frozen-lockfile
error: lockfile had changes, but lockfile is frozen
```

**Problem:** Railway is detecting frontend files and trying to build with `bun` instead of Python.

---

## Solution 1: Set Root Directory (RECOMMENDED)

### In Railway Dashboard:

1. **Go to your backend service** (the one showing the error)
2. **Click "Settings" tab** (left sidebar)
3. **Scroll down to "Root Directory"**
4. **Enter:** `backend`
5. **Click "Save"** (or "Update")
6. **Go to "Deployments" tab**
7. **Click "Redeploy"** (or trigger a new deployment)

**This is the PRIMARY fix!** Railway will now only look in the `backend/` folder.

---

## Solution 2: If Root Directory Doesn't Work

If you've set Root Directory but it's still failing, try these:

### Option A: Delete and Recreate Service

1. **Delete the current backend service** in Railway
2. **Create a new service**
3. **When connecting GitHub repo**, immediately go to Settings
4. **Set Root Directory to `backend` BEFORE first deployment**
5. **Then deploy**

### Option B: Use Railway CLI

```bash
# Link to your project
railway link

# Set root directory via CLI
railway variables set RAILWAY_ROOT_DIRECTORY=backend

# Or deploy with explicit root
cd backend
railway up
```

---

## Solution 3: Force Python Detection

I've created files to force Railway to detect Python:

1. **`railway.json`** in root - Forces backend build
2. **`nixpacks.toml`** in root - Explicit Python configuration
3. **`.railwayignore`** - Ignores frontend files

**After creating these files:**
- Commit and push to GitHub
- Railway will redeploy automatically
- Should now detect Python instead of bun

---

## Verification Checklist

After applying the fix, check the build logs. You should see:

✅ **Correct (Python):**
```
Detecting Python project...
Installing dependencies from requirements.txt...
Starting uvicorn...
```

❌ **Wrong (Still bun):**
```
bun install --frozen-lockfile
```

---

## Step-by-Step Fix (Do This Now)

### Step 1: Check Railway Settings

1. Open Railway Dashboard
2. Click your backend service
3. Go to **Settings** tab
4. Check **"Root Directory"** value
5. **If it's empty or wrong:** Set to `backend` and Save

### Step 2: Commit New Files

The files I created will help force Python detection:

```bash
cd /Users/ankushchhabra/Downloads/Social-Hub
git add railway.json nixpacks.toml .railwayignore
git commit -m "Fix Railway build - force Python detection"
git push
```

### Step 3: Redeploy

- Railway will auto-deploy on push, OR
- Go to Deployments → Click "Redeploy"

### Step 4: Verify

Check build logs - should see Python build, not bun.

---

## Why This Happens

Railway's auto-detection looks for:
- `package.json` → Detects JavaScript/Node.js
- `bun.lockb` → Detects Bun
- `requirements.txt` → Detects Python

Your root has both frontend (package.json, bun.lockb) and backend (requirements.txt in backend/).

**Solution:** Tell Railway to only look in `backend/` folder.

---

## If Still Failing

1. **Check Root Directory is saved:**
   - Settings → Root Directory → Should say `backend`
   - If it says `/` or empty, set it to `backend`

2. **Check service is linked correctly:**
   - Make sure you're editing the BACKEND service, not frontend
   - Backend service should be separate from frontend

3. **Try explicit build command:**
   - Settings → Build Command
   - Set to: `cd backend && pip install -r requirements.txt`

4. **Check deployment logs:**
   - Look for what Railway is detecting
   - Should say "Python" not "Node.js" or "Bun"

---

## Quick Test

After setting Root Directory, the build should:
1. ✅ Skip `bun install`
2. ✅ Run `pip install -r requirements.txt`
3. ✅ Start `uvicorn main:app`

If you still see `bun install`, the Root Directory isn't set correctly.

---

## Summary

**Main Fix:** Set Root Directory to `backend` in Railway Settings

**Backup Fix:** Files I created (`railway.json`, `nixpacks.toml`) will help

**Verify:** Check build logs show Python, not bun

