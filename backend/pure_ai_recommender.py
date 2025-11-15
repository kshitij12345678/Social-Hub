"""
Pure AI Matrix Factorization Recommender
100% Machine Learning - No Statistical Methods
Uses only trained AI model for recommendations
"""

import numpy as np
import sqlite3
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import pickle
import os
from datetime import datetime
import time

# Real AI/ML imports
from sklearn.decomposition import NMF, TruncatedSVD
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from scipy.sparse import csr_matrix
import pandas as pd

class PureAIRecommender:
    """
    Pure AI Recommender - 100% Machine Learning
    No statistical methods, only trained AI model predictions
    """
    
    def __init__(self, db_path: str = "social_hub.db"):
        self.db_path = db_path
        
        # AI Model Components
        self.ai_model = None              # Matrix Factorization AI model
        self.user_item_matrix = None      # Training data matrix
        self.user_factors = None          # AI-learned user representations
        self.item_factors = None          # AI-learned post representations
        self.user_id_to_index = {}        # Mapping for AI model
        self.index_to_user_id = {}
        self.post_id_to_index = {}
        self.index_to_post_id = {}
        
        # AI Model Status
        self.ai_trained = False
        self.model_path = "pure_ai_model.pkl"
        self.last_training_time = None
        
        # AI Hyperparameters
        self.n_factors = 50               # Latent factors for AI to learn
        self.ai_regularization = 0.01     # Lower regularization for better learning
        self.ai_max_iterations = 500      # More iterations for better convergence
        
        print("🤖 Pure AI Matrix Factorization Recommender initialized!")
        print("🧠 100% Machine Learning - No statistical methods!")
    
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
    
    def create_user_item_interaction_matrix(self) -> Tuple[np.ndarray, Dict, Dict]:
        """
        Convert database interactions into AI training matrix
        """
        print("🔍 Creating user-item interaction matrix for AI training...")
        
        # Get all user interactions with enhanced weighting
        interactions_query = """
        SELECT user_id, post_id, interaction_type, created_at FROM (
            SELECT user_id, post_id, 'like' as interaction_type, created_at FROM likes
            UNION ALL
            SELECT user_id, post_id, 'comment' as interaction_type, created_at FROM comments
            UNION ALL
            SELECT user_id, post_id, 'share' as interaction_type, created_at FROM shares
        ) interactions
        ORDER BY created_at DESC
        """
        
        interactions = self.execute_query(interactions_query)
        
        if not interactions:
            print("❌ No interactions found for AI training")
            return None, {}, {}
        
        print(f"📊 Found {len(interactions)} total interactions for AI training")
        
        # Create mappings
        unique_users = sorted(set([row[0] for row in interactions]))
        unique_posts = sorted(set([row[1] for row in interactions]))
        
        # Filter to users with at least 2 interactions for better AI training
        user_interaction_counts = defaultdict(int)
        for user_id, post_id, interaction_type, created_at in interactions:
            user_interaction_counts[user_id] += 1
        
        # Keep users with at least 2 interactions
        active_users = [user_id for user_id, count in user_interaction_counts.items() if count >= 2]
        
        print(f"👥 Filtering to {len(active_users)} active users (2+ interactions)")
        
        # Create bidirectional mappings for AI model
        self.user_id_to_index = {user_id: idx for idx, user_id in enumerate(active_users)}
        self.index_to_user_id = {idx: user_id for user_id, idx in self.user_id_to_index.items()}
        self.post_id_to_index = {post_id: idx for idx, post_id in enumerate(unique_posts)}
        self.index_to_post_id = {idx: post_id for post_id, idx in self.post_id_to_index.items()}
        
        print(f"🤖 AI will train on {len(active_users)} users and {len(unique_posts)} posts")
        
        # Create interaction matrix for AI (users x posts)
        matrix = np.zeros((len(active_users), len(unique_posts)))
        
        # Enhanced interaction weights for better AI learning
        interaction_weights = {'like': 1.0, 'comment': 2.5, 'share': 4.0}
        
        for user_id, post_id, interaction_type, created_at in interactions:
            if user_id in self.user_id_to_index:  # Only active users
                user_idx = self.user_id_to_index[user_id]
                post_idx = self.post_id_to_index[post_id]
                weight = interaction_weights.get(interaction_type, 1.0)
                
                # Add weight (multiple interactions increase strength)
                matrix[user_idx, post_idx] += weight
        
        # Normalize ratings to 0-5 scale for better AI training
        max_rating = np.max(matrix)
        if max_rating > 0:
            matrix = (matrix / max_rating) * 5.0
        
        # Matrix statistics
        total_possible = len(active_users) * len(unique_posts)
        actual_interactions = np.count_nonzero(matrix)
        sparsity = 1 - (actual_interactions / total_possible)
        
        print(f"📈 AI Training Matrix: {matrix.shape[0]}x{matrix.shape[1]}")
        print(f"🔍 Matrix sparsity: {sparsity:.3f} ({sparsity*100:.1f}% empty)")
        print(f"📊 Rating range: {np.min(matrix):.2f} to {np.max(matrix):.2f}")
        
        return matrix, self.user_id_to_index, self.post_id_to_index
    
    def train_pure_ai_model(self, retrain: bool = False) -> Dict:
        """
        Train PURE AI model using Matrix Factorization
        100% Machine Learning - No statistical methods
        """
        if self.ai_trained and not retrain:
            print("✅ Pure AI model already trained. Use retrain=True to retrain.")
            return {"status": "already_trained"}
        
        print("🚀 Training PURE AI Matrix Factorization Model...")
        print("🤖 No statistical methods - 100% Machine Learning!")
        start_time = time.time()
        
        # Step 1: Create training data
        self.user_item_matrix, user_mapping, post_mapping = self.create_user_item_interaction_matrix()
        
        if self.user_item_matrix is None:
            return {"status": "error", "message": "No training data available"}
        
        # Step 2: Initialize AI model with optimized parameters
        print(f"🧠 Initializing Pure AI model with {self.n_factors} latent factors...")
        self.ai_model = NMF(
            n_components=self.n_factors,         # AI learns 50 hidden patterns
            init='nndsvda',                      # Advanced initialization for better convergence
            random_state=42,                     # Reproducible results
            alpha_W=self.ai_regularization,      # Regularization for user factors
            alpha_H=self.ai_regularization,      # Regularization for item factors
            l1_ratio=0.0,                       # Pure L2 regularization for smooth factors
            max_iter=self.ai_max_iterations,     # More iterations for better learning
            verbose=True                        # Show detailed training progress
        )
        
        # Step 3: Train AI model (REAL MACHINE LEARNING)
        print("🤖 Pure AI is learning complex user behavior patterns...")
        try:
            # This is where the AI actually learns!
            self.user_factors = self.ai_model.fit_transform(self.user_item_matrix)
            self.item_factors = self.ai_model.components_
            
            training_time = time.time() - start_time
            self.last_training_time = datetime.now()
            self.ai_trained = True
            
            print(f"✅ Pure AI training completed in {training_time:.2f} seconds!")
            print(f"🧠 AI learned {self.user_factors.shape[1]} user preference factors")
            print(f"📚 AI learned {self.item_factors.shape[1]} post characteristic factors")
            print(f"🔄 AI converged in {self.ai_model.n_iter_} iterations")
            
            # Step 4: Evaluate AI model quality
            training_metrics = self._evaluate_pure_ai_model()
            
            # Step 5: Save AI model
            self._save_pure_ai_model()
            
            return {
                "status": "success",
                "training_time": training_time,
                "user_factors_shape": self.user_factors.shape,
                "item_factors_shape": self.item_factors.shape,
                "convergence_iterations": self.ai_model.n_iter_,
                "metrics": training_metrics
            }
            
        except Exception as e:
            print(f"❌ Pure AI training failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def _evaluate_pure_ai_model(self) -> Dict:
        """
        Evaluate Pure AI model quality
        """
        print("📊 Evaluating Pure AI model quality...")
        
        # Reconstruct original matrix using AI-learned factors
        reconstructed_matrix = np.dot(self.user_factors, self.item_factors)
        
        # Calculate reconstruction error for non-zero entries only
        mask = self.user_item_matrix > 0
        if np.sum(mask) > 0:
            rmse = np.sqrt(mean_squared_error(
                self.user_item_matrix[mask],
                reconstructed_matrix[mask]
            ))
            
            # Calculate explained variance
            original_variance = np.var(self.user_item_matrix[mask])
            residual_variance = np.var(self.user_item_matrix[mask] - reconstructed_matrix[mask])
            explained_variance = max(0, 1 - (residual_variance / original_variance)) if original_variance > 0 else 0
        else:
            rmse = float('inf')
            explained_variance = 0
        
        # Analyze learned factors
        factor_analysis = self._analyze_pure_ai_factors()
        
        metrics = {
            "reconstruction_rmse": float(rmse),
            "explained_variance": float(explained_variance),
            "convergence_iterations": self.ai_model.n_iter_,
            "factor_analysis": factor_analysis,
            "training_matrix_sparsity": 1 - (np.count_nonzero(self.user_item_matrix) / self.user_item_matrix.size)
        }
        
        print(f"🎯 Pure AI Model Quality Metrics:")
        print(f"   • Reconstruction RMSE: {rmse:.4f}")
        print(f"   • Explained Variance: {explained_variance:.4f}")
        print(f"   • AI Convergence: {self.ai_model.n_iter_} iterations")
        
        # Quality assessment
        if rmse < 1.0 and explained_variance > 0.3:
            print("✅ Pure AI model quality: EXCELLENT")
        elif rmse < 1.5 and explained_variance > 0.1:
            print("✅ Pure AI model quality: GOOD")
        else:
            print("⚠️ Pure AI model quality: FAIR - AI is learning basic patterns")
        
        return metrics
    
    def _analyze_pure_ai_factors(self) -> List[Dict]:
        """
        Analyze what patterns the Pure AI learned
        """
        print("🔍 Analyzing Pure AI learned patterns...")
        
        factor_analysis = []
        
        # Analyze top factors
        for factor_idx in range(min(10, self.n_factors)):  # Top 10 factors
            # Find posts that score highest on this AI factor
            factor_scores = self.item_factors[factor_idx, :]
            top_post_indices = np.argsort(factor_scores)[-20:]  # Top 20 posts for this factor
            
            # Get details of these posts
            locations = []
            categories = []
            countries = []
            
            for post_idx in top_post_indices:
                post_id = self.index_to_post_id[post_idx]
                
                # Get post details
                post_details = self.execute_query("""
                    SELECT p.caption, l.name as location, l.category, l.country
                    FROM posts p
                    LEFT JOIN locations l ON p.location_id = l.id
                    WHERE p.id = ?
                """, (post_id,))
                
                if post_details:
                    caption, location, category, country = post_details[0]
                    
                    if location:
                        locations.append(location)
                    if category:
                        categories.append(category)
                    if country:
                        countries.append(country)
            
            # Find AI-discovered dominant themes
            most_common_location = max(set(locations), key=locations.count) if locations else "Mixed"
            most_common_category = max(set(categories), key=categories.count) if categories else "Mixed"
            most_common_country = max(set(countries), key=countries.count) if countries else "Mixed"
            
            ai_interpretation = f"AI Factor {factor_idx}: {most_common_category} in {most_common_location}, {most_common_country}"
            
            factor_analysis.append({
                'ai_factor_id': factor_idx,
                'ai_discovered_location': most_common_location,
                'ai_discovered_category': most_common_category,
                'ai_discovered_country': most_common_country,
                'ai_interpretation': ai_interpretation,
                'factor_strength': float(np.mean(factor_scores))
            })
            
            print(f"🧠 {ai_interpretation}")
        
        return factor_analysis
    
    def get_pure_ai_recommendations(self, user_id: int, limit: int = 10) -> List[Dict]:
        """
        Get 100% Pure AI recommendations - No statistical methods
        """
        print(f"🤖 Getting PURE AI recommendations for user {user_id}...")
        
        if not self.ai_trained:
            print("⚠️ Pure AI model not trained. Training now...")
            training_result = self.train_pure_ai_model()
            if training_result["status"] != "success":
                print("❌ Failed to train Pure AI model")
                return []
        
        if user_id not in self.user_id_to_index:
            print(f"⚠️ User {user_id} not in Pure AI training data")
            return self._get_ai_cold_start_recommendations(user_id, limit)
        
        try:
            # Get user's AI-learned preferences
            user_idx = self.user_id_to_index[user_id]
            user_ai_vector = self.user_factors[user_idx]  # AI-learned user preferences
            
            print(f"🧠 Using AI-learned preferences for user {user_id}")
            
            # Get posts user hasn't interacted with
            user_interactions_query = """
            SELECT DISTINCT post_id FROM (
                SELECT post_id FROM likes WHERE user_id = ?
                UNION
                SELECT post_id FROM comments WHERE user_id = ?
                UNION
                SELECT post_id FROM shares WHERE user_id = ?
            )
            """
            user_interacted_posts = set([
                row[0] for row in self.execute_query(user_interactions_query, (user_id, user_id, user_id))
            ])
            
            # Generate AI predictions for all posts
            ai_predictions = []
            all_confidences = []  # For normalization
            
            for post_idx, post_id in self.index_to_post_id.items():
                if post_id not in user_interacted_posts:
                    post_ai_vector = self.item_factors[:, post_idx]  # AI-learned post characteristics
                    
                    # PURE AI PREDICTION: Dot product of AI-learned vectors
                    raw_ai_confidence = np.dot(user_ai_vector, post_ai_vector)
                    
                    ai_predictions.append((post_id, float(raw_ai_confidence)))
                    all_confidences.append(raw_ai_confidence)
            
            # Calculate percentile-based confidence scores (0-100%)
            if len(all_confidences) > 0:
                # Convert raw scores to percentile rankings
                all_confidences = np.array(all_confidences)
                normalized_predictions = []
                
                for post_id, raw_score in ai_predictions:
                    # Calculate percentile (0-100%)
                    percentile = (np.sum(all_confidences <= raw_score) / len(all_confidences)) * 100
                    
                    # Also keep raw score for sorting
                    normalized_predictions.append((post_id, raw_score, percentile))
                
                # Sort by raw AI confidence scores (highest first)
                normalized_predictions.sort(key=lambda x: x[1], reverse=True)
                ai_predictions = [(post_id, raw_score, percentile) for post_id, raw_score, percentile in normalized_predictions]
            else:
                ai_predictions = []
            
            print(f"🤖 Pure AI generated {len(ai_predictions)} predictions")
            
            # Convert top AI predictions to full post data
            recommendations = []
            for post_id, raw_score, percentile in ai_predictions[:limit * 2]:  # Get extra for filtering
                
                # Get full post details
                post_query = """
                SELECT p.id, p.caption, p.user_id, u.full_name, u.email, u.profile_picture_url,
                       l.name as location, p.media_url, p.media_type, p.travel_date,
                       p.likes_count, p.comments_count, p.shares_count, p.created_at
                FROM posts p
                JOIN users u ON p.user_id = u.id
                LEFT JOIN locations l ON p.location_id = l.id
                WHERE p.id = ?
                """
                
                post_details = self.execute_query(post_query, (post_id,))
                
                if post_details:
                    row = post_details[0]
                    
                    # Create confidence grade
                    if percentile >= 95:
                        confidence_grade = "A+"
                    elif percentile >= 90:
                        confidence_grade = "A"
                    elif percentile >= 80:
                        confidence_grade = "B+"
                    elif percentile >= 70:
                        confidence_grade = "B"
                    else:
                        confidence_grade = "C"
                    
                    recommendations.append({
                        'id': row[0],
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
                        'is_liked_by_user': False,
                        'ai_confidence': percentile / 100.0,  # Convert to 0-1 scale
                        'ai_confidence_percentile': percentile,
                        'ai_confidence_grade': confidence_grade,
                        'raw_ai_score': raw_score,
                        'recommendation_reason': f'Pure AI prediction (Grade {confidence_grade}, {percentile:.1f}th percentile)',
                        'algorithm': 'pure_matrix_factorization_ai',
                        'recommendation_source': 'pure_ai'
                    })
                    
                    if len(recommendations) >= limit:
                        break
            
            print(f"✅ Pure AI recommendations: {len(recommendations)} posts")
            if recommendations:
                print(f"📊 AI confidence range: {recommendations[0]['ai_confidence_percentile']:.1f}th to {recommendations[-1]['ai_confidence_percentile']:.1f}th percentile")
                print(f"🎯 AI grades: {recommendations[0]['ai_confidence_grade']} to {recommendations[-1]['ai_confidence_grade']}")
            
            return recommendations
            
        except Exception as e:
            print(f"❌ Error in Pure AI recommendations: {e}")
            return []
    
    def _get_ai_cold_start_recommendations(self, user_id: int, limit: int) -> List[Dict]:
        """
        Handle new users not in AI training data
        Use AI model's item factors to recommend highest-rated posts
        """
        print(f"🆕 Cold start: User {user_id} not in AI training data")
        print("🤖 Using AI item factors for cold start recommendations...")
        
        if self.item_factors is None:
            return []
        
        try:
            # Use AI-learned item factors to find generally good posts
            # Average across all factors to find posts with highest overall AI scores
            post_ai_scores = np.mean(self.item_factors, axis=0)
            
            # Get top posts by AI scores
            top_post_indices = np.argsort(post_ai_scores)[-limit*2:][::-1]  # Reverse for descending order
            
            recommendations = []
            for post_idx in top_post_indices:
                post_id = self.index_to_post_id[post_idx]
                ai_score = post_ai_scores[post_idx]
                
                # Get full post details
                post_query = """
                SELECT p.id, p.caption, p.user_id, u.full_name, u.email, u.profile_picture_url,
                       l.name as location, p.media_url, p.media_type, p.travel_date,
                       p.likes_count, p.comments_count, p.shares_count, p.created_at
                FROM posts p
                JOIN users u ON p.user_id = u.id
                LEFT JOIN locations l ON p.location_id = l.id
                WHERE p.id = ?
                """
                
                post_details = self.execute_query(post_query, (post_id,))
                
                if post_details:
                    row = post_details[0]
                    recommendations.append({
                        'id': row[0],
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
                        'is_liked_by_user': False,
                        'ai_confidence': float(ai_score),
                        'recommendation_reason': f'AI cold start (score: {ai_score:.3f})',
                        'algorithm': 'pure_ai_cold_start',
                        'recommendation_source': 'pure_ai_cold_start'
                    })
                    
                    if len(recommendations) >= limit:
                        break
            
            print(f"✅ Pure AI cold start recommendations: {len(recommendations)} posts")
            return recommendations
            
        except Exception as e:
            print(f"❌ Error in AI cold start: {e}")
            return []
    
    def _save_pure_ai_model(self):
        """Save Pure AI model to disk"""
        try:
            model_data = {
                'ai_model': self.ai_model,
                'user_factors': self.user_factors,
                'item_factors': self.item_factors,
                'user_id_to_index': self.user_id_to_index,
                'index_to_user_id': self.index_to_user_id,
                'post_id_to_index': self.post_id_to_index,
                'index_to_post_id': self.index_to_post_id,
                'training_time': self.last_training_time,
                'ai_trained': True
            }
            
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            print(f"💾 Pure AI model saved to {self.model_path}")
            
        except Exception as e:
            print(f"❌ Error saving Pure AI model: {e}")
    
    def load_pure_ai_model(self) -> bool:
        """Load pre-trained Pure AI model from disk"""
        try:
            if not os.path.exists(self.model_path):
                print("📝 No saved Pure AI model found. Need to train first.")
                return False
            
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.ai_model = model_data['ai_model']
            self.user_factors = model_data['user_factors']
            self.item_factors = model_data['item_factors']
            self.user_id_to_index = model_data['user_id_to_index']
            self.index_to_user_id = model_data['index_to_user_id']
            self.post_id_to_index = model_data['post_id_to_index']
            self.index_to_post_id = model_data['index_to_post_id']
            self.last_training_time = model_data.get('training_time')
            self.ai_trained = model_data.get('ai_trained', False)
            
            print(f"✅ Pure AI model loaded from {self.model_path}")
            print(f"🤖 Last trained: {self.last_training_time}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading Pure AI model: {e}")
            return False
    
    def get_pure_ai_model_info(self) -> Dict:
        """Get information about the Pure AI model"""
        if not self.ai_trained:
            return {
                "status": "not_trained",
                "message": "Pure AI model needs to be trained first"
            }
        
        return {
            "status": "trained",
            "model_type": "Pure Matrix Factorization AI",
            "last_training_time": self.last_training_time.isoformat() if self.last_training_time else None,
            "n_factors": self.n_factors,
            "n_users": len(self.user_id_to_index),
            "n_posts": len(self.post_id_to_index),
            "user_factors_shape": self.user_factors.shape if self.user_factors is not None else None,
            "item_factors_shape": self.item_factors.shape if self.item_factors is not None else None,
            "convergence_iterations": self.ai_model.n_iter_ if self.ai_model else None,
            "regularization": self.ai_regularization,
            "max_iterations": self.ai_max_iterations
        }

# Example usage and testing
if __name__ == "__main__":
    print("🚀 Pure AI Matrix Factorization Recommender Test")
    print("=" * 60)
    print("🤖 100% Machine Learning - No Statistical Methods!")
    print("=" * 60)
    
    # Initialize Pure AI system
    pure_ai = PureAIRecommender()
    
    # Try to load existing model, otherwise train new one
    if not pure_ai.load_pure_ai_model():
        print("🤖 Training new Pure AI model...")
        training_result = pure_ai.train_pure_ai_model()
        print(f"Pure AI Training result: {training_result}")
    
    # Get model info
    model_info = pure_ai.get_pure_ai_model_info()
    print(f"\n🧠 Pure AI Model Info:")
    for key, value in model_info.items():
        print(f"   • {key}: {value}")
    
    # Test Pure AI recommendations for multiple users
    test_users = [1006, 1008, 1003]  # Users from your evaluation
    
    for test_user_id in test_users:
        print(f"\n🎯 Testing Pure AI recommendations for user {test_user_id}...")
        print("-" * 50)
        
        recommendations = pure_ai.get_pure_ai_recommendations(test_user_id, limit=10)
        
        print(f"\n✅ Got {len(recommendations)} Pure AI recommendations:")
        for i, rec in enumerate(recommendations, 1):
            confidence = rec.get('ai_confidence', 0)
            location = rec.get('location', 'No location')
            user_name = rec['user']['full_name'][:20]
            print(f"   {i}. {user_name} - {location[:30]} [AI: {confidence:.4f}]")
    
    print(f"\n🎯 Pure AI System Summary:")
    print(f"   • 100% Machine Learning predictions")
    print(f"   • No statistical or rule-based methods")
    print(f"   • AI learned {pure_ai.n_factors} latent factors")
    print(f"   • Trained on {len(pure_ai.user_id_to_index)} users and {len(pure_ai.post_id_to_index)} posts")