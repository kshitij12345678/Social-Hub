"""
Recommendation API endpoints for Social Hub
Provides personalized post recommendations using the integrated recommendation system
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from database import get_db
from social_media_api import get_current_user
from database import User
from social_hub_recommender_fixed import SocialHubRecommender

# Create router
router = APIRouter(prefix="/api", tags=["recommendations"])

# Initialize the recommender (singleton)
recommender = None

def get_recommender():
    """Get or create the recommender instance"""
    global recommender
    if recommender is None:
        recommender = SocialHubRecommender()
    return recommender

@router.get("/recommendations/posts")
async def get_recommended_posts(
    limit: int = Query(10, ge=1, le=50, description="Number of recommendations to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized post recommendations for the current user
    
    This endpoint uses a hybrid recommendation system that combines:
    - Collaborative filtering (user-user similarity)
    - Content-based filtering (post features and user preferences)
    - Popularity-based fallback for new users
    """
    try:
        rec_system = get_recommender()
        
        # Get personalized recommendations
        recommendations = rec_system.get_recommended_posts(current_user.id, limit)
        
        if not recommendations:
            raise HTTPException(
                status_code=404, 
                detail="No recommendations found. This might be a new user with limited interaction history."
            )
        
        return {
            "user_id": current_user.id,
            "recommendations": recommendations,
            "total_count": len(recommendations),
            "recommendation_info": {
                "algorithm": "hybrid",
                "combines": ["collaborative_filtering", "content_based", "popularity"],
                "personalized": True
            }
        }
        
    except Exception as e:
        print(f"❌ Recommendation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")

@router.get("/recommendations/popular")
async def get_popular_posts(
    limit: int = Query(10, ge=1, le=50, description="Number of popular posts to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get popular posts (fallback endpoint)
    
    Returns posts ranked by engagement (likes, comments, shares)
    """
    try:
        rec_system = get_recommender()
        
        # Get popular posts as fallback
        popular_posts = rec_system.get_popular_posts_fallback(limit)
        
        return {
            "user_id": current_user.id,
            "posts": popular_posts,
            "total_count": len(popular_posts),
            "recommendation_info": {
                "algorithm": "popularity_based",
                "personalized": False,
                "description": "Posts ranked by engagement metrics"
            }
        }
        
    except Exception as e:
        print(f"❌ Popular posts error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get popular posts: {str(e)}")

@router.get("/recommendations/stats")
async def get_recommendation_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get recommendation statistics and user profile for debugging
    """
    try:
        rec_system = get_recommender()
        
        # Get user stats
        stats = rec_system.get_user_stats(current_user.id)
        
        return {
            "user_id": current_user.id,
            "stats": stats,
            "recommendations_available": stats.get("recommendation_eligibility", {}).get("has_interactions", False)
        }
        
    except Exception as e:
        print(f"❌ Stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get recommendation stats: {str(e)}")

@router.post("/recommendations/train")
async def train_recommendation_models(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually trigger model training (admin endpoint)
    
    This can be called periodically to refresh recommendations based on new user interactions
    """
    try:
        rec_system = get_recommender()
        
        # Train the models
        result = rec_system.train_model()
        
        return {
            "user_id": current_user.id,
            "training_result": result,
            "message": "Recommendation models updated successfully"
        }
        
    except Exception as e:
        print(f"❌ Training error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to train models: {str(e)}")

@router.get("/recommendations/health")
async def health_check():
    """Health check endpoint for the recommendation system"""
    try:
        rec = get_recommender()
        return {
            "status": "healthy",
            "recommender_initialized": rec.recommender is not None,
            "message": "Recommendation system is operational"
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e),
            "message": "Recommendation system failed to initialize"
        }

@router.get("/recommendations/test/{user_id}")
async def test_recommendations(
    user_id: int,
    limit: int = Query(5, ge=1, le=20, description="Number of recommendations to return")
):
    """Test endpoint for recommendations without authentication"""
    try:
        rec = get_recommender()
        
        # Get recommendations for the specified user
        recommendations = rec.get_recommended_posts(user_id=user_id, limit=limit)
        
        return {
            "user_id": user_id,
            "total_recommendations": len(recommendations),
            "recommendations": recommendations,
            "message": f"Successfully generated {len(recommendations)} recommendations"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recommendations: {str(e)}"
        )