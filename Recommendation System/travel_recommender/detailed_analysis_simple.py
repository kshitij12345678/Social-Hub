#!/usr/bin/env python3
"""
SIMPLIFIED DETAILED ANALYSIS - Works with current database structure
Shows exactly HOW and WHY each recommendation is made
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database.models import DatabaseManager
from src.recommender.hybrid import HybridRecommender

def analyze_user_profile_simple(db_manager, user_id):
    """Simple user profile analysis using available data"""
    print(f"\n{'='*80}")
    print(f"🔍 USER PROFILE ANALYSIS - USER {user_id}")
    print(f"{'='*80}")
    
    # Basic user info
    user_info = db_manager.execute_query("""
        SELECT username, full_name, location, travel_style, bio
        FROM users WHERE user_id = ?
    """, (user_id,))
    
    if not user_info:
        print(f"❌ User {user_id} not found!")
        return None
        
    username, full_name, location, travel_style, bio = user_info[0]
    print(f"👤 USER: {full_name} (@{username})")
    print(f"📍 Location: {location}")
    print(f"✈️  Travel Style: {travel_style}")
    print(f"📝 Bio: {bio}")
    
    # User's posts
    user_posts = db_manager.execute_query("""
        SELECT p.post_id, p.caption, l.name as location, l.category
        FROM posts p
        LEFT JOIN locations l ON p.location_id = l.location_id
        WHERE p.user_id = ?
        ORDER BY p.created_at DESC
        LIMIT 5
    """, (user_id,))
    
    print(f"\n📸 USER'S POSTS ({len(user_posts)} shown):")
    user_locations = set()
    user_categories = set()
    for post_id, caption, location, category in user_posts:
        if location:
            user_locations.add(location)
        if category:
            user_categories.add(category)
        print(f"   • Post {post_id}: {caption[:50]}...")
        print(f"     📍 {location or 'Unknown'} | 🏷️ {category or 'Unknown'}")
    
    # User's interactions
    interactions = db_manager.execute_query("""
        SELECT i.post_id, p.caption, l.name as location, l.category, p.user_id as author_id
        FROM interactions i
        JOIN posts p ON i.post_id = p.post_id
        LEFT JOIN locations l ON p.location_id = l.location_id
        WHERE i.user_id = ? AND i.interaction_type = 'like'
        ORDER BY i.timestamp DESC
        LIMIT 10
    """, (user_id,))
    
    print(f"\n❤️  USER'S LIKES ({len(interactions)} shown):")
    liked_locations = {}
    liked_categories = {}
    for post_id, caption, location, category, author_id in interactions:
        if location:
            liked_locations[location] = liked_locations.get(location, 0) + 1
        if category:
            liked_categories[category] = liked_categories.get(category, 0) + 1
        print(f"   • Liked Post {post_id} by User {author_id}")
        print(f"     📝 {caption[:40]}...")
        print(f"     📍 {location or 'Unknown'} | 🏷️ {category or 'Unknown'}")
    
    print(f"\n📊 PREFERENCE PATTERNS:")
    print(f"   🗺️  Liked Locations: {dict(sorted(liked_locations.items(), key=lambda x: x[1], reverse=True))}")
    print(f"   🏷️  Liked Categories: {dict(sorted(liked_categories.items(), key=lambda x: x[1], reverse=True))}")
    
    # Following
    following = db_manager.execute_query("""
        SELECT f.following_id, u.username, u.travel_style
        FROM follows f
        JOIN users u ON f.following_id = u.user_id
        WHERE f.follower_id = ?
        LIMIT 5
    """, (user_id,))
    
    print(f"\n👥 FOLLOWING ({len(following)} users):")
    for followed_id, followed_username, followed_style in following:
        print(f"   • @{followed_username} (User {followed_id}) - {followed_style}")
    
    return {
        'user_info': user_info[0],
        'user_locations': user_locations,
        'user_categories': user_categories,
        'liked_locations': liked_locations,
        'liked_categories': liked_categories,
        'following': [f[0] for f in following]
    }

def analyze_recommendation_detailed(db_manager, user_id, recommendations, user_profile):
    """Detailed analysis of each recommendation"""
    print(f"\n{'='*80}")
    print(f"🤖 DETAILED RECOMMENDATION ANALYSIS")
    print(f"{'='*80}")
    
    for i, rec in enumerate(recommendations, 1):
        post_id = rec['post_id']
        score = rec['hybrid_score']
        algorithm = rec['algorithm']
        
        print(f"\n{i}. 🎯 POST {post_id} - HYBRID SCORE: {score:.4f}")
        print(f"{'='*60}")
        
        # Get post details
        post_details = db_manager.execute_query("""
            SELECT p.user_id, p.caption, l.name as location, l.category, l.country,
                   u.username, u.travel_style, u.location as author_location
            FROM posts p
            LEFT JOIN locations l ON p.location_id = l.location_id
            JOIN users u ON p.user_id = u.user_id
            WHERE p.post_id = ?
        """, (post_id,))
        
        if not post_details:
            continue
            
        author_id, caption, location, category, country, author_username, author_style, author_location = post_details[0]
        
        print(f"📝 CAPTION: {caption}")
        print(f"👤 AUTHOR: @{author_username} (User {author_id}) from {author_location}")
        print(f"📍 LOCATION: {location or 'Unknown'}, {country or 'Unknown'}")
        print(f"🏷️  CATEGORY: {category or 'Unknown'}")
        print(f"✈️  AUTHOR'S STYLE: {author_style}")
        
        # Get tags
        tags = db_manager.execute_query("""
            SELECT tag_name FROM post_tags WHERE post_id = ?
        """, (post_id,))
        tag_list = [tag[0] for tag in tags] if tags else []
        print(f"🏷️  TAGS: {', '.join(tag_list) if tag_list else 'None'}")
        
        # Get popularity
        like_count = db_manager.execute_query("""
            SELECT COUNT(*) FROM interactions 
            WHERE post_id = ? AND interaction_type = 'like'
        """, (post_id,))[0][0]
        print(f"❤️  POPULARITY: {like_count} likes")
        
        print(f"\n🔍 WHY THIS WAS RECOMMENDED:")
        print(f"   🤖 PRIMARY ALGORITHM: {algorithm}")
        
        if 'collab_score' in rec:
            print(f"   👥 COLLABORATIVE SCORE: {rec['collab_score']:.4f}")
            print(f"   🏆 COLLABORATIVE RANK: {rec.get('collab_rank', 'N/A')}")
        
        if 'content_score' in rec:
            print(f"   📝 CONTENT SCORE: {rec.get('content_score', 'N/A')}")
        
        # Analyze matching factors
        print(f"\n   ✅ MATCHING FACTORS:")
        
        # Check if user follows author
        if author_id in user_profile['following']:
            print(f"      🤝 SOCIAL: You follow @{author_username}")
        
        # Location match
        if location and location in user_profile['liked_locations']:
            count = user_profile['liked_locations'][location]
            print(f"      📍 LOCATION MATCH: You liked {count} posts from {location}")
        elif location and location in user_profile['user_locations']:
            print(f"      📍 LOCATION INTEREST: You posted from {location}")
        
        # Category match
        if category and category in user_profile['liked_categories']:
            count = user_profile['liked_categories'][category]
            print(f"      🏷️  CATEGORY MATCH: You liked {count} {category} posts")
        elif category and category in user_profile['user_categories']:
            print(f"      🏷️  CATEGORY INTEREST: You create {category} content")
        
        # Travel style match
        if author_style == user_profile['user_info'][3]:  # travel_style
            print(f"      ✈️  STYLE MATCH: Both prefer {author_style} travel")
        
        # Content keywords (simple analysis)
        user_bio = user_profile['user_info'][4].lower()  # bio
        caption_lower = caption.lower()
        common_words = set(user_bio.split()) & set(caption_lower.split())
        if common_words:
            print(f"      📝 CONTENT KEYWORDS: {', '.join(list(common_words)[:3])}")
        
        print(f"\n   💯 SCORE BREAKDOWN:")
        if algorithm == 'collaborative_filtering':
            print(f"      • Based on users with similar preferences")
            print(f"      • Weighted by social signals and popularity")
        elif algorithm == 'content_based_filtering':
            print(f"      • Based on content similarity (TF-IDF)")
            print(f"      • Location bonus (5x) and category bonus (4x) applied")
        else:
            print(f"      • Hybrid combination of collaborative + content")

def main():
    """Run simplified detailed analysis"""
    
    print("🔬 DETAILED RECOMMENDATION ANALYSIS")
    print("=" * 80)
    
    db_manager = DatabaseManager()
    recommender = HybridRecommender(db_manager)
    
    test_user_id = 1
    
    # Analyze user profile
    user_profile = analyze_user_profile_simple(db_manager, test_user_id)
    if not user_profile:
        return
    
    # Get recommendations
    print(f"\n{'='*80}")
    print("🤖 GETTING RECOMMENDATIONS...")
    print(f"{'='*80}")
    
    recommendations = recommender.recommend_posts(test_user_id, n_recommendations=3)
    
    if not recommendations:
        print("❌ No recommendations found!")
        return
    
    # Analyze each recommendation
    analyze_recommendation_detailed(db_manager, test_user_id, recommendations, user_profile)
    
    # Summary
    print(f"\n{'='*80}")
    print("📋 HOW THE RECOMMENDATION SYSTEM WORKS")
    print(f"{'='*80}")
    
    print("""
🎯 RECOMMENDATION ATTRIBUTES SUMMARY:

1. 👥 COLLABORATIVE FILTERING (Primary):
   • Finds users with similar interaction patterns
   • Recommends posts liked by similar users
   • Considers social connections (follows)
   • Weights by popularity and engagement

2. 🔍 CONTENT-BASED FILTERING (Secondary):
   • TF-IDF analysis of post captions
   • Location matching (5x bonus for familiar places)
   • Category matching (4x bonus for preferred types)
   • Travel style compatibility
   • Keyword/interest alignment

3. 🔄 HYBRID COMBINATION:
   • 60% Collaborative + 40% Content-based weighting
   • Automatic fallback if one method fails
   • Deduplication and relevance filtering
   • Excludes user's own posts and already-liked content

4. 📊 SCORING FACTORS:
   ✅ User similarity (collaborative)
   ✅ Content similarity (TF-IDF)
   ✅ Location preferences
   ✅ Category preferences  
   ✅ Social connections
   ✅ Travel style match
   ✅ Popularity signals
   ✅ Recency and engagement

The system learns from your interactions to find the most relevant travel content! 🌍✈️
    """)

if __name__ == "__main__":
    main()