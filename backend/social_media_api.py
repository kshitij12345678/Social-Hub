"""
Phase 4: Core Social Media Backend APIs
Instagram-like post management and social interactions
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, and_
from typing import Optional, List
import os
import uuid
import shutil
from datetime import datetime
import mimetypes

from database import get_db, User, Post, Like, Comment, Share
# Use existing JWT authentication instead of Appwrite
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth import verify_token
from crud import get_user_by_email

# JWT Authentication - Using your existing JWT system  
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    """Get current user from JWT token"""
    token = credentials.credentials
    email = verify_token(token)
    
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user_by_email(db, email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user
from pydantic import BaseModel

# Create router
router = APIRouter(prefix="/api", tags=["social_media"])

# Pydantic models for requests/responses
class PostCreate(BaseModel):
    caption: str
    location_id: Optional[int] = None
    travel_date: Optional[str] = None

class PostResponse(BaseModel):
    id: int
    user: dict
    caption: str
    media_url: Optional[str]
    media_type: Optional[str]
    location_id: Optional[int]
    travel_date: Optional[str]
    likes_count: int
    comments_count: int
    shares_count: int
    is_liked_by_user: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class CommentCreate(BaseModel):
    comment_text: str

class CommentResponse(BaseModel):
    id: int
    user: dict
    comment_text: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class FeedResponse(BaseModel):
    posts: List[PostResponse]
    next_cursor: Optional[str]
    has_more: bool

# Utility functions
def get_media_upload_path(user_id: int, post_id: int, filename: str) -> str:
    """Generate upload path for media files"""
    timestamp = int(datetime.utcnow().timestamp())
    file_extension = os.path.splitext(filename)[1]
    new_filename = f"{user_id}_{post_id}_{timestamp}{file_extension}"
    return os.path.join("uploads", "posts", new_filename)

def save_uploaded_file(upload_file: UploadFile, file_path: str) -> None:
    """Save uploaded file to specified path"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

def get_media_type(filename: str) -> str:
    """Determine media type from filename"""
    mime_type, _ = mimetypes.guess_type(filename)
    if mime_type:
        if mime_type.startswith('image/'):
            return 'image'
        elif mime_type.startswith('video/'):
            return 'video'
    return 'image'  # Default to image

def format_user_info(user: User) -> dict:
    """Format user information for API responses"""
    return {
        "id": user.id,
        "full_name": user.full_name,
        "profile_picture_url": user.profile_picture_url,
        "location": user.location
    }

def format_post_response(post: Post, current_user: User, db: Session) -> PostResponse:
    """Format post for API response with user interaction status"""
    # Check if current user liked this post
    is_liked = db.query(Like).filter(
        and_(Like.post_id == post.id, Like.user_id == current_user.id)
    ).first() is not None
    
    # Get user info (assuming relationship exists or join)
    user = db.query(User).filter(User.id == post.user_id).first()
    
    # Format media URL properly
    formatted_media_url = None
    if post.media_url:
        if post.media_url.startswith('http'):
            # Already a complete URL (like https://picsum.photos/...)
            formatted_media_url = post.media_url
        else:
            # Local file path, prepend server URL
            formatted_media_url = f"http://localhost:8001/{post.media_url}"
    
    return PostResponse(
        id=post.id,
        user=format_user_info(user),
        caption=post.caption,
        media_url=formatted_media_url,
        media_type=post.media_type,
        location_id=post.location_id,
        travel_date=post.travel_date,
        likes_count=post.likes_count,
        comments_count=post.comments_count,
        shares_count=post.shares_count,
        is_liked_by_user=is_liked,
        created_at=post.created_at
    )

# ==================== POST MANAGEMENT APIs ====================

@router.post("/posts", response_model=PostResponse)
async def create_post(
    caption: str = Form(...),
    media: Optional[UploadFile] = File(None),
    location_id: Optional[int] = Form(None),
    travel_date: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new post with optional media upload"""
    
    # Create post in database first to get ID        
    new_post = Post(
        user_id=current_user.id,
        caption=caption,
        location_id=location_id,
        travel_date=datetime.fromisoformat(travel_date) if travel_date else None,
        media_url=None,
        media_type=None
    )
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    # Handle media upload if provided
    if media and media.filename:
        try:
            # Validate file type
            media_type = get_media_type(media.filename)
            if media_type not in ['image', 'video']:
                raise HTTPException(status_code=400, detail="Invalid media type")
            
            # Generate file path and save
            file_path = get_media_upload_path(current_user.id, new_post.id, media.filename)
            save_uploaded_file(media, file_path)
            
            # Update post with media info
            new_post.media_url = file_path
            new_post.media_type = media_type
            db.commit()
            
        except Exception as e:
            # If media upload fails, delete the post
            db.delete(new_post)
            db.commit()
            raise HTTPException(status_code=500, detail=f"Media upload failed: {str(e)}")
    
    return format_post_response(new_post, current_user, db)

@router.get("/posts", response_model=FeedResponse)
async def get_posts(
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    limit: int = Query(10, description="Number of posts to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get posts feed with cursor-based pagination (infinite scroll)"""
    
    # Build query
    query = db.query(Post).order_by(desc(Post.created_at))
    
    # Apply cursor if provided
    if cursor:
        try:
            cursor_post = db.query(Post).filter(Post.id == int(cursor)).first()
            if cursor_post:
                query = query.filter(Post.created_at < cursor_post.created_at)
        except ValueError:
            pass  # Invalid cursor, ignore
    
    # Get posts with limit + 1 to check if there are more
    posts = query.limit(limit + 1).all()
    
    # Check if there are more posts
    has_more = len(posts) > limit
    if has_more:
        posts = posts[:limit]  # Remove the extra post
    
    # Format response
    formatted_posts = [
        format_post_response(post, current_user, db) 
        for post in posts
    ]
    
    # Set next cursor to the last post ID
    next_cursor = str(posts[-1].id) if posts and has_more else None
    
    return FeedResponse(
        posts=formatted_posts,
        next_cursor=next_cursor,
        has_more=has_more
    )

@router.get("/posts/{user_id}")
async def get_user_posts(
    user_id: int,
    cursor: Optional[str] = Query(None),
    limit: int = Query(10),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get posts by specific user"""
    
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Build query for user's posts
    query = db.query(Post).filter(Post.user_id == user_id).order_by(desc(Post.created_at))
    
    # Apply cursor if provided
    if cursor:
        try:
            cursor_post = db.query(Post).filter(Post.id == int(cursor)).first()
            if cursor_post:
                query = query.filter(Post.created_at < cursor_post.created_at)
        except ValueError:
            pass
    
    # Get posts
    posts = query.limit(limit + 1).all()
    has_more = len(posts) > limit
    if has_more:
        posts = posts[:limit]
    
    # Format response
    formatted_posts = [
        format_post_response(post, current_user, db) 
        for post in posts
    ]
    
    next_cursor = str(posts[-1].id) if posts and has_more else None
    
    return FeedResponse(
        posts=formatted_posts,
        next_cursor=next_cursor,
        has_more=has_more
    )

# ==================== SOCIAL INTERACTION APIs ====================

@router.post("/posts/{post_id}/like")
async def toggle_like_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Like or unlike a post"""
    
    # Check if post exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if user already liked this post
    existing_like = db.query(Like).filter(
        and_(Like.post_id == post_id, Like.user_id == current_user.id)
    ).first()
    
    if existing_like:
        # Unlike: Remove like and decrement count
        db.delete(existing_like)
        post.likes_count = max(0, post.likes_count - 1)
        action = "unliked"
    else:
        # Like: Add like and increment count
        new_like = Like(post_id=post_id, user_id=current_user.id)
        db.add(new_like)
        post.likes_count += 1
        action = "liked"
    
    db.commit()
    
    return {
        "message": f"Post {action}",
        "likes_count": post.likes_count,
        "is_liked": action == "liked"
    }

@router.post("/posts/{post_id}/comment", response_model=CommentResponse)
async def add_comment(
    post_id: int,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a comment to a post"""
    
    # Check if post exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Create comment
    new_comment = Comment(
        post_id=post_id,
        user_id=current_user.id,
        comment_text=comment_data.comment_text
    )
    
    db.add(new_comment)
    post.comments_count += 1
    db.commit()
    db.refresh(new_comment)
    
    return CommentResponse(
        id=new_comment.id,
        user=format_user_info(current_user),
        comment_text=new_comment.comment_text,
        created_at=new_comment.created_at
    )

@router.post("/posts/{post_id}/share")
async def share_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Share a post (increment share count)"""
    
    # Check if post exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if user already shared this post (prevent multiple shares)
    existing_share = db.query(Share).filter(
        and_(Share.post_id == post_id, Share.user_id == current_user.id)
    ).first()
    
    if existing_share:
        return {
            "message": "Post already shared",
            "shares_count": post.shares_count
        }
    
    # Create share record and increment count
    new_share = Share(post_id=post_id, user_id=current_user.id)
    db.add(new_share)
    post.shares_count += 1
    db.commit()
    
    return {
        "message": "Post shared",
        "shares_count": post.shares_count
    }

@router.get("/posts/{post_id}/interactions")
async def get_post_interactions(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get post interaction counts and user's interaction status"""
    
    # Check if post exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check user's interactions
    user_liked = db.query(Like).filter(
        and_(Like.post_id == post_id, Like.user_id == current_user.id)
    ).first() is not None
    
    user_shared = db.query(Share).filter(
        and_(Share.post_id == post_id, Share.user_id == current_user.id)
    ).first() is not None
    
    return {
        "post_id": post_id,
        "likes_count": post.likes_count,
        "comments_count": post.comments_count,
        "shares_count": post.shares_count,
        "user_interactions": {
            "is_liked": user_liked,
            "is_shared": user_shared
        }
    }

@router.get("/posts/{post_id}/comments")
async def get_post_comments(
    post_id: int,
    cursor: Optional[str] = Query(None),
    limit: int = Query(20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comments for a post with pagination"""
    
    # Check if post exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Build query for comments
    query = db.query(Comment).filter(Comment.post_id == post_id).order_by(desc(Comment.created_at))
    
    # Apply cursor if provided
    if cursor:
        try:
            cursor_comment = db.query(Comment).filter(Comment.id == int(cursor)).first()
            if cursor_comment:
                query = query.filter(Comment.created_at < cursor_comment.created_at)
        except ValueError:
            pass
    
    # Get comments
    comments = query.limit(limit + 1).all()
    has_more = len(comments) > limit
    if has_more:
        comments = comments[:limit]
    
    # Format comments with user info
    formatted_comments = []
    for comment in comments:
        user = db.query(User).filter(User.id == comment.user_id).first()
        formatted_comments.append(CommentResponse(
            id=comment.id,
            user=format_user_info(user),
            comment_text=comment.comment_text,
            created_at=comment.created_at
        ))
    
    next_cursor = str(comments[-1].id) if comments and has_more else None
    
    return {
        "comments": formatted_comments,
        "next_cursor": next_cursor,
        "has_more": has_more
    }

# ==================== MEDIA SERVING ====================

@router.get("/uploads/posts/{filename}")
async def serve_post_media(filename: str):
    """Serve uploaded media files"""
    file_path = os.path.join("uploads", "posts", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Media file not found")
    
    return FileResponse(file_path)