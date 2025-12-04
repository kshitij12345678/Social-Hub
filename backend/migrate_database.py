#!/usr/bin/env python3
"""
Database Migration Script
Creates all required tables in the PostgreSQL database.

Usage:
    python migrate_database.py

Make sure DATABASE_URL is set in your environment or .env file.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import database module
sys.path.insert(0, str(Path(__file__).parent))

from database import create_tables, engine, Base
from sqlalchemy import inspect, text

def check_connection():
    """Test database connection."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        print("✅ Database connection successful!")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\nPlease check:")
        print("1. DATABASE_URL environment variable is set correctly")
        print("2. Database server is running and accessible")
        print("3. Network/firewall allows connections")
        print("4. Credentials are correct")
        return False

def list_existing_tables():
    """List existing tables in the database."""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        if tables:
            print(f"\n📋 Existing tables in database: {', '.join(tables)}")
        else:
            print("\n📋 No existing tables found in database")
        return tables
    except Exception as e:
        print(f"⚠️  Could not list tables: {e}")
        return []

def migrate():
    """Create all database tables."""
    print("=" * 60)
    print("Database Migration Script")
    print("=" * 60)
    
    # Check DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set!")
        print("\nPlease set it in your .env file or environment:")
        print("  DATABASE_URL=postgresql+psycopg://user:password@host:port/database")
        sys.exit(1)
    
    # Mask password in URL for display
    display_url = database_url
    if "@" in database_url:
        parts = database_url.split("@")
        if ":" in parts[0]:
            user_pass = parts[0].split("://")[1] if "://" in parts[0] else parts[0]
            if ":" in user_pass:
                user = user_pass.split(":")[0]
                display_url = database_url.replace(f":{user_pass.split(':')[1]}", ":****")
    
    print(f"\n📊 Database URL: {display_url}")
    
    # Test connection
    if not check_connection():
        sys.exit(1)
    
    # List existing tables
    existing_tables = list_existing_tables()
    
    # Expected tables
    expected_tables = ["users", "chat_messages", "groups", "group_members", "pinned_messages"]
    
    # Check if tables already exist
    if existing_tables:
        missing_tables = [t for t in expected_tables if t not in existing_tables]
        if not missing_tables:
            print(f"\n✅ All required tables already exist!")
            print("\nTables found:")
            for table in expected_tables:
                print(f"  - {table}")
            
            response = input("\nDo you want to recreate tables? This will DELETE all data! (yes/no): ")
            if response.lower() != "yes":
                print("\n✅ Migration cancelled. Tables remain unchanged.")
                return True
            else:
                print("\n⚠️  Dropping existing tables...")
                try:
                    Base.metadata.drop_all(bind=engine)
                    print("✅ Existing tables dropped")
                except Exception as e:
                    print(f"❌ Error dropping tables: {e}")
                    sys.exit(1)
    
    # Create tables
    print("\n🔨 Creating database tables...")
    try:
        create_tables()
        print("✅ Database tables created successfully!")
        
        # Verify tables were created
        inspector = inspect(engine)
        created_tables = inspector.get_table_names()
        
        print("\n📋 Created tables:")
        for table in expected_tables:
            if table in created_tables:
                print(f"  ✅ {table}")
            else:
                print(f"  ❌ {table} (missing!)")
        
        # Verify all tables exist
        missing = [t for t in expected_tables if t not in created_tables]
        if missing:
            print(f"\n⚠️  Warning: Some tables are missing: {', '.join(missing)}")
            return False
        
        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Error creating tables: {e}")
        print("\nCommon issues:")
        print("1. Database user doesn't have CREATE TABLE permissions")
        print("2. Database doesn't exist (create it first)")
        print("3. Connection string format is incorrect")
        print("4. Network/firewall blocking connection")
        sys.exit(1)

if __name__ == "__main__":
    success = migrate()
    sys.exit(0 if success else 1)

