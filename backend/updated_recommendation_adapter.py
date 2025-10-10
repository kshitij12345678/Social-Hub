"""
Updated Database Adapter for Social Hub Recommendation System
Handles schema differences between old recommendation system and current backend
"""

from typing import List, Tuple, Dict, Any
import sqlite3
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db, User, Post, Like, Comment, Share, Follow, Location, UserInterest

class UpdatedRecommendationDatabaseAdapter:
    """Database adapter that bridges the schema gap between old recommendation system and current backend"""
    
    def __init__(self):
        self.db_path = "social_hub.db"  # Use current backend database
    
    def get_db_session(self):
        """Get SQLAlchemy database session"""
        return next(get_db())
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """Execute raw SQL query with automatic schema translation"""
        
        # Translate the query to work with current schema
        translated_query = self._translate_query(query)
        
        try:
            # Use SQLAlchemy for raw SQL execution
            db = self.get_db_session()
            result = db.execute(text(translated_query), params)
            rows = result.fetchall()
            db.close()
            
            # Convert rows to list of tuples
            return [tuple(row) for row in rows]
        except Exception as e:
            print(f"❌ Database query error: {e}")
            print(f"Original query: {query}")
            print(f"Translated query: {translated_query}")
            print(f"Params: {params}")
            return []
    
    def _translate_query(self, query: str) -> str:
        """Translate old schema queries to new schema"""
        
        # Create a modifiable copy
        translated = query
        
        # ===== PRIMARY KEY TRANSLATIONS =====
        # Posts table: post_id -> id
        translated = translated.replace("p.post_id", "p.id")
        translated = translated.replace("posts.post_id", "posts.id")
        
        # Users table: user_id -> id (only for primary key references)
        translated = translated.replace("u.user_id", "u.id")
        translated = translated.replace("users.user_id", "users.id")
        
        # Locations table: location_id -> id
        translated = translated.replace("l.location_id", "l.id")
        translated = translated.replace("locations.location_id", "locations.id")
        
        # ===== COLUMN TRANSLATIONS =====
        # Users table: username -> full_name
        translated = translated.replace("u.username", "u.full_name")
        translated = translated.replace("users.username", "users.full_name")
        
        # Posts table: post_type is now media_type
        translated = translated.replace("p.post_type", "p.media_type")
        
        # ===== HANDLE INTERACTIONS TABLE =====
        # The biggest difference - we don't have a unified interactions table
        if "FROM interactions" in translated:
            if "COUNT(*)" in translated and "WHERE user_id" in translated:
                # Count user interactions
                translated = """
                SELECT COUNT(*) FROM (
                    SELECT user_id FROM likes WHERE user_id = ?
                    UNION ALL
                    SELECT user_id FROM comments WHERE user_id = ?
                    UNION ALL  
                    SELECT user_id FROM shares WHERE user_id = ?
                )
                """
            elif "SELECT DISTINCT post_id FROM interactions WHERE user_id" in translated:
                # Get posts user interacted with
                translated = """
                SELECT DISTINCT post_id FROM (
                    SELECT post_id FROM likes WHERE user_id = ?
                    UNION
                    SELECT post_id FROM comments WHERE user_id = ?
                    UNION  
                    SELECT post_id FROM shares WHERE user_id = ?
                )
                """
        
        # Handle interactions table joins
        if "interactions" in translated and "JOIN" in translated:
            # Replace interactions table with UNION of likes, comments, shares
            if "interaction_type" in translated:
                # Complex join with interaction types
                interaction_union = """
                (
                    SELECT user_id, post_id, 'like' as interaction_type, created_at FROM likes
                    UNION ALL
                    SELECT user_id, post_id, 'comment' as interaction_type, created_at FROM comments
                    UNION ALL
                    SELECT user_id, post_id, 'share' as interaction_type, created_at FROM shares
                ) interactions"""
                
                translated = translated.replace("interactions i", interaction_union + " i")
                translated = translated.replace("interactions interactions", interaction_union)
        
        # ===== HANDLE POST_TAGS TABLE =====
        # We don't have post_tags table, so replace with empty values
        if "post_tags" in translated:
            # Remove post_tags joins and replace tag columns with empty strings
            lines = translated.split('\n')
            filtered_lines = []
            
            for line in lines:
                if 'post_tags pt' in line or 'LEFT JOIN post_tags pt' in line:
                    continue  # Skip post_tags joins
                
                # Replace tag references with empty strings
                line = line.replace("pt.tag_name", "''")
                line = line.replace("GROUP_CONCAT(pt.tag_name, ', ') as tags", "'' as tags")
                line = line.replace("GROUP_CONCAT(pt.tag_name, ' ') as tags", "'' as tags")
                
                # Clean up GROUP BY clauses
                if 'GROUP BY' in line:
                    line = line.replace(', pt.tag_name', '').replace('pt.tag_name, ', '')
                
                filtered_lines.append(line)
            
            translated = '\n'.join(filtered_lines)
        
        # ===== HANDLE AGGREGATE QUERIES =====
        # Fix popular posts query with proper interaction counting
        if "COUNT(i.interaction_id) as interaction_count" in translated:
            translated = translated.replace(
                "COUNT(i.interaction_id) as interaction_count",
                "(p.likes_count + p.comments_count + p.shares_count) as interaction_count"
            )
            
            # Remove the interactions join since we're using counts from posts table
            translated = translated.replace("LEFT JOIN interactions i ON p.id = i.post_id", "")
        
        # ===== FINAL CLEANUP =====
        # Remove extra whitespace and empty lines
        lines = [line.strip() for line in translated.split('\n') if line.strip()]
        translated = '\n'.join(lines)
        
        return translated
    
    def get_user_interaction_count(self, user_id: int) -> int:
        """Get total interaction count for a user"""
        query = """
        SELECT COUNT(*) FROM (
            SELECT user_id FROM likes WHERE user_id = ?
            UNION ALL
            SELECT user_id FROM comments WHERE user_id = ?
            UNION ALL  
            SELECT user_id FROM shares WHERE user_id = ?
        )
        """
        result = self.execute_query(query, (user_id, user_id, user_id))
        return result[0][0] if result else 0
    
    def get_user_interacted_posts(self, user_id: int) -> List[int]:
        """Get list of post IDs user has interacted with"""
        query = """
        SELECT DISTINCT post_id FROM (
            SELECT post_id FROM likes WHERE user_id = ?
            UNION
            SELECT post_id FROM comments WHERE user_id = ?
            UNION  
            SELECT post_id FROM shares WHERE user_id = ?
        )
        """
        result = self.execute_query(query, (user_id, user_id, user_id))
        return [row[0] for row in result]
    
    def get_popular_posts(self, limit: int = 10, exclude_user_id: int = None) -> List[Dict]:
        """Get popular posts based on engagement metrics"""
        exclude_clause = ""
        params = []
        
        if exclude_user_id:
            # Exclude posts user has already interacted with
            exclude_clause = """
            AND p.id NOT IN (
                SELECT DISTINCT post_id FROM (
                    SELECT post_id FROM likes WHERE user_id = ?
                    UNION
                    SELECT post_id FROM comments WHERE user_id = ?
                    UNION  
                    SELECT post_id FROM shares WHERE user_id = ?
                )
            )
            """
            params = [exclude_user_id, exclude_user_id, exclude_user_id]
        
        query = f"""
        SELECT p.id, p.caption, p.user_id, u.full_name, l.name as location,
               (p.likes_count + p.comments_count + p.shares_count) as interaction_count
        FROM posts p
        JOIN users u ON p.user_id = u.id
        LEFT JOIN locations l ON p.location_id = l.id
        WHERE 1=1 {exclude_clause}
        ORDER BY interaction_count DESC, p.created_at DESC
        LIMIT ?
        """
        params.append(limit)
        
        result = self.execute_query(query, tuple(params))
        
        posts = []
        for row in result:
            post_id, caption, user_id, author_name, location, interaction_count = row
            posts.append({
                'post_id': post_id,
                'caption': caption[:100] + "..." if caption and len(caption) > 100 else caption,
                'user_id': user_id,
                'author_username': author_name,
                'location': location,
                'popularity_score': interaction_count,
                'recommendation_reason': f'Popular post with {interaction_count} interactions',
                'algorithm': 'popularity_based'
            })
        
        return posts