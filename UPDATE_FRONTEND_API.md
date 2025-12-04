# Update Frontend to Use Railway Backend

## ✅ Backend Deployed Successfully!

Now you need to connect your frontend to the Railway backend.

---

## Step 1: Get Your Railway Backend URL

1. **Railway Dashboard** → Your Backend Service
2. **Settings** → **Domains**
3. **Copy the URL** (e.g., `https://your-service.railway.app`)

---

## Step 2: Update Frontend API Configuration

I've already updated `src/services/api.ts` to use an environment variable.

### Create `.env` File for Local Development

```bash
cd /Users/ankushchhabra/Downloads/Social-Hub
cp .env.example .env
```

Edit `.env`:
```env
VITE_API_URL=http://localhost:8000
```

### Create `.env.production` for Production Build

```bash
# Create production env file
cat > .env.production << EOF
VITE_API_URL=https://your-service.railway.app
EOF
```

**Replace `your-service.railway.app` with your actual Railway URL!**

---

## Step 3: Update CORS in Backend (If Needed)

If your frontend will be on a different domain, update CORS:

**In `backend/main.py`:**

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local dev
        "http://localhost:3000",
        "http://localhost:8080",
        "https://your-frontend-domain.com",  # Add your production frontend URL
        "https://your-frontend.vercel.app",  # If using Vercel
        "https://your-frontend.netlify.app",  # If using Netlify
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

Then commit and redeploy backend.

---

## Step 4: Test Locally

```bash
# Start backend locally (if testing)
cd backend
source venv/bin/activate
uvicorn main:app --reload

# In another terminal, start frontend
npm run dev
```

Frontend should connect to localhost backend.

---

## Step 5: Deploy Frontend

### Option A: Vercel (Recommended)

1. **Go to** https://vercel.com
2. **Import GitHub repository**
3. **Configure:**
   - Framework: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`
4. **Environment Variables:**
   - `VITE_API_URL` = `https://your-service.railway.app`
5. **Deploy**

### Option B: Netlify

1. **Go to** https://netlify.com
2. **Import GitHub repository**
3. **Configure:**
   - Build command: `npm run build`
   - Publish directory: `dist`
4. **Environment Variables:**
   - `VITE_API_URL` = `https://your-service.railway.app`
5. **Deploy**

### Option C: Railway

1. **Railway Dashboard** → **"+ New"** → **"GitHub Repo"**
2. **Select repository**
3. **Settings:**
   - Build Command: `npm run build`
   - Output Directory: `dist`
4. **Variables:**
   - `VITE_API_URL` = `https://your-service.railway.app`

---

## Step 6: Test Everything

1. **Open deployed frontend**
2. **Try registering a user**
3. **Try logging in**
4. **Test other features**

---

## Quick Checklist

- [ ] Get Railway backend URL
- [ ] Update `.env.production` with Railway URL
- [ ] Update CORS in backend (if frontend on different domain)
- [ ] Test locally
- [ ] Deploy frontend
- [ ] Test end-to-end

---

## Files Updated

✅ `src/services/api.ts` - Now uses `VITE_API_URL` environment variable
✅ `.env.example` - Template for environment variables

---

## Summary

**Backend:** ✅ Deployed on Railway  
**Frontend:** ⏭️ Update API URL → Deploy  
**Next:** Test everything end-to-end!

