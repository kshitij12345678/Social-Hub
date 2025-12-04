# Database Deployment Guide

This guide will help you deploy your PostgreSQL database to the cloud and connect your backend to it.

## Overview

Your application uses **PostgreSQL** as the database. For production deployment, you have several options:

1. **Managed PostgreSQL Services** (Recommended - Easiest)
   - AWS RDS PostgreSQL
   - Google Cloud SQL
   - Azure Database for PostgreSQL
   - Heroku Postgres
   - Railway PostgreSQL
   - Supabase
   - Neon
   - Render PostgreSQL

2. **Self-Hosted PostgreSQL** (More control, more maintenance)
   - Docker container on a VPS
   - Direct installation on a server

---

## Option 1: Managed PostgreSQL Services (Recommended)

### A. Railway PostgreSQL (Easiest for Quick Start)

**Steps:**
1. Go to [railway.app](https://railway.app) and sign up
2. Create a new project
3. Click "New" → "Database" → "Add PostgreSQL"
4. Railway will automatically create a PostgreSQL instance
5. Click on the database service → "Variables" tab
6. Copy the `DATABASE_URL` (it will look like: `postgresql://postgres:password@hostname.railway.app:5432/railway`)

**Update your backend:**
- Set `DATABASE_URL` environment variable to the Railway connection string
- Make sure to use `postgresql+psycopg://` prefix for SQLAlchemy:
  ```
  DATABASE_URL=postgresql+psycopg://postgres:password@hostname.railway.app:5432/railway
  ```

---

### B. Supabase (Free Tier Available)

**Steps:**
1. Go to [supabase.com](https://supabase.com) and sign up
2. Create a new project
3. Go to "Settings" → "Database"
4. Find "Connection string" → "URI"
5. Copy the connection string (format: `postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres`)

**Update your backend:**
```
DATABASE_URL=postgresql+psycopg://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres
```

---

### C. Neon (Serverless PostgreSQL)

**Steps:**
1. Go to [neon.tech](https://neon.tech) and sign up
2. Create a new project
3. Copy the connection string from the dashboard
4. Use it as your `DATABASE_URL`

---

### D. Render PostgreSQL

**Steps:**
1. Go to [render.com](https://render.com) and sign up
2. Click "New" → "PostgreSQL"
3. Configure:
   - Name: `socialhub-db`
   - Database: `socialhub_db`
   - User: `socialhub`
   - Region: Choose closest to your backend
4. After creation, go to "Connections" tab
5. Copy the "Internal Database URL" or "External Database URL"
6. Update format for SQLAlchemy:
   ```
   DATABASE_URL=postgresql+psycopg://user:password@hostname:5432/database
   ```

---

### E. AWS RDS PostgreSQL

**Steps:**
1. Log in to AWS Console
2. Go to RDS → "Create database"
3. Choose:
   - Engine: PostgreSQL
   - Version: 15.x (or latest)
   - Template: Free tier (if eligible) or Production
   - DB instance identifier: `socialhub-db`
   - Master username: `socialhub`
   - Master password: (create a strong password)
   - DB instance class: `db.t3.micro` (free tier) or larger
   - Storage: 20 GB (minimum)
   - VPC: Default VPC (or create new)
   - Public access: Yes (if backend is outside AWS)
   - Security group: Create new or use existing (allow port 5432)
4. Click "Create database"
5. Wait for creation (5-10 minutes)
6. Go to database → "Connectivity & security" tab
7. Copy the "Endpoint" (e.g., `socialhub-db.xxxxx.us-east-1.rds.amazonaws.com`)
8. Connection string format:
   ```
   DATABASE_URL=postgresql+psycopg://socialhub:password@socialhub-db.xxxxx.us-east-1.rds.amazonaws.com:5432/socialhub_db
   ```

**Important:** Update security group to allow inbound connections on port 5432 from your backend server's IP.

---

### F. Google Cloud SQL

**Steps:**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Enable Cloud SQL API
3. Go to SQL → "Create instance"
4. Choose PostgreSQL
5. Configure:
   - Instance ID: `socialhub-db`
   - Root password: (set a strong password)
   - Region: Choose closest to your backend
   - Database version: PostgreSQL 15
   - Machine type: Shared core (for small apps) or Dedicated
6. Click "Create"
7. After creation:
   - Go to "Databases" tab → Create database: `socialhub_db`
   - Go to "Users" tab → Create user: `socialhub` with password
   - Go to "Connections" tab → Add network (your backend server IP) or enable public IP
8. Connection string format:
   ```
   DATABASE_URL=postgresql+psycopg://socialhub:password@[PUBLIC_IP]:5432/socialhub_db
   ```
   Or use Cloud SQL Proxy for better security.

---

## Option 2: Self-Hosted PostgreSQL (Docker)

If you prefer to host PostgreSQL yourself on a VPS:

### Using Docker Compose

Create a `docker-compose.db.yml` file:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: socialhub-postgres
    environment:
      POSTGRES_USER: socialhub
      POSTGRES_PASSWORD: your_secure_password
      POSTGRES_DB: socialhub_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - socialhub-network

volumes:
  postgres_data:

networks:
  socialhub-network:
    driver: bridge
```

**Deploy:**
```bash
# On your VPS
docker-compose -f docker-compose.db.yml up -d
```

**Connection string:**
```
DATABASE_URL=postgresql+psycopg://socialhub:your_secure_password@your-server-ip:5432/socialhub_db
```

---

## Step-by-Step Deployment Process

### Step 1: Deploy PostgreSQL Database

Choose one of the options above and create your database instance. Make sure to:
- ✅ Note down the connection string
- ✅ Save the database password securely
- ✅ Ensure the database is accessible from your backend server

### Step 2: Create Database Schema

Once your database is deployed, you need to create the tables. You have two options:

#### Option A: Using Python Script (Recommended)

Create a migration script `backend/migrate_database.py`:

```python
from database import create_tables, engine
import sys

def migrate():
    try:
        print("Creating database tables...")
        create_tables()
        print("✅ Database tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate()
```

Run it:
```bash
cd backend
python migrate_database.py
```

#### Option B: Using Alembic (For Future Migrations)

If you want to use Alembic for migrations:

```bash
cd backend
alembic init alembic
# Configure alembic.ini with your DATABASE_URL
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### Step 3: Update Backend Environment Variables

Update your backend's environment variables (`.env` file or deployment platform):

```env
# Database Connection
DATABASE_URL=postgresql+psycopg://user:password@host:port/database

# Other existing variables
SECRET_KEY=your-secret-key
ROCKET_CHAT_URL=your-rocket-chat-url
ROCKET_CHAT_ADMIN_USERNAME=admin
ROCKET_CHAT_ADMIN_PASSWORD=password
GOOGLE_CLIENT_ID=your-google-client-id
```

**Important:** 
- Replace `postgresql://` with `postgresql+psycopg://` for SQLAlchemy
- Make sure the password is URL-encoded if it contains special characters
- For production, use environment variables, never hardcode credentials

### Step 4: Test Database Connection

Test the connection from your backend:

```bash
cd backend
python -c "from database import engine; engine.connect(); print('✅ Database connected!')"
```

### Step 5: Verify Tables Created

Connect to your database and verify:

```bash
# Using psql (if you have PostgreSQL client)
psql "postgresql://user:password@host:port/database" -c "\dt"

# Or using Python
python -c "from database import engine; from sqlalchemy import inspect; inspector = inspect(engine); print(inspector.get_table_names())"
```

You should see these tables:
- users
- chat_messages
- groups
- group_members
- pinned_messages

### Step 6: Deploy Backend

Now deploy your backend to your hosting platform (Heroku, Railway, Render, AWS, etc.) with the `DATABASE_URL` environment variable set.

### Step 7: Deploy Frontend

Deploy your frontend and update the API URL to point to your deployed backend.

---

## Security Best Practices

1. **Use Strong Passwords**: Generate a strong, random password for your database
2. **Enable SSL/TLS**: Most managed services enable SSL by default. Update connection string:
   ```
   DATABASE_URL=postgresql+psycopg://user:password@host:port/database?sslmode=require
   ```
3. **Restrict Access**: Only allow connections from your backend server IP
4. **Use Connection Pooling**: Already configured in `database.py`
5. **Never Commit Credentials**: Keep `.env` files out of git
6. **Use Secrets Management**: Use your platform's secrets management (AWS Secrets Manager, etc.)

---

## Troubleshooting

### Connection Refused
- Check if database is running
- Verify firewall/security group allows port 5432
- Check if database allows public connections (if needed)

### Authentication Failed
- Verify username and password
- Check if user has proper permissions
- Ensure database name is correct

### SSL Required
- Add `?sslmode=require` to connection string
- Or use `?sslmode=prefer` for optional SSL

### Connection Timeout
- Check network connectivity
- Verify security group/firewall rules
- Check if database endpoint is correct

---

## Migration from Local Database

If you have data in your local database that you want to migrate:

### Export Local Data
```bash
pg_dump -U socialhub -d socialhub_db > local_backup.sql
```

### Import to Production
```bash
psql "postgresql://user:password@host:port/database" < local_backup.sql
```

---

## Recommended Services by Use Case

- **Quick Start / Prototyping**: Railway, Supabase, Neon
- **Production / Enterprise**: AWS RDS, Google Cloud SQL
- **Budget-Conscious**: Supabase (free tier), Railway (pay-as-you-go)
- **Serverless**: Neon, Supabase
- **Full Control**: Self-hosted on VPS

---

## Next Steps

After deploying the database:
1. ✅ Database deployed and accessible
2. ✅ Tables created
3. ✅ Backend connected to database
4. ⏭️ Deploy backend (see backend deployment guide)
5. ⏭️ Deploy frontend (see frontend deployment guide)

---

## Quick Reference

**Connection String Format:**
```
postgresql+psycopg://[username]:[password]@[host]:[port]/[database]
```

**Required Tables:**
- users
- chat_messages
- groups
- group_members
- pinned_messages

**Environment Variable:**
```
DATABASE_URL=postgresql+psycopg://...
```

