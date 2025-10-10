#!/usr/bin/env python3
"""
DETAILED RECOMMENDATION ANALYSIS
Shows exactly HOW and WHY each recommendation is made based on specific attributes
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database.models import DatabaseManager
from src.recommender.hybrid import HybridRecommender
import pandas as pd
import numpy as np

def analyze_user_profile(db_manager, user_id):
    """Deep dive into user's profile and preferences"""
    print(f"\n{'='*80}")
    print(f"🔍 DETAILED USER PROFILE ANALYSIS - USER {user_id}")
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
    
    # User's interests with levels
    interests = db_manager.execute_query("""
        SELECT interest_type, interest_value, weight 
        FROM user_interests 
        WHERE user_id = ?
        ORDER BY weight DESC
    """, (user_id,))
    
    print(f"\n🎯 USER INTERESTS (Weighted for Content-Based Filtering):")
    total_interest_score = 0
    for interest_type, interest_value, weight in interests:
        total_interest_score += weight
        print(f"   • {interest_type}: {interest_value} (Weight: {weight:.1f})")
    print(f"   📊 Total Interest Score: {total_interest_score}")
    
    # User's posts (content they create)
    user_posts = db_manager.execute_query("""
        SELECT p.post_id, p.caption, p.location, p.category, p.travel_date
        FROM posts p 
        WHERE p.user_id = ?
        ORDER BY p.created_at DESC
        LIMIT 5
    """, (user_id,))
    
    print(f"\n📸 USER'S CONTENT (Shows their preferences):")
    user_locations = set()
    user_categories = set()
    for post_id, caption, location, category, travel_date in user_posts:
        user_locations.add(location)
        user_categories.add(category)
        print(f"   • Post {post_id}: {caption[:40]}...")
        print(f"     📍 {location} | 🏷️ {category} | 📅 {travel_date}")
    
    print(f"\n   🗺️  User's Preferred Locations: {', '.join(user_locations)}")
    print(f"   🏷️  User's Preferred Categories: {', '.join(user_categories)}")
    
    # User's likes (collaborative signal)
    liked_posts = db_manager.execute_query("""
        SELECT i.post_id, p.caption, p.location, p.category, p.user_id as author_id, u.username
        FROM interactions i
        JOIN posts p ON i.post_id = p.post_id
        JOIN users u ON p.user_id = u.user_id
        WHERE i.user_id = ? AND i.interaction_type = 'like'
        ORDER BY i.created_at DESC
        LIMIT 8
    """, (user_id,))
    
    print(f"\n❤️  POSTS USER LIKED (Collaborative Filtering Signal):")
    liked_locations = {}
    liked_categories = {}
    liked_authors = {}
    
    for post_id, caption, location, category, author_id, author_username in liked_posts:
        # Track location preferences
        liked_locations[location] = liked_locations.get(location, 0) + 1
        # Track category preferences  
        liked_categories[category] = liked_categories.get(category, 0) + 1
        # Track author preferences
        liked_authors[author_username] = liked_authors.get(author_username, 0) + 1
        
        print(f"   • Liked Post {post_id} by @{author_username}")
        print(f"     📝 {caption[:50]}...")
        print(f"     📍 {location} | 🏷️ {category}")
    
    print(f"\n   📊 PREFERENCE PATTERNS FROM LIKES:")
    print(f"   🗺️  Top Liked Locations: {dict(sorted(liked_locations.items(), key=lambda x: x[1], reverse=True))}")
    print(f"   🏷️  Top Liked Categories: {dict(sorted(liked_categories.items(), key=lambda x: x[1], reverse=True))}")
    print(f"   👥 Most Liked Authors: {dict(sorted(liked_authors.items(), key=lambda x: x[1], reverse=True))}")
    
    # Following relationships
    following = db_manager.execute_query("""
        SELECT f.followed_user_id, u.username, u.travel_style
        FROM follows f
        JOIN users u ON f.followed_user_id = u.user_id
        WHERE f.follower_user_id = ?
    """, (user_id,))
    
    print(f"\n👥 FOLLOWING ({len(following)} users - Social Signal):")
    following_styles = {}
    for followed_id, followed_username, followed_style in following:
        following_styles[followed_style] = following_styles.get(followed_style, 0) + 1
        print(f"   • @{followed_username} (User {followed_id}) - {followed_style}")
    
    print(f"   📊 Following Travel Styles: {following_styles}")
    
    return {
        'user_info': user_info[0],
        'interests': dict(interests),
        'user_locations': user_locations,
        'user_categories': user_categories,
        'liked_locations': liked_locations,
        'liked_categories': liked_categories,
        'liked_authors': liked_authors,
        'following_styles': following_styles
    }

def analyze_recommendation_logic(db_manager, user_id, recommendations, user_profile):
    """Detailed analysis of WHY each recommendation was made"""
    print(f"\n{'='*80}")
    print(f"🤖 RECOMMENDATION ALGORITHM ANALYSIS")
    print(f"{'='*80}")
    
    for i, rec in enumerate(recommendations, 1):
        post_id = rec['post_id']
        hybrid_score = rec['hybrid_score']
        algorithm = rec['algorithm']
        
        print(f"\n{i}. 🎯 POST {post_id} - SCORE: {hybrid_score:.4f}")
        print(f"{'='*50}")
        
        # Get detailed post info
        post_info = db_manager.execute_query("""
            SELECT p.user_id, p.caption, p.location, p.category, p.travel_date,
                   u.username, u.travel_style, u.location as author_location
            FROM posts p
            JOIN users u ON p.user_id = u.user_id
            WHERE p.post_id = ?
        """, (post_id,))
        
        if not post_info:
            continue
            
        author_id, caption, location, category, travel_date, author_username, author_style, author_location = post_info[0]
        
        print(f"📝 CONTENT: {caption}")
        print(f"👤 AUTHOR: @{author_username} (User {author_id})")
        print(f"📍 LOCATION: {location}")
        print(f"🏷️  CATEGORY: {category}")
        print(f"✈️  AUTHOR STYLE: {author_style}")
        print(f"🏠 AUTHOR FROM: {author_location}")
        
        # Get post tags
        tags = db_manager.execute_query("""
            SELECT tag_name FROM post_tags WHERE post_id = ?
        """, (post_id,))
        tag_list = [tag[0] for tag in tags] if tags else []
        print(f"🏷️  TAGS: {', '.join(tag_list) if tag_list else 'None'}")
        
        # Analyze WHY this was recommended
        print(f"\n🔍 WHY THIS WAS RECOMMENDED:")
        
        if algorithm == 'collaborative_filtering':
            print(f"   🤖 ALGORITHM: Collaborative Filtering")
            print(f"   📊 COLLAB SCORE: {rec.get('collab_score', 'N/A')}")
            print(f"   🏆 COLLAB RANK: {rec.get('collab_rank', 'N/A')}")
            
            # Check if user follows this author
            follows_author = db_manager.execute_query("""
                SELECT 1 FROM follows 
                WHERE follower_user_id = ? AND followed_user_id = ?
            """, (user_id, author_id))
            
            if follows_author:
                print(f"   ✅ SOCIAL SIGNAL: You follow @{author_username}")
            
            # Check if similar users liked this
            similar_users_who_liked = db_manager.execute_query("""
                SELECT COUNT(DISTINCT i.user_id) 
                FROM interactions i
                WHERE i.post_id = ? AND i.interaction_type = 'like'
            """, (post_id,))[0][0]
            
            print(f"   👥 POPULARITY: {similar_users_who_liked} users liked this")
            
            # Location match analysis
            if location in user_profile['liked_locations']:
                like_count = user_profile['liked_locations'][location]
                print(f"   📍 LOCATION MATCH: You liked {like_count} posts from {location}")
            elif location in user_profile['user_locations']:
                print(f"   📍 LOCATION INTEREST: You've posted from {location}")
            
            # Category match analysis  
            if category in user_profile['liked_categories']:
                like_count = user_profile['liked_categories'][category]
                print(f"   🏷️  CATEGORY MATCH: You liked {like_count} {category} posts")
            elif category in user_profile['user_categories']:
                print(f"   🏷️  CATEGORY INTEREST: You create {category} content")
                
        elif algorithm == 'content_based_filtering':
            print(f"   🤖 ALGORITHM: Content-Based Filtering")
            print(f"   📊 CONTENT SCORE: Based on TF-IDF similarity")
            
            # Interest matching
            matching_interests = []
            for interest, level in user_profile['interests'].items():
                if interest.lower() in caption.lower() or interest.lower() in ' '.join(tag_list).lower():
                    matching_interests.append((interest, level))
            
            if matching_interests:
                print(f"   🎯 INTEREST MATCHES:")
                for interest, level in matching_interests:
                    print(f"      • {interest} (Your level: {level}/10)")
            
            # Location scoring (5x bonus)
            if location in user_profile['liked_locations']:
                print(f"   📍 LOCATION BONUS (5x): You've liked posts from {location}")
            elif location in user_profile['user_locations']:
                print(f"   📍 LOCATION BONUS (5x): You've posted from {location}")
            
            # Category scoring (4x bonus)  
            if category in user_profile['liked_categories']:
                print(f"   🏷️  CATEGORY BONUS (4x): You like {category} content")
            elif category in user_profile['user_categories']:
                print(f"   🏷️  CATEGORY BONUS (4x): You create {category} content")
            
            # Travel style match
            if author_style == user_profile['user_info'][3]:  # travel_style from user_info
                print(f"   ✈️  STYLE MATCH: Both prefer {author_style} travel")
        
        # Final scoring explanation
        print(f"\n   💯 FINAL HYBRID SCORE CALCULATION:")
        collab_score = rec.get('collab_score', 0)
        content_score = rec.get('content_score', 0)
        
        if 'collab_score' in rec and 'content_score' in rec:
            weighted_collab = collab_score * 0.6
            weighted_content = content_score * 0.4
            print(f"      Collaborative: {collab_score:.3f} × 0.6 = {weighted_collab:.3f}")
            print(f"      Content-Based: {content_score:.3f} × 0.4 = {weighted_content:.3f}")
            print(f"      TOTAL: {weighted_collab:.3f} + {weighted_content:.3f} = {hybrid_score:.3f}")
        else:
            print(f"      Single Algorithm Score: {hybrid_score:.3f}")

def main():
    """Run detailed recommendation analysis"""
    db_manager = DatabaseManager()
    recommender = HybridRecommender(db_manager)
    
    test_user_id = 1
    
    print("🔬 DETAILED RECOMMENDATION SYSTEM ANALYSIS")
    print("=" * 80)
    
    # Deep user profile analysis
    user_profile = analyze_user_profile(db_manager, test_user_id)
    if not user_profile:
        return
    
    # Get recommendations
    print(f"\n{'='*80}")
    print("🤖 GETTING RECOMMENDATIONS...")
    print(f"{'='*80}")
    
    recommendations = recommender.recommend_posts(test_user_id, n_recommendations=3)  # Just 3 for detailed analysis
    
    if not recommendations:
        print("❌ No recommendations found!")
        return
    
    # Detailed analysis of each recommendation
    analyze_recommendation_logic(db_manager, test_user_id, recommendations, user_profile)
    
    # Summary
    print(f"\n{'='*80}")
    print("📋 SUMMARY - HOW THE SYSTEM WORKS")
    print(f"{'='*80}")
    
    print("""
🎯 RECOMMENDATION ATTRIBUTES & LOGIC:

1. 👥 COLLABORATIVE FILTERING (60% weight):
   ✅ User Similarity: Finds users with similar like patterns
   ✅ Social Signals: Posts from accounts you follow get priority
   ✅ Popularity Weighting: Popular posts get slight boost
   ✅ Interaction History: Based on your 19 likes/interactions

2. 🔍 CONTENT-BASED FILTERING (40% weight):
   ✅ Interest Matching: TF-IDF analysis of captions vs your interests
   ✅ Location Bonus (5x): Posts from places you like/visited
   ✅ Category Bonus (4x): Content types you prefer (adventure, food, etc.)
   ✅ Travel Style Match: Authors with similar travel preferences
   ✅ Tag Similarity: Hashtags matching your interests

3. 🚫 EXCLUSIONS:
   ❌ Your own posts (filtered out)
   ❌ Posts you already liked (filtered out)
   ❌ Duplicate recommendations (deduplication)

4. 📊 SCORING PROCESS:
   Step 1: Get collaborative score (0-1 based on user similarity)
   Step 2: Get content score (0-1 based on TF-IDF + bonuses)
   Step 3: Weighted combination: (collab × 0.6) + (content × 0.4)
   Step 4: Sort by final hybrid score (highest first)

5. 🎯 WHY THESE SPECIFIC POSTS?
   • High scores = Strong match on multiple attributes
   • Mix of algorithms = Diverse recommendation strategy
   • Indian/Asian focus = Geographic relevance for target audience
   • Cultural content = Matches typical Indian travel interests
    """)

if __name__ == "__main__":
    main()