#!/usr/bin/env python3
"""
Test Collaborative Filtering Component Separately
"""

import sys
import os
sys.path.append('/home/kshitij/Downloads/Social Hub/Social-Hub/backend')

import sqlite3
from typing import List, Dict, Tuple
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class CollaborativeFilteringTester:
    """Standalone Collaborative Filtering for testing"""
    
    def __init__(self, db_path: str = "social_hub.db"):
        self.db_path = db_path
        self.user_item_matrix = None
        self.user_similarity_matrix = None
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def execute_query(self, query: str, params: tuple = ()) -> List[tuple]:
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
    
    def build_user_item_matrix(self):
        """Build user-item interaction matrix for collaborative filtering"""
        print("🔄 Building user-item interaction matrix...")
        
        # Get all interactions from combined tables
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
        
        interactions = self.execute_query(interactions_query)
        
        if not interactions:
            print("❌ No interactions found!")
            return None
            
        # Convert to DataFrame
        df = pd.DataFrame(interactions, columns=['user_id', 'post_id', 'interaction_type', 'value'])
        
        # Weight different interaction types
        interaction_weights = {
            'like': 1.0,
            'comment': 2.0,
            'share': 3.0
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
        print(f"📊 Matrix density: {(self.user_item_matrix > 0).sum().sum() / (self.user_item_matrix.shape[0] * self.user_item_matrix.shape[1]):.4f}")
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
            print(f"❌ No similar users found for user {user_id}")
            return []
        
        print(f"👥 Found {len(similar_users)} similar users")
        for i, (sim_user, score) in enumerate(similar_users[:5]):
            print(f"   {i+1}. User {sim_user} (similarity: {score:.3f})")
        
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
        user_posts = set([row[0] for row in self.execute_query(user_posts_query, (user_id, user_id, user_id))])
        print(f"🚫 User has already interacted with {len(user_posts)} posts")
        
        # Get posts liked by similar users from combined interaction tables
        similar_user_ids = [user[0] for user in similar_users[:10]]  # Top 10 similar users
        
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
        
        recommended_posts = self.execute_query(similar_users_posts_query, tuple(similar_user_ids))
        
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

def test_collaborative_filtering():
    print("🧪 Testing Collaborative Filtering Component...")
    
    try:
        cf = CollaborativeFilteringTester()
        
        print("\n1️⃣ Building User-Item Matrix...")
        matrix = cf.build_user_item_matrix()
        if matrix is not None:
            print(f"📊 Matrix shape: {matrix.shape}")
            print(f"📈 Sample users in matrix: {list(matrix.index[:5])}")
            print(f"📈 Sample posts in matrix: {list(matrix.columns[:5])}")
        
        print("\n2️⃣ Calculating User Similarities...")
        similarity_df = cf.calculate_user_similarity()
        if similarity_df is not None:
            print("✅ Similarity matrix calculated successfully")
        
        print("\n3️⃣ Testing with User 1...")
        similar_users = cf.find_similar_users(1, 5)
        print(f"👥 Similar users to User 1:")
        for user_id, similarity in similar_users:
            print(f"   User {user_id}: {similarity:.3f} similarity")
        
        print("\n4️⃣ Getting Collaborative Recommendations...")
        recommendations = cf.recommend_posts_collaborative(1, 5)
        print(f"\n🎯 Collaborative Recommendations for User 1:")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. Post {rec['post_id']}: {rec['caption']}")
            print(f"   By: {rec['author_username']} | Score: {rec['popularity_score']:.2f}")
            print(f"   Location: {rec['location']}")
            print()
        
        print("✅ Collaborative Filtering test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Collaborative Filtering test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_collaborative_filtering()