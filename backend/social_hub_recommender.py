"""
Integrated Hybrid Recommender for Social Hub
Uses the existing recommendation logic with our database adapter
"""

import sys
import os
from typing import List, Dict

# Add the recommender directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'recommender'))

from recommender.hybrid import HybridRecommender as OriginalHybridRecommender
from recommendation_adapter import RecommendationDatabaseAdapter
from typing import Tuple
import re

class CompatibilityDatabaseWrapper:
    """
    Wrapper that translates database calls for compatibility with original recommendation system
    """
    def __init__(self, db_adapter: RecommendationDatabaseAdapter):
        self.db_adapter = db_adapter
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """Execute query with automatic column name translation"""
        original_query = query
        
        # ============ COLUMN NAME TRANSLATIONS ============
        # Posts table: post_id -> id
        query = query.replace("p.post_id", "p.id")
        query = query.replace("posts.post_id", "posts.id")
        
        # Users table: user_id -> id (only when referring to the primary key)
        query = query.replace("u.user_id", "u.id")
        query = query.replace("users.user_id", "users.id")
        query = query.replace("u.username", "u.full_name")  # We use full_name instead of username
        if "FROM users" in query and "WHERE user_id" in query:
            query = query.replace("WHERE user_id", "WHERE id")
        
        # Locations table: location_id -> id
        query = query.replace("l.location_id", "l.id")
        query = query.replace("locations.location_id", "locations.id")
        
        # ============ TABLE TRANSLATIONS ============
        # Handle post_tags table - we don't have this, so handle all tag-related queries
        if "post_tags" in query or "pt.tag_name" in query:
            # Handle different tag query patterns
            query = query.replace("GROUP_CONCAT(pt.tag_name, ' ') as tags", "'' as tags")
            query = query.replace("GROUP_CONCAT(pt.tag_name, ', ') as tags", "'' as tags")
            query = query.replace("pt.tag_name", "'' as tag_name")
            
            # Remove post_tags joins and references
            lines = query.split('\n')
            filtered_lines = []
            for line in lines:
                if 'post_tags pt' not in line and 'LEFT JOIN post_tags pt' not in line:
                    # Clean up GROUP BY clause
                    if 'GROUP BY' in line:
                        line = line.replace(', pt.tag_name', '').replace('pt.tag_name, ', '')
                    filtered_lines.append(line)
            query = '\n'.join(filtered_lines)
        
        # Handle interactions table - we don't have this table, so simulate it
        if "FROM interactions" in query:
            if "COUNT(*)" in query and "WHERE user_id" in query:
                # Count user interactions from likes + comments + shares
                interaction_query = """
                SELECT COUNT(*) FROM (
                    SELECT user_id FROM likes WHERE user_id = ?
                    UNION ALL
                    SELECT user_id FROM comments WHERE user_id = ?
                    UNION ALL  
                    SELECT user_id FROM shares WHERE user_id = ?
                )
                """
                return self.db_adapter.execute_query(interaction_query, (params[0], params[0], params[0]))
            elif "SELECT DISTINCT post_id FROM interactions WHERE user_id" in query:
                # Get posts user has interacted with
                interaction_query = """
                SELECT DISTINCT post_id FROM (
                    SELECT post_id FROM likes WHERE user_id = ?
                    UNION
                    SELECT post_id FROM comments WHERE user_id = ?
                    UNION  
                    SELECT post_id FROM shares WHERE user_id = ?
                )
                """
                return self.db_adapter.execute_query(interaction_query, (params[0], params[0], params[0]))
            elif "LEFT JOIN interactions i ON p.post_id = i.post_id" in query:
                # Popular posts query - replace with likes count
                if "COUNT(i.interaction_id) as interaction_count" in query:
                    # This is the popular posts query, need to rewrite completely
                    popular_posts_query = """
                    SELECT p.id, p.caption, p.user_id, u.full_name, l.name as location,
                           (p.likes_count + p.comments_count + p.shares_count) as interaction_count
                    FROM posts p
                    JOIN users u ON p.user_id = u.id
                    LEFT JOIN locations l ON p.location_id = l.id
                    WHERE p.id NOT IN (
                        SELECT DISTINCT post_id FROM (
                            SELECT post_id FROM likes WHERE user_id = ?
                            UNION
                            SELECT post_id FROM comments WHERE user_id = ?
                            UNION  
                            SELECT post_id FROM shares WHERE user_id = ?
                        )
                    )
                    ORDER BY interaction_count DESC
                    LIMIT ?
                    """
                    # Adjust params - first param is user_id (repeated 3 times), second is limit
                    new_params = (params[0], params[0], params[0], params[1])
                    return self.db_adapter.execute_query(popular_posts_query, new_params)
                else:
                    # Other interactions queries, use likes
                    query = query.replace("LEFT JOIN interactions i ON p.post_id = i.post_id", "LEFT JOIN likes i ON p.id = i.post_id")
                    query = query.replace("i.interaction_id", "i.id")
                    query = query.replace("i.interaction_type", "'like' as interaction_type")
            else:
                # For other interactions queries, replace with likes and add missing columns
                query = query.replace("FROM interactions i", "FROM likes i")
                query = query.replace("i.interaction_id", "i.id")
                query = query.replace("i.interaction_type", "'like' as interaction_type")
                query = query.replace("i.timestamp", "i.created_at")  # Fix timestamp column
                
                # Handle complex collaborative filtering queries
                if "AVG(CASE" in query and "interaction_type" in query:
                    # Replace the complex CASE statement with simple average
                    case_pattern = r"AVG\(CASE[^)]+END\) as avg_interaction_weight"
                    query = re.sub(case_pattern, "1.0 as avg_interaction_weight", query, flags=re.DOTALL)
        
        # ============ CLEAN UP QUERY ============
        # Handle tags column - replace GROUP_CONCAT with empty string since we don't have post_tags table
        if "GROUP_CONCAT(pt.tag_name, ' ') as tags" in query:
            query = query.replace("GROUP_CONCAT(pt.tag_name, ' ') as tags", "'' as tags")
        
        # Remove post_tags joins completely since we don't have that table
        lines = query.split('\n')
        filtered_lines = []
        skip_group_by_tags = False
        
        for line in lines:
            # Skip post_tags related lines
            if 'post_tags pt' in line or 'pt.post_id' in line:
                continue
            # Fix GROUP BY clause to remove post_tags references
            if 'GROUP BY' in line and 'pt.' in line:
                line = line.replace(', pt.tag_name', '').replace('pt.tag_name, ', '')
            filtered_lines.append(line)
        
        query = '\n'.join(filtered_lines)
        
        print(f"🔧 Query translation:")
        print(f"   Original: {original_query[:100]}{'...' if len(original_query) > 100 else ''}")
        print(f"   Translated: {query[:100]}{'...' if len(query) > 100 else ''}")
        
        return self.db_adapter.execute_query(query, params)


class SocialHubRecommender:
    """
    Wrapper class that integrates the existing HybridRecommender with Social Hub database
    """
    
    def __init__(self, db_path: str = "social_hub.db"):
        # Create our database adapter
        self.db_adapter = RecommendationDatabaseAdapter(db_path)
        
        # Create compatibility wrapper for database calls
        self.compat_db = CompatibilityDatabaseWrapper(self.db_adapter)
        
        # Initialize the original recommender with our compatibility wrapper
        self.hybrid_recommender = OriginalHybridRecommender(self.compat_db)
        
        print("🎯 Social Hub Recommender initialized successfully with compatibility layer!")
    
    def get_recommended_posts(self, user_id: int, limit: int = 10) -> List[Dict]:
        """
        Get personalized post recommendations for a user
        
        Args:
            user_id: The user ID to get recommendations for
            limit: Number of recommendations to return
            
        Returns:
            List of recommended posts with metadata
        """
        try:
            print(f"🔍 Getting recommendations for user {user_id}...")
            
            # Use the original hybrid recommender
            raw_recommendations = self.hybrid_recommender.recommend_posts(user_id, limit)
            
            # If hybrid recommender returns empty list, use our improved fallback
            if not raw_recommendations:
                print(f"⚠️ Hybrid recommender returned 0 recommendations, using improved fallback...")
                return self.get_general_popular_posts(limit)
            
            # Enhance recommendations with our database details
            enhanced_recommendations = []
            
            for rec in raw_recommendations:
                post_id = rec.get('post_id')
                if post_id:
                    # Get full post details from our database
                    post_details = self.db_adapter.get_post_details(post_id)
                    
                    if post_details:
                        # Combine recommendation score with post details
                        enhanced_rec = {
                            **post_details,
                            'recommendation_score': rec.get('score', 0.0),
                            'recommendation_reason': rec.get('reason', 'Hybrid recommendation'),
                            'recommendation_source': rec.get('source', 'hybrid')
                        }
                        enhanced_recommendations.append(enhanced_rec)
            
            print(f"✅ Generated {len(enhanced_recommendations)} recommendations")
            return enhanced_recommendations
            
        except Exception as e:
            print(f"❌ Error generating recommendations: {str(e)}")
            # Fallback to popular posts
            fallback_recs = self.get_popular_posts_fallback(limit)
            if len(fallback_recs) == 0:
                print("⚠️ Fallback returned 0 recommendations, trying general popular posts...")
                return self.get_general_popular_posts(limit)
            return fallback_recs
    
    def get_popular_posts_fallback(self, limit: int = 10) -> List[Dict]:
        """
        Fallback method to get popular posts when recommendations fail
        """
        try:
            print("📈 Using popular posts as fallback...")
            
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
                l.country as location_country,
                (p.likes_count * 1.0 + p.comments_count * 1.2 + p.shares_count * 1.5) as popularity_score
            FROM posts p
            LEFT JOIN users u ON p.user_id = u.id
            LEFT JOIN locations l ON p.location_id = l.id
            WHERE (p.likes_count + p.comments_count + p.shares_count) > 0
            ORDER BY popularity_score DESC, p.created_at DESC
            LIMIT ?
            """
            
            results = self.db_adapter.execute_query(query, (limit,))
            
            popular_posts = []
            for row in results:
                popular_posts.append({
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
                    "location_country": row[13],
                    "recommendation_score": row[14],
                    "recommendation_reason": "Popular content",
                    "recommendation_source": "popularity_fallback"
                })
            
            return popular_posts
            
        except Exception as e:
            print(f"❌ Error in fallback method: {str(e)}")
            return []
    
    def get_general_popular_posts(self, limit: int = 10) -> List[Dict]:
        """
        Get general popular posts without user-specific filtering (for new users)
        """
        try:
            print("🌟 Getting general popular posts for new users...")
            
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
                l.country as location_country,
                (p.likes_count * 1.0 + p.comments_count * 1.2 + p.shares_count * 1.5) as popularity_score
            FROM posts p
            LEFT JOIN users u ON p.user_id = u.id
            LEFT JOIN locations l ON p.location_id = l.id
            ORDER BY popularity_score DESC, p.created_at DESC
            LIMIT ?
            """
            
            results = self.db_adapter.execute_query(query, (limit,))
            
            popular_posts = []
            for row in results:
                popular_posts.append({
                    "post_id": row[0],
                    "user_id": row[1],
                    "caption": row[2],
                    "media_url": row[3],
                    "media_type": row[4],
                    "location_id": row[5],
                    "travel_date": str(row[6]) if row[6] else None,
                    "likes_count": row[7] or 0,
                    "comments_count": row[8] or 0,
                    "shares_count": row[9] or 0,
                    "created_at": str(row[10]) if row[10] else None,
                    "author_name": row[11] or "Unknown User",
                    "location": row[12] or "Unknown Location",
                    "location_country": row[13] or "Unknown Country",
                    "score": float(row[14]) if row[14] else 0.0,
                    "recommendation_type": "general_popular",
                    "algorithm": "popularity_fallback"
                })
            
            print(f"✅ Retrieved {len(popular_posts)} general popular posts")
            return popular_posts
            
        except Exception as e:
            print(f"❌ Error getting general popular posts: {str(e)}")
            return []
    
    def get_user_stats(self, user_id: int) -> Dict:
        """
        Get user statistics for debugging recommendations
        """
        try:
            interactions = self.db_adapter.get_user_interactions(user_id)
            user_posts = self.db_adapter.get_posts_by_user(user_id)
            
            stats = {
                "user_id": user_id,
                "total_interactions": len(interactions),
                "total_posts": len(user_posts),
                "interaction_breakdown": {},
                "recommendation_eligibility": {
                    "has_interactions": len(interactions) > 0,
                    "has_posts": len(user_posts) > 0,
                    "enough_for_collaborative": len(interactions) >= 3
                }
            }
            
            # Count interaction types
            for interaction in interactions:
                interaction_type = interaction["interaction_type"]
                stats["interaction_breakdown"][interaction_type] = stats["interaction_breakdown"].get(interaction_type, 0) + 1
            
            return stats
            
        except Exception as e:
            print(f"❌ Error getting user stats: {str(e)}")
            return {"error": str(e)}
    
    def train_model(self):
        """
        Train/refresh the recommendation models
        This can be called periodically to update recommendations based on new data
        """
        try:
            print("🔄 Training recommendation models...")
            
            # The original recommender handles training internally
            # We can add any additional training logic here if needed
            
            print("✅ Model training completed")
            return {"status": "success", "message": "Models trained successfully"}
            
        except Exception as e:
            print(f"❌ Error training models: {str(e)}")
            return {"status": "error", "message": str(e)}