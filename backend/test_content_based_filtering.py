#!/usr/bin/env python3
"""
Test Content-Based Filtering Component Separately
"""

import sys
import os
sys.path.append('/home/kshitij/Downloads/Social Hub/Social-Hub/backend')

import sqlite3
from typing import List, Dict, Tuple
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

class ContentBasedFilteringTester:
    """Standalone Content-Based Filtering for testing"""
    
    def __init__(self, db_path: str = "social_hub.db"):
        self.db_path = db_path
        self.tfidf_vectorizer = None
        self.content_features_matrix = None
        self.posts_df = None
        self.content_similarity_matrix = None
    
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
    
    def preprocess_text(self, text):
        """Clean and preprocess text for TF-IDF"""
        if not text:
            return ""
        
        # Remove emojis and special characters, keep basic words
        text = re.sub(r'[^\w\s]', ' ', text)
        # Convert to lowercase
        text = text.lower()
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def build_content_features(self):
        """Build content feature matrix using post captions, locations, and user preferences"""
        print("🔄 Building content feature matrix...")
        
        # Get all posts with their metadata (updated for current schema)
        posts_query = """
        SELECT 
            p.id,
            p.caption,
            p.user_id,
            p.media_type as post_type,
            p.travel_date,
            l.name as location_name,
            l.country,
            l.continent,
            l.category as location_category,
            u.travel_style,
            u.location as user_location
        FROM posts p
        LEFT JOIN locations l ON p.location_id = l.id
        LEFT JOIN users u ON p.user_id = u.id
        """
        
        posts_data = self.execute_query(posts_query)
        
        if not posts_data:
            print("❌ No posts found!")
            return None
        
        # Convert to DataFrame
        columns = ['post_id', 'caption', 'user_id', 'post_type', 'travel_date', 
                  'location_name', 'country', 'continent', 'location_category', 
                  'travel_style', 'user_location']
        
        self.posts_df = pd.DataFrame(posts_data, columns=columns)
        
        print(f"📊 Found {len(self.posts_df)} posts for content analysis")
        
        # Create combined text features for each post
        content_features = []
        
        for _, post in self.posts_df.iterrows():
            # Combine different text features
            feature_text = []
            
            # Add caption (main content)
            if post['caption']:
                feature_text.append(self.preprocess_text(post['caption']))
            
            # Add location information (heavily weighted for better location matching)
            if post['location_name']:
                location_text = post['location_name'].lower()
                feature_text.extend([location_text] * 3)  # Weight location 3x
            
            if post['country']:
                country_text = post['country'].lower()
                feature_text.extend([country_text] * 2)  # Weight country 2x
            
            if post['continent']:
                continent_text = post['continent'].lower()
                feature_text.append(continent_text)
            
            if post['location_category']:
                category_text = post['location_category'].lower()
                feature_text.extend([category_text] * 2)  # Weight category 2x
            
            # Add travel style
            if post['travel_style']:
                feature_text.append(post['travel_style'].lower())
            
            # Add post type
            if post['post_type']:
                feature_text.append(post['post_type'].lower())
            
            # Join all features
            combined_text = ' '.join(feature_text)
            content_features.append(combined_text)
        
        # Create TF-IDF matrix
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=500,  # Reduced for faster processing
            stop_words='english',
            ngram_range=(1, 2),  # Include both unigrams and bigrams
            min_df=2,  # Ignore terms that appear in less than 2 documents
            max_df=0.8  # Ignore terms that appear in more than 80% of documents
        )
        
        self.content_features_matrix = self.tfidf_vectorizer.fit_transform(content_features)
        
        print(f"✅ Content features matrix created: {self.content_features_matrix.shape}")
        print(f"✅ TF-IDF vocabulary size: {len(self.tfidf_vectorizer.vocabulary_)}")
        
        # Show top features
        feature_names = self.tfidf_vectorizer.get_feature_names_out()
        print(f"📝 Sample features: {list(feature_names[:10])}")
        
        return self.content_features_matrix
    
    def calculate_content_similarity(self):
        """Calculate cosine similarity between posts based on content"""
        if self.content_features_matrix is None:
            self.build_content_features()
            
        if self.content_features_matrix is None:
            return None
        
        print("🔄 Calculating content similarity matrix...")
        
        # Calculate cosine similarity
        self.content_similarity_matrix = cosine_similarity(self.content_features_matrix)
        
        print("✅ Content similarity matrix calculated")
        return self.content_similarity_matrix
    
    def find_similar_posts(self, post_id: int, n_similar: int = 10) -> List[Tuple[int, float]]:
        """Find most similar posts to the given post"""
        if self.content_similarity_matrix is None:
            self.calculate_content_similarity()
        
        # Find the index of the post in our DataFrame
        post_indices = self.posts_df[self.posts_df['post_id'] == post_id].index
        
        if len(post_indices) == 0:
            print(f"❌ Post {post_id} not found")
            return []
        
        post_idx = post_indices[0]
        
        # Get similarity scores for this post
        similarity_scores = self.content_similarity_matrix[post_idx]
        
        # Get indices of most similar posts (excluding the post itself)
        similar_indices = np.argsort(similarity_scores)[::-1][1:n_similar+1]
        
        # Return post IDs and similarity scores
        similar_posts = []
        for idx in similar_indices:
            similar_post_id = self.posts_df.iloc[idx]['post_id']
            similarity_score = similarity_scores[idx]
            similar_posts.append((int(similar_post_id), float(similarity_score)))
        
        return similar_posts
    
    def recommend_posts_content_based(self, user_id: int, n_recommendations: int = 10) -> List[Dict]:
        """Recommend posts based on content similarity to user's interaction history"""
        print(f"🔍 Finding content-based recommendations for user {user_id}...")
        
        if self.posts_df is None:
            self.build_content_features()
        
        # First validate user exists
        user_exists = self.execute_query("SELECT COUNT(*) FROM users WHERE id = ?", (user_id,))[0][0]
        
        if user_exists == 0:
            print(f"❌ User {user_id} does not exist")
            return []
        
        # Get posts the user has interacted with
        user_interactions_query = """
        SELECT DISTINCT interactions.post_id, interactions.interaction_type,
               p.caption, l.name as location_name
        FROM (
            SELECT post_id, 'like' as interaction_type, created_at FROM likes WHERE user_id = ?
            UNION ALL
            SELECT post_id, 'comment' as interaction_type, created_at FROM comments WHERE user_id = ?
            UNION ALL
            SELECT post_id, 'share' as interaction_type, created_at FROM shares WHERE user_id = ?
        ) interactions
        JOIN posts p ON interactions.post_id = p.id
        LEFT JOIN locations l ON p.location_id = l.id  
        ORDER BY interactions.created_at DESC
        """
        
        user_interactions = self.execute_query(user_interactions_query, (user_id, user_id, user_id))
        
        if not user_interactions:
            print(f"❌ No interactions found for user {user_id}")
            return []
        
        print(f"📊 User has {len(user_interactions)} interactions to analyze")
        
        # Get posts user has already seen
        seen_posts = set([interaction[0] for interaction in user_interactions])
        
        # Find similar posts for each interacted post
        all_similar_posts = {}
        
        for post_id, interaction_type, caption, location in user_interactions[:5]:  # Analyze top 5 recent interactions
            print(f"🔍 Analyzing similar posts to: Post {post_id} ({interaction_type})")
            
            similar_posts = self.find_similar_posts(post_id, 5)
            
            # Weight based on interaction type
            interaction_weights = {
                'like': 1.0,
                'comment': 2.0,
                'share': 3.0
            }
            weight = interaction_weights.get(interaction_type, 1.0)
            
            for similar_post_id, similarity_score in similar_posts:
                if similar_post_id not in seen_posts:
                    weighted_score = similarity_score * weight
                    if similar_post_id in all_similar_posts:
                        all_similar_posts[similar_post_id] += weighted_score
                    else:
                        all_similar_posts[similar_post_id] = weighted_score
        
        # Sort by aggregated similarity score
        recommended_post_ids = sorted(all_similar_posts.items(), key=lambda x: x[1], reverse=True)
        
        # Get post details for recommendations
        recommendations = []
        for post_id, similarity_score in recommended_post_ids[:n_recommendations]:
            post_details_query = """
            SELECT p.id, p.caption, p.user_id, u.full_name, l.name as location
            FROM posts p
            JOIN users u ON p.user_id = u.id
            LEFT JOIN locations l ON p.location_id = l.id
            WHERE p.id = ?
            """
            
            post_details = self.execute_query(post_details_query, (post_id,))
            
            if post_details:
                pid, caption, author_id, author_name, location = post_details[0]
                recommendations.append({
                    'post_id': pid,
                    'caption': caption[:100] + "..." if caption and len(caption) > 100 else caption,
                    'author_id': author_id,
                    'author_username': author_name,
                    'location': location,
                    'popularity_score': similarity_score,
                    'recommendation_reason': f'Similar to your liked content (score: {similarity_score:.3f})',
                    'algorithm': 'content_based_filtering'
                })
        
        print(f"✅ Found {len(recommendations)} content-based recommendations")
        return recommendations

def test_content_based_filtering():
    print("🧪 Testing Content-Based Filtering Component...")
    
    try:
        cbf = ContentBasedFilteringTester()
        
        print("\n1️⃣ Building Content Features...")
        matrix = cbf.build_content_features()
        if matrix is not None:
            print(f"📊 Content matrix shape: {matrix.shape}")
        
        print("\n2️⃣ Calculating Content Similarities...")
        similarity_matrix = cbf.calculate_content_similarity()
        if similarity_matrix is not None:
            print(f"✅ Content similarity matrix shape: {similarity_matrix.shape}")
        
        print("\n3️⃣ Testing Similar Posts for Post 100...")
        similar_posts = cbf.find_similar_posts(100, 5)
        print(f"🔗 Similar posts to Post 100:")
        for post_id, similarity in similar_posts:
            print(f"   Post {post_id}: {similarity:.3f} similarity")
        
        print("\n4️⃣ Getting Content-Based Recommendations...")
        recommendations = cbf.recommend_posts_content_based(1, 5)
        print(f"\n🎯 Content-Based Recommendations for User 1:")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. Post {rec['post_id']}: {rec['caption']}")
            print(f"   By: {rec['author_username']} | Score: {rec['popularity_score']:.3f}")
            print(f"   Location: {rec['location']}")
            print(f"   Reason: {rec['recommendation_reason']}")
            print()
        
        print("✅ Content-Based Filtering test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Content-Based Filtering test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_content_based_filtering()