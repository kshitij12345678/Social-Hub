"""
TRAVEL RECOMMENDATION SYSTEM - THEORETICAL FLOW ANALYSIS
========================================================

This document provides a comprehensive theoretical view of how the travel recommendation
system works, including the exact flow and mathematical foundations.

SYSTEM ARCHITECTURE OVERVIEW:
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          HYBRID RECOMMENDATION SYSTEM                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│  INPUT: User ID                                                                 │
│  OUTPUT: Ranked list of recommended posts with scores                          │
│                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│  │  COLLABORATIVE  │    │  CONTENT-BASED  │    │    HYBRID       │            │
│  │   FILTERING     │────│   FILTERING     │────│   COMBINER      │            │
│  │   (60% weight)  │    │   (40% weight)  │    │  (Final Score)  │            │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘            │
└─────────────────────────────────────────────────────────────────────────────────┘
"""

import sqlite3
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sys
import os

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.models import get_db_connection
from src.recommender.hybrid import HybridRecommender

def explain_theoretical_flow():
    """
    THEORETICAL FLOW EXPLANATION
    ===========================
    
    PHASE 1: DATA PREPARATION
    ┌─────────────────────────────────────────────────────────────────┐
    │  1. Database Extraction                                         │
    │     - Users table: user profiles, interests, locations         │
    │     - Posts table: content, categories, locations              │
    │     - Interactions table: likes, comments, shares              │
    │     - Follows table: user relationships                        │
    │                                                                 │
    │  2. Data Structures Creation                                    │
    │     - User-Item Matrix (users × posts)                         │
    │     - Content Feature Vectors (TF-IDF)                         │
    │     - User Similarity Matrix                                    │
    │     - Location/Category Preference Profiles                    │
    └─────────────────────────────────────────────────────────────────┘
    
    PHASE 2: COLLABORATIVE FILTERING (60% of final score)
    ┌─────────────────────────────────────────────────────────────────┐
    │  Mathematical Foundation: Memory-Based Collaborative Filtering  │
    │                                                                 │
    │  Step 1: Build User-Item Matrix                                 │
    │    Matrix[user_i][post_j] = interaction_score                   │
    │    - Like = 1.0, Comment = 1.5, Share = 2.0                   │
    │                                                                 │
    │  Step 2: Calculate User Similarities                            │
    │    similarity(u1, u2) = cosine_similarity(vector_u1, vector_u2) │
    │    Formula: cos(θ) = (A·B) / (||A|| × ||B||)                   │
    │                                                                 │
    │  Step 3: Find Similar Users                                     │
    │    - Identify top-k similar users (k=10)                       │
    │    - Filter out users with similarity < threshold (0.1)        │
    │                                                                 │
    │  Step 4: Generate Recommendations                               │
    │    score(user, post) = Σ(similarity(user, neighbor) ×          │
    │                          neighbor_rating(post))                │
    │                        / Σ(similarity(user, neighbor))         │
    └─────────────────────────────────────────────────────────────────┘
    
    PHASE 3: CONTENT-BASED FILTERING (40% of final score)
    ┌─────────────────────────────────────────────────────────────────┐
    │  Mathematical Foundation: TF-IDF Vector Space Model             │
    │                                                                 │
    │  Step 1: Feature Extraction                                     │
    │    - Text Features: TF-IDF on post descriptions                 │
    │    - Location Features: Weighted by user preferences            │
    │    - Category Features: Weighted by user interests              │
    │                                                                 │
    │  Step 2: TF-IDF Calculation                                     │
    │    TF(t,d) = (frequency of term t in document d)               │
    │    IDF(t) = log(N / |{d: t ∈ d}|)                              │
    │    TF-IDF(t,d) = TF(t,d) × IDF(t)                              │
    │                                                                 │
    │  Step 3: User Profile Building                                  │
    │    user_profile = weighted_average(interacted_posts_vectors)    │
    │                                                                 │
    │  Step 4: Content Similarity                                     │
    │    content_score = cosine_similarity(user_profile, post_vector) │
    │                                                                 │
    │  Step 5: Bonus Calculations                                     │
    │    - Location Match Bonus: +5x multiplier                      │
    │    - Category Match Bonus: +4x multiplier                      │
    │    - Interest Alignment Bonus: +2x multiplier                  │
    └─────────────────────────────────────────────────────────────────┘
    
    PHASE 4: HYBRID COMBINATION
    ┌─────────────────────────────────────────────────────────────────┐
    │  Mathematical Foundation: Weighted Linear Combination           │
    │                                                                 │
    │  Final Score Calculation:                                       │
    │  hybrid_score = (0.6 × collaborative_score) +                  │
    │                 (0.4 × content_based_score)                    │
    │                                                                 │
    │  Normalization:                                                 │
    │  - All scores normalized to [0, 1] range                       │
    │  - Min-max scaling applied per algorithm                       │
    │                                                                 │
    │  Ranking:                                                       │
    │  - Posts sorted by hybrid_score (descending)                   │
    │  - Top-N recommendations returned (default N=10)               │
    └─────────────────────────────────────────────────────────────────┘
    """
    
    print("TRAVEL RECOMMENDATION SYSTEM - THEORETICAL FLOW")
    print("=" * 60)
    print()
    
    # Connect to database to show real data flow
    conn = get_db_connection()
    
    print("1. DATA PREPARATION PHASE")
    print("-" * 30)
    
    # Show database structure
    cursor = conn.cursor()
    
    # Users data
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"   Users in system: {user_count}")
    
    # Posts data
    cursor.execute("SELECT COUNT(*) FROM posts")
    post_count = cursor.fetchone()[0]
    print(f"   Posts in system: {post_count}")
    
    # Interactions data
    cursor.execute("SELECT COUNT(*) FROM interactions")
    interaction_count = cursor.fetchone()[0]
    print(f"   Interactions recorded: {interaction_count}")
    
    # Calculate sparsity
    sparsity = 1 - (interaction_count / (user_count * post_count))
    print(f"   Matrix sparsity: {sparsity:.2%}")
    print()
    
    print("2. COLLABORATIVE FILTERING MATHEMATICS")
    print("-" * 40)
    
    # Show user-item matrix construction
    query = """
    SELECT user_id, post_id, 
           CASE interaction_type 
               WHEN 'like' THEN 1.0
               WHEN 'comment' THEN 1.5  
               WHEN 'share' THEN 2.0
           END as score
    FROM interactions 
    LIMIT 5
    """
    
    sample_interactions = pd.read_sql_query(query, conn)
    print("   Sample User-Item Matrix entries:")
    print(sample_interactions.to_string(index=False))
    print()
    
    print("   Cosine Similarity Formula:")
    print("   similarity(A,B) = (A·B) / (||A|| × ||B||)")
    print("   where A·B = Σ(A[i] × B[i])")
    print("   ||A|| = √(Σ(A[i]²))")
    print()
    
    print("3. CONTENT-BASED FILTERING MATHEMATICS")
    print("-" * 42)
    
    # Show TF-IDF calculation example
    cursor.execute("SELECT description FROM posts LIMIT 3")
    sample_descriptions = [row[0] for row in cursor.fetchall()]
    
    print("   Sample post descriptions for TF-IDF:")
    for i, desc in enumerate(sample_descriptions, 1):
        print(f"   Post {i}: {desc[:50]}...")
    print()
    
    print("   TF-IDF Calculation:")
    print("   TF(term, doc) = frequency of term in document")
    print("   IDF(term) = log(total_docs / docs_containing_term)")
    print("   TF-IDF(term, doc) = TF(term, doc) × IDF(term)")
    print()
    
    print("   Bonus Multipliers:")
    print("   - Location Match: 5.0x")
    print("   - Category Match: 4.0x") 
    print("   - Interest Alignment: 2.0x")
    print()
    
    print("4. HYBRID COMBINATION FORMULA")
    print("-" * 35)
    print("   Final Score = (0.6 × collaborative_score) + (0.4 × content_score)")
    print("   Weight Distribution: 60% Collaborative, 40% Content-based")
    print()
    
    print("5. STEP-BY-STEP FLOW FOR USER RECOMMENDATION")
    print("-" * 50)
    print("   Input: user_id = 1")
    print("   ↓")
    print("   Step 1: Extract user interaction history")
    print("   Step 2: Build user profile from interactions")
    print("   Step 3: Find similar users (collaborative)")
    print("   Step 4: Calculate content preferences (content-based)")
    print("   Step 5: Generate candidate posts")
    print("   Step 6: Score each post using both algorithms")
    print("   Step 7: Apply hybrid weighting")
    print("   Step 8: Rank and return top recommendations")
    print("   ↓")
    print("   Output: Ranked list of recommended posts")
    print()
    
    conn.close()

def demonstrate_actual_calculation():
    """
    Demonstrate the actual calculation process with real data
    """
    print("6. REAL CALCULATION DEMONSTRATION")
    print("-" * 40)
    
    recommender = HybridRecommender()
    user_id = 1
    
    print(f"Generating recommendations for User {user_id}...")
    print()
    
    # Get user profile
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT u.name, u.location, u.bio 
        FROM users u 
        WHERE u.user_id = ?
    """, (user_id,))
    
    user_info = cursor.fetchone()
    print(f"User Profile: {user_info[0]} from {user_info[1]}")
    print(f"Bio: {user_info[2]}")
    print()
    
    # Show user's interaction history
    cursor.execute("""
        SELECT p.title, p.location, p.category, i.interaction_type
        FROM interactions i
        JOIN posts p ON i.post_id = p.post_id
        WHERE i.user_id = ?
        ORDER BY i.created_at DESC
    """, (user_id,))
    
    interactions = cursor.fetchall()
    print("User's Interaction History:")
    for interaction in interactions:
        print(f"  - {interaction[3].upper()}: {interaction[0]} ({interaction[1]}, {interaction[2]})")
    print()
    
    # Generate recommendations with detailed scoring
    recommendations = recommender.recommend_posts(user_id, num_recommendations=3)
    
    print("Generated Recommendations with Scoring Breakdown:")
    print("=" * 55)
    
    for i, (post_id, score) in enumerate(recommendations, 1):
        cursor.execute("""
            SELECT title, description, location, category 
            FROM posts 
            WHERE post_id = ?
        """, (post_id,))
        
        post_info = cursor.fetchone()
        print(f"\n{i}. {post_info[0]} (Score: {score:.4f})")
        print(f"   Location: {post_info[2]}")
        print(f"   Category: {post_info[3]}")
        print(f"   Description: {post_info[1][:80]}...")
        
        # Calculate individual algorithm scores for transparency
        collab_score = recommender.collaborative_recommender.recommend_posts_collaborative(user_id, num_recommendations=50)
        content_score = recommender.content_based_recommender.recommend_posts_content(user_id, num_recommendations=50)
        
        collab_post_score = next((s for p, s in collab_score if p == post_id), 0)
        content_post_score = next((s for p, s in content_score if p == post_id), 0)
        
        print(f"   Collaborative Score: {collab_post_score:.4f} (60% weight)")
        print(f"   Content-based Score: {content_post_score:.4f} (40% weight)")
        print(f"   Hybrid Calculation: ({collab_post_score:.4f} × 0.6) + ({content_post_score:.4f} × 0.4) = {score:.4f}")
    
    conn.close()
    print()
    
    print("7. ALGORITHM COMPLEXITY ANALYSIS")
    print("-" * 40)
    print("Time Complexity:")
    print("  - Collaborative Filtering: O(U × P) for matrix construction + O(U²) for similarity")
    print("  - Content-based Filtering: O(P × V) for TF-IDF + O(U × V) for profiles")
    print("  - Hybrid Combination: O(P) for score combination")
    print("  Where U = users, P = posts, V = vocabulary size")
    print()
    print("Space Complexity:")
    print("  - User-Item Matrix: O(U × P)")
    print("  - TF-IDF Matrix: O(P × V)")
    print("  - User Similarity Matrix: O(U²)")
    print()

def explain_decision_factors():
    """
    Explain what factors influence the recommendation decisions
    """
    print("8. DECISION FACTORS ANALYSIS")
    print("-" * 35)
    print()
    
    print("COLLABORATIVE FILTERING FACTORS:")
    print("  ✓ User Similarity Patterns")
    print("    - Users with similar interaction histories")
    print("    - Weight: Like=1.0, Comment=1.5, Share=2.0")
    print("    - Minimum similarity threshold: 0.1")
    print()
    print("  ✓ Interaction Recency")
    print("    - More recent interactions have higher influence")
    print("    - Historical patterns are preserved")
    print()
    
    print("CONTENT-BASED FILTERING FACTORS:")
    print("  ✓ Text Similarity (TF-IDF)")
    print("    - Description content matching")
    print("    - Keyword importance weighting")
    print()
    print("  ✓ Location Preferences (5x multiplier)")
    print("    - User's home location influence")
    print("    - Previously visited locations")
    print("    - Geographic clustering")
    print()
    print("  ✓ Category Interests (4x multiplier)")
    print("    - Adventure, Cultural, Spiritual, Food, Nature")
    print("    - Historical interaction categories")
    print()
    print("  ✓ User Interest Tags (2x multiplier)")
    print("    - Profile-declared interests")
    print("    - Implicit interest extraction")
    print()
    
    print("HYBRID WEIGHTING RATIONALE:")
    print("  • 60% Collaborative: Captures community preferences")
    print("  • 40% Content-based: Ensures content relevance")
    print("  • Balance prevents over-fitting to either approach")
    print("  • Handles cold-start problem effectively")
    print()

if __name__ == "__main__":
    explain_theoretical_flow()
    print("\n" + "="*80 + "\n")
    demonstrate_actual_calculation()
    print("\n" + "="*80 + "\n")
    explain_decision_factors()
    
    print("\nTHEORETICAL FLOW SUMMARY:")
    print("=" * 30)
    print("This recommendation system combines the best of both worlds:")
    print("• Collaborative filtering finds users with similar tastes")
    print("• Content-based filtering ensures topical relevance")
    print("• Hybrid approach balances exploration vs exploitation")
    print("• Mathematical foundations ensure reproducible results")
    print("• Bonus systems emphasize travel-specific preferences")