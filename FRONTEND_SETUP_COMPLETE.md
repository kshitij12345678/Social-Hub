# Frontend Setup - Ready for Deployment

## ✅ Configuration Updated

I've updated your frontend to use the Railway backend URL.

### Files Updated:
- ✅ `src/services/api.ts` - Now uses `VITE_API_URL` environment variable
- ✅ `.env.production` - Created with your Railway URL

---

## Your Backend URL

```
https://social-hub-production-f278.up.railway.app
```

**Note:** Currently showing 502 error - need to fix backend first (see BACKEND_502_FIX.md)

---

## Frontend Configuration

### For Local Development

Create `.env.local` (or use existing):
```env
VITE_API_URL=http://localhost:8000
```

### For Production Build

`.env.production` is already created:
```env
VITE_API_URL=https://social-hub-production-f278.up.railway.app
```

---

## Deploy Frontend

### Option 1: Vercel (Recommended)

1. **Go to** https://vercel.com
2. **Import GitHub repository**
3. **Configure:**
   - Framework: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`
4. **Environment Variables:**
   - `VITE_API_URL` = `https://social-hub-production-f278.up.railway.app`
5. **Deploy**

### Option 2: Netlify

1. **Go to** https://netlify.com
2. **Import GitHub repository**
3. **Configure:**
   - Build command: `npm run build`
   - Publish directory: `dist`
4. **Environment Variables:**
   - `VITE_API_URL` = `https://social-hub-production-f278.up.railway.app`
5. **Deploy**

### Option 3: Railway

1. **Railway Dashboard** → **"+ New"** → **"GitHub Repo"**
2. **Select repository**
3. **Settings:**
   - Build Command: `npm run build`
   - Output Directory: `dist`
4. **Variables:**
   - `VITE_API_URL` = `https://social-hub-production-f278.up.railway.app`

---

## Update CORS After Frontend Deployment

Once you deploy your frontend, add its URL to CORS in `backend/main.py`:

```python
allow_origins=[
    "http://localhost:5173",
    "https://your-frontend.vercel.app",  # Add your frontend URL
    # ... other origins
],
```

Then redeploy backend.

---

## Current Status

- ✅ Frontend configured to use Railway backend
- ⚠️ Backend showing 502 error (needs fixing)
- ⏭️ Fix backend first, then deploy frontend

---

## Next Steps

1. **Fix backend 502 error** (check Railway logs)
2. **Test backend** - should return 200 OK
3. **Deploy frontend** with Railway URL
4. **Update CORS** with frontend URL
5. **Test everything** end-to-end

---

**Priority:** Fix the backend 502 error first, then proceed with frontend deployment!

