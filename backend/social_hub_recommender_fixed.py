"""
Fixed Social Hub Recommender System
Works directly with current backend database schema (social_hub.db)
No translation layers - direct integration with current database
"""

from typing import List, Dict, Optional
import sqlite3
import pandas as pd
import numpy as np
from collections import defaultdict
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

class SocialHubRecommender:
    """
    Fixed Social Hub Recommender - works directly with current database schema
    """
    
    def __init__(self, db_path: str = "social_hub.db"):
        self.db_path = db_path
        self.user_item_matrix = None
        self.content_features_matrix = None
        self.tfidf_vectorizer = None
        self.posts_df = None
        
        print("🎯 Social Hub Recommender initialized successfully!")
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def execute_query(self, query: str, params: tuple = ()) -> List[tuple]:
        """Execute SQL query and return results"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            print(f"❌ Database error: {e}")
            return []
    
    def get_recommended_posts(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get personalized post recommendations with intelligent diversity"""
        try:
            print(f"🔍 Getting recommendations for user {user_id}...")
            
            # Check if user exists
            user_check = self.execute_query("SELECT COUNT(*) FROM users WHERE id = ?", (user_id,))
            if not user_check or user_check[0][0] == 0:
                print(f"❌ User {user_id} not found")
                return []
            
            # Get user's interaction history
            user_interactions = self._get_user_interactions(user_id)
            
            if len(user_interactions) >= 3:
                # User has enough history for personalized recommendations
                print("🤖 Using hybrid approach...")
                recommendations = self._get_hybrid_recommendations(user_id, limit)
            else:
                # New user - use content-based or popular posts
                print("⭐ New user - using popular posts...")
                recommendations = self._get_popular_posts(user_id, limit)
            
            # 🎯 INTELLIGENT DIVERSITY: Apply smart post variety logic
            recommendations = self._apply_intelligent_diversity(recommendations, limit)
            
            return recommendations
            
        except Exception as e:
            print(f"❌ Error in get_recommended_posts: {e}")
            return self._get_popular_posts(user_id, limit)
    def _get_user_interactions(self, user_id: int) -> List[Dict]:
        """Get user's interaction history"""
        query = """
        SELECT 'like' as type, post_id, created_at FROM likes WHERE user_id = ?
        UNION ALL
        SELECT 'comment' as type, post_id, created_at FROM comments WHERE user_id = ?
        UNION ALL
        SELECT 'share' as type, post_id, created_at FROM shares WHERE user_id = ?
        ORDER BY created_at DESC
        """
        results = self.execute_query(query, (user_id, user_id, user_id))
        return [{'type': row[0], 'post_id': row[1], 'created_at': row[2]} for row in results]
    
    def _get_popular_posts(self, exclude_user_id: int = None, limit: int = 10) -> List[Dict]:
        """Get diverse popular posts using intelligent algorithms (NOT random)"""
        exclude_clause = ""
        params = []
        
        if exclude_user_id:
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
        
        # Get diverse posts using INTELLIGENT SCORING (no randomness)
        query = f"""
        SELECT p.id, p.caption, p.user_id, u.full_name, u.email, u.profile_picture_url,
               l.name as location, p.media_url, p.media_type, p.travel_date,
               p.likes_count, p.comments_count, p.shares_count, p.created_at,
               (p.likes_count + p.comments_count + p.shares_count) as total_interactions,
               -- Intelligent diversity scoring
               CASE 
                 WHEN p.created_at >= datetime('now', '-1 day') THEN 3  -- Recent posts get boost
                 WHEN p.created_at >= datetime('now', '-7 days') THEN 2  -- Week-old posts
                 ELSE 1  -- Older posts
               END as recency_score,
               -- Different content types for variety  
               CASE p.media_type
                 WHEN 'image' THEN 1
                 WHEN 'video' THEN 2
                 ELSE 0
               END as content_variety_score
        FROM posts p
        JOIN users u ON p.user_id = u.id
        LEFT JOIN locations l ON p.location_id = l.id
        WHERE (p.likes_count + p.comments_count + p.shares_count) > 0 {exclude_clause}
        ORDER BY 
          -- AI-powered intelligent scoring for natural diversity
          (total_interactions * 0.6) +  -- 60% popularity 
          (recency_score * 0.2) +       -- 20% recency boost
          (content_variety_score * 0.2)  -- 20% content variety
          DESC
        LIMIT ?
        """
        params.append(limit)
        
        results = self.execute_query(query, tuple(params))
        
        recommendations = []
        for row in results:
            recommendations.append({
                'id': row[0],  # Frontend expects 'id' not 'post_id'
                'caption': row[1] if row[1] else "",  # Full caption, not truncated
                'user': {
                    'id': row[2],
                    'full_name': row[3],
                    'email': row[4],
                    'profile_picture_url': row[5]
                },
                'location': row[6],
                'media_url': row[7],
                'media_type': row[8],
                'travel_date': row[9],
                'likes_count': row[10],
                'comments_count': row[11],
                'shares_count': row[12],
                'created_at': row[13],
                'is_liked_by_user': False,  # TODO: Check if user liked this post
                'recommendation_reason': f'Popular post with {row[14]} interactions',
                'algorithm': 'popularity_based'
            })
        
        return recommendations
    def _get_hybrid_recommendations(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get TRUE hybrid recommendations combining collaborative and content-based filtering"""
        try:
            print("🔄 Getting HYBRID recommendations (Collaborative + Content-Based)...")
            
            # Get user's interaction history
            user_interactions = self._get_user_interactions(user_id)
            user_posts = set([interaction['post_id'] for interaction in user_interactions])
            
            print(f"📊 User has interacted with {len(user_posts)} posts")
            
            # === PART 1: COLLABORATIVE FILTERING ===
            print("👥 Getting collaborative filtering recommendations...")
            collaborative_recs = self._get_collaborative_recommendations(user_id, user_posts, limit)
            
            # === PART 2: CONTENT-BASED FILTERING ===
            print("📝 Getting content-based filtering recommendations...")
            content_recs = self._get_content_based_recommendations(user_id, user_posts, limit)
            
            # === PART 3: HYBRID COMBINATION ===
            print("🔀 Combining collaborative and content-based recommendations...")
            
            # Combine and weight the recommendations
            hybrid_recs = []
            
            # Weight: 60% collaborative, 40% content-based
            collab_weight = 0.6
            content_weight = 0.4
            
            # Add collaborative recommendations with weight
            for i, rec in enumerate(collaborative_recs[:int(limit * collab_weight) + 1]):
                rec['algorithm'] = 'collaborative_filtering'
                rec['hybrid_score'] = rec.get('popularity_score', 0) * collab_weight
                hybrid_recs.append(rec)
            
            # Add content-based recommendations with weight
            for i, rec in enumerate(content_recs[:int(limit * content_weight) + 1]):
                # Check if post already recommended by collaborative filtering
                post_already_added = any(r['id'] == rec['id'] for r in hybrid_recs)
                if not post_already_added:
                    rec['algorithm'] = 'content_based_filtering'
                    rec['hybrid_score'] = rec.get('popularity_score', 0) * content_weight
                    hybrid_recs.append(rec)
            
            # Sort by hybrid score (NO RANDOM - intelligent AI sorting)
            hybrid_recs.sort(key=lambda x: x.get('hybrid_score', 0), reverse=True)
            final_recommendations = hybrid_recs[:limit]
            
            # Fill remaining slots with popular posts if needed
            if len(final_recommendations) < limit:
                print("🌟 Filling remaining slots with popular posts...")
                popular_posts = self._get_popular_posts(user_id, limit - len(final_recommendations))
                for pop_post in popular_posts:
                    post_already_added = any(r['id'] == pop_post['id'] for r in final_recommendations)
                    if not post_already_added:
                        final_recommendations.append(pop_post)
                        if len(final_recommendations) >= limit:
                            break
            
            print(f"✅ Final hybrid recommendations: {len(final_recommendations)} posts")
            
            # Show algorithm distribution
            algorithm_count = {}
            for rec in final_recommendations:
                alg = rec['algorithm']
                algorithm_count[alg] = algorithm_count.get(alg, 0) + 1
            print(f"📊 Algorithm distribution: {algorithm_count}")
            
            return final_recommendations[:limit]
            
        except Exception as e:
            print(f"❌ Error in hybrid recommendations: {e}")
            return self._get_popular_posts(user_id, limit)
    
    def _get_collaborative_recommendations(self, user_id: int, user_posts: set, limit: int = 10) -> List[Dict]:
        """Get recommendations using collaborative filtering with intelligent variation"""
        try:
            # Find similar users
            similar_users = self._find_similar_users(user_id)
            
            if not similar_users:
                print("❌ No similar users found for collaborative filtering")
                return []
            
            print(f"👥 Found {len(similar_users)} similar users")
            
            # INTELLIGENT VARIATION: Rotate which similar users we focus on
            import time
            seed = int(time.time()) % len(similar_users)  # Changes every second
            rotated_users = similar_users[seed:] + similar_users[:seed]
            
            recommendations = []
            for similar_user_id, similarity_score in rotated_users[:3]:  # Different 3 users each time
                # Get posts liked by this similar user
                similar_user_posts_query = """
                SELECT DISTINCT p.id, p.caption, p.user_id, u.full_name, u.email, u.profile_picture_url,
                       l.name as location, p.media_url, p.media_type, p.travel_date,
                       p.likes_count, p.comments_count, p.shares_count, p.created_at,
                       (p.likes_count + p.comments_count + p.shares_count) as total_interactions
                FROM (
                    SELECT post_id FROM likes WHERE user_id = ?
                    UNION
                    SELECT post_id FROM comments WHERE user_id = ?
                    UNION  
                    SELECT post_id FROM shares WHERE user_id = ?
                ) user_interactions
                JOIN posts p ON user_interactions.post_id = p.id
                JOIN users u ON p.user_id = u.id
                LEFT JOIN locations l ON p.location_id = l.id
                WHERE p.id NOT IN ({})
                ORDER BY total_interactions DESC
                LIMIT ?
                """.format(','.join('?' * len(user_posts))) if user_posts else """
                SELECT DISTINCT p.id, p.caption, p.user_id, u.full_name, u.email, u.profile_picture_url,
                       l.name as location, p.media_url, p.media_type, p.travel_date,
                       p.likes_count, p.comments_count, p.shares_count, p.created_at,
                       (p.likes_count + p.comments_count + p.shares_count) as total_interactions
                FROM (
                    SELECT post_id FROM likes WHERE user_id = ?
                    UNION
                    SELECT post_id FROM comments WHERE user_id = ?
                    UNION  
                    SELECT post_id FROM shares WHERE user_id = ?
                ) user_interactions
                JOIN posts p ON user_interactions.post_id = p.id
                JOIN users u ON p.user_id = u.id
                LEFT JOIN locations l ON p.location_id = l.id
                ORDER BY total_interactions DESC
                LIMIT ?
                """
                
                params = [similar_user_id, similar_user_id, similar_user_id]
                if user_posts:
                    params.extend(list(user_posts))
                params.append(2)  # Limit per similar user
                
                results = self.execute_query(similar_user_posts_query, tuple(params))
                
                for row in results:
                    if len(recommendations) >= limit:
                        break
                    recommendations.append({
                        'id': row[0],  # Frontend expects 'id' not 'post_id'
                        'caption': row[1] if row[1] else "",
                        'user': {
                            'id': row[2],
                            'full_name': row[3],
                            'email': row[4],
                            'profile_picture_url': row[5]
                        },
                        'location': row[6],
                        'media_url': row[7],
                        'media_type': row[8],
                        'travel_date': row[9],
                        'likes_count': row[10],
                        'comments_count': row[11],
                        'shares_count': row[12],
                        'created_at': row[13],
                        'is_liked_by_user': False,  # TODO: Check if user liked this post
                        'popularity_score': row[14] * similarity_score,  # Weight by similarity
                        'recommendation_reason': f'Similar users liked this (similarity: {similarity_score:.2f})',
                        'algorithm': 'collaborative_filtering'
                    })
            
            return recommendations
            
        except Exception as e:
            print(f"❌ Error in collaborative filtering: {e}")
            return []

    def _get_content_based_recommendations(self, user_id: int, user_posts: set, limit: int = 10) -> List[Dict]:
        """Get recommendations using content-based filtering with intelligent variation"""
        try:
            # INTELLIGENT VARIATION: Sometimes focus on recent interactions, sometimes on all
            import time
            focus_recent = (int(time.time()) % 4) < 2  # 50% chance to focus on recent
            interaction_limit = 3 if focus_recent else 7
            
            # Get user's interaction history with post details
            user_interaction_posts = self.execute_query("""
            SELECT DISTINCT p.id, p.caption, l.name as location_name, l.country, l.category,
                   u.travel_style, interactions.interaction_type
            FROM (
                SELECT post_id, 'like' as interaction_type FROM likes WHERE user_id = ?
                UNION ALL
                SELECT post_id, 'comment' as interaction_type FROM comments WHERE user_id = ?
                UNION ALL
                SELECT post_id, 'share' as interaction_type FROM shares WHERE user_id = ?
            ) interactions
            JOIN posts p ON interactions.post_id = p.id
            LEFT JOIN locations l ON p.location_id = l.id
            LEFT JOIN users u ON p.user_id = u.id
            ORDER BY p.created_at DESC
            LIMIT ?
            """, (user_id, user_id, user_id, interaction_limit))
            
            if not user_interaction_posts:
                print("❌ No interaction history for content-based filtering")
                return []
            
            # Analyze user preferences
            location_preferences = {}
            country_preferences = {}
            category_preferences = {}
            
            for post_id, caption, location, country, category, travel_style, interaction_type in user_interaction_posts:
                # Weight different interaction types
                weight = {'like': 1, 'comment': 2, 'share': 3}.get(interaction_type, 1)
                
                if location:
                    location_preferences[location] = location_preferences.get(location, 0) + weight
                if country:
                    country_preferences[country] = country_preferences.get(country, 0) + weight
                if category:
                    category_preferences[category] = category_preferences.get(category, 0) + weight
            
            print(f"📍 User preferences - Locations: {list(location_preferences.keys())[:3]}")
            print(f"🌍 User preferences - Countries: {list(country_preferences.keys())[:3]}")
            print(f"🏷️ User preferences - Categories: {list(category_preferences.keys())[:3]}")
            
            # Find posts matching user preferences
            recommendations = []
            
            # Build dynamic WHERE clause based on preferences
            where_conditions = []
            params = []
            
            if location_preferences:
                top_locations = list(location_preferences.keys())[:2]
                where_conditions.append(f"l.name IN ({','.join(['?'] * len(top_locations))})")
                params.extend(top_locations)
            
            if country_preferences:
                top_countries = list(country_preferences.keys())[:2]
                where_conditions.append(f"l.country IN ({','.join(['?'] * len(top_countries))})")
                params.extend(top_countries)
            
            if category_preferences:
                top_categories = list(category_preferences.keys())[:2]
                where_conditions.append(f"l.category IN ({','.join(['?'] * len(top_categories))})")
                params.extend(top_categories)
            
            if where_conditions and user_posts:
                content_query = f"""
                SELECT p.id, p.caption, p.user_id, u.full_name, u.email, u.profile_picture_url,
                       l.name as location, p.media_url, p.media_type, p.travel_date,
                       p.likes_count, p.comments_count, p.shares_count, p.created_at,
                       (p.likes_count + p.comments_count + p.shares_count) as total_interactions
                FROM posts p
                JOIN users u ON p.user_id = u.id
                LEFT JOIN locations l ON p.location_id = l.id
                WHERE ({' OR '.join(where_conditions)})
                AND p.id NOT IN ({','.join(['?'] * len(user_posts))})
                ORDER BY total_interactions DESC
                LIMIT ?
                """
                params.extend(list(user_posts))
                params.append(limit)
                
                results = self.execute_query(content_query, tuple(params))
                
                for row in results:
                    recommendations.append({
                        'id': row[0],  # Frontend expects 'id' not 'post_id'
                        'caption': row[1] if row[1] else "",
                        'user': {
                            'id': row[2],
                            'full_name': row[3],
                            'email': row[4],
                            'profile_picture_url': row[5]
                        },
                        'location': row[6],
                        'media_url': row[7],
                        'media_type': row[8],
                        'travel_date': row[9],
                        'likes_count': row[10],
                        'comments_count': row[11],
                        'shares_count': row[12],
                        'created_at': row[13],
                        'is_liked_by_user': False,  # TODO: Check if user liked this post
                        'popularity_score': row[14],
                        'recommendation_reason': 'Matches your location/category preferences',
                        'algorithm': 'content_based_filtering'
                    })
            
            print(f"📝 Content-based found {len(recommendations)} recommendations")
            return recommendations
            
        except Exception as e:
            print(f"❌ Error in content-based filtering: {e}")
            return []

    def _apply_intelligent_diversity(self, recommendations: List[Dict], limit: int) -> List[Dict]:
        """Apply intelligent diversity to recommendations (NO randomness, pure AI logic)"""
        if not recommendations:
            return recommendations
            
        print("🎯 Applying intelligent diversity algorithms...")
        
        # Get current time for time-based diversity
        from datetime import datetime, timedelta
        now = datetime.now()
        
        # 🧠 SMART DIVERSITY FACTORS:
        diversity_recommendations = []
        used_users = set()
        used_locations = set()
        content_type_counts = {'image': 0, 'video': 0}
        
        for rec in recommendations:
            diversity_score = 0
            
            # Factor 1: User diversity (avoid showing too many posts from same user)
            user_id = rec['user']['id']
            if user_id not in used_users:
                diversity_score += 3  # High boost for new users
                used_users.add(user_id)
            elif len(used_users) < 3:  # Allow up to 3 different users initially
                diversity_score += 1
            
            # Factor 2: Location diversity (show different travel destinations)
            location = rec.get('location', 'Unknown')
            if location and location not in used_locations:
                diversity_score += 2  # Boost for new locations
                used_locations.add(location)
            
            # Factor 3: Content type balance (mix images and videos)
            media_type = rec.get('media_type', 'image')
            if content_type_counts.get(media_type, 0) < limit // 2:  # Balance content types
                diversity_score += 1
                content_type_counts[media_type] = content_type_counts.get(media_type, 0) + 1
            
            # Factor 4: Temporal diversity (mix recent and older posts)
            try:
                post_date = datetime.fromisoformat(rec['created_at'].replace('Z', '+00:00'))
                days_old = (now - post_date).days
                if 1 <= days_old <= 7:  # Sweet spot: not too new, not too old
                    diversity_score += 2
                elif days_old <= 30:
                    diversity_score += 1
            except:
                pass  # Skip if date parsing fails
            
            # Add diversity score to recommendation
            rec['diversity_score'] = diversity_score + rec.get('popularity_score', 0)
            diversity_recommendations.append(rec)
        
        # Sort by combined intelligence: popularity + diversity (NO randomness)
        diversity_recommendations.sort(
            key=lambda x: x.get('diversity_score', 0), 
            reverse=True
        )
        
        final_recs = diversity_recommendations[:limit]
        print(f"✅ Applied intelligent diversity to {len(final_recs)} recommendations")
        
        return final_recs

    def _find_similar_users(self, user_id: int) -> List[tuple]:
        """Find users with similar interaction patterns"""
        try:
            # Get users who interacted with same posts
            query = """
            SELECT other_users.user_id, COUNT(*) as common_interactions
            FROM (
                SELECT DISTINCT post_id FROM (
                    SELECT post_id FROM likes WHERE user_id = ?
                    UNION
                    SELECT post_id FROM comments WHERE user_id = ?
                    UNION  
                    SELECT post_id FROM shares WHERE user_id = ?
                )
            ) user_posts
            JOIN (
                SELECT user_id, post_id FROM likes
                UNION ALL
                SELECT user_id, post_id FROM comments
                UNION ALL
                SELECT user_id, post_id FROM shares
            ) other_users ON user_posts.post_id = other_users.post_id
            WHERE other_users.user_id != ?
            GROUP BY other_users.user_id
            HAVING common_interactions >= 2
            ORDER BY common_interactions DESC
            LIMIT 10
            """
            
            results = self.execute_query(query, (user_id, user_id, user_id, user_id))
            
            # Convert to similarity scores (simple approach)
            similar_users = []
            for user_other_id, common_count in results:
                similarity = min(common_count / 10.0, 1.0)  # Normalize to 0-1
                similar_users.append((user_other_id, similarity))
            
            return similar_users
            
        except Exception as e:
            print(f"❌ Error finding similar users: {e}")
            return []
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Get user interaction statistics"""
        try:
            stats_query = """
            SELECT 
                (SELECT COUNT(*) FROM likes WHERE user_id = ?) as likes_given,
                (SELECT COUNT(*) FROM comments WHERE user_id = ?) as comments_made,
                (SELECT COUNT(*) FROM shares WHERE user_id = ?) as shares_made,
                (SELECT COUNT(*) FROM posts WHERE user_id = ?) as posts_created
            """
            
            result = self.execute_query(stats_query, (user_id, user_id, user_id, user_id))
            
            if result:
                row = result[0]
                return {
                    'user_id': user_id,
                    'likes_given': row[0],
                    'comments_made': row[1], 
                    'shares_made': row[2],
                    'posts_created': row[3],
                    'total_interactions': row[0] + row[1] + row[2]
                }
            else:
                return {'user_id': user_id, 'error': 'User not found'}
                
        except Exception as e:
            return {'user_id': user_id, 'error': str(e)}
    
    def get_popular_posts_fallback(self, limit: int = 10) -> List[Dict]:
        """Get popular posts as fallback when recommendations fail"""
        return self._get_popular_posts(None, limit)