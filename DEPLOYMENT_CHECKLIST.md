# Deployment Checklist

Complete step-by-step checklist for deploying Social Hub application.

## Prerequisites

- [ ] Code is committed to git repository
- [ ] All environment variables documented
- [ ] Database backup created (if migrating from local)

---

## Phase 1: Database Deployment

### Step 1: Choose Database Provider
- [ ] Select a PostgreSQL hosting service (Railway, Supabase, AWS RDS, etc.)
- [ ] Create account on chosen platform
- [ ] Create PostgreSQL database instance
- [ ] Note down connection details:
  - [ ] Host/Endpoint
  - [ ] Port (usually 5432)
  - [ ] Database name
  - [ ] Username
  - [ ] Password
  - [ ] Full connection string

### Step 2: Configure Database
- [ ] Database instance is running
- [ ] Database is accessible from your network
- [ ] Security group/firewall allows connections (if needed)
- [ ] SSL/TLS is enabled (recommended)

### Step 3: Run Database Migration
- [ ] Set `DATABASE_URL` environment variable locally
- [ ] Test connection: `python backend/migrate_database.py`
- [ ] Verify all 5 tables created:
  - [ ] users
  - [ ] chat_messages
  - [ ] groups
  - [ ] group_members
  - [ ] pinned_messages

---

## Phase 2: Backend Deployment

### Step 1: Prepare Backend
- [ ] All dependencies in `requirements.txt` are up to date
- [ ] Environment variables documented in `.env.example`
- [ ] No hardcoded credentials in code
- [ ] CORS settings updated for production frontend URL

### Step 2: Choose Backend Hosting
- [ ] Select hosting platform (Heroku, Railway, Render, AWS, etc.)
- [ ] Create backend application/service

### Step 3: Configure Backend Environment
Set these environment variables on your hosting platform:

- [ ] `DATABASE_URL` - PostgreSQL connection string
- [ ] `SECRET_KEY` - JWT secret key (generate strong random string)
- [ ] `ROCKET_CHAT_URL` - Rocket.Chat server URL
- [ ] `ROCKET_CHAT_ADMIN_USERNAME` - Admin username
- [ ] `ROCKET_CHAT_ADMIN_PASSWORD` - Admin password
- [ ] `GOOGLE_CLIENT_ID` - Google OAuth client ID (if using)
- [ ] `GOOGLE_CLIENT_SECRET` - Google OAuth secret (if using)
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration (default: 30)

### Step 4: Deploy Backend
- [ ] Connect git repository to hosting platform
- [ ] Set build command (if needed): `pip install -r requirements.txt`
- [ ] Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- [ ] Deploy backend
- [ ] Note backend URL (e.g., `https://api.yourdomain.com`)

### Step 5: Verify Backend
- [ ] Backend is accessible at the URL
- [ ] Health check endpoint works: `GET /` or `/docs`
- [ ] Database connection works (check logs)
- [ ] API endpoints respond correctly
- [ ] CORS is configured for frontend domain

---

## Phase 3: Frontend Deployment

### Step 1: Prepare Frontend
- [ ] Update API base URL in frontend code
- [ ] Check `src/services/api.ts` for API endpoint configuration
- [ ] Update CORS settings if needed
- [ ] Build frontend locally to test: `npm run build`

### Step 2: Choose Frontend Hosting
- [ ] Select hosting platform (Vercel, Netlify, AWS S3+CloudFront, etc.)
- [ ] Create frontend application/project

### Step 3: Configure Frontend Environment
Set these environment variables (if using):

- [ ] `VITE_API_URL` - Backend API URL (e.g., `https://api.yourdomain.com`)
- [ ] `VITE_GOOGLE_CLIENT_ID` - Google OAuth client ID (if using)

### Step 4: Deploy Frontend
- [ ] Connect git repository
- [ ] Set build command: `npm run build`
- [ ] Set output directory: `dist`
- [ ] Deploy frontend
- [ ] Note frontend URL (e.g., `https://yourdomain.com`)

### Step 5: Update Backend CORS
- [ ] Add frontend URL to backend CORS allowed origins
- [ ] Redeploy backend if needed

---

## Phase 4: Post-Deployment

### Step 1: Testing
- [ ] Frontend loads correctly
- [ ] User registration works
- [ ] User login works
- [ ] API calls to backend succeed
- [ ] Database operations work (create, read, update)
- [ ] File uploads work (profile pictures)
- [ ] Rocket.Chat integration works (if applicable)

### Step 2: Security
- [ ] All environment variables are set (not using defaults)
- [ ] HTTPS is enabled (SSL certificates)
- [ ] Database credentials are secure
- [ ] API keys are not exposed in frontend code
- [ ] CORS is properly configured

### Step 3: Monitoring
- [ ] Set up error logging/monitoring
- [ ] Set up database monitoring
- [ ] Set up uptime monitoring
- [ ] Configure alerts for critical issues

### Step 4: Backup
- [ ] Database backup is configured
- [ ] Backup schedule is set (daily recommended)
- [ ] Backup restoration is tested

---

## Quick Reference

### Database Connection String Format
```
postgresql+psycopg://username:password@host:port/database
```

### Required Database Tables
- users
- chat_messages
- groups
- group_members
- pinned_messages

### Backend Environment Variables
```env
DATABASE_URL=postgresql+psycopg://...
SECRET_KEY=your-secret-key
ROCKET_CHAT_URL=https://...
ROCKET_CHAT_ADMIN_USERNAME=admin
ROCKET_CHAT_ADMIN_PASSWORD=password
```

### Frontend Environment Variables
```env
VITE_API_URL=https://api.yourdomain.com
VITE_GOOGLE_CLIENT_ID=your-client-id
```

---

## Common Issues & Solutions

### Database Connection Failed
- Check DATABASE_URL format
- Verify database is accessible
- Check firewall/security group rules
- Ensure SSL mode is correct

### Backend Won't Start
- Check all environment variables are set
- Verify Python version matches requirements
- Check logs for specific errors
- Ensure port is correctly configured

### Frontend Can't Connect to Backend
- Verify API URL is correct
- Check CORS settings in backend
- Ensure backend is accessible
- Check browser console for errors

### Database Tables Missing
- Run migration script: `python backend/migrate_database.py`
- Check database user has CREATE TABLE permissions
- Verify DATABASE_URL points to correct database

---

## Deployment Platforms Comparison

| Platform | Database | Backend | Frontend | Free Tier |
|----------|----------|---------|----------|-----------|
| Railway | ✅ | ✅ | ✅ | Limited |
| Render | ✅ | ✅ | ✅ | Limited |
| Heroku | ✅ | ✅ | ✅ | No |
| Vercel | ❌ | ✅ | ✅ | Yes |
| Netlify | ❌ | ❌ | ✅ | Yes |
| AWS | ✅ | ✅ | ✅ | Limited |
| Supabase | ✅ | ❌ | ❌ | Yes |

---

## Next Steps After Deployment

1. **Set up custom domain** (optional)
2. **Configure SSL certificates** (usually automatic)
3. **Set up monitoring and alerts**
4. **Configure automated backups**
5. **Set up CI/CD pipeline** (optional)
6. **Document deployment process** for team
7. **Set up staging environment** (recommended)

---

## Support Resources

- Database Deployment: See `DATABASE_DEPLOYMENT_GUIDE.md`
- Backend Setup: See `backend/README.md`
- Frontend Setup: See `README.md`
- Troubleshooting: Check platform-specific documentation

