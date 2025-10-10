from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional, List
import os
import uuid
import shutil
from pathlib import Path
from google.oauth2 import id_token
from google.auth.transport import requests

# Import our modules
from database import get_db, create_tables, User, Post
from schemas import (
    UserRegistration, UserLogin, UserResponse, Token, Message, GoogleAuthRequest, 
    UserProfileUpdate, PostCreate, PostResponse, CommentCreate, CommentResponse,
    LocationCreate, LocationResponse, RecommendationResponse, FeedResponse,
    AppwriteUserSync
)
from crud import create_user, authenticate_user, get_user_by_email, get_user_by_id, create_google_user, get_user_by_google_id
from auth import create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
from social_crud import (
    sync_appwrite_user, create_post, get_posts_feed, get_user_posts, get_post_by_id,
    like_post, create_comment, get_post_comments, share_post, create_location,
    get_locations, get_user_stats, get_trending_posts
)
from blob_storage import blob_storage
from recommender.hybrid import HybridRecommender

# Phase 3: Appwrite Integration (Original)
from auth_middleware import AppwriteAuthMiddleware, get_current_user
from auth_endpoints import router as auth_router

# Phase 5: Fixed Appwrite Integration
from auth_middleware_fixed import FixedAppwriteAuthMiddleware, get_current_user_fixed

# Phase 4: Social Media APIs
from social_media_api import router as social_media_router

# Phase 6: Recommendation System
from recommendation_api import router as recommendation_router

# Create FastAPI app
app = FastAPI(
    title="Social Hub API",
    description="Backend API for Social Hub - A Social Media Platform",
    version="1.0.0"
)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads/profile_pictures")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Mount static files to serve uploaded images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:3000", 
        "http://localhost:8000", 
        "http://localhost:8080",
        "http://localhost:8081",  # Add the current frontend port
        "https://accounts.google.com"  # Add Google's domain
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Temporarily disable Appwrite middleware - using existing JWT auth
# app.add_middleware(
#     FixedAppwriteAuthMiddleware,
#     protected_paths=[
#         "/api/posts",
#         "/api/profile", 
#         "/api/feed",
#         "/api/messages",
#         "/api/notifications",
#         "/api/user"
#     ]
# )

# Phase 3: Include Appwrite Authentication Router
app.include_router(auth_router)

# Phase 4: Include Social Media APIs
app.include_router(social_media_router)

# Phase 6: Include Recommendation APIs  
app.include_router(recommendation_router)

# Security
security = HTTPBearer()

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

# Root endpoint
@app.get("/", response_model=Message)
async def root():
    return {"message": "Welcome to Social Hub API"}

# Health check endpoint
@app.get("/health", response_model=Message)
async def health_check():
    return {"message": "API is healthy and running!"}

# Register endpoint
@app.post("/auth/register", response_model=Token)
async def register(user: UserRegistration, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    try:
        db_user = create_user(db, user)
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": db_user.email}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse.from_orm(db_user)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

# Login endpoint
@app.post("/auth/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    # Authenticate user
    db_user = authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(db_user)
    }

# Google OAuth endpoint
@app.post("/auth/google", response_model=Token)
async def google_auth(google_request: GoogleAuthRequest, db: Session = Depends(get_db)):
    try:
        print(f"Received Google token: {google_request.token[:50]}...")  # Print first 50 chars
        
        # Get Google Client ID from environment
        GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
        print(f"Using Google Client ID: {GOOGLE_CLIENT_ID}")
        
        if not GOOGLE_CLIENT_ID:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google OAuth not configured"
            )
        
        # Verify the Google token with clock skew tolerance
        idinfo = id_token.verify_oauth2_token(
            google_request.token, 
            requests.Request(), 
            GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=10  # Allow 10 seconds of clock skew
        )
        
        # Extract user information from Google
        google_id = idinfo['sub']
        email = idinfo['email']
        full_name = idinfo.get('name', '')
        profile_picture = idinfo.get('picture', '')
        
        # Check if user exists by email or google_id
        existing_user = get_user_by_email(db, email)
        
        if existing_user:
            # User exists - update with Google info if needed
            if not existing_user.google_id:
                existing_user.google_id = google_id
                existing_user.auth_provider = "google"
                if profile_picture:
                    existing_user.profile_picture_url = profile_picture
                db.commit()
                db.refresh(existing_user)
            
            db_user = existing_user
        else:
            # Create new Google user
            db_user = create_google_user(db, {
                "full_name": full_name,
                "email": email,
                "google_id": google_id,
                "profile_picture_url": profile_picture
            })
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": db_user.email}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse.from_orm(db_user)
        }
        
    except ValueError as e:
        print(f"Google token verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid Google token: {str(e)}"
        )
    except Exception as e:
        print(f"Google auth error: {str(e)}")
        print(f"Error type: {type(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to authenticate with Google: {str(e)}"
        )

# Get current user (protected endpoint)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    email = verify_token(token)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user_by_email(db, email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

# Get user profile (protected endpoint)
@app.get("/auth/me", response_model=UserResponse)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    return UserResponse.from_orm(current_user)

# Update user profile (protected endpoint)
@app.put("/auth/profile", response_model=UserResponse)
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    print(f"Updating profile for user {current_user.email} with data: {profile_data}")
    
    # Update the user fields (email is not editable)
    current_user.full_name = profile_data.full_name
    if profile_data.bio is not None:
        current_user.bio = profile_data.bio
    if profile_data.education_school is not None:
        current_user.education_school = profile_data.education_school
    if profile_data.education_degree is not None:
        current_user.education_degree = profile_data.education_degree
    if profile_data.location is not None:
        current_user.location = profile_data.location
    if profile_data.phone is not None:
        current_user.phone = profile_data.phone
    
    try:
        db.commit()
        db.refresh(current_user)
        result = UserResponse.from_orm(current_user)
        print(f"Profile update successful, returning: {result}")
        return result
    except Exception as e:
        print(f"Error updating profile: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )

# Upload profile picture endpoint
@app.post("/auth/upload-profile-picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate file type
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPEG, PNG, GIF, and WebP images are allowed."
        )
    
    # Validate file size (limit to 5MB)
    if file.size and file.size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size too large. Maximum size is 5MB."
        )
    
    try:
        # Generate unique filename
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        unique_filename = f"{current_user.id}_{uuid.uuid4().hex}.{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Update user's profile picture URL
        profile_picture_url = f"http://localhost:8001/uploads/profile_pictures/{unique_filename}"
        current_user.profile_picture_url = profile_picture_url
        
        db.commit()
        db.refresh(current_user)
        
        return {
            "message": "Profile picture uploaded successfully",
            "profile_picture_url": profile_picture_url
        }
        
    except Exception as e:
        db.rollback()
        # Clean up file if it was created
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload profile picture"
        )

# Logout endpoint (client-side token removal)
@app.post("/auth/logout", response_model=Message)
async def logout():
    return {"message": "Successfully logged out"}

# ==================== SOCIAL MEDIA ENDPOINTS ====================

# Appwrite user sync endpoint
@app.post("/auth/sync-appwrite", response_model=UserResponse)
async def sync_appwrite_user_endpoint(
    appwrite_data: AppwriteUserSync,
    db: Session = Depends(get_db)
):
    """Sync user data from Appwrite authentication"""
    try:
        user = sync_appwrite_user(db, appwrite_data)
        return UserResponse.from_orm(user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync user: {str(e)}"
        )

# ==================== LOCATION ENDPOINTS ====================

@app.post("/locations", response_model=LocationResponse)
async def create_location_endpoint(
    location: LocationCreate,
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Create a new location"""
    try:
        db_location = create_location(db, location)
        return LocationResponse.from_orm(db_location)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create location: {str(e)}"
        )

@app.get("/locations", response_model=list[LocationResponse])
async def get_locations_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all locations"""
    locations = get_locations(db, skip=skip, limit=limit)
    return [LocationResponse.from_orm(loc) for loc in locations]

# ==================== POST ENDPOINTS ====================

@app.post("/posts", response_model=PostResponse)
async def create_post_endpoint(
    post: PostCreate,
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Create a new post with optional media upload"""
    try:
        image_url = None
        video_url = None
        
        # Handle file upload if provided
        if file:
            if not blob_storage.is_valid_media_file(file.filename):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid file type. Please upload an image or video."
                )
            
            # Save media file
            media_url = await blob_storage.save_post_media(file, current_user.id)
            
            # Determine if it's image or video
            file_type = blob_storage.get_file_type(file.filename)
            if file_type == 'image':
                image_url = media_url
            elif file_type == 'video':
                video_url = media_url
        
        # Create post
        db_post = create_post(db, post, current_user.id, image_url, video_url)
        
        # Convert to response format
        post_dict = {
            'id': db_post.id,
            'user_id': db_post.user_id,
            'caption': db_post.caption,
            'image_url': db_post.image_url,
            'video_url': db_post.video_url,
            'location_id': db_post.location_id,
            'travel_date': db_post.travel_date,
            'post_type': db_post.post_type,
            'likes_count': db_post.likes_count,
            'comments_count': db_post.comments_count,
            'shares_count': db_post.shares_count,
            'created_at': db_post.created_at,
            'updated_at': db_post.updated_at,
            'author_name': current_user.full_name,
            'author_profile_picture': current_user.profile_picture_url,
            'location_name': None,
            'is_liked': False,
            'is_shared': False
        }
        
        return PostResponse(**post_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create post: {str(e)}"
        )

@app.get("/posts/feed", response_model=list[PostResponse])
async def get_feed_endpoint(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get user's feed posts"""
    try:
        posts_data = get_posts_feed(db, current_user.id, skip=skip, limit=limit)
        return [PostResponse(**post) for post in posts_data]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get feed: {str(e)}"
        )

@app.get("/posts/recommended", response_model=list[RecommendationResponse])
async def get_recommended_posts_endpoint(
    limit: int = 10,
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get recommended posts for user"""
    try:
        recommender = HybridRecommender(db)
        recommendations = recommender.recommend_posts(current_user.id, limit)
        return [RecommendationResponse(**rec) for rec in recommendations]
    except Exception as e:
        # Fallback to trending posts if recommendation fails
        trending = get_trending_posts(db, limit=limit)
        fallback_recommendations = []
        for post in trending:
            fallback_recommendations.append({
                'post_id': post.id,
                'caption': post.caption,
                'image_url': post.image_url,
                'video_url': post.video_url,
                'created_at': post.created_at.isoformat(),
                'author_name': 'Unknown',
                'author_profile_picture': None,
                'location_name': None,
                'likes_count': post.likes_count,
                'comments_count': post.comments_count,
                'shares_count': post.shares_count,
                'popularity_score': float(post.likes_count + post.comments_count * 2 + post.shares_count * 3),
                'recommendation_reason': 'Trending post',
                'algorithm': 'popularity_based'
            })
        return [RecommendationResponse(**rec) for rec in fallback_recommendations]

@app.get("/posts/{post_id}", response_model=PostResponse)
async def get_post_endpoint(
    post_id: int,
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get a specific post by ID"""
    post = get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Get author info
    author = get_user_by_id(db, post.user_id)
    
    post_dict = {
        'id': post.id,
        'user_id': post.user_id,
        'caption': post.caption,
        'image_url': post.image_url,
        'video_url': post.video_url,
        'location_id': post.location_id,
        'travel_date': post.travel_date,
        'post_type': post.post_type,
        'likes_count': post.likes_count,
        'comments_count': post.comments_count,
        'shares_count': post.shares_count,
        'created_at': post.created_at,
        'updated_at': post.updated_at,
        'author_name': author.full_name if author else 'Unknown',
        'author_profile_picture': author.profile_picture_url if author else None,
        'location_name': None,  # TODO: Add location lookup
        'is_liked': False,  # TODO: Check if current user liked
        'is_shared': False  # TODO: Check if current user shared
    }
    
    return PostResponse(**post_dict)

@app.get("/users/{user_id}/posts", response_model=list[PostResponse])
async def get_user_posts_endpoint(
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get posts by a specific user"""
    posts = get_user_posts(db, user_id, skip=skip, limit=limit)
    author = get_user_by_id(db, user_id)
    
    posts_data = []
    for post in posts:
        post_dict = {
            'id': post.id,
            'user_id': post.user_id,
            'caption': post.caption,
            'image_url': post.image_url,
            'video_url': post.video_url,
            'location_id': post.location_id,
            'travel_date': post.travel_date,
            'post_type': post.post_type,
            'likes_count': post.likes_count,
            'comments_count': post.comments_count,
            'shares_count': post.shares_count,
            'created_at': post.created_at,
            'updated_at': post.updated_at,
            'author_name': author.full_name if author else 'Unknown',
            'author_profile_picture': author.profile_picture_url if author else None,
            'location_name': None,
            'is_liked': False,
            'is_shared': False
        }
        posts_data.append(post_dict)
    
    return [PostResponse(**post) for post in posts_data]

# ==================== INTERACTION ENDPOINTS ====================

@app.post("/posts/{post_id}/like")
async def like_post_endpoint(
    post_id: int,
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Like or unlike a post"""
    try:
        result = like_post(db, post_id, current_user.id)
        
        # Get updated post data
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        is_liked = result is not None
        
        return {
            "is_liked": is_liked,
            "likes_count": post.likes_count,
            "message": "Post liked" if is_liked else "Post unliked"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to like post: {str(e)}"
        )

@app.post("/posts/{post_id}/share")
async def share_post_endpoint(
    post_id: int,
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Share or unshare a post"""
    try:
        result = share_post(db, post_id, current_user.id)
        
        # Get updated post data
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        is_shared = result is not None
        
        return {
            "shares_count": post.shares_count,
            "message": "Post shared" if is_shared else "Post unshared"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to share post: {str(e)}"
        )

@app.post("/posts/{post_id}/comments", response_model=CommentResponse)
async def create_comment_endpoint(
    post_id: int,
    comment: CommentCreate,
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Create a comment on a post"""
    try:
        db_comment = create_comment(db, post_id, current_user.id, comment)
        
        # Create proper response object
        user_data = UserResponse(
            id=current_user.id,
            full_name=current_user.full_name,
            email=current_user.email,
            profile_picture_url=current_user.profile_picture_url,
            location=current_user.location,
            travel_style=current_user.travel_style,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at
        )
        
        return CommentResponse(
            id=db_comment.id,
            user=user_data,
            comment_text=db_comment.comment_text,
            created_at=db_comment.created_at
        )
    except Exception as e:
        print(f"Error creating comment: {e}")  # Debug print
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create comment: {str(e)}"
        )

@app.get("/posts/{post_id}/comments", response_model=List[CommentResponse])
async def get_post_comments_endpoint(
    post_id: int,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get comments for a post"""
    try:
        comments_data = get_post_comments(db, post_id, skip=skip, limit=limit)
        
        # Convert to CommentResponse format
        comment_responses = []
        for comment in comments_data:
            # Get the user details for this comment
            comment_user = db.query(User).filter(User.id == comment['user_id']).first()
            if comment_user:
                user_response = UserResponse(
                    id=comment_user.id,
                    full_name=comment_user.full_name,
                    email=comment_user.email,
                    profile_picture_url=comment_user.profile_picture_url,
                    location=comment_user.location,
                    travel_style=comment_user.travel_style,
                    created_at=comment_user.created_at,
                    updated_at=comment_user.updated_at
                )
                
                comment_response = CommentResponse(
                    id=comment['id'],
                    user=user_response,
                    comment_text=comment['comment_text'],
                    created_at=comment['created_at']
                )
                comment_responses.append(comment_response)
        
        return comment_responses
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get comments: {str(e)}"
        )

# ==================== USER STATS ENDPOINTS ====================

@app.get("/users/{user_id}/stats")
async def get_user_stats_endpoint(
    user_id: int,
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get user statistics"""
    try:
        stats = get_user_stats(db, user_id)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user stats: {str(e)}"
        )

@app.get("/posts/trending", response_model=list[PostResponse])
async def get_trending_posts_endpoint(
    days: int = 7,
    limit: int = 20,
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get trending posts"""
    try:
        posts = get_trending_posts(db, days=days, limit=limit)
        posts_data = []
        
        for post in posts:
            author = get_user_by_id(db, post.user_id)
            post_dict = {
                'id': post.id,
                'user_id': post.user_id,
                'caption': post.caption,
                'image_url': post.image_url,
                'video_url': post.video_url,
                'location_id': post.location_id,
                'travel_date': post.travel_date,
                'post_type': post.post_type,
                'likes_count': post.likes_count,
                'comments_count': post.comments_count,
                'shares_count': post.shares_count,
                'created_at': post.created_at,
                'updated_at': post.updated_at,
                'author_name': author.full_name if author else 'Unknown',
                'author_profile_picture': author.profile_picture_url if author else None,
                'location_name': None,
                'is_liked': False,
                'is_shared': False
            }
            posts_data.append(post_dict)
        
        return [PostResponse(**post) for post in posts_data]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get trending posts: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
