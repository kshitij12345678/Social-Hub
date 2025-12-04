# Railway CLI Tunnel Setup Guide

This guide will help you set up a Railway CLI tunnel to connect to your PostgreSQL database locally.

## Prerequisites

✅ Railway CLI installed: `npm install -g @railway/cli`  
✅ Node.js installed (you have v25.0.0)

## Step-by-Step Instructions

### Step 1: Login to Railway

Open your terminal and run:

```bash
railway login
```

This will:
- Open your browser
- Ask you to authorize Railway CLI
- Complete the login automatically

**Expected output:**
```
Opening browser...
Logged in as: your-email@example.com
```

---

### Step 2: Link to Your Project

Navigate to your project directory and link it:

```bash
cd /Users/ankushchhabra/Downloads/Social-Hub
railway link
```

You'll be prompted to select your project. Choose:
- **Project**: `motivated-spontaneity` (or your project name)
- **Environment**: `production`

**Expected output:**
```
? Select a project: motivated-spontaneity
? Select an environment: production
Linked to project motivated-spontaneity (production)
```

---

### Step 3: Create Tunnel to PostgreSQL

Now create a tunnel to your PostgreSQL database:

```bash
railway connect postgres
```

This will:
- Find your PostgreSQL service
- Create a local tunnel
- Show you the local connection details

**Expected output:**
```
Creating tunnel to postgres...
Tunnel established on localhost:5432
Connection string: postgresql://postgres:PASSWORD@localhost:5432/railway
```

**Note the local port** (usually 5432, but could be different like 5433, 5434, etc.)

---

### Step 4: Update Your .env File

Once the tunnel is running, update your `.env` file with the local connection:

```bash
# In backend/.env
DATABASE_URL=postgresql+psycopg://postgres:jLDqXkXJFTMtapRTPynxdKWEZEkDSsJG@localhost:5432/railway
```

**Important:** 
- Replace `5432` with the actual port shown in Step 3
- Keep the tunnel running in that terminal window!

---

### Step 5: Test the Connection

In a **new terminal window**, test the connection:

```bash
cd /Users/ankushchhabra/Downloads/Social-Hub/backend
source venv/bin/activate
python test_database_connection.py
```

You should see:
```
✅ Database connection successful!
✅ All required tables exist!
```

---

### Step 6: Run Database Migration

Once connected, create the tables:

```bash
python migrate_database.py
```

---

## Keeping the Tunnel Running

**Important:** The tunnel must stay running while you're using the database.

- Keep the terminal with `railway connect postgres` running
- Don't close that terminal window
- If you close it, the connection will break

**To stop the tunnel:**
- Press `Ctrl+C` in the tunnel terminal

**To restart the tunnel:**
- Run `railway connect postgres` again

---

## Alternative: Run Tunnel in Background

You can run the tunnel in the background:

```bash
# Start tunnel in background
railway connect postgres &

# Or use nohup to keep it running after terminal closes
nohup railway connect postgres > railway_tunnel.log 2>&1 &
```

---

## Troubleshooting

### "Not logged in"
```bash
railway login
```

### "No project linked"
```bash
cd /Users/ankushchhabra/Downloads/Social-Hub
railway link
```

### "Cannot find postgres service"
- Make sure you're in the correct project
- Check Railway dashboard - is PostgreSQL service running?
- Try: `railway service` to list services

### "Port already in use"
If port 5432 is already used by local PostgreSQL:
- Railway will use a different port (check the output)
- Update your `.env` with the correct port

### Connection still fails
- Make sure tunnel is running (check the terminal)
- Verify the port in connection string matches tunnel port
- Try restarting the tunnel: `railway connect postgres`

---

## Quick Reference

```bash
# Login
railway login

# Link project
railway link

# Create tunnel (keep this running!)
railway connect postgres

# In another terminal, test connection
cd backend
source venv/bin/activate
python test_database_connection.py

# Run migration
python migrate_database.py
```

---

## Next Steps

Once the tunnel is working:
1. ✅ Test connection
2. ✅ Run migration to create tables
3. ✅ Start your backend: `uvicorn main:app --reload`
4. ✅ Your app will now connect to Railway database via tunnel!

