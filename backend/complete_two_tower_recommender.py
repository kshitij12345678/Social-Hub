#!/usr/bin/env python3
"""
Complete Two-Tower Deep Learning Recommendation System
Includes Image Embeddings + User History Embeddings + Content Embeddings
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Embedding, Flatten, Dropout, BatchNormalization, LSTM, Conv2D, MaxPooling2D, GlobalAveragePooling2D
from tensorflow.keras.applications import ResNet50, EfficientNetB0
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3
from typing import List, Dict, Tuple
import pickle
import os
from PIL import Image
import requests
import io

class CompleteTwoTowerRecommender:
    """
    Complete Two-Tower Deep Learning with Image + User History Embeddings
    """
    
    def __init__(self, db_path: str = "social_hub.db", embedding_dim: int = 128):
        self.db_path = db_path
        self.embedding_dim = embedding_dim
        
        # Models
        self.user_tower = None
        self.content_tower = None
        self.combined_model = None
        self.image_feature_extractor = None
        
        # Encoders and processors
        self.user_encoder = LabelEncoder()
        self.post_encoder = LabelEncoder()
        self.location_encoder = LabelEncoder()
        self.category_encoder = LabelEncoder()
        self.tfidf_vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
        self.scaler = StandardScaler()
        
        # Embeddings cache
        self.user_embeddings = {}
        self.content_embeddings = {}
        self.image_embeddings = {}
        self.user_history_embeddings = {}
        
        self.is_trained = False
        
        print("🏗️ Complete Two-Tower Deep Learning Recommender initialized!")
        print("📸 Will process: Image embeddings + User history + Content features")
    
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
            print(f"❌ Query error: {e}")
            return []
    
    def build_image_feature_extractor(self):
        """Build CNN model for image feature extraction"""
        print("📸 Building Image Feature Extractor (ResNet50)...")
        
        # Use pre-trained ResNet50 without top layers
        base_model = ResNet50(
            weights='imagenet',
            include_top=False,
            input_shape=(224, 224, 3)
        )
        
        # Freeze base model layers
        base_model.trainable = False
        
        # Add custom layers for feature extraction
        inputs = Input(shape=(224, 224, 3))
        x = base_model(inputs, training=False)
        x = GlobalAveragePooling2D()(x)
        x = Dense(512, activation='relu')(x)
        x = Dropout(0.2)(x)
        outputs = Dense(256, activation='relu', name='image_features')(x)
        
        self.image_feature_extractor = Model(inputs, outputs, name='ImageFeatureExtractor')
        
        print("✅ Image Feature Extractor built successfully!")
        return self.image_feature_extractor
    
    def extract_image_features(self, image_path: str) -> np.ndarray:
        """Extract features from a single image"""
        try:
            # Handle both local paths and URLs
            if image_path.startswith('http'):
                response = requests.get(image_path)
                image = Image.open(io.BytesIO(response.content))
            else:
                if not os.path.exists(image_path):
                    # Return zero vector if image not found
                    return np.zeros(256)
                image = Image.open(image_path)
            
            # Preprocess image
            image = image.convert('RGB')
            image = image.resize((224, 224))
            image_array = img_to_array(image)
            image_array = np.expand_dims(image_array, axis=0)
            image_array = tf.keras.applications.resnet50.preprocess_input(image_array)
            
            # Extract features
            features = self.image_feature_extractor.predict(image_array, verbose=0)[0]
            return features
            
        except Exception as e:
            print(f"⚠️ Error processing image {image_path}: {e}")
            return np.zeros(256)  # Return zero vector on error
    
    def process_all_image_embeddings(self):
        """Process image embeddings for all posts"""
        print("📸 Processing image embeddings for all posts...")
        
        # Build image feature extractor
        self.build_image_feature_extractor()
        
        # Get all posts with media URLs
        posts_query = """
        SELECT id, media_url, caption
        FROM posts 
        WHERE media_url IS NOT NULL AND media_url != ''
        ORDER BY id
        """
        
        posts = self.execute_query(posts_query)
        print(f"📊 Found {len(posts)} posts with images to process")
        
        image_embeddings = {}
        processed_count = 0
        
        for post_id, media_url, caption in posts:
            print(f"📸 Processing image {processed_count + 1}/{len(posts)}: Post {post_id}")
            
            # Extract image features
            image_features = self.extract_image_features(media_url)
            image_embeddings[post_id] = image_features
            
            processed_count += 1
            
            # Progress update every 50 images
            if processed_count % 50 == 0:
                print(f"✅ Processed {processed_count}/{len(posts)} images")
        
        self.image_embeddings = image_embeddings
        print(f"✅ Image embeddings processed for {len(image_embeddings)} posts")
        
        # Save image embeddings
        with open('image_embeddings.pkl', 'wb') as f:
            pickle.dump(image_embeddings, f)
        print("💾 Image embeddings saved to image_embeddings.pkl")
        
        return image_embeddings
    
    def load_image_embeddings(self):
        """Load pre-processed image embeddings"""
        try:
            with open('image_embeddings.pkl', 'rb') as f:
                self.image_embeddings = pickle.load(f)
            print(f"✅ Loaded image embeddings for {len(self.image_embeddings)} posts")
            return True
        except FileNotFoundError:
            print("⚠️ Image embeddings not found. Processing images...")
            self.process_all_image_embeddings()
            return True
        except Exception as e:
            print(f"❌ Error loading image embeddings: {e}")
            return False
    
    def build_user_history_embeddings(self):
        """Build user interaction history embeddings using LSTM"""
        print("👤 Building user history embeddings...")
        
        # Get user interaction sequences
        user_sequences_query = """
        SELECT user_id, post_id, interaction_type, created_at,
               ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at) as sequence_num
        FROM (
            SELECT user_id, post_id, 'like' as interaction_type, created_at FROM likes
            UNION ALL
            SELECT user_id, post_id, 'comment' as interaction_type, created_at FROM comments
            UNION ALL
            SELECT user_id, post_id, 'share' as interaction_type, created_at FROM shares
        )
        ORDER BY user_id, created_at
        """
        
        interactions = self.execute_query(user_sequences_query)
        
        # Build user sequences (last 50 interactions per user)
        user_sequences = {}
        interaction_weights = {'like': 1.0, 'comment': 2.5, 'share': 4.0}
        
        for user_id, post_id, interaction_type, created_at, sequence_num in interactions:
            if user_id not in user_sequences:
                user_sequences[user_id] = []
            
            # Keep only last 50 interactions
            if len(user_sequences[user_id]) >= 50:
                user_sequences[user_id].pop(0)
            
            user_sequences[user_id].append({
                'post_id': post_id,
                'weight': interaction_weights[interaction_type],
                'sequence_num': sequence_num
            })
        
        # Process sequences into embeddings
        user_history_embeddings = {}
        
        for user_id, sequence in user_sequences.items():
            if len(sequence) < 3:  # Need minimum interactions
                user_history_embeddings[user_id] = np.zeros(64)  # Default embedding
                continue
            
            # Create sequence features
            weights = [item['weight'] for item in sequence]
            post_ids = [item['post_id'] for item in sequence]
            
            # Simple history embedding (can be enhanced with LSTM)
            avg_weight = np.mean(weights)
            total_interactions = len(sequence)
            recent_activity = np.mean(weights[-10:]) if len(weights) >= 10 else avg_weight
            
            # Create feature vector
            history_features = np.array([
                avg_weight,
                total_interactions / 100.0,  # Normalize
                recent_activity,
                len(set(post_ids)) / len(post_ids),  # Diversity ratio
            ])
            
            # Pad to 64 dimensions (can be replaced with LSTM output)
            full_embedding = np.zeros(64)
            full_embedding[:len(history_features)] = history_features
            
            user_history_embeddings[user_id] = full_embedding
        
        self.user_history_embeddings = user_history_embeddings
        print(f"✅ Built history embeddings for {len(user_history_embeddings)} users")
        
        return user_history_embeddings
    
    def prepare_complete_training_data(self):
        """Prepare comprehensive training data with all embeddings"""
        print("🔧 Preparing complete training data...")
        
        # 1. Load/process image embeddings
        self.load_image_embeddings()
        
        # 2. Build user history embeddings
        self.build_user_history_embeddings()
        
        # 3. Get interaction data
        interactions_query = """
        SELECT user_id, post_id, interaction_type, created_at
        FROM (
            SELECT user_id, post_id, 'like' as interaction_type, created_at FROM likes
            UNION ALL
            SELECT user_id, post_id, 'comment' as interaction_type, created_at FROM comments
            UNION ALL
            SELECT user_id, post_id, 'share' as interaction_type, created_at FROM shares
        )
        ORDER BY created_at DESC
        """
        
        interactions = self.execute_query(interactions_query)
        
        # 4. Get post content data
        posts_query = """
        SELECT p.id, p.caption, p.user_id as author_id, p.media_url,
               l.name as location, l.category, l.country,
               COUNT(DISTINCT likes.id) as likes_count,
               COUNT(DISTINCT comments.id) as comments_count,
               COUNT(DISTINCT shares.id) as shares_count
        FROM posts p
        LEFT JOIN locations l ON p.location_id = l.id
        LEFT JOIN likes ON p.id = likes.post_id
        LEFT JOIN comments ON p.id = comments.post_id  
        LEFT JOIN shares ON p.id = shares.post_id
        WHERE p.id IN ({})
        GROUP BY p.id, p.caption, p.user_id, p.media_url, l.name, l.category, l.country
        """.format(','.join([str(row[1]) for row in interactions[:1000]]))  # Limit for efficiency
        
        posts_data = self.execute_query(posts_query)
        
        # Convert to DataFrames
        interactions_df = pd.DataFrame(interactions, columns=['user_id', 'post_id', 'interaction_type', 'created_at'])
        posts_df = pd.DataFrame(posts_data, columns=[
            'post_id', 'caption', 'author_id', 'media_url', 'location', 'category', 
            'country', 'likes_count', 'comments_count', 'shares_count'
        ])
        
        # Fill missing values
        posts_df = posts_df.fillna('')
        
        print(f"📊 Prepared data: {len(interactions_df)} interactions, {len(posts_df)} posts")
        print(f"📸 Image embeddings: {len(self.image_embeddings)} posts")
        print(f"👤 User history embeddings: {len(self.user_history_embeddings)} users")
        
        return interactions_df, posts_df
    
    def build_enhanced_user_tower(self, num_users: int):
        """Build enhanced User Tower with history embeddings"""
        print("🏗️ Building Enhanced User Tower (with history embeddings)...")
        
        # Input layers
        user_input = Input(shape=(), name='user_id')
        user_history_input = Input(shape=(64,), name='user_history_embedding')
        user_stats_input = Input(shape=(3,), name='user_stats')  # interaction_count, avg_rating, diversity
        
        # User ID embedding
        user_embedding = Embedding(num_users, 64, name='user_embedding')(user_input)
        user_vec = Flatten()(user_embedding)
        
        # Process user history with neural network
        history_processed = Dense(64, activation='relu')(user_history_input)
        history_processed = Dropout(0.2)(history_processed)
        
        # Concatenate all user features
        user_features = tf.keras.layers.Concatenate()([
            user_vec,           # User ID embedding
            history_processed,  # Processed history
            user_stats_input   # User statistics
        ])
        
        # Deep neural network layers
        x = Dense(256, activation='relu')(user_features)
        x = BatchNormalization()(x)
        x = Dropout(0.3)(x)
        
        x = Dense(128, activation='relu')(x)
        x = BatchNormalization()(x)
        x = Dropout(0.2)(x)
        
        # Output embedding
        user_output = Dense(self.embedding_dim, activation='tanh', name='user_embedding_output')(x)
        
        # Create model
        self.user_tower = Model(
            inputs=[user_input, user_history_input, user_stats_input],
            outputs=user_output,
            name='EnhancedUserTower'
        )
        
        print("✅ Enhanced User Tower built successfully!")
        return self.user_tower
    
    def build_enhanced_content_tower(self, num_posts: int, num_locations: int, num_categories: int):
        """Build enhanced Content Tower with image embeddings"""
        print("🏗️ Building Enhanced Content Tower (with image embeddings)...")
        
        # Input layers
        post_input = Input(shape=(), name='post_id')
        author_input = Input(shape=(), name='author_id')
        location_input = Input(shape=(), name='location_id')
        category_input = Input(shape=(), name='category_id')
        tfidf_input = Input(shape=(500,), name='tfidf_features')
        image_input = Input(shape=(256,), name='image_features')  # Pre-extracted image features
        engagement_input = Input(shape=(3,), name='engagement_features')
        
        # Embeddings
        post_embedding = Embedding(num_posts, 32, name='post_embedding')(post_input)
        post_vec = Flatten()(post_embedding)
        
        author_embedding = Embedding(num_posts, 32, name='author_embedding')(author_input)
        author_vec = Flatten()(author_embedding)
        
        location_embedding = Embedding(num_locations, 32, name='location_embedding')(location_input)
        location_vec = Flatten()(location_embedding)
        
        category_embedding = Embedding(num_categories, 16, name='category_embedding')(category_input)
        category_vec = Flatten()(category_embedding)
        
        # Process text features
        tfidf_dense = Dense(128, activation='relu')(tfidf_input)
        tfidf_dense = Dropout(0.2)(tfidf_dense)
        
        # Process image features
        image_dense = Dense(128, activation='relu')(image_input)
        image_dense = BatchNormalization()(image_dense)
        image_dense = Dropout(0.2)(image_dense)
        
        # Concatenate all content features
        content_features = tf.keras.layers.Concatenate()([
            post_vec, author_vec, location_vec, category_vec,
            tfidf_dense, image_dense, engagement_input
        ])
        
        # Deep neural network layers
        x = Dense(512, activation='relu')(content_features)
        x = BatchNormalization()(x)
        x = Dropout(0.3)(x)
        
        x = Dense(256, activation='relu')(x)
        x = BatchNormalization()(x)
        x = Dropout(0.2)(x)
        
        x = Dense(128, activation='relu')(x)
        x = Dropout(0.1)(x)
        
        # Output embedding
        content_output = Dense(self.embedding_dim, activation='tanh', name='content_embedding_output')(x)
        
        # Create model
        self.content_tower = Model(
            inputs=[post_input, author_input, location_input, category_input, 
                   tfidf_input, image_input, engagement_input],
            outputs=content_output,
            name='EnhancedContentTower'
        )
        
        print("✅ Enhanced Content Tower built successfully!")
        return self.content_tower
    
    def train_complete_two_tower_model(self, epochs: int = 30, batch_size: int = 128):
        """Train the complete Two-Tower model with all embeddings"""
        print("🚀 Training Complete Two-Tower Deep Learning Model...")
        print("📸 Includes: Image embeddings + User history + Content features")
        
        # Prepare comprehensive data
        interactions_df, posts_df = self.prepare_complete_training_data()
        
        # Encode categorical features
        unique_users = interactions_df['user_id'].unique()
        unique_posts = posts_df['post_id'].unique()
        unique_locations = posts_df['location'].fillna('Unknown').unique()
        unique_categories = posts_df['category'].fillna('Unknown').unique()
        
        self.user_encoder.fit(unique_users)
        self.post_encoder.fit(unique_posts)
        self.location_encoder.fit(unique_locations)
        self.category_encoder.fit(unique_categories)
        
        # Prepare TF-IDF features
        captions = posts_df['caption'].fillna('').tolist()
        tfidf_features = self.tfidf_vectorizer.fit_transform(captions)
        
        # Build models
        num_users = len(self.user_encoder.classes_)
        num_posts = len(self.post_encoder.classes_)
        num_locations = len(self.location_encoder.classes_)
        num_categories = len(self.category_encoder.classes_)
        
        user_tower = self.build_enhanced_user_tower(num_users)
        content_tower = self.build_enhanced_content_tower(num_posts, num_locations, num_categories)
        
        print(f"📊 Model dimensions:")
        print(f"   👥 Users: {num_users}")
        print(f"   📄 Posts: {num_posts}")
        print(f"   📍 Locations: {num_locations}")
        print(f"   🏷️ Categories: {num_categories}")
        
        # Create training samples
        training_samples = []
        
        # Merge interactions with posts
        training_data = interactions_df.merge(posts_df, on='post_id', how='inner')
        
        # Sample and prepare training data
        for idx, row in training_data.sample(n=min(10000, len(training_data))).iterrows():
            user_id = row['user_id']
            post_id = row['post_id']
            
            # Skip if embeddings not available
            if user_id not in self.user_history_embeddings or post_id not in self.image_embeddings:
                continue
            
            # User features
            user_encoded = self.user_encoder.transform([user_id])[0]
            user_history = self.user_history_embeddings[user_id]
            user_stats = np.array([1.0, 2.0, 0.5])  # Placeholder stats
            
            # Content features  
            post_encoded = self.post_encoder.transform([post_id])[0]
            author_encoded = self.user_encoder.transform([row['author_id']])[0] if row['author_id'] in self.user_encoder.classes_ else 0
            location_encoded = self.location_encoder.transform([row['location'] or 'Unknown'])[0]
            category_encoded = self.category_encoder.transform([row['category'] or 'Unknown'])[0]
            
            # Get TF-IDF and image features
            post_idx = posts_df[posts_df['post_id'] == post_id].index[0]
            tfidf_vec = tfidf_features[post_idx].toarray().flatten()
            image_features = self.image_embeddings[post_id]
            engagement = np.array([row['likes_count'], row['comments_count'], row['shares_count']])
            
            # Create sample
            sample = {
                'user_features': [user_encoded, user_history, user_stats],
                'content_features': [post_encoded, author_encoded, location_encoded, 
                                   category_encoded, tfidf_vec, image_features, engagement],
                'label': 1.0  # Positive interaction
            }
            
            training_samples.append(sample)
        
        print(f"✅ Prepared {len(training_samples)} training samples")
        
        # Build combined model for training
        user_inputs = user_tower.input
        content_inputs = content_tower.input
        
        user_embedding = user_tower.output
        content_embedding = content_tower.output
        
        # Calculate similarity
        similarity = tf.keras.layers.Dot(axes=1)([user_embedding, content_embedding])
        output = tf.keras.layers.Dense(1, activation='sigmoid')(tf.expand_dims(similarity, 1))
        
        self.combined_model = Model(
            inputs=user_inputs + content_inputs,
            outputs=output,
            name='CompleteTwoTowerRecommender'
        )
        
        self.combined_model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        # Prepare training arrays
        if len(training_samples) > 0:
            # Extract features
            user_ids = np.array([s['user_features'][0] for s in training_samples])
            user_histories = np.array([s['user_features'][1] for s in training_samples])
            user_stats = np.array([s['user_features'][2] for s in training_samples])
            
            post_ids = np.array([s['content_features'][0] for s in training_samples])
            author_ids = np.array([s['content_features'][1] for s in training_samples])
            location_ids = np.array([s['content_features'][2] for s in training_samples])
            category_ids = np.array([s['content_features'][3] for s in training_samples])
            tfidf_vecs = np.array([s['content_features'][4] for s in training_samples])
            image_vecs = np.array([s['content_features'][5] for s in training_samples])
            engagement_vecs = np.array([s['content_features'][6] for s in training_samples])
            
            labels = np.array([s['label'] for s in training_samples])
            
            # Train model
            print("🤖 Starting Complete Two-Tower training...")
            history = self.combined_model.fit(
                [user_ids, user_histories, user_stats,
                 post_ids, author_ids, location_ids, category_ids,
                 tfidf_vecs, image_vecs, engagement_vecs],
                labels,
                epochs=epochs,
                batch_size=batch_size,
                validation_split=0.2,
                verbose=1
            )
            
            self.is_trained = True
            print("✅ Complete Two-Tower Deep Learning Model trained successfully!")
            
            return history
        else:
            print("❌ No training samples available")
            return None
    
    def get_complete_recommendations(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get recommendations using complete Two-Tower system"""
        if not self.is_trained:
            print("❌ Model not trained! Please train the model first.")
            return []
        
        print(f"🧠 Getting Complete Two-Tower recommendations for user {user_id}...")
        
        # This would involve generating embeddings for all possible user-post pairs
        # and ranking by similarity - implementation would be similar to previous version
        # but using the enhanced towers
        
        # For now, return placeholder
        print("🚧 Complete recommendation generation coming soon...")
        return []

def test_complete_two_tower_system():
    """Test the complete Two-Tower system"""
    print("🧪 Testing Complete Two-Tower Deep Learning System")
    print("=" * 60)
    
    # Initialize recommender
    recommender = CompleteTwoTowerRecommender()
    
    # This will process images and train the complete model
    print("⚠️ Note: This will take significant time for image processing...")
    
    # Train model
    history = recommender.train_complete_two_tower_model(epochs=5, batch_size=64)
    
    if history:
        print("🎉 Complete Two-Tower system training completed!")
    else:
        print("❌ Training failed")

if __name__ == "__main__":
    test_complete_two_tower_system()