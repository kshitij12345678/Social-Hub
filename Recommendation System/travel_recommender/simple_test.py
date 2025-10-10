#!/usr/bin/env python3
"""
Simple Test Case for Manual Verification
Tests the hybrid recommender with User ID 1 and shows what we should expect
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database.models import DatabaseManager
from src.recommender.hybrid import HybridRecommender

def test_user_1_recommendations():
    """Test recommendations for User 1 and show expected output"""
    
    print("🔍 SIMPLE TEST: User 1 Recommendations")
    print("=" * 50)
    
    # Initialize
    db_manager = DatabaseManager()
    recommender = HybridRecommender(db_manager)
    
    # Test user
    user_id = 1
    
    print(f"Testing recommendations for User {user_id}...")
    
    # Get recommendations
    try:
        recommendations = recommender.recommend_posts(user_id, n_recommendations=5)
        
        print(f"\n✅ SUCCESS: Got {len(recommendations)} recommendations")
        print("\n📋 RECOMMENDATIONS:")
        print("-" * 30)
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                post_id = rec['post_id']
                score = rec['hybrid_score']
                caption = rec['caption'][:50] + "..." if len(rec['caption']) > 50 else rec['caption']
                author = rec['author_username']
                location = rec['location']
                algorithm = rec['algorithm']
                print(f"{i}. Post {post_id} - Score: {score:.4f}")
                print(f"   📝 {caption}")
                print(f"   👤 by @{author} from {location}")
                print(f"   🤖 Algorithm: {algorithm}")
                print()
            
        print("\n" + "=" * 50)
        print("🎯 EXPECTED OUTPUT EXPLANATION:")
        print("=" * 50)
        
        print("""
WHAT YOU SHOULD SEE:

1. ✅ SUCCESS MESSAGE: "Got X recommendations" 
   - If X > 0: System is working, found relevant posts
   - If X = 0: Either no data OR user has no suitable recommendations

2. 📊 RECOMMENDATION FORMAT:
   - Each line shows: "Post [ID] - Score: [0.XXXX]"
   - Post IDs should be different numbers (not user 1's own posts)
   - Scores should be between 0.0000 and 1.0000
   - Scores should be in DESCENDING order (highest first)

3. 🔍 WHAT SCORES MEAN:
   - Score > 0.8: Excellent match (user likes similar content)
   - Score 0.6-0.8: Good match (some similarity in preferences)  
   - Score 0.4-0.6: Moderate match (weak similarity)
   - Score < 0.4: Poor match (minimal relevance)

4. ✅ VERIFICATION CHECKLIST:
   - Are there 5 recommendations (or fewer if limited data)?
   - Are scores in descending order?
   - Are post IDs reasonable numbers?
   - No error messages?

5. 🚨 IF YOU SEE PROBLEMS:
   - "Got 0 recommendations" = Need to check data or algorithm
   - Error messages = Code issue to fix
   - Duplicate post IDs = Bug in deduplication
   - Scores > 1.0 or < 0.0 = Scoring algorithm issue
        """)
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print("\n🔧 This means there's a bug to fix!")

if __name__ == "__main__":
    test_user_1_recommendations()