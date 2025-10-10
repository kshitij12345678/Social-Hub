from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from enum import Enum

# Auth provider enum
class AuthProvider(str, Enum):
    LOCAL = "local"
    GOOGLE = "google"

# Request models
class UserRegistration(BaseModel):
    full_name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class GoogleAuthRequest(BaseModel):
    token: str  # Google ID token

class UserProfileUpdate(BaseModel):
    full_name: str
    bio: Optional[str] = None
    education_school: Optional[str] = None
    education_degree: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    # Email is not editable - it's tied to authentication provider

# Response models
class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    bio: Optional[str] = None
    education_school: Optional[str] = None
    education_degree: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    auth_provider: AuthProvider
    profile_picture_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== SOCIAL MEDIA SCHEMAS ====================

# Post schemas
class PostCreate(BaseModel):
    caption: Optional[str] = None
    location_id: Optional[int] = None
    travel_date: Optional[datetime] = None
    post_type: Optional[str] = "photo"  # photo, video, story

class PostResponse(BaseModel):
    id: int
    user_id: int
    caption: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    location_id: Optional[int] = None
    travel_date: Optional[datetime] = None
    post_type: str
    likes_count: int
    comments_count: int
    shares_count: int
    created_at: datetime
    updated_at: datetime
    
    # Author info
    author_name: Optional[str] = None
    author_profile_picture: Optional[str] = None
    
    # Location info
    location_name: Optional[str] = None
    
    # User interaction status
    is_liked: Optional[bool] = False
    is_shared: Optional[bool] = False
    
    class Config:
        from_attributes = True

# Comment schemas
class CommentCreate(BaseModel):
    comment_text: str

class CommentResponse(BaseModel):
    id: int
    user: UserResponse
    comment_text: str
    created_at: datetime
    
    # Author info
    author_name: Optional[str] = None
    author_profile_picture: Optional[str] = None
    
    class Config:
        from_attributes = True

# Location schemas
class LocationCreate(BaseModel):
    name: str
    country: str
    continent: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    category: Optional[str] = None  # beach, mountain, city, historical

class LocationResponse(BaseModel):
    id: int
    name: str
    country: str
    continent: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    category: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Interaction schemas
class LikeResponse(BaseModel):
    id: int
    user_id: int
    post_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ShareResponse(BaseModel):
    id: int
    user_id: int
    post_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Recommendation schemas
class RecommendationResponse(BaseModel):
    post_id: int
    caption: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    created_at: Optional[str] = None
    author_name: Optional[str] = None
    author_profile_picture: Optional[str] = None
    location_name: Optional[str] = None
    likes_count: int
    comments_count: int
    shares_count: int
    popularity_score: float
    recommendation_reason: str
    algorithm: str

# Feed schemas
class FeedResponse(BaseModel):
    posts: list[PostResponse]
    has_more: bool
    next_cursor: Optional[int] = None

# Appwrite sync schemas
class AppwriteUserSync(BaseModel):
    appwrite_user_id: str
    email: str
    name: str
    profile_picture_url: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class Message(BaseModel):
    message: str
