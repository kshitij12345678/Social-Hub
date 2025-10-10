#!/usr/bin/env python3
"""
Manual Verification Test for Recommendation System
This test shows detailed recommendations for a specific user so you can manually verify the logic.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database.models import DatabaseManager
from src.recommender.hybrid import HybridRecommender

def print_user_profile(db_manager, user_id):
    """Print detailed user profile for manual verification"""
    print(f"\n{'='*60}")
    print(f"USER PROFILE ANALYSIS FOR USER {user_id}")
    print(f"{'='*60}")
    
    # Get user details
    user_info = db_manager.execute_query(
        "SELECT name, age, location FROM users WHERE user_id = ?", 
        (user_id,)
    )
    
    if not user_info:
        print(f"❌ User {user_id} does not exist!")
        return False
        
    user = user_info[0]
    print(f"👤 User: {user[0]} (Age: {user[1]}, Location: {user[2]})")
    
    # Get user's interests
    interests = db_manager.execute_query("""
        SELECT ui.interest, ui.interest_level 
        FROM user_interests ui 
        WHERE ui.user_id = ?
        ORDER BY ui.interest_level DESC
    """, (user_id,))
    
    print(f"\n🎯 User Interests:")
    for interest, level in interests:
        print(f"   • {interest}: {level}/10")
    
    # Get user's posts
    user_posts = db_manager.execute_query("""
        SELECT p.post_id, p.caption, p.location, p.category
        FROM posts p 
        WHERE p.user_id = ?
        ORDER BY p.post_id DESC
        LIMIT 5
    """, (user_id,))
    
    print(f"\n📸 User's Recent Posts:")
    for post_id, caption, location, category in user_posts:
        print(f"   • Post {post_id}: {caption[:50]}...")
        print(f"     Location: {location}, Category: {category}")
    
    # Get user's interactions (likes)
    interactions = db_manager.execute_query("""
        SELECT i.post_id, p.caption, p.location, p.category, p.user_id as post_author
        FROM interactions i
        JOIN posts p ON i.post_id = p.post_id
        WHERE i.user_id = ? AND i.interaction_type = 'like'
        ORDER BY i.post_id DESC
        LIMIT 10
    """, (user_id,))
    
    print(f"\n❤️  User's Recent Likes ({len(interactions)} shown):")
    for post_id, caption, location, category, author_id in interactions:
        print(f"   • Liked Post {post_id} by User {author_id}")
        print(f"     Content: {caption[:40]}...")
        print(f"     Location: {location}, Category: {category}")
    
    # Get users this user follows
    following = db_manager.execute_query("""
        SELECT f.followed_user_id, u.name 
        FROM follows f
        JOIN users u ON f.followed_user_id = u.user_id
        WHERE f.follower_user_id = ?
        LIMIT 5
    """, (user_id,))
    
    print(f"\n👥 Following:")
    for followed_id, followed_name in following:
        print(f"   • User {followed_id}: {followed_name}")
    
    return True

def print_recommendations_analysis(db_manager, user_id, recommendations):
    """Print detailed analysis of why each post was recommended"""
    print(f"\n{'='*60}")
    print(f"RECOMMENDATION ANALYSIS FOR USER {user_id}")
    print(f"{'='*60}")
    
    if not recommendations:
        print("❌ No recommendations found!")
        return
    
    print(f"✅ Found {len(recommendations)} recommendations:")
    
    for i, (post_id, score) in enumerate(recommendations, 1):
        # Get post details
        post_info = db_manager.execute_query("""
            SELECT p.user_id, p.caption, p.location, p.category, u.name
            FROM posts p
            JOIN users u ON p.user_id = u.user_id
            WHERE p.post_id = ?
        """, (post_id,))
        
        if not post_info:
            continue
            
        author_id, caption, location, category, author_name = post_info[0]
        
        print(f"\n{i}. 📍 Post {post_id} (Score: {score:.3f})")
        print(f"   👤 Author: {author_name} (User {author_id})")
        print(f"   📝 Caption: {caption[:60]}...")
        print(f"   📍 Location: {location}")
        print(f"   🏷️  Category: {category}")
        
        # Check if user follows the author
        follows_author = db_manager.execute_query("""
            SELECT 1 FROM follows 
            WHERE follower_user_id = ? AND followed_user_id = ?
        """, (user_id, author_id))
        
        if follows_author:
            print(f"   👥 ✅ You follow this author")
        
        # Get post tags
        tags = db_manager.execute_query("""
            SELECT tag FROM post_tags WHERE post_id = ?
        """, (post_id,))
        
        if tags:
            tag_list = [tag[0] for tag in tags]
            print(f"   🏷️  Tags: {', '.join(tag_list)}")
        
        # Check how many people liked this post
        like_count = db_manager.execute_query("""
            SELECT COUNT(*) FROM interactions 
            WHERE post_id = ? AND interaction_type = 'like'
        """, (post_id,))[0][0]
        
        print(f"   ❤️  {like_count} likes")

def expected_recommendations_for_user_1():
    """Explain what we should expect for User 1"""
    print(f"\n{'='*60}")
    print("EXPECTED RECOMMENDATIONS ANALYSIS")
    print(f"{'='*60}")
    
    print("""
🎯 WHAT TO EXPECT FOR USER 1:

Based on our recommendation system logic, User 1 should get recommendations that:

1. 📊 COLLABORATIVE FILTERING (60% weight):
   - Posts liked by users with similar interaction patterns
   - Users who liked similar posts to User 1's likes
   - Higher scores for posts from users with overlapping interests

2. 🔍 CONTENT-BASED FILTERING (40% weight):
   - Posts matching User 1's interests (adventure, photography, etc.)
   - Posts from similar locations to User 1's posts/likes
   - Posts with similar tags/categories to User 1's preferences
   - 5x bonus for location matches, 4x for category matches

3. 🚫 EXCLUSIONS:
   - User 1's own posts (excluded)
   - Posts User 1 already liked (excluded)

4. ⭐ EXPECTED CHARACTERISTICS:
   - High scores (0.8-1.0) for perfect matches
   - Medium scores (0.4-0.7) for partial matches  
   - Diverse mix of adventure, photography, and travel content
   - Posts from locations User 1 has shown interest in
   - Content from users with similar travel preferences

5. 📈 SCORE INTERPRETATION:
   - Score > 0.8: Excellent match (similar users + content match)
   - Score 0.6-0.8: Good match (either collaborative or content strong)
   - Score 0.4-0.6: Moderate match (some similarity)
   - Score < 0.4: Weak match (minimal similarity)
    """)

def main():
    """Run comprehensive manual verification test"""
    db_manager = DatabaseManager()
    recommender = HybridRecommender(db_manager)
    
    # Test with User 1 (should have good data)
    test_user_id = 1
    
    print("🔍 MANUAL VERIFICATION TEST FOR RECOMMENDATION SYSTEM")
    print("=" * 60)
    
    # Show user profile first
    if not print_user_profile(db_manager, test_user_id):
        return
    
    # Show expected recommendations
    expected_recommendations_for_user_1()
    
    # Get actual recommendations
    print(f"\n{'='*60}")
    print("GETTING ACTUAL RECOMMENDATIONS...")
    print(f"{'='*60}")
    
    recommendations = recommender.recommend_posts_hybrid(test_user_id, num_recommendations=8)
    
    # Analyze recommendations
    print_recommendations_analysis(db_manager, test_user_id, recommendations)
    
    # Summary for manual verification
    print(f"\n{'='*60}")
    print("MANUAL VERIFICATION CHECKLIST")
    print(f"{'='*60}")
    
    print("""
✅ VERIFY THESE POINTS:

1. 🚫 NO SELF-POSTS: None of the recommended posts should be by User 1
2. 🚫 NO ALREADY-LIKED: None should be posts User 1 already liked  
3. 📊 RELEVANCE: Posts should match User 1's interests (adventure, photography)
4. 📍 LOCATION LOGIC: Higher scores for posts from similar/interesting locations
5. 👥 SOCIAL SIGNALS: Some posts should be from users User 1 follows
6. 🏷️  TAG MATCHING: Posts should have relevant tags/categories
7. 📈 SCORE ORDERING: Scores should be in descending order
8. 🎯 VARIETY: Should see mix of content types, not all identical

❓ QUESTIONS TO ASK:
- Do the recommended posts make sense for this user's profile?
- Are the scores reasonable and properly ordered?
- Is there good variety in the recommendations?
- Do location and interest matches get higher scores?
    """)

if __name__ == "__main__":
    main()