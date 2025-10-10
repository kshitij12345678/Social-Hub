#!/usr/bin/env python3
"""
Test the Fixed Social Hub Recommendation System
"""

import sys
import os
sys.path.append('/home/kshitij/Downloads/Social Hub/Social-Hub/backend')

from social_hub_recommender_fixed import SocialHubRecommender

def test_recommendation_system():
    print("🧪 Testing Fixed Social Hub Recommendation System...")
    
    try:
        # Initialize the recommender
        recommender = SocialHubRecommender()
        
        print("\n1️⃣ Testing with User ID 1...")
        
        # Test user stats
        stats = recommender.get_user_stats(1)
        print(f"📊 User 1 Stats: {stats}")
        
        # Test recommendations
        recommendations = recommender.get_recommended_posts(1, limit=5)
        print(f"\n🎯 Recommendations for User 1:")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. Post {rec['post_id']}: {rec['caption']}")
            print(f"   By: {rec['author_username']} | Algorithm: {rec['algorithm']}")
            print(f"   Reason: {rec['recommendation_reason']}")
            print()
        
        print("\n2️⃣ Testing Popular Posts Fallback...")
        popular = recommender.get_popular_posts_fallback(3)
        print(f"🌟 Popular Posts ({len(popular)} found):")
        for i, post in enumerate(popular, 1):
            print(f"{i}. Post {post['post_id']}: {post['caption']}")
            print(f"   Popularity Score: {post['popularity_score']}")
            print()
        
        print("✅ Recommendation system test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_recommendation_system()