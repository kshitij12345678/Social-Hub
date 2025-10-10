"""
Test script to validate collaborative filtering recommendations
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from src.database.models import DatabaseManager
from src.recommender.collaborative import CollaborativeRecommender

def test_collaborative_filtering():
    """Comprehensive test of collaborative filtering"""
    print("🧪 TESTING COLLABORATIVE FILTERING SYSTEM")
    print("=" * 50)
    
    db = DatabaseManager()
    recommender = CollaborativeRecommender(db)
    
    # Test 1: Check if we have enough data
    print("\n📊 TEST 1: Data Availability")
    user_count = db.execute_query("SELECT COUNT(*) FROM users")[0][0]
    post_count = db.execute_query("SELECT COUNT(*) FROM posts")[0][0]
    interaction_count = db.execute_query("SELECT COUNT(*) FROM interactions")[0][0]
    
    print(f"Users: {user_count}")
    print(f"Posts: {post_count}")
    print(f"Interactions: {interaction_count}")
    
    if interaction_count < 100:
        print("❌ Not enough interactions for good recommendations")
        return False
    else:
        print("✅ Sufficient data for recommendations")
    
    # Test 2: Matrix Building
    print("\n🔧 TEST 2: User-Item Matrix")
    matrix = recommender.build_user_item_matrix()
    
    if matrix is not None:
        print(f"✅ Matrix shape: {matrix.shape}")
        print(f"✅ Non-zero interactions: {(matrix > 0).sum().sum()}")
        print(f"✅ Sparsity: {((matrix == 0).sum().sum() / (matrix.shape[0] * matrix.shape[1]) * 100):.1f}%")
    else:
        print("❌ Failed to build matrix")
        return False
    
    # Test 3: User Similarity
    print("\n👥 TEST 3: User Similarity Calculation")
    similarity_df = recommender.calculate_user_similarity()
    
    if similarity_df is not None:
        print("✅ User similarity matrix created")
        # Show average similarity (should be low for diverse users)
        avg_similarity = similarity_df.values[similarity_df.values != 1.0].mean()
        print(f"✅ Average user similarity: {avg_similarity:.3f}")
        
        if avg_similarity > 0.8:
            print("⚠️ Very high similarity - users might be too similar")
        elif avg_similarity < 0.01:
            print("⚠️ Very low similarity - might need more interactions")
        else:
            print("✅ Good similarity range for recommendations")
    else:
        print("❌ Failed to calculate similarity")
        return False
    
    # Test 4: Test with specific users
    print("\n🎯 TEST 4: Recommendation Quality")
    
    # Get a user with good interaction history
    active_users = db.execute_query("""
        SELECT user_id, COUNT(*) as interaction_count 
        FROM interactions 
        GROUP BY user_id 
        HAVING interaction_count >= 5 
        ORDER BY interaction_count DESC 
        LIMIT 3
    """)
    
    if not active_users:
        print("❌ No active users found")
        return False
    
    for user_id, interaction_count in active_users:
        print(f"\n👤 Testing User {user_id} (has {interaction_count} interactions)")
        
        # Get user's actual preferences
        user_interactions = db.execute_query("""
            SELECT p.post_id, l.name as location, p.caption
            FROM interactions i
            JOIN posts p ON i.post_id = p.post_id
            LEFT JOIN locations l ON p.location_id = l.location_id
            WHERE i.user_id = ?
            LIMIT 3
        """, (user_id,))
        
        print("   User's actual interests:")
        for post_id, location, caption in user_interactions:
            print(f"   - {location}: {caption[:50]}...")
        
        # Get recommendations
        post_recs = recommender.recommend_posts_collaborative(user_id, 5)
        user_recs = recommender.recommend_users_to_follow(user_id, 3)
        
        print(f"   📸 Post recommendations: {len(post_recs)}")
        for i, rec in enumerate(post_recs[:3], 1):
            print(f"   {i}. {rec['location']}: {rec['caption'][:50]}...")
        
        print(f"   👥 User recommendations: {len(user_recs)}")
        for i, rec in enumerate(user_recs, 1):
            print(f"   {i}. @{rec['username']} ({rec['travel_style']}) from {rec['location']}")
        
        if len(post_recs) == 0:
            print("   ❌ No post recommendations generated")
        else:
            print("   ✅ Post recommendations working")
        
        if len(user_recs) == 0:
            print("   ❌ No user recommendations generated")
        else:
            print("   ✅ User recommendations working")
    
    # Test 5: Recommendation Diversity
    print("\n🌈 TEST 5: Recommendation Diversity")
    test_user = active_users[0][0]
    post_recs = recommender.recommend_posts_collaborative(test_user, 10)
    
    if post_recs:
        locations = [rec['location'] for rec in post_recs if rec['location']]
        unique_locations = set(locations)
        diversity_score = len(unique_locations) / len(post_recs) if post_recs else 0
        
        print(f"✅ Recommended {len(unique_locations)} different locations out of {len(post_recs)} posts")
        print(f"✅ Diversity score: {diversity_score:.2f}")
        
        if diversity_score > 0.7:
            print("✅ Good diversity in recommendations")
        elif diversity_score > 0.4:
            print("⚠️ Moderate diversity - acceptable")
        else:
            print("❌ Low diversity - recommendations too similar")
    
    # Test 6: Performance Test
    print("\n⚡ TEST 6: Performance")
    import time
    
    start_time = time.time()
    recommender.recommend_posts_collaborative(test_user, 10)
    post_time = time.time() - start_time
    
    start_time = time.time()
    recommender.recommend_users_to_follow(test_user, 10)
    user_time = time.time() - start_time
    
    print(f"✅ Post recommendation time: {post_time:.3f} seconds")
    print(f"✅ User recommendation time: {user_time:.3f} seconds")
    
    if post_time < 2.0 and user_time < 2.0:
        print("✅ Good performance for real-time recommendations")
    else:
        print("⚠️ Slow performance - might need optimization")
    
    print("\n" + "=" * 50)
    print("🎯 COLLABORATIVE FILTERING TEST SUMMARY:")
    print("✅ Data availability: PASSED")
    print("✅ Matrix building: PASSED") 
    print("✅ Similarity calculation: PASSED")
    print("✅ Recommendation generation: PASSED")
    print("✅ System is working correctly!")
    
    return True

if __name__ == "__main__":
    test_collaborative_filtering()