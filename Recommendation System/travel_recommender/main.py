from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database.models import DatabaseManager
from src.recommender.hybrid import HybridRecommender
from config import Config

app = FastAPI(title="Travel Instagram Recommendation System", version="1.0.0")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db_manager = DatabaseManager(Config.DATABASE_PATH)
recommender = HybridRecommender(db_manager)

@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "message": "🌍 Welcome to Travel Instagram Recommendation System!",
        "version": "1.0.0",
        "endpoints": {
            "post_recommendations": "/recommendations/posts/{user_id}",
            "user_recommendations": "/recommendations/users/{user_id}",
            "destination_recommendations": "/recommendations/destinations/{user_id}",
            "user_stats": "/users/{user_id}/stats"
        }
    }

@app.get("/recommendations/posts/{user_id}")
async def get_post_recommendations(user_id: int, limit: int = 10):
    """Get recommended posts for a user"""
    try:
        recommendations = recommender.recommend_posts(user_id, limit)
        return {
            "user_id": user_id,
            "recommendations": recommendations,
            "count": len(recommendations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recommendations/users/{user_id}")
async def get_user_recommendations(user_id: int, limit: int = 10):
    """Get recommended users to follow"""
    try:
        recommendations = recommender.recommend_users(user_id, limit)
        return {
            "user_id": user_id,
            "recommendations": recommendations,
            "count": len(recommendations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recommendations/destinations/{user_id}")
async def get_destination_recommendations(user_id: int, limit: int = 10):
    """Get recommended travel destinations"""
    try:
        recommendations = recommender.recommend_destinations(user_id, limit)
        return {
            "user_id": user_id,
            "recommendations": recommendations,
            "count": len(recommendations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}/stats")
async def get_user_stats(user_id: int):
    """Get user statistics"""
    try:
        stats_query = """
            SELECT 
                (SELECT COUNT(*) FROM posts WHERE user_id = ?) as posts_count,
                (SELECT COUNT(*) FROM interactions WHERE user_id = ?) as interactions_count,
                (SELECT COUNT(*) FROM follows WHERE follower_id = ?) as following_count,
                (SELECT COUNT(*) FROM follows WHERE following_id = ?) as followers_count
        """
        
        result = db_manager.execute_query(stats_query, (user_id, user_id, user_id, user_id))
        
        if result:
            posts, interactions, following, followers = result[0]
            return {
                "user_id": user_id,
                "stats": {
                    "posts": posts,
                    "interactions": interactions,
                    "following": following,
                    "followers": followers
                }
            }
        else:
            raise HTTPException(status_code=404, detail="User not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        result = db_manager.execute_query("SELECT COUNT(*) FROM users")
        user_count = result[0][0] if result else 0
        
        return {
            "status": "healthy",
            "database": "connected",
            "users_in_db": user_count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.API_HOST, port=Config.API_PORT, reload=Config.DEBUG)