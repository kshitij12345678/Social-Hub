"""
Database adapter for recommendation system integration
Bridges the existing Social Hub database with the recommendation system
"""

import sqlite3
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from database import SessionLocal, User, Post, Like, Comment, Share, Location
from datetime import datetime

class RecommendationDatabaseAdapter:
    """
    Adapter class that provides the recommendation system's expected interface
    while using our existing Social Hub database
    """
    
    def __init__(self, db_path: str = "social_hub.db"):
        self.db_path = db_path
    
    def get_connection(self):
        """Get SQLite connection for direct SQL queries (needed by recommendation system)"""
        return sqlite3.connect(self.db_path)
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """Execute SQL query and return results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.commit()
            return results
        finally:
            conn.close()
    
    def get_sqlalchemy_session(self) -> Session:
        """Get SQLAlchemy session for ORM operations"""
        return SessionLocal()
    
    # ==================== USER OPERATIONS ====================
    
    def get_user_interactions(self, user_id: int) -> List[Dict]:
        """Get user's interaction history (likes, comments, shares)"""
        query = """
        SELECT 
            'like' as interaction_type,
            post_id,
            created_at,
            1.0 as weight
        FROM likes 
        WHERE user_id = ?
        
        UNION ALL
        
        SELECT 
            'comment' as interaction_type,
            post_id,
            created_at,
            1.2 as weight
        FROM comments 
        WHERE user_id = ?
        
        UNION ALL
        
        SELECT 
            'share' as interaction_type,
            post_id,
            created_at,
            1.5 as weight
        FROM shares 
        WHERE user_id = ?
        
        ORDER BY created_at DESC
        """
        
        results = self.execute_query(query, (user_id, user_id, user_id))
        
        interactions = []
        for row in results:
            interactions.append({
                "interaction_type": row[0],
                "post_id": row[1],
                "created_at": row[2],
                "weight": row[3]
            })
        
        return interactions
    
    # ==================== COMPATIBILITY METHODS ====================
    # These methods provide compatibility with the original recommendation system
    
    def execute_query_compat(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """
        Execute query with automatic column name translation for compatibility
        """
        # Replace user_id references in users table with id
        if "FROM users" in query and "user_id" in query:
            query = query.replace("WHERE user_id", "WHERE id")
            query = query.replace("users.user_id", "users.id")
        
        # Replace interactions table with our actual tables
        if "FROM interactions" in query:
            # Map interactions table to our likes table for simplicity
            query = query.replace("FROM interactions", "FROM likes")
        
        return self.execute_query(query, params)
    
    def get_user_profile(self, user_id: int) -> Optional[Dict]:
        """Get user profile information"""
        query = """
        SELECT id, full_name, email, bio, location, created_at
        FROM users 
        WHERE id = ?
        """
        
        results = self.execute_query(query, (user_id,))
        
        if not results:
            return None
        
        row = results[0]
        return {
            "user_id": row[0],
            "full_name": row[1],
            "email": row[2],
            "bio": row[3],
            "location": row[4],
            "created_at": row[5]
        }
    
    # ==================== POST OPERATIONS ====================
    
    def get_post_details(self, post_id: int) -> Optional[Dict]:
        """Get detailed post information"""
        query = """
        SELECT 
            p.id,
            p.user_id,
            p.caption,
            p.media_url,
            p.media_type,
            p.location_id,
            p.travel_date,
            p.likes_count,
            p.comments_count,
            p.shares_count,
            p.created_at,
            u.full_name,
            l.name as location_name,
            l.country as location_country
        FROM posts p
        LEFT JOIN users u ON p.user_id = u.id
        LEFT JOIN locations l ON p.location_id = l.id
        WHERE p.id = ?
        """
        
        results = self.execute_query(query, (post_id,))
        
        if not results:
            return None
        
        row = results[0]
        return {
            "post_id": row[0],
            "user_id": row[1],
            "caption": row[2],
            "media_url": row[3],
            "media_type": row[4],
            "location_id": row[5],
            "travel_date": row[6],
            "likes_count": row[7],
            "comments_count": row[8],
            "shares_count": row[9],
            "created_at": row[10],
            "author_name": row[11],
            "location_name": row[12],
            "location_country": row[13]
        }
    
    def get_all_posts(self, limit: int = 1000) -> List[Dict]:
        """Get all posts for recommendation training"""
        query = """
        SELECT 
            p.id,
            p.user_id,
            p.caption,
            p.media_url,
            p.media_type,
            p.location_id,
            p.travel_date,
            p.likes_count,
            p.comments_count,
            p.shares_count,
            p.created_at,
            l.name as location_name,
            l.country as location_country,
            l.category as location_category
        FROM posts p
        LEFT JOIN locations l ON p.location_id = l.id
        ORDER BY p.created_at DESC
        LIMIT ?
        """
        
        results = self.execute_query(query, (limit,))
        
        posts = []
        for row in results:
            posts.append({
                "post_id": row[0],
                "user_id": row[1],
                "caption": row[2] or "",
                "media_url": row[3],
                "media_type": row[4],
                "location_id": row[5],
                "travel_date": row[6],
                "likes_count": row[7],
                "comments_count": row[8],
                "shares_count": row[9],
                "created_at": row[10],
                "location_name": row[11] or "",
                "location_country": row[12] or "",
                "location_category": row[13] or ""
            })
        
        return posts
    
    def get_posts_by_user(self, user_id: int) -> List[Dict]:
        """Get all posts by a specific user"""
        query = """
        SELECT 
            p.id,
            p.user_id,
            p.caption,
            p.location_id,
            p.travel_date,
            p.likes_count,
            p.comments_count,
            p.shares_count,
            p.created_at,
            l.name as location_name,
            l.country as location_country,
            l.category as location_category
        FROM posts p
        LEFT JOIN locations l ON p.location_id = l.id
        WHERE p.user_id = ?
        ORDER BY p.created_at DESC
        """
        
        results = self.execute_query(query, (user_id,))
        
        posts = []
        for row in results:
            posts.append({
                "post_id": row[0],
                "user_id": row[1],
                "caption": row[2] or "",
                "location_id": row[3],
                "travel_date": row[4],
                "likes_count": row[5],
                "comments_count": row[6],
                "shares_count": row[7],
                "created_at": row[8],
                "location_name": row[9] or "",
                "location_country": row[10] or "",
                "location_category": row[11] or ""
            })
        
        return posts
    
    # ==================== INTERACTION OPERATIONS ====================
    
    def get_user_similarity_data(self) -> List[Tuple]:
        """Get user interaction data for collaborative filtering"""
        query = """
        SELECT user_id, post_id, 
               CASE 
                   WHEN interaction_type = 'like' THEN 1.0
                   WHEN interaction_type = 'comment' THEN 1.2
                   WHEN interaction_type = 'share' THEN 1.5
                   ELSE 1.0
               END as rating
        FROM (
            SELECT user_id, post_id, 'like' as interaction_type FROM likes
            UNION ALL
            SELECT user_id, post_id, 'comment' as interaction_type FROM comments
            UNION ALL
            SELECT user_id, post_id, 'share' as interaction_type FROM shares
        ) interactions
        """
        
        return self.execute_query(query)
    
    def get_post_popularity_scores(self) -> List[Tuple]:
        """Get post popularity scores for content-based filtering"""
        query = """
        SELECT 
            id as post_id,
            (likes_count * 1.0 + comments_count * 1.2 + shares_count * 1.5) as popularity_score,
            likes_count,
            comments_count,
            shares_count,
            created_at
        FROM posts
        WHERE (likes_count + comments_count + shares_count) > 0
        ORDER BY popularity_score DESC
        """
        
        return self.execute_query(query)
    
    # ==================== LOCATION OPERATIONS ====================
    
    def get_locations(self) -> List[Dict]:
        """Get all travel locations"""
        query = """
        SELECT id, name, country, continent, category, latitude, longitude
        FROM locations
        ORDER BY name
        """
        
        results = self.execute_query(query)
        
        locations = []
        for row in results:
            locations.append({
                "location_id": row[0],
                "name": row[1],
                "country": row[2],
                "continent": row[3],
                "category": row[4],
                "latitude": row[5],
                "longitude": row[6]
            })
        
        return locations