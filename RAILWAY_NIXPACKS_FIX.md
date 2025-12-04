# Fix Nixpacks Build Error

## Error
```
error: undefined variable 'pip'
```

This happens because `nixpacks.toml` is trying to use `pip` as a Nix package, but it should use Python's built-in pip.

## Solution

I've fixed the `nixpacks.toml` files to use:
- `python3 -m pip` instead of just `pip`
- `python3 -m uvicorn` instead of just `uvicorn`

## Better Solution: Remove nixpacks.toml

Actually, **the best solution is to let Railway auto-detect Python**. The `nixpacks.toml` might be causing issues.

### Option 1: Delete nixpacks.toml (Recommended)

```bash
cd /Users/ankushchhabra/Downloads/Social-Hub
rm nixpacks.toml
rm backend/nixpacks.toml
```

Then:
1. **Set Root Directory to `backend`** in Railway Settings
2. Railway will auto-detect Python from `requirements.txt`
3. Redeploy

### Option 2: Keep Fixed nixpacks.toml

I've fixed the files, but Railway's auto-detection is usually better.

## What to Do Now

1. **Delete nixpacks.toml files:**
   ```bash
   rm /Users/ankushchhabra/Downloads/Social-Hub/nixpacks.toml
   rm /Users/ankushchhabra/Downloads/Social-Hub/backend/nixpacks.toml
   ```

2. **Verify Root Directory is set:**
   - Railway Dashboard → Backend Service → Settings
   - Root Directory should be: `backend`

3. **Redeploy:**
   - Railway will auto-detect Python
   - Should work without nixpacks.toml

## Why This Happens

Railway's Nixpacks builder:
- Auto-detects Python from `requirements.txt`
- Works best when you let it auto-detect
- Custom `nixpacks.toml` can sometimes cause issues

**Best practice:** Set Root Directory to `backend` and let Railway auto-detect!

