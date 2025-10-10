import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from collections import defaultdict
import random

from .collaborative import CollaborativeRecommender
from .content_based import ContentBasedRecommender

class HybridRecommender:
    def __init__(self, db_manager):
        self.db = db_manager
        self.collaborative = CollaborativeRecommender(db_manager)
        self.content_based = ContentBasedRecommender(db_manager)
        
        # Hybrid configuration
        self.collaborative_weight = 0.6  # 60% collaborative
        self.content_weight = 0.4       # 40% content-based
        self.min_interactions_for_collaborative = 3  # Minimum interactions needed for collaborative
        
    def recommend_posts(self, user_id: int, n_recommendations: int = 10) -> List[Dict]:
        """
        Hybrid post recommendation combining collaborative and content-based approaches
        """
        print(f"🔄 Generating hybrid recommendations for user {user_id}...")
        
        # First, validate that user exists
        user_exists = self.db.execute_query(
            "SELECT COUNT(*) FROM users WHERE id = ?", 
            (user_id,)
        )[0][0]

        if user_exists == 0:
            print(f"   ❌ User {user_id} does not exist")
            return []

        # Check user's interaction history from all interaction tables
        user_interaction_count = self.db.execute_query(
            """SELECT COUNT(*) FROM (
                SELECT user_id FROM likes WHERE user_id = ?
                UNION ALL
                SELECT user_id FROM comments WHERE user_id = ?
                UNION ALL
                SELECT user_id FROM shares WHERE user_id = ?
            )""", 
            (user_id, user_id, user_id)
        )[0][0]
        
        print(f"   ✅ User exists with {user_interaction_count} interactions")
        
        # Get recommendations from both systems
        collaborative_recs = []
        content_recs = []
        
        # Always try content-based (works even for new users)
        try:
            print("   🤖 Getting content-based recommendations...")
            content_recs = self.content_based.recommend_posts_content_based(
                user_id, n_recommendations * 2
            )
        except Exception as e:
            print(f"   ⚠️ Content-based failed: {e}")
        
        # Use collaborative if user has enough interactions
        if user_interaction_count >= self.min_interactions_for_collaborative:
            try:
                print("   👥 Getting collaborative recommendations...")
                collaborative_recs = self.collaborative.recommend_posts_collaborative(
                    user_id, n_recommendations * 2
                )
            except Exception as e:
                print(f"   ⚠️ Collaborative failed: {e}")
                
        # Combine recommendations using hybrid approach
        if len(collaborative_recs) > 0 and len(content_recs) > 0:
            # Weighted combination approach
            final_recs = self._combine_post_recommendations(
                collaborative_recs, content_recs, n_recommendations
            )
            approach = "hybrid"
            print(f"   ✅ Using hybrid approach: {len(collaborative_recs)} collab + {len(content_recs)} content")
            
        elif len(collaborative_recs) > 0:
            # Fallback to collaborative only
            final_recs = collaborative_recs[:n_recommendations]
            approach = "collaborative_only"
            print(f"   ✅ Using collaborative approach only: {len(collaborative_recs)} recommendations")
            
        elif len(content_recs) > 0:
            # Fallback to content-based only
            final_recs = content_recs[:n_recommendations]
            approach = "content_only"
            print(f"   ✅ Using content-based approach only: {len(content_recs)} recommendations")
            
        else:
            # Fallback to popular posts
            print("   ⚠️  Falling back to popular posts...")
            final_recs = self._get_popular_posts(user_id, n_recommendations)
            approach = "popularity_fallback"
        
        # Add hybrid metadata
        for rec in final_recs:
            rec['hybrid_approach'] = approach
            rec['user_interaction_count'] = user_interaction_count
        
        print(f"✅ Generated {len(final_recs)} hybrid recommendations using {approach}")
        return final_recs
    
    def recommend_users(self, user_id: int, n_recommendations: int = 10) -> List[Dict]:
        """
        Hybrid user recommendation combining collaborative and content-based approaches
        """
        print(f"🔄 Generating hybrid user recommendations for user {user_id}...")
        
        # Validate user exists
        user_exists = self.db.execute_query(
            "SELECT COUNT(*) FROM users WHERE user_id = ?", 
            (user_id,)
        )[0][0]
        
        if user_exists == 0:
            print(f"   ❌ User {user_id} does not exist")
            return []
        
        user_interaction_count = self.db.execute_query(
            "SELECT COUNT(*) FROM interactions WHERE user_id = ?", 
            (user_id,)
        )[0][0]
        
        collaborative_recs = []
        content_recs = []
        
        # Get recommendations from both systems
        if user_interaction_count >= self.min_interactions_for_collaborative:
            try:
                print("   👥 Getting collaborative user recommendations...")
                collaborative_recs = self.collaborative.recommend_users_to_follow(
                    user_id, n_recommendations * 2
                )
            except Exception as e:
                print(f"   ⚠️ Collaborative user recs failed: {e}")
        
        try:
            print("   🎯 Getting content-based user recommendations...")
            content_recs = self._get_content_based_users(user_id, n_recommendations * 2)
        except Exception as e:
            print(f"   ⚠️ Content-based user recs failed: {e}")
        
        # Combine user recommendations
        if len(collaborative_recs) > 0 and len(content_recs) > 0:
            final_recs = self._combine_user_recommendations(
                collaborative_recs, content_recs, n_recommendations
            )
            approach = "hybrid"
        elif len(collaborative_recs) > 0:
            final_recs = collaborative_recs[:n_recommendations]
            approach = "collaborative_only"
        elif len(content_recs) > 0:
            final_recs = content_recs[:n_recommendations]
            approach = "content_only" 
        else:
            final_recs = self._get_popular_users(n_recommendations)
            approach = "popularity_fallback"
        
        # Add metadata
        for rec in final_recs:
            rec['hybrid_approach'] = approach
        
        print(f"✅ Generated {len(final_recs)} user recommendations using {approach}")
        return final_recs
    
    def recommend_destinations(self, user_id: int, n_recommendations: int = 10) -> List[Dict]:
        """
        Hybrid destination recommendation
        """
        print(f"🔄 Generating hybrid destination recommendations for user {user_id}...")
        
        # Validate user exists
        user_exists = self.db.execute_query(
            "SELECT COUNT(*) FROM users WHERE user_id = ?", 
            (user_id,)
        )[0][0]
        
        if user_exists == 0:
            print(f"   ❌ User {user_id} does not exist")
            return []
        
        # Use content-based for destinations (works better for location analysis)
        try:
            content_dest_recs = self.content_based.recommend_destinations_content_based(
                user_id, n_recommendations
            )
            
            if len(content_dest_recs) > 0:
                # Enhance with collaborative insights
                enhanced_recs = self._enhance_destinations_with_collaborative(
                    user_id, content_dest_recs
                )
                
                for rec in enhanced_recs:
                    rec['hybrid_approach'] = 'content_with_collaborative_enhancement'
                
                print(f"✅ Generated {len(enhanced_recs)} enhanced destination recommendations")
                return enhanced_recs
            
        except Exception as e:
            print(f"   ⚠️ Content-based destinations failed: {e}")
        
        # Fallback to popular destinations
        popular_destinations = self._get_popular_destinations(n_recommendations)
        for rec in popular_destinations:
            rec['hybrid_approach'] = 'popularity_fallback'
        
        print(f"✅ Using popular destinations fallback: {len(popular_destinations)} recommendations")
        return popular_destinations
    
    def _combine_post_recommendations(self, collab_recs: List[Dict], content_recs: List[Dict], 
                                    n_final: int) -> List[Dict]:
        """
        Intelligently combine collaborative and content-based post recommendations
        """
        print("   🔀 Combining post recommendations...")
        
        # Create combined scoring
        combined_scores = {}
        post_details = {}
        
        # Process collaborative recommendations
        for i, rec in enumerate(collab_recs):
            post_id = rec['post_id']
            # Higher rank = higher score (inverse ranking)
            collab_score = (len(collab_recs) - i) / len(collab_recs)
            combined_scores[post_id] = collab_score * self.collaborative_weight
            post_details[post_id] = rec.copy()
            post_details[post_id]['collab_score'] = collab_score
            post_details[post_id]['collab_rank'] = i + 1
        
        # Process content-based recommendations
        for i, rec in enumerate(content_recs):
            post_id = rec['post_id']
            content_score = (len(content_recs) - i) / len(content_recs)
            
            if post_id in combined_scores:
                # Post appears in both - boost its score
                combined_scores[post_id] += content_score * self.content_weight
                post_details[post_id]['content_score'] = content_score
                post_details[post_id]['content_rank'] = i + 1
                post_details[post_id]['appears_in_both'] = True
            else:
                # Post only in content-based
                combined_scores[post_id] = content_score * self.content_weight
                post_details[post_id] = rec.copy()
                post_details[post_id]['content_score'] = content_score
                post_details[post_id]['content_rank'] = i + 1
                post_details[post_id]['collab_score'] = 0
        
        # Sort by combined score
        sorted_posts = sorted(
            combined_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Build final recommendations
        final_recommendations = []
        for post_id, combined_score in sorted_posts[:n_final]:
            rec = post_details[post_id].copy()
            rec['hybrid_score'] = combined_score
            rec['recommendation_reason'] = self._get_hybrid_reason(rec)
            final_recommendations.append(rec)
        
        return final_recommendations
    
    def _combine_user_recommendations(self, collab_recs: List[Dict], content_recs: List[Dict], 
                                    n_final: int) -> List[Dict]:
        """
        Combine collaborative and content-based user recommendations
        """
        print("   🔀 Combining user recommendations...")
        
        # Prioritize collaborative for user recommendations (works better)
        seen_users = set()
        final_recs = []
        
        # Take top collaborative recommendations first
        collab_take = min(int(n_final * 0.7), len(collab_recs))  # 70% from collaborative
        for rec in collab_recs[:collab_take]:
            if rec['user_id'] not in seen_users:
                rec['primary_reason'] = 'similar_users'
                final_recs.append(rec)
                seen_users.add(rec['user_id'])
        
        # Fill remaining with content-based
        content_take = n_final - len(final_recs)
        for rec in content_recs[:content_take * 2]:  # Look at more to avoid duplicates
            if rec['user_id'] not in seen_users and len(final_recs) < n_final:
                rec['primary_reason'] = 'similar_interests'
                final_recs.append(rec)
                seen_users.add(rec['user_id'])
        
        return final_recs
    
    def _enhance_destinations_with_collaborative(self, user_id: int, 
                                               dest_recs: List[Dict]) -> List[Dict]:
        """
        Enhance destination recommendations with collaborative insights
        """
        print("   ✨ Enhancing destinations with collaborative insights...")
        
        try:
            # Find similar users
            similar_users = self.collaborative.find_similar_users(user_id, n_similar=10)
            
            if not similar_users:
                return dest_recs
            
            # Get destinations popular among similar users
            similar_user_ids = [user[0] for user in similar_users[:5]]
            
            popular_among_similar_query = """
            SELECT l.name, COUNT(i.interaction_id) as popularity
            FROM interactions i
            JOIN posts p ON i.post_id = p.post_id
            JOIN locations l ON p.location_id = l.location_id
            WHERE i.user_id IN ({})
            GROUP BY l.name
            ORDER BY popularity DESC
            """.format(','.join(['?'] * len(similar_user_ids)))
            
            similar_popularity = dict(self.db.execute_query(
                popular_among_similar_query, tuple(similar_user_ids)
            ))
            
            # Enhance destination scores
            for rec in dest_recs:
                dest_name = rec.get('name')
                if dest_name in similar_popularity:
                    popularity_boost = min(similar_popularity[dest_name] / 10, 2.0)
                    rec['recommendation_score'] = rec.get('recommendation_score', 0) + popularity_boost
                    rec['collaborative_boost'] = popularity_boost
                    if 'reasons' not in rec:
                        rec['reasons'] = []
                    rec['reasons'].append(f"Popular among travelers like you")
            
            # Re-sort by enhanced scores
            dest_recs.sort(key=lambda x: x.get('recommendation_score', 0), reverse=True)
            
        except Exception as e:
            print(f"   ⚠️ Collaborative enhancement failed: {e}")
        
        return dest_recs
    
    def _get_hybrid_reason(self, rec: Dict) -> str:
        """
        Generate explanation for why this post was recommended
        """
        reasons = []
        
        if rec.get('appears_in_both', False):
            reasons.append("Matches both your behavior and interests")
        elif rec.get('collab_score', 0) > 0:
            reasons.append("Similar users loved this")
        
        if rec.get('content_score', 0) > 0:
            reasons.append("Matches your travel preferences")
        
        return "; ".join(reasons) if reasons else rec.get('recommendation_reason', 'Recommended for you')
    
    def _get_content_based_users(self, user_id: int, n_users: int) -> List[Dict]:
        """
        Get users with similar content preferences
        """
        # Get user's location and travel style preferences
        user_prefs_query = """
        SELECT l.name, l.category, u.travel_style, COUNT(*) as interaction_count
        FROM interactions i
        JOIN posts p ON i.post_id = p.post_id
        JOIN locations l ON p.location_id = l.location_id
        JOIN users u ON p.user_id = u.user_id
        WHERE i.user_id = ?
        GROUP BY l.name, l.category, u.travel_style
        ORDER BY interaction_count DESC
        LIMIT 5
        """
        
        user_prefs = self.db.execute_query(user_prefs_query, (user_id,))
        
        if not user_prefs:
            return []
        
        # Find users with similar preferences
        preferred_locations = [pref[0] for pref in user_prefs]
        preferred_categories = [pref[1] for pref in user_prefs if pref[1]]
        
        similar_users_query = """
        SELECT DISTINCT u.user_id, u.username, u.full_name, u.bio, 
               u.location, u.travel_style,
               COUNT(DISTINCT p.post_id) as post_count,
               COUNT(DISTINCT i.interaction_id) as interaction_count
        FROM users u
        JOIN posts p ON u.user_id = p.user_id
        JOIN locations l ON p.location_id = l.location_id
        LEFT JOIN interactions i ON u.user_id = i.user_id
        WHERE u.user_id != ? 
        AND (l.name IN ({}) OR l.category IN ({}))
        GROUP BY u.user_id, u.username, u.full_name, u.bio, u.location, u.travel_style
        HAVING post_count > 0
        ORDER BY interaction_count DESC, post_count DESC
        LIMIT ?
        """.format(
            ','.join(['?'] * len(preferred_locations)),
            ','.join(['?'] * len(preferred_categories))
        )
        
        params = [user_id] + preferred_locations + preferred_categories + [n_users]
        similar_users_data = self.db.execute_query(similar_users_query, tuple(params))
        
        recommendations = []
        for user_data in similar_users_data:
            user_rec_id, username, full_name, bio, location, travel_style, post_count, interaction_count = user_data
            recommendations.append({
                'user_id': user_rec_id,
                'username': username,
                'full_name': full_name,
                'bio': bio[:150] + "..." if bio and len(bio) > 150 else bio,
                'location': location,
                'travel_style': travel_style,
                'post_count': post_count,
                'engagement_score': interaction_count,
                'recommendation_reason': 'Similar travel interests',
                'algorithm': 'content_based_users'
            })
        
        return recommendations
    
    def _get_popular_posts(self, user_id: int, n_posts: int) -> List[Dict]:
        """
        Fallback to popular posts
        """
        # Get posts user hasn't seen
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
        
        popular_posts = self.db.execute_query(popular_posts_query, (user_id, user_id, user_id, n_posts))
        
        recommendations = []
        for post_data in popular_posts:
            post_id, caption, author_id, author_username, location, interaction_count = post_data
            recommendations.append({
                'post_id': post_id,
                'caption': caption[:100] + "..." if caption and len(caption) > 100 else caption,
                'author_id': author_id,
                'author_username': author_username,
                'location': location,
                'popularity_score': interaction_count,
                'recommendation_reason': 'Popular content',
                'algorithm': 'popularity_based'
            })
        
        return recommendations
    
    def _get_popular_users(self, n_users: int) -> List[Dict]:
        """
        Fallback to popular users
        """
        popular_users_query = """
        SELECT u.user_id, u.username, u.full_name, u.bio, u.location, u.travel_style,
               COUNT(DISTINCT p.post_id) as post_count,
               COUNT(DISTINCT f.follower_id) as follower_count
        FROM users u
        LEFT JOIN posts p ON u.user_id = p.user_id
        LEFT JOIN follows f ON u.user_id = f.following_id
        GROUP BY u.user_id, u.username, u.full_name, u.bio, u.location, u.travel_style
        ORDER BY follower_count DESC, post_count DESC
        LIMIT ?
        """
        
        popular_users = self.db.execute_query(popular_users_query, (n_users,))
        
        recommendations = []
        for user_data in popular_users:
            user_rec_id, username, full_name, bio, location, travel_style, post_count, follower_count = user_data
            recommendations.append({
                'user_id': user_rec_id,
                'username': username,
                'full_name': full_name,
                'bio': bio[:150] + "..." if bio and len(bio) > 150 else bio,
                'location': location,
                'travel_style': travel_style,
                'post_count': post_count,
                'follower_count': follower_count,
                'recommendation_reason': 'Popular traveler',
                'algorithm': 'popularity_based'
            })
        
        return recommendations
    
    def _get_popular_destinations(self, n_destinations: int) -> List[Dict]:
        """
        Fallback to popular destinations
        """
        popular_destinations_query = """
        SELECT l.location_id, l.name, l.country, l.continent, l.category,
               COUNT(DISTINCT p.post_id) as post_count,
               COUNT(DISTINCT i.interaction_id) as total_interactions
        FROM locations l
        LEFT JOIN posts p ON l.location_id = p.location_id
        LEFT JOIN interactions i ON p.post_id = i.post_id
        GROUP BY l.location_id, l.name, l.country, l.continent, l.category
        ORDER BY total_interactions DESC, post_count DESC
        LIMIT ?
        """
        
        popular_destinations = self.db.execute_query(popular_destinations_query, (n_destinations,))
        
        recommendations = []
        for dest_data in popular_destinations:
            loc_id, name, country, continent, category, post_count, interactions = dest_data
            recommendations.append({
                'location_id': loc_id,
                'name': name,
                'country': country,
                'continent': continent,
                'category': category,
                'post_count': post_count,
                'interaction_count': interactions,
                'recommendation_reason': 'Popular destination',
                'algorithm': 'popularity_based'
            })
        
        return recommendations
    
    def get_recommendation_explanation(self, user_id: int) -> Dict:
        """
        Provide explanation of how recommendations are generated for this user
        """
        user_interaction_count = self.db.execute_query(
            "SELECT COUNT(*) FROM interactions WHERE user_id = ?", 
            (user_id,)
        )[0][0]
        
        explanation = {
            'user_id': user_id,
            'interaction_count': user_interaction_count,
            'recommendation_strategy': {},
            'data_available': {}
        }
        
        # Determine strategy
        if user_interaction_count >= self.min_interactions_for_collaborative:
            explanation['recommendation_strategy']['posts'] = 'hybrid'
            explanation['recommendation_strategy']['users'] = 'hybrid'
            explanation['recommendation_strategy']['description'] = f"Using hybrid approach (collaborative + content-based) because you have {user_interaction_count} interactions"
        else:
            explanation['recommendation_strategy']['posts'] = 'content_only'
            explanation['recommendation_strategy']['users'] = 'content_only'
            explanation['recommendation_strategy']['description'] = f"Using content-based approach because you have only {user_interaction_count} interactions (need {self.min_interactions_for_collaborative}+ for hybrid)"
        
        explanation['recommendation_strategy']['destinations'] = 'content_with_collaborative_enhancement'
        
        # Data available
        user_stats = self.collaborative.get_user_travel_stats(user_id)
        explanation['data_available'] = user_stats
        
        return explanation

if __name__ == "__main__":
    # Test the hybrid recommender
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
    
    from src.database.models import DatabaseManager
    
    db = DatabaseManager()
    hybrid_recommender = HybridRecommender(db)
    
    # Test with different user scenarios
    test_users = [1, 25, 50]  # Different interaction levels
    
    for user_id in test_users:
        print(f"\n🧪 Testing Hybrid Recommender for User {user_id}")
        print("=" * 60)
        
        # Get explanation
        explanation = hybrid_recommender.get_recommendation_explanation(user_id)
        print(f"Strategy: {explanation['recommendation_strategy']['description']}")
        
        # Test post recommendations
        post_recs = hybrid_recommender.recommend_posts(user_id, 5)
        print(f"\n📊 Hybrid Post Recommendations:")
        for i, rec in enumerate(post_recs, 1):
            approach = rec.get('hybrid_approach', 'unknown')
            score = rec.get('hybrid_score', rec.get('similarity_score', 0))
            print(f"{i}. {rec['caption'][:60]}... (Location: {rec.get('location', 'Unknown')})")
            print(f"   Score: {score:.3f} | Approach: {approach} | Reason: {rec.get('recommendation_reason', 'N/A')}")
        
        # Test user recommendations  
        user_recs = hybrid_recommender.recommend_users(user_id, 3)
        print(f"\n👥 Hybrid User Recommendations:")
        for i, rec in enumerate(user_recs, 1):
            approach = rec.get('hybrid_approach', 'unknown')
            print(f"{i}. @{rec['username']} ({rec['travel_style']}) from {rec['location']}")
            print(f"   Approach: {approach} | Reason: {rec.get('recommendation_reason', 'N/A')}")
        
        # Test destination recommendations
        dest_recs = hybrid_recommender.recommend_destinations(user_id, 3)
        print(f"\n🏞️ Hybrid Destination Recommendations:")
        for i, rec in enumerate(dest_recs, 1):
            approach = rec.get('hybrid_approach', 'unknown')
            score = rec.get('recommendation_score', 0)
            print(f"{i}. {rec['name']}, {rec['country']} ({rec['category']}) - Score: {score:.3f}")
            print(f"   Approach: {approach}")
            if rec.get('reasons'):
                print(f"   Reasons: {', '.join(rec['reasons'][:2])}")
    
    print("\n✅ Hybrid recommendation system test complete!")