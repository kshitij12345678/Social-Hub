#!/usr/bin/env python3
"""
Simplified Two-Tower Deep Learning Recommendation System
Focus on Text + User History embeddings (no heavy image processing for now)
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Embedding, Flatten, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3
from typing import List, Dict, Tuple
import pickle

class SimplifiedTwoTowerRecommender:
    """
    Simplified Two-Tower Implementation
    - User Tower: User history + interaction patterns
    - Content Tower: Text features + metadata + engagement
    """
    
    def __init__(self, db_path: str = "social_hub.db", embedding_dim: int = 128):
        self.db_path = db_path
        self.embedding_dim = embedding_dim
        
        # Models
        self.user_tower = None
        self.content_tower = None
        self.combined_model = None
        
        # Encoders
        self.user_encoder = LabelEncoder()
        self.post_encoder = LabelEncoder()
        self.location_encoder = LabelEncoder()
        self.category_encoder = LabelEncoder()
        self.tfidf_vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
        
        # Cache
        self.user_embeddings = {}
        self.content_embeddings = {}
        self.user_profiles = {}
        
        self.is_trained = False
        
        print("🏗️ Simplified Two-Tower Deep Learning Recommender initialized!")
    
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
            print(f"❌ Query error: {e}")
            return []
    
    def build_user_profiles(self):
        """Build detailed user profiles from interaction history"""
        print("👤 Building user interaction profiles...")
        
        user_profile_query = """
        WITH user_interactions AS (
            SELECT user_id, post_id, 'like' as type, 1.0 as weight FROM likes
            UNION ALL
            SELECT user_id, post_id, 'comment' as type, 2.5 as weight FROM comments
            UNION ALL
            SELECT user_id, post_id, 'share' as type, 4.0 as weight FROM shares
        ),
        user_post_details AS (
            SELECT ui.user_id, ui.post_id, ui.type, ui.weight,
                   l.category, l.name as location, l.country,
                   p.user_id as author_id
            FROM user_interactions ui
            JOIN posts p ON ui.post_id = p.id
            LEFT JOIN locations l ON p.location_id = l.id
        )
        SELECT 
            user_id,
            COUNT(*) as total_interactions,
            AVG(weight) as avg_interaction_weight,
            COUNT(DISTINCT category) as category_diversity,
            COUNT(DISTINCT location) as location_diversity,
            COUNT(DISTINCT country) as country_diversity,
            COUNT(DISTINCT author_id) as author_diversity,
            COUNT(CASE WHEN type = 'like' THEN 1 END) as likes_count,
            COUNT(CASE WHEN type = 'comment' THEN 1 END) as comments_count,
            COUNT(CASE WHEN type = 'share' THEN 1 END) as shares_count
        FROM user_post_details
        GROUP BY user_id
        HAVING total_interactions >= 3
        """
        
        user_profiles = self.execute_query(user_profile_query)
        
        profiles_dict = {}
        for row in user_profiles:
            user_id = row[0]
            profiles_dict[user_id] = {
                'total_interactions': row[1],
                'avg_interaction_weight': row[2],
                'category_diversity': row[3],
                'location_diversity': row[4],
                'country_diversity': row[5],
                'author_diversity': row[6],
                'likes_count': row[7] or 0,
                'comments_count': row[8] or 0,
                'shares_count': row[9] or 0
            }
        
        self.user_profiles = profiles_dict
        print(f"✅ Built profiles for {len(profiles_dict)} users")
        return profiles_dict
    
    def prepare_training_data(self):
        """Prepare training data with user profiles and content features"""
        print("🔧 Preparing Two-Tower training data...")
        
        # Build user profiles first
        self.build_user_profiles()
        
        # Get interactions
        interactions_query = """
        SELECT user_id, post_id, interaction_type, weight
        FROM (
            SELECT user_id, post_id, 'like' as interaction_type, 1.0 as weight FROM likes
            UNION ALL
            SELECT user_id, post_id, 'comment' as interaction_type, 2.5 as weight FROM comments
            UNION ALL
            SELECT user_id, post_id, 'share' as interaction_type, 4.0 as weight FROM shares
        )
        WHERE user_id IN ({})
        ORDER BY RANDOM()
        LIMIT 5000
        """.format(','.join(map(str, self.user_profiles.keys())))
        
        interactions = self.execute_query(interactions_query)
        
        # Get post content
        post_content_query = """
        SELECT p.id, p.caption, p.user_id as author_id,
               l.name as location, l.category, l.country,
               COUNT(DISTINCT likes.id) as likes_count,
               COUNT(DISTINCT comments.id) as comments_count,
               COUNT(DISTINCT shares.id) as shares_count
        FROM posts p
        LEFT JOIN locations l ON p.location_id = l.id
        LEFT JOIN likes ON p.id = likes.post_id
        LEFT JOIN comments ON p.id = comments.post_id
        LEFT JOIN shares ON p.id = shares.post_id
        WHERE p.caption IS NOT NULL AND p.caption != ''
        GROUP BY p.id, p.caption, p.user_id, l.name, l.category, l.country
        """
        
        posts = self.execute_query(post_content_query)
        
        # Convert to DataFrames
        interactions_df = pd.DataFrame(interactions, columns=['user_id', 'post_id', 'interaction_type', 'weight'])
        posts_df = pd.DataFrame(posts, columns=[
            'post_id', 'caption', 'author_id', 'location', 'category', 'country',
            'likes_count', 'comments_count', 'shares_count'
        ])
        
        posts_df = posts_df.fillna('Unknown')
        
        print(f"📊 Training data: {len(interactions_df)} interactions, {len(posts_df)} posts")
        return interactions_df, posts_df
    
    def build_user_tower(self, num_users: int):
        """Build User Tower with interaction history features"""
        print("🏗️ Building User Tower...")
        
        # Inputs
        user_id_input = Input(shape=(), name='user_id')
        user_profile_input = Input(shape=(10,), name='user_profile_features')  # 10 profile features
        
        # User embedding
        user_embedding = Embedding(num_users, 64)(user_id_input)
        user_vec = Flatten()(user_embedding)
        
        # Process profile features
        profile_dense = Dense(64, activation='relu')(user_profile_input)
        profile_dense = Dropout(0.2)(profile_dense)
        
        # Combine features
        combined = tf.keras.layers.Concatenate()([user_vec, profile_dense])
        
        # Deep layers
        x = Dense(256, activation='relu')(combined)
        x = BatchNormalization()(x)
        x = Dropout(0.3)(x)
        
        x = Dense(128, activation='relu')(x)
        x = Dropout(0.2)(x)
        
        # Output embedding
        output = Dense(self.embedding_dim, activation='tanh')(x)
        
        self.user_tower = Model(
            inputs=[user_id_input, user_profile_input],
            outputs=output,
            name='UserTower'
        )
        
        print("✅ User Tower built!")
        return self.user_tower
    
    def build_content_tower(self, num_posts: int, num_locations: int, num_categories: int, tfidf_dim: int = 500):
        """Build Content Tower with text and metadata features"""
        print("🏗️ Building Content Tower...")
        
        # Inputs
        post_id_input = Input(shape=(), name='post_id')
        location_input = Input(shape=(), name='location_id')
        category_input = Input(shape=(), name='category_id')
        tfidf_input = Input(shape=(tfidf_dim,), name='tfidf_features')
        engagement_input = Input(shape=(3,), name='engagement_features')
        
        # Embeddings
        post_embedding = Embedding(num_posts, 32)(post_id_input)
        post_vec = Flatten()(post_embedding)
        
        location_embedding = Embedding(num_locations, 32)(location_input)
        location_vec = Flatten()(location_embedding)
        
        category_embedding = Embedding(num_categories, 16)(category_input)
        category_vec = Flatten()(category_embedding)
        
        # Process TF-IDF
        tfidf_dense = Dense(128, activation='relu')(tfidf_input)
        tfidf_dense = Dropout(0.2)(tfidf_dense)
        
        # Combine all features
        combined = tf.keras.layers.Concatenate()([
            post_vec, location_vec, category_vec, tfidf_dense, engagement_input
        ])
        
        # Deep layers
        x = Dense(256, activation='relu')(combined)
        x = BatchNormalization()(x)
        x = Dropout(0.3)(x)
        
        x = Dense(128, activation='relu')(x)
        x = Dropout(0.2)(x)
        
        # Output embedding
        output = Dense(self.embedding_dim, activation='tanh')(x)
        
        self.content_tower = Model(
            inputs=[post_id_input, location_input, category_input, tfidf_input, engagement_input],
            outputs=output,
            name='ContentTower'
        )
        
        print("✅ Content Tower built!")
        return self.content_tower
    
    def train_simplified_two_tower(self, epochs: int = 20, batch_size: int = 128):
        """Train the simplified Two-Tower model"""
        print("🚀 Training Simplified Two-Tower Model...")
        
        # Prepare data
        interactions_df, posts_df = self.prepare_training_data()
        
        # Encode features
        unique_users = list(self.user_profiles.keys())
        unique_posts = posts_df['post_id'].unique()
        unique_locations = posts_df['location'].unique()
        unique_categories = posts_df['category'].unique()
        
        self.user_encoder.fit(unique_users)
        self.post_encoder.fit(unique_posts)
        self.location_encoder.fit(unique_locations)
        self.category_encoder.fit(unique_categories)
        
        # TF-IDF on captions
        captions = posts_df['caption'].fillna('').tolist()
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(captions)
        tfidf_dim = tfidf_matrix.shape[1]
        
        # Build towers
        num_users = len(unique_users)
        num_posts = len(unique_posts)
        num_locations = len(unique_locations)
        num_categories = len(unique_categories)
        
        user_tower = self.build_user_tower(num_users)
        content_tower = self.build_content_tower(num_posts, num_locations, num_categories, tfidf_dim)
        
        print(f"📊 Model dimensions: {num_users} users, {num_posts} posts")
        
        # Prepare training samples
        training_samples = []
        
        # Merge interactions with posts
        merged_data = interactions_df.merge(posts_df, on='post_id', how='inner')
        
        for idx, row in merged_data.sample(n=min(3000, len(merged_data))).iterrows():
            user_id = row['user_id']
            post_id = row['post_id']
            
            if user_id not in self.user_profiles:
                continue
            
            # User features
            user_encoded = self.user_encoder.transform([user_id])[0]
            profile = self.user_profiles[user_id]
            user_profile_vec = np.array([
                profile['total_interactions'] / 100.0,  # Normalize
                profile['avg_interaction_weight'] / 4.0,
                profile['category_diversity'] / 10.0,
                profile['location_diversity'] / 20.0,
                profile['country_diversity'] / 5.0,
                profile['author_diversity'] / 50.0,
                profile['likes_count'] / 100.0,
                profile['comments_count'] / 50.0,
                profile['shares_count'] / 20.0,
                1.0  # Bias term
            ])
            
            # Content features
            post_encoded = self.post_encoder.transform([post_id])[0]
            location_encoded = self.location_encoder.transform([row['location']])[0]
            category_encoded = self.category_encoder.transform([row['category']])[0]
            
            # Get TF-IDF for this post
            post_idx = posts_df[posts_df['post_id'] == post_id].index[0]
            tfidf_vec = tfidf_matrix[post_idx].toarray().flatten()
            
            engagement_vec = np.array([
                row['likes_count'], row['comments_count'], row['shares_count']
            ])
            
            training_samples.append({
                'user_features': [user_encoded, user_profile_vec],
                'content_features': [post_encoded, location_encoded, category_encoded, tfidf_vec, engagement_vec],
                'label': 1.0  # Positive interaction
            })
        
        print(f"✅ Prepared {len(training_samples)} training samples")
        
        if len(training_samples) == 0:
            print("❌ No training samples available")
            return None
        
        # Build combined model
        user_inputs = user_tower.input
        content_inputs = content_tower.input
        
        user_emb = user_tower.output
        content_emb = content_tower.output
        
        # Calculate dot product similarity
        similarity = tf.keras.layers.Dot(axes=1)([user_emb, content_emb])
        
        # Reshape for dense layer
        similarity_reshaped = tf.keras.layers.Reshape((1,))(similarity)
        output = tf.keras.layers.Dense(1, activation='sigmoid')(similarity_reshaped)
        
        self.combined_model = Model(
            inputs=user_inputs + content_inputs,
            outputs=output,
            name='SimplifiedTwoTower'
        )
        
        self.combined_model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        # Prepare arrays
        user_ids = np.array([s['user_features'][0] for s in training_samples])
        user_profiles = np.array([s['user_features'][1] for s in training_samples])
        
        post_ids = np.array([s['content_features'][0] for s in training_samples])
        location_ids = np.array([s['content_features'][1] for s in training_samples])
        category_ids = np.array([s['content_features'][2] for s in training_samples])
        tfidf_vecs = np.array([s['content_features'][3] for s in training_samples])
        engagement_vecs = np.array([s['content_features'][4] for s in training_samples])
        
        labels = np.array([s['label'] for s in training_samples])
        
        # Train
        print("🤖 Starting training...")
        history = self.combined_model.fit(
            [user_ids, user_profiles, post_ids, location_ids, category_ids, tfidf_vecs, engagement_vecs],
            labels,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.2,
            verbose=1
        )
        
        # Generate embeddings for inference
        self.generate_all_embeddings(training_samples, posts_df, tfidf_matrix)
        
        self.is_trained = True
        print("✅ Simplified Two-Tower model trained successfully!")
        
        return history
    
    def generate_all_embeddings(self, training_samples, posts_df, tfidf_matrix):
        """Generate embeddings for all users and posts"""
        print("🧠 Generating embeddings for inference...")
        
        # User embeddings
        user_embeddings = {}
        processed_users = set()
        
        for sample in training_samples:
            user_id_encoded = sample['user_features'][0]
            user_profile = sample['user_features'][1]
            
            if user_id_encoded in processed_users:
                continue
            
            embedding = self.user_tower.predict([
                np.array([user_id_encoded]),
                np.array([user_profile])
            ], verbose=0)[0]
            
            # Map back to original user_id
            original_user_id = self.user_encoder.inverse_transform([user_id_encoded])[0]
            user_embeddings[original_user_id] = embedding
            processed_users.add(user_id_encoded)
        
        # Content embeddings
        content_embeddings = {}
        
        for idx, row in posts_df.iterrows():
            post_id = row['post_id']
            
            try:
                post_encoded = self.post_encoder.transform([post_id])[0]
                location_encoded = self.location_encoder.transform([row['location']])[0]
                category_encoded = self.category_encoder.transform([row['category']])[0]
                tfidf_vec = tfidf_matrix[idx].toarray().flatten()
                engagement_vec = np.array([row['likes_count'], row['comments_count'], row['shares_count']])
                
                embedding = self.content_tower.predict([
                    np.array([post_encoded]),
                    np.array([location_encoded]),
                    np.array([category_encoded]),
                    np.array([tfidf_vec]),
                    np.array([engagement_vec])
                ], verbose=0)[0]
                
                content_embeddings[post_id] = embedding
                
            except Exception as e:
                continue
        
        self.user_embeddings = user_embeddings
        self.content_embeddings = content_embeddings
        
        print(f"✅ Generated embeddings: {len(user_embeddings)} users, {len(content_embeddings)} posts")
    
    def get_two_tower_recommendations(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get recommendations using Two-Tower embeddings"""
        if not self.is_trained or user_id not in self.user_embeddings:
            print(f"❌ User {user_id} not available for Two-Tower recommendations")
            return []
        
        print(f"🧠 Getting Two-Tower recommendations for user {user_id}...")
        
        user_embedding = self.user_embeddings[user_id]
        
        # Calculate similarities
        similarities = []
        for post_id, content_embedding in self.content_embeddings.items():
            similarity = cosine_similarity([user_embedding], [content_embedding])[0][0]
            similarities.append((post_id, similarity))
        
        # Sort and get top recommendations
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_recommendations = similarities[:limit]
        
        # Convert to recommendation format
        recommendations = []
        for post_id, similarity in top_recommendations:
            # Get post details
            post_query = """
            SELECT p.id, p.caption, p.user_id, u.full_name,
                   l.name as location, p.media_url, p.created_at,
                   COUNT(DISTINCT likes.id) as likes_count
            FROM posts p
            LEFT JOIN users u ON p.user_id = u.id
            LEFT JOIN locations l ON p.location_id = l.id
            LEFT JOIN likes ON p.id = likes.post_id
            WHERE p.id = ?
            GROUP BY p.id
            """
            
            post_data = self.execute_query(post_query, (post_id,))
            
            if post_data:
                row = post_data[0]
                recommendations.append({
                    'id': row[0],
                    'caption': row[1],
                    'user_id': row[2],
                    'author_name': row[3],
                    'location': row[4],
                    'media_url': row[5],
                    'created_at': row[6],
                    'likes_count': row[7],
                    'ai_confidence': similarity,
                    'algorithm': 'two_tower_deep_learning',
                    'recommendation_reason': f'Deep learning similarity: {similarity:.4f}'
                })
        
        print(f"✅ Generated {len(recommendations)} Two-Tower recommendations")
        return recommendations

# Test function
def test_simplified_two_tower():
    """Test the simplified Two-Tower system"""
    print("🧪 Testing Simplified Two-Tower Deep Learning System")
    print("=" * 60)
    
    recommender = SimplifiedTwoTowerRecommender()
    
    # Train
    history = recommender.train_simplified_two_tower(epochs=15, batch_size=64)
    
    if history:
        # Test recommendations
        test_users = list(recommender.user_embeddings.keys())[:3]
        
        for user_id in test_users:
            print(f"\n🎯 Two-Tower recommendations for user {user_id}:")
            recommendations = recommender.get_two_tower_recommendations(user_id, limit=5)
            
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec['author_name']} - {rec['location']} "
                      f"[Similarity: {rec['ai_confidence']:.4f}]")
    
    print("\n🎉 Simplified Two-Tower test completed!")

if __name__ == "__main__":
    test_simplified_two_tower()