"""
Debug script to check how the system handles non-existent users
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from src.database.models import DatabaseManager
from src.recommender.hybrid import HybridRecommender

def debug_non_existent_user():
    print("🔍 DEBUGGING NON-EXISTENT USER HANDLING")
    print("=" * 50)
    
    db = DatabaseManager()
    hybrid = HybridRecommender(db)
    
    # Test with non-existent user
    fake_user_id = 9999
    
    print(f"\n1. Checking if user {fake_user_id} exists:")
    user_exists = db.execute_query("SELECT COUNT(*) FROM users WHERE user_id = ?", (fake_user_id,))
    print(f"   User exists: {user_exists[0][0] > 0}")
    
    print(f"\n2. Checking interactions for user {fake_user_id}:")
    interactions = db.execute_query("SELECT COUNT(*) FROM interactions WHERE user_id = ?", (fake_user_id,))
    print(f"   Interaction count: {interactions[0][0]}")
    
    print(f"\n3. Testing content-based recommendations:")
    try:
        content_recs = hybrid.content_based.recommend_posts_content_based(fake_user_id, 5)
        print(f"   Content-based returned: {len(content_recs)} recommendations")
        
        if len(content_recs) > 0:
            print("   ❌ This is WRONG - should not recommend for non-existent user!")
            print("   First recommendation:", content_recs[0])
        else:
            print("   ✅ Correctly returned no recommendations")
            
    except Exception as e:
        print(f"   Exception: {e}")
    
    print(f"\n4. Testing hybrid recommendations:")
    try:
        hybrid_recs = hybrid.recommend_posts(fake_user_id, 5)
        print(f"   Hybrid returned: {len(hybrid_recs)} recommendations")
        
        if len(hybrid_recs) > 0:
            print("   ❌ This is WRONG - should validate user exists first!")
            for i, rec in enumerate(hybrid_recs[:3], 1):
                approach = rec.get('hybrid_approach', 'unknown')
                print(f"     {i}. {rec.get('caption', '')[:50]}... (Approach: {approach})")
        else:
            print("   ✅ Correctly returned no recommendations")
            
    except Exception as e:
        print(f"   Exception: {e}")
    
    print(f"\n5. What SHOULD happen:")
    print("   - Check if user exists in database")
    print("   - If user doesn't exist, return empty list or error")
    print("   - Don't generate recommendations for non-existent users")
    
    print(f"\n6. Testing with existing user for comparison:")
    existing_user = 1
    try:
        existing_recs = hybrid.recommend_posts(existing_user, 3)
        print(f"   Existing user {existing_user}: {len(existing_recs)} recommendations")
        print("   ✅ This is correct behavior")
    except Exception as e:
        print(f"   Exception with existing user: {e}")

if __name__ == "__main__":
    debug_non_existent_user()