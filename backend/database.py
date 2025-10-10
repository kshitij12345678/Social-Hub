from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Enum, Text, Float, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
import enum

# Database URL - using SQLite for simplicity (unified database)
DATABASE_URL = "sqlite:///./social_hub.db"

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Auth provider enum
class AuthProvider(enum.Enum):
    LOCAL = "local"
    GOOGLE = "google"

# User model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    bio = Column(String(500), nullable=True)  # User bio/description
    hashed_password = Column(String(255), nullable=True)  # Nullable for Google users
    google_id = Column(String(255), unique=True, nullable=True, index=True)  # Google user ID
    auth_provider = Column(Enum(AuthProvider), default=AuthProvider.LOCAL)  # Track auth method
    profile_picture_url = Column(String(500), nullable=True)  # For Google profile pics
    
    # Additional profile fields
    education_school = Column(String(255), nullable=True)  # School/University
    education_degree = Column(String(255), nullable=True)  # Degree/Field of study
    location = Column(String(255), nullable=True)  # Location/City
    phone = Column(String(20), nullable=True)  # Phone number
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ==================== SOCIAL MEDIA MODELS ====================

# Locations model for travel destinations
class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    country = Column(String(100), nullable=False)
    continent = Column(String(50), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    category = Column(String(100), nullable=True)  # beach, mountain, city, historical
    created_at = Column(DateTime, default=datetime.utcnow)

# Posts model for social media content
class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    caption = Column(Text, nullable=True)  # Allow existing posts without captions
    media_url = Column(String(500), nullable=True)  # Single field for images/videos
    media_type = Column(Enum('image', 'video', name='media_type_enum'), nullable=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    travel_date = Column(DateTime, nullable=True)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Note: Relationships will be defined after all models are created

# Post Tags model
class PostTag(Base):
    __tablename__ = "post_tags"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    tag_name = Column(String(50), nullable=False)
    
    # Note: Relationships will be defined after all models are created

# Likes model
class Like(Base):
    __tablename__ = "likes"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Note: Relationships will be defined after all models are created

# Comments model
class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    comment_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Note: Relationships will be defined after all models are created

# Shares model
class Share(Base):
    __tablename__ = "shares"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Note: Relationships will be defined after all models are created

# Follows model for user connections
class Follow(Base):
    __tablename__ = "follows"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    following_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Note: Relationships will be defined after all models are created

# User Interests model for recommendations
class UserInterest(Base):
    __tablename__ = "user_interests"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    interest_type = Column(String(50), nullable=False)  # destination, activity, style
    interest_value = Column(String(100), nullable=False)
    weight = Column(Float, default=1.0)  # importance score
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Note: Relationships will be defined after all models are created

# Update User model with additional fields
User.travel_style = Column(String(50), nullable=True)  # adventure, luxury, budget, family, solo

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
