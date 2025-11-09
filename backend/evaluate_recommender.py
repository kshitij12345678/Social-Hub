#!/usr/bin/env python3
"""
Social Hub Recommendation System Evaluation Script
Comprehensive testing and scoring of recommendation accuracy and performance
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict
import math
import random

# Import the recommender system
from social_hub_recommender_fixed import SocialHubRecommender

class RecommendationEvaluator:
    """
    Comprehensive evaluation of Social Hub recommendation system
    """
    
    def __init__(self, db_path: str = "social_hub.db"):
        self.db_path = db_path
        self.recommender = SocialHubRecommender(db_path)
        print("🔍 Recommendation Evaluator initialized!")
    
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
    
    def get_active_users(self, days: int = 30, limit: int = 50) -> List[int]:
        """Get list of active users who have interactions"""
        query = """
        SELECT DISTINCT user_id, COUNT(*) as interaction_count
        FROM (
            SELECT user_id FROM likes WHERE created_at >= datetime('now', '-{} days')
            UNION ALL
            SELECT user_id FROM comments WHERE created_at >= datetime('now', '-{} days')
            UNION ALL 
            SELECT user_id FROM shares WHERE created_at >= datetime('now', '-{} days')
        )
        GROUP BY user_id
        HAVING interaction_count >= 2
        ORDER BY interaction_count DESC
        LIMIT ?
        """.format(days, days, days)
        
        results = self.execute_query(query, (limit,))
        return [row[0] for row in results]
    
    def simulate_user_interactions(self, user_id: int, recommendations: List[Dict]) -> Dict:
        """
        Simulate user interactions with recommendations based on their historical behavior
        This replaces real-time tracking for evaluation purposes
        """
        # Get user's historical interaction patterns
        user_interactions = self.recommender._get_user_interactions(user_id)
        
        if not user_interactions:
            return {'liked': 0, 'commented': 0, 'shared': 0, 'total_interactions': 0}
        
        # Calculate user's interaction probability based on history
        total_past_interactions = len(user_interactions)
        like_rate = len([i for i in user_interactions if i['type'] == 'like']) / total_past_interactions
        comment_rate = len([i for i in user_interactions if i['type'] == 'comment']) / total_past_interactions
        share_rate = len([i for i in user_interactions if i['type'] == 'share']) / total_past_interactions
        
        # Simulate interactions with recommendations
        simulated_interactions = {'liked': 0, 'commented': 0, 'shared': 0, 'total_interactions': 0}
        
        for rec in recommendations:
            # Base interaction probability (higher for better recommendations)
            base_prob = min(rec.get('popularity_score', 0.1) / 100.0, 0.3)
            
            # Simulate like
            if random.random() < (like_rate * base_prob * 2):
                simulated_interactions['liked'] += 1
                simulated_interactions['total_interactions'] += 1
            
            # Simulate comment (less likely)
            if random.random() < (comment_rate * base_prob * 1.5):
                simulated_interactions['commented'] += 1
                simulated_interactions['total_interactions'] += 1
            
            # Simulate share (least likely)
            if random.random() < (share_rate * base_prob):
                simulated_interactions['shared'] += 1
                simulated_interactions['total_interactions'] += 1
        
        return simulated_interactions
    
    def calculate_ctr(self, user_id: int, recommendations: List[Dict]) -> float:
        """Calculate Click-Through Rate (simulated)"""
        if not recommendations:
            return 0.0
        
        interactions = self.simulate_user_interactions(user_id, recommendations)
        ctr = (interactions['total_interactions'] / len(recommendations)) * 100
        return min(ctr, 100.0)  # Cap at 100%
    
    def calculate_precision_at_k(self, user_id: int, recommendations: List[Dict], k: int = 10) -> float:
        """Calculate Precision@K (simulated)"""
        if not recommendations or k <= 0:
            return 0.0
        
        top_k_recs = recommendations[:k]
        interactions = self.simulate_user_interactions(user_id, top_k_recs)
        
        # Precision = relevant items / total items
        precision = (interactions['total_interactions'] / k) * 100
        return min(precision, 100.0)
    
    def calculate_diversity_score(self, recommendations: List[Dict]) -> float:
        """Calculate recommendation diversity"""
        if not recommendations:
            return 0.0
        
        # Count unique authors
        unique_authors = len(set(rec.get('author_name', 'Unknown') for rec in recommendations))
        
        # Count unique locations (approximate from caption)
        unique_locations = len(set(rec.get('location_name', 'Unknown') for rec in recommendations))
        
        # Calculate time diversity (posts from different time periods)
        creation_dates = []
        for rec in recommendations:
            if rec.get('created_at'):
                try:
                    creation_dates.append(datetime.fromisoformat(rec['created_at'].replace('Z', '+00:00')))
                except:
                    pass
        
        time_diversity = 1.0
        if len(creation_dates) > 1:
            date_range = (max(creation_dates) - min(creation_dates)).days
            time_diversity = min(date_range / 30.0, 1.0)  # Normalize to 30 days max
        
        total_recs = len(recommendations)
        
        # Diversity score (0-100)
        author_diversity = min(unique_authors / total_recs, 1.0)
        location_diversity = min(unique_locations / total_recs, 1.0)
        
        diversity_score = (author_diversity + location_diversity + time_diversity) / 3 * 100
        return diversity_score
    
    def calculate_coverage(self) -> Dict:
        """Calculate system coverage"""
        # Total posts in system
        total_posts = self.execute_query("SELECT COUNT(*) FROM posts")[0][0]
        
        # Posts that could be recommended (have basic requirements)
        recommendable_posts = self.execute_query("""
            SELECT COUNT(*) FROM posts p 
            WHERE p.caption IS NOT NULL AND p.caption != ''
        """)[0][0]
        
        coverage_percentage = (recommendable_posts / total_posts) * 100 if total_posts > 0 else 0
        
        return {
            'total_posts': total_posts,
            'recommendable_posts': recommendable_posts,
            'coverage_percentage': coverage_percentage
        }
    
    def analyze_algorithm_distribution(self, all_recommendations: List[List[Dict]]) -> Dict:
        """Analyze distribution of recommendation algorithms"""
        algorithm_counts = defaultdict(int)
        total_recommendations = 0
        
        for user_recs in all_recommendations:
            for rec in user_recs:
                algorithm = rec.get('algorithm', 'unknown')
                algorithm_counts[algorithm] += 1
                total_recommendations += 1
        
        # Convert to percentages
        algorithm_distribution = {}
        for alg, count in algorithm_counts.items():
            algorithm_distribution[alg] = (count / total_recommendations) * 100 if total_recommendations > 0 else 0
        
        return algorithm_distribution
    
    def evaluate_recommendation_quality(self, recommendations: List[Dict]) -> Dict:
        """Evaluate the quality of recommendations"""
        if not recommendations:
            return {'quality_score': 0, 'issues': ['No recommendations generated']}
        
        quality_metrics = {
            'has_content': 0,
            'has_location': 0,
            'has_author': 0,
            'recent_posts': 0,
            'popular_posts': 0
        }
        
        issues = []
        
        for rec in recommendations:
            # Check content quality
            if rec.get('caption') and len(rec['caption'].strip()) > 10:
                quality_metrics['has_content'] += 1
            
            if rec.get('location_name'):
                quality_metrics['has_location'] += 1
            
            if rec.get('author_name'):
                quality_metrics['has_author'] += 1
            
            # Check recency (posts from last 30 days)
            if rec.get('created_at'):
                try:
                    created_date = datetime.fromisoformat(rec['created_at'].replace('Z', '+00:00'))
                    if (datetime.now() - created_date).days <= 30:
                        quality_metrics['recent_posts'] += 1
                except:
                    pass
            
            # Check popularity (posts with some engagement)
            if rec.get('likes_count', 0) > 0 or rec.get('comments_count', 0) > 0:
                quality_metrics['popular_posts'] += 1
        
        total_recs = len(recommendations)
        
        # Calculate quality score (0-100)
        content_score = (quality_metrics['has_content'] / total_recs) * 20
        location_score = (quality_metrics['has_location'] / total_recs) * 20
        author_score = (quality_metrics['has_author'] / total_recs) * 20
        recency_score = (quality_metrics['recent_posts'] / total_recs) * 20
        popularity_score = (quality_metrics['popular_posts'] / total_recs) * 20
        
        quality_score = content_score + location_score + author_score + recency_score + popularity_score
        
        # Check for issues
        if quality_metrics['has_content'] / total_recs < 0.8:
            issues.append("Low content quality (many posts with short/empty captions)")
        
        if quality_metrics['has_location'] / total_recs < 0.5:
            issues.append("Many recommendations missing location information")
        
        if quality_metrics['recent_posts'] / total_recs < 0.3:
            issues.append("Too many old posts in recommendations")
        
        return {
            'quality_score': quality_score,
            'metrics': quality_metrics,
            'issues': issues
        }
    
    def run_comprehensive_evaluation(self, num_users: int = 20) -> Dict:
        """Run comprehensive evaluation of the recommendation system"""
        print(f"🚀 Starting comprehensive evaluation with {num_users} users...")
        
        # Get active users for testing
        active_users = self.get_active_users(days=30, limit=num_users)
        
        if len(active_users) < 5:
            print("⚠️  Warning: Very few active users found. Results may not be representative.")
        
        print(f"📊 Evaluating {len(active_users)} active users")
        
        # Collect metrics
        all_ctrs = []
        all_precisions = []
        all_diversities = []
        all_recommendations = []
        algorithm_performance = defaultdict(list)
        quality_scores = []
        
        for i, user_id in enumerate(active_users):
            print(f"   Evaluating user {user_id} ({i+1}/{len(active_users)})")
            
            try:
                # Get recommendations for this user
                recommendations = self.recommender.get_recommended_posts(user_id, limit=15)
                
                if not recommendations:
                    print(f"     ⚠️  No recommendations for user {user_id}")
                    continue
                
                all_recommendations.append(recommendations)
                
                # Calculate metrics
                ctr = self.calculate_ctr(user_id, recommendations)
                precision = self.calculate_precision_at_k(user_id, recommendations, k=10)
                diversity = self.calculate_diversity_score(recommendations)
                quality = self.evaluate_recommendation_quality(recommendations)
                
                all_ctrs.append(ctr)
                all_precisions.append(precision)
                all_diversities.append(diversity)
                quality_scores.append(quality['quality_score'])
                
                # Track algorithm performance
                for rec in recommendations:
                    alg = rec.get('algorithm', 'hybrid')
                    algorithm_performance[alg].append(ctr)
                
                print(f"     CTR: {ctr:.2f}%, Precision@10: {precision:.2f}%, Diversity: {diversity:.2f}%")
                
            except Exception as e:
                print(f"     ❌ Error evaluating user {user_id}: {e}")
                continue
        
        # Calculate overall metrics
        results = {
            'evaluation_timestamp': datetime.now().isoformat(),
            'users_evaluated': len(active_users),
            'successful_evaluations': len(all_ctrs),
            'overall_metrics': {
                'average_ctr': sum(all_ctrs) / len(all_ctrs) if all_ctrs else 0,
                'average_precision_at_10': sum(all_precisions) / len(all_precisions) if all_precisions else 0,
                'average_diversity_score': sum(all_diversities) / len(all_diversities) if all_diversities else 0,
                'average_quality_score': sum(quality_scores) / len(quality_scores) if quality_scores else 0,
            },
            'system_metrics': {
                'coverage': self.calculate_coverage(),
                'algorithm_distribution': self.analyze_algorithm_distribution(all_recommendations)
            },
            'performance_grades': {},
            'recommendations': []
        }
        
        # Grade the system performance
        avg_ctr = results['overall_metrics']['average_ctr']
        avg_precision = results['overall_metrics']['average_precision_at_10']
        avg_diversity = results['overall_metrics']['average_diversity_score']
        avg_quality = results['overall_metrics']['average_quality_score']
        
        # Grading criteria (A=90-100, B=80-89, C=70-79, D=60-69, F=<60)
        def get_grade(score):
            if score >= 90: return 'A'
            elif score >= 80: return 'B'
            elif score >= 70: return 'C'
            elif score >= 60: return 'D'
            else: return 'F'
        
        results['performance_grades'] = {
            'engagement_grade': get_grade(avg_ctr * 5),  # Scale CTR (max ~20%) to 100
            'relevance_grade': get_grade(avg_precision * 3),  # Scale precision to 100
            'diversity_grade': get_grade(avg_diversity),
            'quality_grade': get_grade(avg_quality),
        }
        
        # Overall system score (weighted average)
        overall_score = (
            (avg_ctr * 5) * 0.3 +        # 30% weight on engagement
            (avg_precision * 3) * 0.3 +   # 30% weight on relevance
            avg_diversity * 0.2 +          # 20% weight on diversity
            avg_quality * 0.2              # 20% weight on quality
        )
        
        results['overall_score'] = overall_score
        results['overall_grade'] = get_grade(overall_score)
        
        # Generate recommendations for improvement
        recommendations = []
        
        if avg_ctr < 15:
            recommendations.append("📈 Improve user engagement by tuning recommendation algorithms")
        
        if avg_precision < 25:
            recommendations.append("🎯 Enhance recommendation relevance by improving collaborative filtering")
        
        if avg_diversity < 60:
            recommendations.append("🌟 Increase content diversity to prevent filter bubbles")
        
        if avg_quality < 70:
            recommendations.append("✨ Improve content quality filtering")
        
        if results['system_metrics']['coverage']['coverage_percentage'] < 50:
            recommendations.append("📚 Increase content coverage by improving post discoverability")
        
        results['recommendations'] = recommendations
        
        return results
    
    def print_evaluation_report(self, results: Dict):
        """Print a formatted evaluation report"""
        print("\n" + "="*80)
        print("🎯 SOCIAL HUB RECOMMENDATION SYSTEM EVALUATION REPORT")
        print("="*80)
        
        print(f"\n📊 EVALUATION SUMMARY")
        print(f"   • Timestamp: {results['evaluation_timestamp']}")
        print(f"   • Users Evaluated: {results['users_evaluated']}")
        print(f"   • Successful Evaluations: {results['successful_evaluations']}")
        
        print(f"\n🎯 OVERALL PERFORMANCE")
        print(f"   • Overall Score: {results['overall_score']:.1f}/100")
        print(f"   • Overall Grade: {results['overall_grade']}")
        
        print(f"\n📈 DETAILED METRICS")
        metrics = results['overall_metrics']
        print(f"   • Average CTR: {metrics['average_ctr']:.2f}%")
        print(f"   • Average Precision@10: {metrics['average_precision_at_10']:.2f}%")
        print(f"   • Average Diversity Score: {metrics['average_diversity_score']:.2f}%")
        print(f"   • Average Quality Score: {metrics['average_quality_score']:.2f}%")
        
        print(f"\n🎓 PERFORMANCE GRADES")
        grades = results['performance_grades']
        print(f"   • Engagement Grade: {grades['engagement_grade']}")
        print(f"   • Relevance Grade: {grades['relevance_grade']}")
        print(f"   • Diversity Grade: {grades['diversity_grade']}")
        print(f"   • Quality Grade: {grades['quality_grade']}")
        
        print(f"\n🔧 SYSTEM METRICS")
        coverage = results['system_metrics']['coverage']
        print(f"   • Content Coverage: {coverage['coverage_percentage']:.1f}%")
        print(f"   • Total Posts: {coverage['total_posts']}")
        print(f"   • Recommendable Posts: {coverage['recommendable_posts']}")
        
        print(f"\n🤖 ALGORITHM DISTRIBUTION")
        alg_dist = results['system_metrics']['algorithm_distribution']
        for alg, percentage in alg_dist.items():
            print(f"   • {alg.replace('_', ' ').title()}: {percentage:.1f}%")
        
        if results['recommendations']:
            print(f"\n💡 RECOMMENDATIONS FOR IMPROVEMENT")
            for i, rec in enumerate(results['recommendations'], 1):
                print(f"   {i}. {rec}")
        
        print("\n" + "="*80)

def main():
    """Main evaluation function"""
    print("🔍 Social Hub Recommendation System Evaluator")
    print("=" * 50)
    
    try:
        evaluator = RecommendationEvaluator()
        
        # Run comprehensive evaluation
        results = evaluator.run_comprehensive_evaluation(num_users=25)
        
        # Print detailed report
        evaluator.print_evaluation_report(results)
        
        # Save results to file
        with open(f"recommendation_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to recommendation_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()