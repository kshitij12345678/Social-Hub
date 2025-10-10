from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from database import (
    User, Post, Like, Comment, Share, Location, Follow, UserInterest,
    PostTag
)
from schemas import (
    PostCreate, CommentCreate, LocationCreate, AppwriteUserSync
)

# ==================== USER OPERATIONS ====================

def sync_appwrite_user(db: Session, appwrite_data: AppwriteUserSync) -> User:
    """Sync user from Appwrite to our database"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == appwrite_data.email).first()
    
    if existing_user:
        # Update existing user with Appwrite data
        existing_user.full_name = appwrite_data.name
        if appwrite_data.profile_picture_url:
            existing_user.profile_picture_url = appwrite_data.profile_picture_url
        existing_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_user)
        return existing_user
    else:
        # Create new user
        new_user = User(
            full_name=appwrite_data.name,
            email=appwrite_data.email,
            profile_picture_url=appwrite_data.profile_picture_url,
            auth_provider="google",  # Assuming Appwrite users are Google authenticated
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()

# ==================== LOCATION OPERATIONS ====================

def create_location(db: Session, location: LocationCreate) -> Location:
    """Create a new location"""
    db_location = Location(**location.dict())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

def get_location_by_name(db: Session, name: str, country: str) -> Optional[Location]:
    """Get location by name and country"""
    return db.query(Location).filter(
        and_(Location.name == name, Location.country == country)
    ).first()

def get_locations(db: Session, skip: int = 0, limit: int = 100) -> List[Location]:
    """Get all locations with pagination"""
    return db.query(Location).offset(skip).limit(limit).all()

# ==================== POST OPERATIONS ====================

def create_post(db: Session, post: PostCreate, user_id: int, 
                image_url: Optional[str] = None, video_url: Optional[str] = None) -> Post:
    """Create a new post"""
    db_post = Post(
        user_id=user_id,
        caption=post.caption,
        image_url=image_url,
        video_url=video_url,
        location_id=post.location_id,
        travel_date=post.travel_date,
        post_type=post.post_type,
        likes_count=0,
        comments_count=0,
        shares_count=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def get_posts_feed(db: Session, user_id: int, skip: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
    """Get posts for user's feed with author and location info"""
    query = db.query(
        Post.id,
        Post.user_id,
        Post.caption,
        Post.image_url,
        Post.video_url,
        Post.location_id,
        Post.travel_date,
        Post.post_type,
        Post.likes_count,
        Post.comments_count,
        Post.shares_count,
        Post.created_at,
        Post.updated_at,
        User.full_name.label('author_name'),
        User.profile_picture_url.label('author_profile_picture'),
        Location.name.label('location_name')
    ).join(User, Post.user_id == User.id)\
     .outerjoin(Location, Post.location_id == Location.id)\
     .filter(Post.user_id != user_id)\
     .order_by(desc(Post.created_at))\
     .offset(skip)\
     .limit(limit)
    
    results = query.all()
    
    # Convert to list of dictionaries
    posts = []
    for result in results:
        post_dict = {
            'id': result.id,
            'user_id': result.user_id,
            'caption': result.caption,
            'image_url': result.image_url,
            'video_url': result.video_url,
            'location_id': result.location_id,
            'travel_date': result.travel_date,
            'post_type': result.post_type,
            'likes_count': result.likes_count,
            'comments_count': result.comments_count,
            'shares_count': result.shares_count,
            'created_at': result.created_at,
            'updated_at': result.updated_at,
            'author_name': result.author_name,
            'author_profile_picture': result.author_profile_picture,
            'location_name': result.location_name,
            'is_liked': is_post_liked_by_user(db, result.id, user_id),
            'is_shared': is_post_shared_by_user(db, result.id, user_id)
        }
        posts.append(post_dict)
    
    return posts

def get_user_posts(db: Session, user_id: int, skip: int = 0, limit: int = 20) -> List[Post]:
    """Get posts created by a specific user"""
    return db.query(Post).filter(Post.user_id == user_id)\
             .order_by(desc(Post.created_at))\
             .offset(skip)\
             .limit(limit)\
             .all()

def get_post_by_id(db: Session, post_id: int) -> Optional[Post]:
    """Get post by ID"""
    return db.query(Post).filter(Post.id == post_id).first()

def delete_post(db: Session, post_id: int, user_id: int) -> bool:
    """Delete a post (only by the owner)"""
    post = db.query(Post).filter(and_(Post.id == post_id, Post.user_id == user_id)).first()
    if post:
        db.delete(post)
        db.commit()
        return True
    return False

# ==================== INTERACTION OPERATIONS ====================

def like_post(db: Session, post_id: int, user_id: int) -> Optional[Like]:
    """Like a post (or unlike if already liked)"""
    # Check if already liked
    existing_like = db.query(Like).filter(
        and_(Like.post_id == post_id, Like.user_id == user_id)
    ).first()
    
    if existing_like:
        # Unlike
        db.delete(existing_like)
        # Decrease like count
        post = db.query(Post).filter(Post.id == post_id).first()
        if post:
            post.likes_count = max(0, post.likes_count - 1)
        db.commit()
        return None
    else:
        # Like
        new_like = Like(post_id=post_id, user_id=user_id, created_at=datetime.utcnow())
        db.add(new_like)
        # Increase like count
        post = db.query(Post).filter(Post.id == post_id).first()
        if post:
            post.likes_count += 1
        db.commit()
        db.refresh(new_like)
        return new_like

def is_post_liked_by_user(db: Session, post_id: int, user_id: int) -> bool:
    """Check if post is liked by user"""
    like = db.query(Like).filter(
        and_(Like.post_id == post_id, Like.user_id == user_id)
    ).first()
    return like is not None

def create_comment(db: Session, post_id: int, user_id: int, comment: CommentCreate) -> Comment:
    """Create a comment on a post"""
    db_comment = Comment(
        post_id=post_id,
        user_id=user_id,
        comment_text=comment.comment_text,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_comment)
    
    # Increase comment count
    post = db.query(Post).filter(Post.id == post_id).first()
    if post:
        post.comments_count += 1
    
    db.commit()
    db.refresh(db_comment)
    return db_comment

def get_post_comments(db: Session, post_id: int, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
    """Get comments for a post with author info"""
    query = db.query(
        Comment.id,
        Comment.user_id,
        Comment.post_id,
        Comment.comment_text,
        Comment.created_at,
        Comment.updated_at,
        User.full_name.label('author_name'),
        User.profile_picture_url.label('author_profile_picture')
    ).join(User, Comment.user_id == User.id)\
     .filter(Comment.post_id == post_id)\
     .order_by(Comment.created_at)\
     .offset(skip)\
     .limit(limit)
    
    results = query.all()
    
    # Convert to list of dictionaries
    comments = []
    for result in results:
        comment_dict = {
            'id': result.id,
            'user_id': result.user_id,
            'post_id': result.post_id,
            'comment_text': result.comment_text,
            'created_at': result.created_at,
            'updated_at': result.updated_at,
            'author_name': result.author_name,
            'author_profile_picture': result.author_profile_picture
        }
        comments.append(comment_dict)
    
    return comments

def share_post(db: Session, post_id: int, user_id: int) -> Optional[Share]:
    """Share a post (or unshare if already shared)"""
    # Check if already shared
    existing_share = db.query(Share).filter(
        and_(Share.post_id == post_id, Share.user_id == user_id)
    ).first()
    
    if existing_share:
        # Unshare
        db.delete(existing_share)
        # Decrease share count
        post = db.query(Post).filter(Post.id == post_id).first()
        if post:
            post.shares_count = max(0, post.shares_count - 1)
        db.commit()
        return None
    else:
        # Share
        new_share = Share(post_id=post_id, user_id=user_id, created_at=datetime.utcnow())
        db.add(new_share)
        # Increase share count
        post = db.query(Post).filter(Post.id == post_id).first()
        if post:
            post.shares_count += 1
        db.commit()
        db.refresh(new_share)
        return new_share

def is_post_shared_by_user(db: Session, post_id: int, user_id: int) -> bool:
    """Check if post is shared by user"""
    share = db.query(Share).filter(
        and_(Share.post_id == post_id, Share.user_id == user_id)
    ).first()
    return share is not None

# ==================== ANALYTICS / STATS ====================

def get_user_stats(db: Session, user_id: int) -> Dict[str, int]:
    """Get user statistics"""
    posts_count = db.query(Post).filter(Post.user_id == user_id).count()
    followers_count = db.query(Follow).filter(Follow.following_id == user_id).count()
    following_count = db.query(Follow).filter(Follow.follower_id == user_id).count()
    
    # Total likes received on user's posts
    total_likes = db.query(func.sum(Post.likes_count)).filter(Post.user_id == user_id).scalar() or 0
    
    return {
        'posts_count': posts_count,
        'followers_count': followers_count,
        'following_count': following_count,
        'total_likes_received': total_likes
    }

def get_trending_posts(db: Session, days: int = 7, limit: int = 20) -> List[Post]:
    """Get trending posts from the last N days"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    return db.query(Post)\
             .filter(Post.created_at >= cutoff_date)\
             .order_by(desc(Post.likes_count + Post.comments_count * 2 + Post.shares_count * 3))\
             .limit(limit)\
             .all()