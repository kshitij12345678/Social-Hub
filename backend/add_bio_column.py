#!/usr/bin/env python3
"""
Add bio column to existing users table
"""
import sqlite3
import os

def add_bio_column():
    # Database file path
    db_path = "social_hub.db"
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} does not exist!")
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if bio column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'bio' in columns:
            print("Bio column already exists!")
            return
        
        # Add bio column
        cursor.execute("ALTER TABLE users ADD COLUMN bio TEXT;")
        conn.commit()
        
        print("✅ Successfully added bio column to users table!")
        
        # Show updated table structure
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        print("\n📋 Updated table structure:")
        for col in columns:
            print(f"  • {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    add_bio_column()
