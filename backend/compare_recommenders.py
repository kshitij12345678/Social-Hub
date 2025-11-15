#!/usr/bin/env python3
"""
Social Hub Recommendation Systems Comparison
Comprehensive evaluation comparing Statistical vs Pure AI Matrix Factorization methods
"""

import sqlite3
import json
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import math
import random
import time

# Import all three recommendation systems
from social_hub_recommender_fixed import SocialHubRecommender
from pure_ai_recommender import PureAIRecommender
from simplified_two_tower_recommender import SimplifiedTwoTowerRecommender

class RecommenderComparison:
    """
    Compare Statistical vs Pure AI vs Two-Tower Deep Learning recommendation systems
    """
    
    def __init__(self, db_path: str = "social_hub.db"):
        self.db_path = db_path
        
        # Initialize all three systems
        print("🔍 Initializing Statistical Recommender...")
        self.statistical_recommender = SocialHubRecommender(db_path)
        
        print("🧠 Initializing Pure AI Recommender...")
        self.ai_recommender = PureAIRecommender()
        
        print("🚀 Initializing Two-Tower Deep Learning Recommender...")
        self.two_tower_recommender = SimplifiedTwoTowerRecommender(db_path)
        
        # Track if Two-Tower is trained
        self.two_tower_trained = False
        
        print("✅ All three recommendation systems loaded!")
    
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
    
    def get_test_users(self, limit: int = 20) -> List[int]:
        """Get active users for testing both systems"""
        query = """
        SELECT DISTINCT user_id, COUNT(*) as interaction_count
        FROM (
            SELECT user_id FROM likes
            UNION ALL
            SELECT user_id FROM comments
            UNION ALL 
            SELECT user_id FROM shares
        )
        GROUP BY user_id
        HAVING interaction_count >= 3
        ORDER BY interaction_count DESC
        LIMIT ?
        """
        
        results = self.execute_query(query, (limit,))
        return [row[0] for row in results]
    
    def calculate_precision_recall(self, user_id: int, recommendations: List[Dict]) -> Dict:
        """
        Calculate Precision and Recall using content similarity approach
        This method evaluates how well recommendations match user's historical preferences
        """
        if not recommendations:
            return {'precision': 0, 'recall': 0, 'f1_score': 0}
        
        # Get user's preferred content categories and locations with weights
        user_preferences_query = """
        SELECT 
            l.category, 
            l.name as location,
            COUNT(*) as interaction_weight
        FROM posts p
        JOIN locations l ON p.location_id = l.id
        WHERE p.id IN (
            SELECT post_id FROM likes WHERE user_id = ? 
            UNION ALL
            SELECT post_id FROM comments WHERE user_id = ? 
            UNION ALL
            SELECT post_id FROM shares WHERE user_id = ?
        )
        GROUP BY l.category, l.name
        ORDER BY interaction_weight DESC
        """
        
        preferences = self.execute_query(user_preferences_query, (user_id, user_id, user_id))
        
        if not preferences:
            return {'precision': 0, 'recall': 0, 'f1_score': 0}
        
        # Create weighted preference scores
        category_scores = {}
        location_scores = {}
        total_interactions = sum([pref[2] for pref in preferences])
        
        for category, location, weight in preferences:
            if category:
                category_scores[category] = category_scores.get(category, 0) + weight
            if location:
                location_scores[location] = location_scores.get(location, 0) + weight
        
        # Normalize scores to probabilities
        for cat in category_scores:
            category_scores[cat] = category_scores[cat] / total_interactions
        for loc in location_scores:
            location_scores[loc] = location_scores[loc] / total_interactions
        
        # Evaluate recommendations
        relevant_recommendations = 0
        total_relevance_score = 0
        
        for rec in recommendations:
            relevance_score = 0
            location = rec.get('location', '')
            
            # Get category for this recommendation
            category_query = """
            SELECT l.category FROM locations l 
            JOIN posts p ON p.location_id = l.id 
            WHERE p.id = ?
            """
            category_result = self.execute_query(category_query, (rec['id'],))
            category = category_result[0][0] if category_result and category_result[0][0] else ''
            
            # Calculate relevance based on user preferences
            if location in location_scores:
                relevance_score += location_scores[location]
            if category in category_scores:
                relevance_score += category_scores[category]
            
            # Consider a recommendation "relevant" if relevance > threshold
            if relevance_score > 0.1:  # 10% threshold
                relevant_recommendations += 1
            
            total_relevance_score += relevance_score
        
        # Calculate metrics
        precision = relevant_recommendations / len(recommendations) if recommendations else 0
        
        # For recall: how many of user's top preferences are covered
        top_preferences = len([score for score in list(category_scores.values()) + list(location_scores.values()) if score > 0.1])
        recall = min(relevant_recommendations / top_preferences, 1.0) if top_preferences > 0 else 0
        
        # F1-Score
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'precision': round(precision, 3),
            'recall': round(recall, 3),
            'f1_score': round(f1_score, 3),
            'relevant_recommendations': relevant_recommendations,
            'total_recommended': len(recommendations),
            'user_top_preferences': top_preferences,
            'avg_relevance_score': round(total_relevance_score / len(recommendations), 3) if recommendations else 0
        }

    def calculate_similarity_based_precision_recall(self, user_id: int, recommendations: List[Dict]) -> Dict:
        """
        Fallback method: Calculate precision/recall based on content similarity
        to user's historical preferences
        """
        if not recommendations:
            return {'precision': 0, 'recall': 0, 'f1_score': 0}
        
        # Get user's preferred categories and locations
        user_preferences_query = """
        SELECT l.category, l.name as location, COUNT(*) as interaction_count
        FROM posts p
        JOIN locations l ON p.location_id = l.id
        WHERE p.id IN (
            SELECT post_id FROM likes WHERE user_id = ?
            UNION
            SELECT post_id FROM comments WHERE user_id = ?
            UNION  
            SELECT post_id FROM shares WHERE user_id = ?
        )
        GROUP BY l.category, l.name
        ORDER BY interaction_count DESC
        """
        
        preferences = self.execute_query(user_preferences_query, (user_id, user_id, user_id))
        
        if not preferences:
            return {'precision': 0, 'recall': 0, 'f1_score': 0}
        
        # Extract top categories and locations
        top_categories = set([row[0] for row in preferences[:5] if row[0]])  # Top 5 categories
        top_locations = set([row[1] for row in preferences[:5] if row[1]])   # Top 5 locations
        
        # Count how many recommendations match user preferences
        relevant_recommendations = 0
        
        for rec in recommendations:
            location = rec.get('location', '')
            
            # Get category for this recommendation
            category_query = """
            SELECT l.category FROM locations l 
            JOIN posts p ON p.location_id = l.id 
            WHERE p.id = ?
            """
            category_result = self.execute_query(category_query, (rec['id'],))
            category = category_result[0][0] if category_result and category_result[0][0] else ''
            
            # Check if recommendation matches user preferences
            if location in top_locations or category in top_categories:
                relevant_recommendations += 1
        
        # Calculate metrics
        precision = relevant_recommendations / len(recommendations) if recommendations else 0
        recall = relevant_recommendations / len(top_categories.union(top_locations)) if (top_categories or top_locations) else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'precision': round(precision, 3),
            'recall': round(recall, 3), 
            'f1_score': round(f1_score, 3),
            'relevant_recommendations': relevant_recommendations,
            'total_recommended': len(recommendations),
            'user_preferences_count': len(top_categories) + len(top_locations)
        }

    def evaluate_recommendation_quality(self, user_id: int, recommendations: List[Dict], system_name: str) -> Dict:
        """
        Evaluate core recommendation metrics: Precision, Recall, Diversity, F1-Score
        """
        if not recommendations:
            return {
                'precision': 0,
                'recall': 0,
                'f1_score': 0,
                'diversity_score': 0,
                'quality_grade': 'F'
            }
        
        # 1. Calculate Precision and Recall
        precision_recall_metrics = self.calculate_precision_recall(user_id, recommendations)
        
        # 2. Calculate Diversity Score (content variety)
        locations = [rec.get('location', 'Unknown') for rec in recommendations]
        unique_locations = len(set(locations))
        location_diversity = unique_locations / len(recommendations) if recommendations else 0
        
        user_ids = [rec.get('user', {}).get('id', 0) for rec in recommendations]
        unique_users = len(set(user_ids))
        user_diversity = unique_users / len(recommendations) if recommendations else 0
        
        # Overall Diversity Score
        diversity_score = (location_diversity + user_diversity) / 2
        
        # 3. Quality Grade based on F1-Score (most important metric)
        f1_score = precision_recall_metrics['f1_score']
        if f1_score >= 0.7:
            quality_grade = 'A+'
        elif f1_score >= 0.5:
            quality_grade = 'A'
        elif f1_score >= 0.3:
            quality_grade = 'B'
        elif f1_score >= 0.1:
            quality_grade = 'C'
        else:
            quality_grade = 'D'
        
        return {
            'precision': precision_recall_metrics['precision'],
            'recall': precision_recall_metrics['recall'],
            'f1_score': precision_recall_metrics['f1_score'],
            'diversity_score': round(diversity_score, 3),
            'quality_grade': quality_grade,
            'total_recommendations': len(recommendations),
            'true_positives': precision_recall_metrics.get('true_positives', 0),
            'evaluation_method': 'train_test_split' if 'test_posts_count' in precision_recall_metrics else 'similarity_based'
        }
    
    def calculate_coverage_metric(self, user_id: int, recommendations: List[Dict]) -> float:
        """
        Calculate Coverage: How well recommendations cover user's diverse interests
        Coverage = Number of different categories/locations recommended / Total categories user has interacted with
        """
        if not recommendations:
            return 0.0
        
        # Get user's historical categories/locations
        user_interests_query = """
        SELECT DISTINCT l.name as location, l.category
        FROM posts p
        JOIN locations l ON p.location_id = l.id
        WHERE p.id IN (
            SELECT DISTINCT post_id FROM likes WHERE user_id = ?
            UNION
            SELECT DISTINCT post_id FROM comments WHERE user_id = ?
            UNION
            SELECT DISTINCT post_id FROM shares WHERE user_id = ?
        )
        """
        
        user_interests = self.execute_query(user_interests_query, (user_id, user_id, user_id))
        
        if not user_interests:
            return 0.0
        
        # Extract user's known interests
        user_locations = set([row[0] for row in user_interests if row[0]])
        user_categories = set([row[1] for row in user_interests if row[1]])
        user_total_interests = len(user_locations) + len(user_categories)
        
        if user_total_interests == 0:
            return 0.0
        
        # Extract recommendation interests
        rec_locations = set([rec.get('location', '') for rec in recommendations if rec.get('location')])
        rec_categories = set()
        
        # Get categories for recommended posts
        for rec in recommendations:
            location_query = """
            SELECT l.category FROM locations l 
            JOIN posts p ON p.location_id = l.id 
            WHERE p.id = ?
            """
            category_result = self.execute_query(location_query, (rec['id'],))
            if category_result and category_result[0][0]:
                rec_categories.add(category_result[0][0])
        
        # Calculate coverage
        covered_locations = len(user_locations.intersection(rec_locations))
        covered_categories = len(user_categories.intersection(rec_categories))
        total_covered = covered_locations + covered_categories
        
        coverage = total_covered / user_total_interests if user_total_interests > 0 else 0
        return round(coverage, 3)

    def calculate_recommendation_quality_score(self, user_id: int, recommendations: List[Dict]) -> float:
        """
        Calculate overall recommendation quality based on multiple factors:
        - Content relevance to user preferences
        - Popularity balance (mix of popular and niche content)
        - Freshness (newer content gets bonus)
        """
        if not recommendations:
            return 0.0
        
        total_quality = 0.0
        
        # Get user's interaction patterns
        user_patterns_query = """
        SELECT 
            AVG(p.likes_count) as avg_liked_popularity,
            COUNT(DISTINCT l.category) as category_diversity,
            COUNT(DISTINCT p.user_id) as creator_diversity
        FROM posts p
        JOIN locations l ON p.location_id = l.id
        WHERE p.id IN (
            SELECT post_id FROM likes WHERE user_id = ?
            UNION
            SELECT post_id FROM comments WHERE user_id = ?
            UNION
            SELECT post_id FROM shares WHERE user_id = ?
        )
        """
        
        patterns = self.execute_query(user_patterns_query, (user_id, user_id, user_id))
        
        if not patterns or not patterns[0][0]:
            return 0.0
        
        avg_user_preference_popularity = patterns[0][0]
        
        for rec in recommendations:
            quality_score = 0.0
            
            # Factor 1: Popularity alignment (30% weight)
            rec_popularity = rec.get('likes_count', 0)
            if avg_user_preference_popularity > 0:
                # Score based on how close recommendation popularity is to user's typical preference
                popularity_ratio = min(rec_popularity / avg_user_preference_popularity, 2.0)  # Cap at 2x
                popularity_score = 1.0 - abs(1.0 - popularity_ratio) if popularity_ratio <= 2.0 else 0.5
                quality_score += popularity_score * 0.3
            
            # Factor 2: Content freshness (20% weight)  
            # Newer posts get higher scores (assuming higher post IDs are newer)
            freshness_score = min(rec['id'] / 3000.0, 1.0)  # Normalize against expected max post ID
            quality_score += freshness_score * 0.2
            
            # Factor 3: Creator diversity (25% weight)
            # Bonus for content from different creators
            creator_diversity_score = 0.8  # Base score for variety
            quality_score += creator_diversity_score * 0.25
            
            # Factor 4: Engagement potential (25% weight)
            # Posts with moderate engagement often have good quality
            engagement_score = min((rec.get('likes_count', 0) + rec.get('comments_count', 0)) / 20.0, 1.0)
            quality_score += engagement_score * 0.25
            
            total_quality += quality_score
        
        # Average quality across all recommendations
        avg_quality = total_quality / len(recommendations)
        return round(avg_quality, 3)
    
    def evaluate_system_performance(self, system_name: str, recommender, test_users: List[int]) -> Dict:
        """
        Evaluate overall system performance
        """
        print(f"\n🔍 Evaluating {system_name} System Performance...")
        start_time = time.time()
        
        all_metrics = {
            'response_times': [],
            'precision_scores': [],
            'recall_scores': [],
            'f1_scores': [],
            'diversity_scores': [],
            'coverage_scores': [],
            'successful_recommendations': 0,
            'failed_recommendations': 0
        }
        
        for i, user_id in enumerate(test_users):
            print(f"  📊 Testing user {user_id} ({i+1}/{len(test_users)})")
            
            try:
                # Time the recommendation generation
                rec_start = time.time()
                
                if system_name == 'Statistical':
                    recommendations = recommender.get_recommended_posts(user_id, limit=10)
                elif system_name == 'Pure AI':
                    recommendations = recommender.get_pure_ai_recommendations(user_id, limit=10)
                elif system_name == 'Two-Tower':
                    recommendations = recommender.get_two_tower_recommendations(user_id, limit=10)
                else:
                    recommendations = []
                
                rec_time = time.time() - rec_start
                all_metrics['response_times'].append(rec_time)
                
                if recommendations:
                    all_metrics['successful_recommendations'] += 1
                    
                    # Evaluate core recommendation metrics
                    quality_metrics = self.evaluate_recommendation_quality(user_id, recommendations, system_name)
                    all_metrics['precision_scores'].append(quality_metrics['precision'])
                    all_metrics['recall_scores'].append(quality_metrics['recall'])
                    all_metrics['f1_scores'].append(quality_metrics['f1_score'])
                    all_metrics['diversity_scores'].append(quality_metrics['diversity_score'])
                    
                    # Calculate coverage metric
                    coverage_score = self.calculate_coverage_metric(user_id, recommendations)
                    all_metrics['coverage_scores'].append(coverage_score)
                    
                    # Add quality score for better evaluation
                    if 'quality_scores' not in all_metrics:
                        all_metrics['quality_scores'] = []
                    quality_score = self.calculate_recommendation_quality_score(user_id, recommendations)
                    all_metrics['quality_scores'].append(quality_score)
                    
                else:
                    all_metrics['failed_recommendations'] += 1
                    
            except Exception as e:
                print(f"    ❌ Error for user {user_id}: {e}")
                all_metrics['failed_recommendations'] += 1
        
        # Calculate aggregate metrics
        total_time = time.time() - start_time
        
        # Average metrics
        avg_response_time = np.mean(all_metrics['response_times']) if all_metrics['response_times'] else 0
        avg_precision = np.mean(all_metrics['precision_scores']) if all_metrics['precision_scores'] else 0
        avg_recall = np.mean(all_metrics['recall_scores']) if all_metrics['recall_scores'] else 0
        avg_f1 = np.mean(all_metrics['f1_scores']) if all_metrics['f1_scores'] else 0
        avg_diversity = np.mean(all_metrics['diversity_scores']) if all_metrics['diversity_scores'] else 0
        avg_coverage = np.mean(all_metrics['coverage_scores']) if all_metrics['coverage_scores'] else 0
        avg_quality = np.mean(all_metrics.get('quality_scores', [])) if all_metrics.get('quality_scores') else 0
        
        # Success rate
        total_tests = len(test_users)
        success_rate = all_metrics['successful_recommendations'] / total_tests if total_tests > 0 else 0
        
        # Overall system score (0-100) - weighted by importance
        system_score = (
            (success_rate * 20) +           # 20% weight for reliability
            (avg_f1 * 30) +                # 30% weight for F1-score (most important)
            (avg_diversity * 20) +          # 20% weight for diversity
            (avg_coverage * 20) +           # 20% weight for coverage
            (min(1.0/avg_response_time, 10) * 1.0)  # 10% weight for speed
        ) if avg_response_time > 0 else 0
        
        return {
            'system_name': system_name,
            'total_evaluation_time': round(total_time, 2),
            'avg_response_time': round(avg_response_time, 4),
            'success_rate': round(success_rate, 3),
            'avg_precision': round(avg_precision, 3),
            'avg_recall': round(avg_recall, 3),
            'avg_f1_score': round(avg_f1, 3),
            'avg_diversity_score': round(avg_diversity, 3),
            'avg_coverage_score': round(avg_coverage, 3),
            'avg_quality_score': round(avg_quality, 3),
            'system_score': round(system_score, 1),
            'successful_recommendations': all_metrics['successful_recommendations'],
            'failed_recommendations': all_metrics['failed_recommendations'],
            'total_tests': total_tests
        }
    
    def train_two_tower_if_needed(self):
        """Train Two-Tower system if not already trained"""
        if not self.two_tower_trained:
            print("🚀 Training Two-Tower Deep Learning System...")
            try:
                history = self.two_tower_recommender.train_simplified_two_tower(epochs=10, batch_size=64)
                if history:
                    self.two_tower_trained = True
                    print("✅ Two-Tower system trained successfully!")
                else:
                    print("❌ Two-Tower system training failed!")
            except Exception as e:
                print(f"❌ Two-Tower training error: {e}")
                self.two_tower_trained = False

    def compare_systems(self, test_users: Optional[List[int]] = None, num_test_users: int = 15) -> Dict:
        """
        Main comparison function - evaluates all three systems and provides detailed comparison
        """
        print("🎯 SOCIAL HUB RECOMMENDATION SYSTEMS - THREE-WAY COMPARISON")
        print("=" * 70)
        
        # Get test users
        if test_users is None:
            test_users = self.get_test_users(num_test_users)
        
        print(f"👥 Testing with {len(test_users)} active users")
        
        # Train Two-Tower if needed
        self.train_two_tower_if_needed()
        
        # Evaluate Statistical System
        statistical_results = self.evaluate_system_performance(
            'Statistical', self.statistical_recommender, test_users
        )
        
        # Evaluate Pure AI System
        ai_results = self.evaluate_system_performance(
            'Pure AI', self.ai_recommender, test_users
        )
        
        # Evaluate Two-Tower System (if trained)
        two_tower_results = None
        if self.two_tower_trained:
            two_tower_results = self.evaluate_system_performance(
                'Two-Tower', self.two_tower_recommender, test_users
            )
        
        # Generate comparison report
        comparison = self.generate_three_way_comparison_report(
            statistical_results, ai_results, two_tower_results
        )
        
        return {
            'statistical_results': statistical_results,
            'ai_results': ai_results,
            'two_tower_results': two_tower_results,
            'comparison': comparison,
            'test_metadata': {
                'test_users': test_users,
                'evaluation_date': datetime.now().isoformat(),
                'num_test_users': len(test_users),
                'two_tower_trained': self.two_tower_trained
            }
        }
    
    def generate_three_way_comparison_report(self, statistical: Dict, ai: Dict, two_tower: Optional[Dict]) -> Dict:
        """
        Generate detailed comparison report between all three systems
        """
        print("\n📊 GENERATING THREE-WAY COMPARISON REPORT...")
        
        systems = {
            'Statistical': statistical,
            'Pure AI': ai
        }
        
        if two_tower:
            systems['Two-Tower'] = two_tower
        
        # Performance comparison
        performance_comparison = {}
        
        # Compare each metric
        metrics_to_compare = [
            'avg_response_time', 'success_rate', 'avg_precision',
            'avg_recall', 'avg_f1_score', 'avg_diversity_score',
            'avg_coverage_score', 'system_score'
        ]
        
        for metric in metrics_to_compare:
            metric_data = {}
            values = {}
            
            for system_name, system_results in systems.items():
                values[system_name] = system_results.get(metric, 0)
                metric_data[f'{system_name.lower().replace("-", "_")}_value'] = values[system_name]
            
            # Determine winner (lower is better for response_time)
            if metric == 'avg_response_time':
                winner = min(values, key=values.get)
                best_value = min(values.values())
            else:
                winner = max(values, key=values.get)
                best_value = max(values.values())
            
            metric_data['winner'] = winner
            metric_data['best_value'] = best_value
            metric_data['all_values'] = values
            
            performance_comparison[metric] = metric_data
        
        # Overall winner based on system_score
        overall_winner = performance_comparison['system_score']['winner']
        
        # Generate recommendations
        recommendations = []
        
        winner_scores = {name: results['system_score'] for name, results in systems.items()}
        sorted_systems = sorted(winner_scores.items(), key=lambda x: x[1], reverse=True)
        
        recommendations.append(f"{sorted_systems[0][0]} system shows the best overall performance ({sorted_systems[0][1]:.1f})")
        recommendations.append(f"Performance ranking: {' > '.join([f'{name} ({score:.1f})' for name, score in sorted_systems])}")
        
        # Add specific recommendations based on metrics
        if performance_comparison['avg_response_time']['winner']:
            fastest = performance_comparison['avg_response_time']['winner']
            recommendations.append(f"{fastest} system is fastest for real-time recommendations")
        
        if performance_comparison['avg_f1_score']['winner']:
            most_accurate = performance_comparison['avg_f1_score']['winner']
            recommendations.append(f"{most_accurate} provides the most accurate recommendations")
        
        if performance_comparison['avg_diversity_score']['winner']:
            most_diverse = performance_comparison['avg_diversity_score']['winner']
            recommendations.append(f"{most_diverse} offers the best content diversity")
        
        return {
            'overall_winner': overall_winner,
            'performance_comparison': performance_comparison,
            'recommendations': recommendations,
            'system_ranking': sorted_systems,
            'summary': {
                'strengths_by_system': {
                    name: self._identify_system_strengths(results, performance_comparison, name)
                    for name, results in systems.items()
                },
                'key_insights': self._generate_key_insights(performance_comparison, systems)
            }
        }

    def generate_comparison_report(self, statistical: Dict, ai: Dict) -> Dict:
        """
        Generate detailed comparison report between both systems
        """
        print("\n📊 GENERATING COMPARISON REPORT...")
        
        # Performance comparison
        performance_comparison = {}
        
        # Compare each metric
        metrics_to_compare = [
            'avg_response_time', 'success_rate', 'avg_precision',
            'avg_recall', 'avg_f1_score', 'avg_diversity_score',
            'avg_coverage_score', 'system_score'
        ]
        
        for metric in metrics_to_compare:
            stat_value = statistical.get(metric, 0)
            ai_value = ai.get(metric, 0)
            
            # Determine winner (lower is better for response_time)
            if metric == 'avg_response_time':
                winner = 'Statistical' if stat_value < ai_value else 'Pure AI'
                improvement = abs(stat_value - ai_value) / max(stat_value, ai_value, 0.0001) * 100
            else:
                winner = 'Statistical' if stat_value > ai_value else 'Pure AI'
                improvement = abs(stat_value - ai_value) / max(stat_value, ai_value, 0.0001) * 100
            
            performance_comparison[metric] = {
                'statistical_value': stat_value,
                'ai_value': ai_value,
                'winner': winner,
                'improvement_percentage': round(improvement, 1),
                'difference': round(abs(stat_value - ai_value), 4)
            }
        
        # Overall winner
        overall_winner = 'Statistical' if statistical['system_score'] > ai['system_score'] else 'Pure AI'
        score_difference = abs(statistical['system_score'] - ai['system_score'])
        
        # Generate recommendations
        recommendations = []
        
        if performance_comparison['system_score']['winner'] == 'Statistical':
            recommendations.append("Statistical system shows superior overall performance")
        else:
            recommendations.append("Pure AI system demonstrates better overall performance")
        
        if performance_comparison['avg_response_time']['winner'] == 'Statistical':
            recommendations.append("Statistical system is faster for real-time recommendations")
        else:
            recommendations.append("Pure AI system has competitive response times")
        
        if performance_comparison['avg_f1_score']['winner'] == 'Pure AI':
            recommendations.append("Pure AI provides more accurate recommendations (higher F1-score)")
        
        if performance_comparison['avg_precision']['winner'] == 'Pure AI':
            recommendations.append("Pure AI has better precision in recommendations")
        
        if performance_comparison['avg_diversity_score']['winner'] == 'Pure AI':
            recommendations.append("Pure AI offers better content diversity")
        
        if performance_comparison['avg_coverage_score']['winner'] == 'Pure AI':
            recommendations.append("Pure AI covers user interests more comprehensively")
        
        return {
            'overall_winner': overall_winner,
            'score_difference': round(score_difference, 1),
            'performance_comparison': performance_comparison,
            'recommendations': recommendations,
            'summary': {
                'statistical_strengths': self._identify_strengths(statistical, performance_comparison, 'Statistical'),
                'ai_strengths': self._identify_strengths(ai, performance_comparison, 'Pure AI'),
                'key_differences': self._identify_key_differences(performance_comparison)
            }
        }
    
    def _identify_system_strengths(self, system_results: Dict, comparison: Dict, system_name: str) -> List[str]:
        """Identify key strengths of each system in three-way comparison"""
        strengths = []
        
        for metric, comp_data in comparison.items():
            if comp_data['winner'] == system_name:
                metric_name = metric.replace('avg_', '').replace('_', ' ').title()
                best_value = comp_data['best_value']
                strengths.append(f"{metric_name}: {best_value:.3f} (Winner)")
        
        return strengths
    
    def _generate_key_insights(self, comparison: Dict, systems: Dict) -> List[str]:
        """Generate key insights from three-way comparison"""
        insights = []
        
        # Response time insight
        response_times = comparison['avg_response_time']['all_values']
        fastest = min(response_times, key=response_times.get)
        slowest = max(response_times, key=response_times.get)
        insights.append(f"Speed: {fastest} is {response_times[slowest]/response_times[fastest]:.1f}x faster than {slowest}")
        
        # Accuracy insight
        f1_scores = comparison['avg_f1_score']['all_values']
        best_f1 = max(f1_scores, key=f1_scores.get)
        insights.append(f"Accuracy: {best_f1} achieves {f1_scores[best_f1]:.1f}% F1-Score")
        
        # Diversity insight
        diversity_scores = comparison['avg_diversity_score']['all_values']
        most_diverse = max(diversity_scores, key=diversity_scores.get)
        insights.append(f"Diversity: {most_diverse} provides {diversity_scores[most_diverse]:.1f}% content diversity")
        
        return insights

    def _identify_strengths(self, system_results: Dict, comparison: Dict, system_name: str) -> List[str]:
        """Identify key strengths of each system"""
        strengths = []
        
        for metric, comp_data in comparison.items():
            if comp_data.get('winner') == system_name and comp_data.get('improvement_percentage', 0) > 5:
                metric_name = metric.replace('avg_', '').replace('_', ' ').title()
                strengths.append(f"{metric_name} ({comp_data['improvement_percentage']:.1f}% better)")
        
        return strengths
    
    def _identify_key_differences(self, comparison: Dict) -> List[str]:
        """Identify key differences between systems"""
        differences = []
        
        # Significant differences (>10% improvement)
        for metric, comp_data in comparison.items():
            if comp_data['improvement_percentage'] > 10:
                metric_name = metric.replace('avg_', '').replace('_', ' ').title()
                differences.append(
                    f"{metric_name}: {comp_data['winner']} is {comp_data['improvement_percentage']:.1f}% better"
                )
        
        return differences
    
    def print_detailed_report(self, results: Dict):
        """
        Print a comprehensive, formatted comparison report for all systems
        """
        print("\n" + "="*90)
        print("🎯 SOCIAL HUB RECOMMENDATION SYSTEMS - COMPREHENSIVE COMPARISON REPORT")
        print("="*90)
        
        statistical = results['statistical_results']
        ai = results['ai_results']
        two_tower = results.get('two_tower_results')
        comparison = results['comparison']
        
        # System Overview
        print("\n📊 SYSTEM PERFORMANCE OVERVIEW")
        print("-" * 85)
        
        if two_tower:
            print(f"{'Metric':<25} {'Statistical':<15} {'Pure AI':<15} {'Two-Tower':<15} {'Winner':<15}")
            print("-" * 85)
        else:
            print(f"{'Metric':<30} {'Statistical':<15} {'Pure AI':<15} {'Winner':<15}")
            print("-" * 75)
        
        metrics_display = {
            'system_score': 'Overall Score',
            'success_rate': 'Success Rate',
            'avg_response_time': 'Response Time (s)',
            'avg_precision': 'Precision',
            'avg_recall': 'Recall',
            'avg_f1_score': 'F1-Score',
            'avg_diversity_score': 'Diversity Score',
            'avg_coverage_score': 'Coverage Score'
        }
        
        for metric, display_name in metrics_display.items():
            comp_data = comparison['performance_comparison'][metric]
            
            if two_tower:
                stat_val = f"{comp_data.get('statistical_value', 0):.3f}"
                ai_val = f"{comp_data.get('pure_ai_value', 0):.3f}"
                tt_val = f"{comp_data.get('two_tower_value', 0):.3f}"
                winner = comp_data['winner']
                
                print(f"{display_name:<25} {stat_val:<15} {ai_val:<15} {tt_val:<15} {winner:<15}")
            else:
                stat_val = f"{comp_data.get('statistical_value', 0):.3f}"
                ai_val = f"{comp_data.get('ai_value', 0):.3f}"
                winner = comp_data['winner']
                
                print(f"{display_name:<30} {stat_val:<15} {ai_val:<15} {winner:<15}")
        
        # Overall Winner and Rankings
        print("\n" + "="*60)
        print(f"🏆 OVERALL WINNER: {comparison['overall_winner']}")
        
        if 'system_ranking' in comparison:
            print("📊 SYSTEM RANKINGS:")
            for i, (system, score) in enumerate(comparison['system_ranking'], 1):
                print(f"  {i}. {system}: {score:.1f} points")
        
        print("="*60)
        
        # System Strengths
        if 'strengths_by_system' in comparison.get('summary', {}):
            for system_name, strengths in comparison['summary']['strengths_by_system'].items():
                print(f"\n💪 {system_name.upper()} SYSTEM STRENGTHS:")
                for strength in strengths:
                    print(f"  ✅ {strength}")
        else:
            # Fallback for old format
            if 'statistical_strengths' in comparison.get('summary', {}):
                print(f"\n💪 STATISTICAL SYSTEM STRENGTHS:")
                for strength in comparison['summary']['statistical_strengths']:
                    print(f"  ✅ {strength}")
            
            if 'ai_strengths' in comparison.get('summary', {}):
                print(f"\n🧠 PURE AI SYSTEM STRENGTHS:")
                for strength in comparison['summary']['ai_strengths']:
                    print(f"  ✅ {strength}")
        
        # Key Insights
        if 'key_insights' in comparison.get('summary', {}):
            print(f"\n🔍 KEY INSIGHTS:")
            for insight in comparison['summary']['key_insights']:
                print(f"  📈 {insight}")
        elif 'key_differences' in comparison.get('summary', {}):
            print(f"\n🔍 KEY DIFFERENCES:")
            for diff in comparison['summary']['key_differences']:
                print(f"  📈 {diff}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in comparison['recommendations']:
            print(f"  🎯 {rec}")
        
        # Performance Analysis
        systems_data = [
            ('Statistical', statistical),
            ('Pure AI', ai)
        ]
        
        if two_tower:
            systems_data.append(('Two-Tower', two_tower))
        
        print(f"\n📈 PERFORMANCE ANALYSIS:")
        for system_name, system_data in systems_data:
            print(f"  {system_name} System:")
            print(f"    • Processed {system_data['total_tests']} users in {system_data['total_evaluation_time']:.2f}s")
            print(f"    • Success Rate: {system_data['success_rate']:.1%}")
            print(f"    • Average Response Time: {system_data['avg_response_time']:.4f}s")
        
        # Quality Analysis
        print(f"\n🎯 RECOMMENDATION QUALITY ANALYSIS:")
        
        # F1-Score Analysis (Most Important)
        better_f1 = "Pure AI" if ai['avg_f1_score'] > statistical['avg_f1_score'] else "Statistical"
        f1_diff = abs(ai['avg_f1_score'] - statistical['avg_f1_score'])
        print(f"  📈 F1-Score: {better_f1} system is more accurate")
        print(f"    Statistical: {statistical['avg_f1_score']:.3f} | Pure AI: {ai['avg_f1_score']:.3f} | Difference: {f1_diff:.3f}")
        
        # Precision vs Recall Trade-off
        print(f"  🎯 Precision Analysis:")
        print(f"    Statistical: {statistical['avg_precision']:.3f} | Pure AI: {ai['avg_precision']:.3f}")
        print(f"  🔍 Recall Analysis:")
        print(f"    Statistical: {statistical['avg_recall']:.3f} | Pure AI: {ai['avg_recall']:.3f}")
        
        # Diversity and Coverage
        better_diversity = "Pure AI" if ai['avg_diversity_score'] > statistical['avg_diversity_score'] else "Statistical"
        diversity_diff = abs(ai['avg_diversity_score'] - statistical['avg_diversity_score'])
        print(f"  🌈 Diversity: {better_diversity} offers more varied content (difference: {diversity_diff:.3f})")
        
        better_coverage = "Pure AI" if ai['avg_coverage_score'] > statistical['avg_coverage_score'] else "Statistical"
        coverage_diff = abs(ai['avg_coverage_score'] - statistical['avg_coverage_score'])
        print(f"  📊 Coverage: {better_coverage} covers user interests better (difference: {coverage_diff:.3f})")
        
        print("\n" + "="*80)

def main():
    """
    Main evaluation function
    """
    print("🚀 Starting Social Hub Recommendation Systems Comparison...")
    
    # Initialize comparator
    comparator = RecommenderComparison()
    
    # Run comparison
    results = comparator.compare_systems(num_test_users=15)
    
    # Print detailed report
    comparator.print_detailed_report(results)
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"recommendation_comparison_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: {filename}")
    print("✅ Comparison completed successfully!")

if __name__ == "__main__":
    main()