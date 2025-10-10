import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from typing import List, Dict, Tuple
import sqlite3

class CollaborativeRecommender:
    def __init__(self, db_manager):
        self.db = db_manager
        self.user_item_matrix = None
        self.svd_model = None
        self.user_similarity_matrix = None
        self.user_similarity_df = None
        
    def build_user_item_matrix(self):
        """Build user-item interaction matrix for collaborative filtering"""
        print("🔄 Building user-item interaction matrix...")
        
        # Get all interactions from combined tables to build user-item matrix
        # Updated for current backend database schema
        interactions_query = """
        SELECT 
            user_id,
            post_id,
            interaction_type,
            1 as interaction_value
        FROM (
            SELECT user_id, post_id, 'like' as interaction_type FROM likes
            UNION ALL
            SELECT user_id, post_id, 'comment' as interaction_type FROM comments
            UNION ALL
            SELECT user_id, post_id, 'share' as interaction_type FROM shares
        )
        """
        
        interactions = self.db.execute_query(interactions_query)
        
        if not interactions:
            print("❌ No interactions found!")
            return None
            
        # Convert to DataFrame
        df = pd.DataFrame(interactions, columns=['user_id', 'post_id', 'interaction_type', 'value'])
        
        # Weight different interaction types
        interaction_weights = {
            'like': 1.0,
            'comment': 2.0,
            'share': 3.0,
            'save': 2.5
        }
        
        df['weighted_value'] = df['interaction_type'].map(interaction_weights)
        
        # Group by user and post, sum the weighted values
        df_grouped = df.groupby(['user_id', 'post_id'])['weighted_value'].sum().reset_index()
        
        # Create user-item matrix
        self.user_item_matrix = df_grouped.pivot(
            index='user_id', 
            columns='post_id', 
            values='weighted_value'
        ).fillna(0)
        
        print(f"✅ Matrix created: {self.user_item_matrix.shape[0]} users × {self.user_item_matrix.shape[1]} posts")
        return self.user_item_matrix
    
    def calculate_user_similarity(self):
        """Calculate user-user similarity matrix"""
        if self.user_item_matrix is None:
            self.build_user_item_matrix()
            
        if self.user_item_matrix is None:
            return None
            
        print("🔄 Calculating user similarity matrix...")
        
        # Calculate cosine similarity between users
        self.user_similarity_matrix = cosine_similarity(self.user_item_matrix)
        
        # Convert to DataFrame for easier handling
        user_ids = self.user_item_matrix.index
        self.user_similarity_df = pd.DataFrame(
            self.user_similarity_matrix,
            index=user_ids,
            columns=user_ids
        )
        
        print("✅ User similarity matrix calculated")
        return self.user_similarity_df
    
    def find_similar_users(self, user_id: int, n_similar: int = 10) -> List[Tuple[int, float]]:
        """Find most similar users to the given user"""
        if self.user_similarity_df is None:
            self.calculate_user_similarity()
            
        if user_id not in self.user_similarity_df.index:
            print(f"❌ User {user_id} not found in similarity matrix")
            return []
        
        # Get similarity scores for the user
        user_similarities = self.user_similarity_df.loc[user_id]
        
        # Sort by similarity (excluding the user themselves)
        similar_users = user_similarities[user_similarities.index != user_id].sort_values(ascending=False)
        
        # Return top N similar users with their similarity scores
        return [(int(user), float(score)) for user, score in similar_users.head(n_similar).items()]
    
    def recommend_posts_collaborative(self, user_id: int, n_recommendations: int = 10) -> List[Dict]:
        """Recommend posts based on collaborative filtering"""
        print(f"🔍 Finding collaborative recommendations for user {user_id}...")
        
        # Find similar users
        similar_users = self.find_similar_users(user_id, n_similar=20)
        
        if not similar_users:
            return []
        
        # Get posts that similar users liked but target user hasn't interacted with
        similar_user_ids = [user[0] for user in similar_users[:10]]  # Top 10 similar users
        
        # Get posts the target user has already interacted with
        user_posts_query = """
        SELECT DISTINCT post_id FROM (
            SELECT post_id FROM likes WHERE user_id = ?
            UNION
            SELECT post_id FROM comments WHERE user_id = ?
            UNION
            SELECT post_id FROM shares WHERE user_id = ?
        )
        """
        user_posts = set([row[0] for row in self.db.execute_query(user_posts_query, (user_id, user_id, user_id))])
        
        # Get posts liked by similar users from combined interaction tables
        similar_users_posts_query = """
        SELECT 
            interactions.post_id,
            p.caption,
            l.name as location_name,
            p.user_id as post_author,
            u.full_name as author_username,
            COUNT(*) as interaction_count,
            AVG(CASE 
                WHEN interactions.interaction_type = 'like' THEN 1.0
                WHEN interactions.interaction_type = 'comment' THEN 2.0  
                WHEN interactions.interaction_type = 'share' THEN 3.0
                ELSE 1.0
            END) as avg_interaction_weight
        FROM (
            SELECT user_id, post_id, 'like' as interaction_type FROM likes
            UNION ALL
            SELECT user_id, post_id, 'comment' as interaction_type FROM comments
            UNION ALL
            SELECT user_id, post_id, 'share' as interaction_type FROM shares
        ) interactions
        JOIN posts p ON interactions.post_id = p.id
        JOIN users u ON p.user_id = u.id
        LEFT JOIN locations l ON p.location_id = l.id
        WHERE interactions.user_id IN ({})
        GROUP BY interactions.post_id, p.caption, l.name, p.user_id, u.full_name
        ORDER BY interaction_count DESC, avg_interaction_weight DESC
        """.format(','.join(['?'] * len(similar_user_ids)))
        
        recommended_posts = self.db.execute_query(similar_users_posts_query, tuple(similar_user_ids))
        
        # Filter out posts the user has already seen and format results
        recommendations = []
        for post_data in recommended_posts:
            post_id, caption, location, author_id, author_username, interaction_count, avg_weight = post_data
            
            if post_id not in user_posts and len(recommendations) < n_recommendations:
                recommendations.append({
                    'post_id': post_id,
                    'caption': caption[:100] + "..." if caption and len(caption) > 100 else caption,
                    'location': location,
                    'author_id': author_id,
                    'author_username': author_username,
                    'popularity_score': float(interaction_count * avg_weight) if avg_weight else 0,
                    'recommendation_reason': 'Similar users liked this',
                    'algorithm': 'collaborative_filtering'
                })
        
        print(f"✅ Found {len(recommendations)} collaborative recommendations")
        return recommendations
    
    def recommend_users_to_follow(self, user_id: int, n_recommendations: int = 10) -> List[Dict]:
        """Recommend users to follow based on collaborative filtering"""
        print(f"🔍 Finding users to follow for user {user_id}...")
        
        # Find similar users
        similar_users = self.find_similar_users(user_id, n_similar=30)
        
        if not similar_users:
            return []
        
        # Get users that the target user is already following
        following_query = "SELECT following_id FROM follows WHERE follower_id = ?"
        already_following = set([row[0] for row in self.db.execute_query(following_query, (user_id,))])
        already_following.add(user_id)  # Don't recommend following yourself
        
        # Get users that similar users follow
        similar_user_ids = [user[0] for user in similar_users[:15]]  # Top 15 similar users
        
        users_to_follow_query = """
        SELECT 
            f.following_id,
            u.full_name as username,
            u.full_name,
            u.bio,
            u.location,
            u.travel_style,
            COUNT(f.following_id) as follow_count,
            (SELECT COUNT(*) FROM posts WHERE user_id = f.following_id) as post_count,
            (SELECT COUNT(*) FROM (
                SELECT user_id FROM likes WHERE user_id = f.following_id
                UNION ALL
                SELECT user_id FROM comments WHERE user_id = f.following_id  
                UNION ALL
                SELECT user_id FROM shares WHERE user_id = f.following_id
            )) as interaction_count
        FROM follows f
        JOIN users u ON f.following_id = u.id
        WHERE f.follower_id IN ({})
        GROUP BY f.following_id, u.full_name, u.bio, u.location, u.travel_style
        ORDER BY follow_count DESC, post_count DESC
        """.format(','.join(['?'] * len(similar_user_ids)))
        
        potential_follows = self.db.execute_query(users_to_follow_query, tuple(similar_user_ids))
        
        # Format recommendations
        recommendations = []
        for user_data in potential_follows:
            user_to_follow_id, username, full_name, bio, location, travel_style, follow_count, post_count, interaction_count = user_data
            
            if user_to_follow_id not in already_following and len(recommendations) < n_recommendations:
                recommendations.append({
                    'user_id': user_to_follow_id,
                    'username': username,
                    'full_name': full_name,
                    'bio': bio[:150] + "..." if bio and len(bio) > 150 else bio,
                    'location': location,
                    'travel_style': travel_style,
                    'follower_score': follow_count,
                    'post_count': post_count,
                    'engagement_score': interaction_count,
                    'recommendation_reason': 'Popular among similar travelers',
                    'algorithm': 'collaborative_filtering'
                })
        
        print(f"✅ Found {len(recommendations)} user recommendations")
        return recommendations
    
    def get_user_travel_stats(self, user_id: int) -> Dict:
        """Get travel statistics for a user"""
        stats_query = """
        SELECT 
            COUNT(DISTINCT p.id) as posts_count,
            (SELECT COUNT(*) FROM (
                SELECT user_id FROM likes WHERE user_id = u.id
                UNION ALL
                SELECT user_id FROM comments WHERE user_id = u.id
                UNION ALL  
                SELECT user_id FROM shares WHERE user_id = u.id
            )) as interactions_given,
            COUNT(DISTINCT f1.following_id) as following_count,
            COUNT(DISTINCT f2.follower_id) as followers_count,
            COUNT(DISTINCT l.id) as locations_visited,
            GROUP_CONCAT(DISTINCT l.name) as visited_locations
        FROM users u
        LEFT JOIN posts p ON u.id = p.user_id
        LEFT JOIN follows f1 ON u.id = f1.follower_id
        LEFT JOIN follows f2 ON u.id = f2.following_id
        LEFT JOIN locations l ON p.location_id = l.id
        WHERE u.id = ?
        """
        
        result = self.db.execute_query(stats_query, (user_id,))
        
        if result:
            posts, interactions, following, followers, locations, visited = result[0]
            return {
                'user_id': user_id,
                'posts_count': posts or 0,
                'interactions_given': interactions or 0,
                'following_count': following or 0,
                'followers_count': followers or 0,
                'locations_visited': locations or 0,
                'visited_locations': visited.split(',') if visited else []
            }
        
        return {}

if __name__ == "__main__":
    # Test the collaborative recommender
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
    
    from src.database.models import DatabaseManager
    
    db = DatabaseManager()
    recommender = CollaborativeRecommender(db)
    
    # Test with user ID 1
    print("🧪 Testing Collaborative Recommender...")
    
    # Build matrix
    recommender.build_user_item_matrix()
    
    # Test recommendations
    post_recs = recommender.recommend_posts_collaborative(1, 5)
    user_recs = recommender.recommend_users_to_follow(1, 5)
    
    print(f"\n📊 Post Recommendations for User 1:")
    for i, rec in enumerate(post_recs, 1):
        print(f"{i}. {rec['caption']} (Location: {rec['location']})")
    
    print(f"\n👥 User Recommendations for User 1:")
    for i, rec in enumerate(user_recs, 1):
        print(f"{i}. @{rec['username']} - {rec['travel_style']} traveler from {rec['location']}")
    
    print("\n✅ Collaborative filtering test complete!")