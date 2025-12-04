# Fix PORT Environment Variable Issue

## Problem

Railway is not expanding `$PORT` in the Dockerfile CMD, causing:
```
Error: Invalid value for '--port': '$PORT' is not a valid integer.
```

## Solution Applied

I've updated the configuration to properly handle the PORT variable:

1. **Updated Dockerfile** - Uses `$PORT` with proper shell expansion
2. **Updated railway.json** - Added explicit startCommand that Railway will use

## What Changed

### Dockerfile
- Changed CMD to use `$PORT` directly (Railway will expand it)
- Added default PORT=8000 as fallback

### railway.json
- Added `startCommand` that Railway will use instead of Dockerfile CMD
- This ensures PORT is properly expanded

## Next Steps

1. **Commit and push changes:**
   ```bash
   git add backend/Dockerfile railway.json
   git commit -m "Fix PORT environment variable handling"
   git push
   ```

2. **Railway will auto-redeploy**

3. **Check logs** - should see:
   ```
   Starting uvicorn on 0.0.0.0:PORT
   ```

## Alternative: Use Procfile

Railway also respects Procfile. The `backend/Procfile` is already set correctly:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

If Dockerfile still doesn't work, Railway will fall back to Procfile.

## Verification

After redeploy, check logs:
- Should NOT see: `Error: Invalid value for '--port': '$PORT'`
- Should see: `Uvicorn running on http://0.0.0.0:XXXX` (where XXXX is the port)

Then test:
```bash
curl https://social-hub-production-f278.up.railway.app/health
```

Should return: `{"message": "API is healthy and running!"}`

