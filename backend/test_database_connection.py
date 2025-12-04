#!/usr/bin/env python3
"""
Quick Database Connection Test Script

Tests if the database connection is working correctly.

Usage:
    python test_database_connection.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from database import engine, DATABASE_URL
from sqlalchemy import inspect, text

def test_connection():
    """Test database connection."""
    print("=" * 60)
    print("Database Connection Test")
    print("=" * 60)
    
    # Display masked URL
    display_url = DATABASE_URL
    if "@" in DATABASE_URL:
        parts = DATABASE_URL.split("@")
        if "://" in parts[0]:
            user_pass = parts[0].split("://")[1]
            if ":" in user_pass:
                display_url = DATABASE_URL.replace(f":{user_pass.split(':')[1]}", ":****")
    
    print(f"\n📊 Database URL: {display_url}")
    
    # Test connection
    print("\n🔌 Testing connection...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print("✅ Connection successful!")
            print(f"\n📋 PostgreSQL Version: {version.split(',')[0]}")
            return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_tables():
    """Check if tables exist."""
    print("\n📋 Checking tables...")
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = ["users", "chat_messages", "groups", "group_members", "pinned_messages"]
        
        if not tables:
            print("⚠️  No tables found in database")
            print("   Run: python migrate_database.py")
            return False
        
        print(f"\nFound {len(tables)} table(s):")
        for table in tables:
            status = "✅" if table in expected_tables else "⚠️"
            print(f"  {status} {table}")
        
        missing = [t for t in expected_tables if t not in tables]
        if missing:
            print(f"\n⚠️  Missing tables: {', '.join(missing)}")
            print("   Run: python migrate_database.py")
            return False
        
        print("\n✅ All required tables exist!")
        return True
        
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return False

def test_query():
    """Test a simple query."""
    print("\n🔍 Testing query...")
    try:
        from database import SessionLocal, User
        
        db = SessionLocal()
        try:
            count = db.query(User).count()
            print(f"✅ Query successful! Found {count} user(s) in database")
            return True
        finally:
            db.close()
    except Exception as e:
        print(f"⚠️  Query test failed: {e}")
        print("   This is normal if tables don't exist yet")
        return False

if __name__ == "__main__":
    if not os.getenv("DATABASE_URL"):
        print("❌ ERROR: DATABASE_URL environment variable not set!")
        print("\nPlease set it in your .env file or environment:")
        print("  DATABASE_URL=postgresql+psycopg://user:password@host:port/database")
        sys.exit(1)
    
    connection_ok = test_connection()
    if not connection_ok:
        sys.exit(1)
    
    tables_ok = test_tables()
    query_ok = test_query()
    
    print("\n" + "=" * 60)
    if connection_ok and tables_ok:
        print("✅ Database is ready to use!")
    elif connection_ok:
        print("⚠️  Database connected but tables need to be created")
        print("   Run: python migrate_database.py")
    else:
        print("❌ Database connection failed")
    print("=" * 60)

