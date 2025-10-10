import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional

class DatabaseManager:
    def __init__(self, db_path: str = "data/travel_social.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize all database tables"""
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table - travel enthusiasts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT,
                bio TEXT,
                profile_picture TEXT,
                location TEXT,
                travel_style TEXT, -- adventure, luxury, budget, family, solo
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Locations table - travel destinations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS locations (
                location_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                country TEXT NOT NULL,
                continent TEXT,
                latitude REAL,
                longitude REAL,
                category TEXT -- beach, mountain, city, historical, etc.
            )
        ''')
        
        # Posts table - travel content
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                post_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                caption TEXT,
                image_url TEXT,
                video_url TEXT,
                location_id INTEGER,
                travel_date DATE,
                post_type TEXT CHECK(post_type IN ('photo', 'video', 'story')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (location_id) REFERENCES locations (location_id)
            )
        ''')
        
        # Post tags - travel themes/categories
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS post_tags (
                tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                tag_name TEXT NOT NULL,
                FOREIGN KEY (post_id) REFERENCES posts (post_id),
                UNIQUE(post_id, tag_name)
            )
        ''')
        
        # Interactions table - user engagement
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                post_id INTEGER NOT NULL,
                interaction_type TEXT CHECK(interaction_type IN ('like', 'comment', 'share', 'save')) NOT NULL,
                comment_text TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (post_id) REFERENCES posts (post_id)
            )
        ''')
        
        # Follows table - user connections
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS follows (
                follow_id INTEGER PRIMARY KEY AUTOINCREMENT,
                follower_id INTEGER NOT NULL,
                following_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (follower_id) REFERENCES users (user_id),
                FOREIGN KEY (following_id) REFERENCES users (user_id),
                UNIQUE(follower_id, following_id)
            )
        ''')
        
        # User interests - travel preferences
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_interests (
                interest_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                interest_type TEXT NOT NULL, -- destination, activity, style
                interest_value TEXT NOT NULL,
                weight REAL DEFAULT 1.0, -- importance score
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                UNIQUE(user_id, interest_type, interest_value)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully!")
    
    def execute_query(self, query: str, params: tuple = None):
        """Execute a query and return results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def execute_insert(self, query: str, params: tuple = None):
        """Execute insert query and return last row id"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        last_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return last_id

if __name__ == "__main__":
    db = DatabaseManager()
    print("Database setup complete!")