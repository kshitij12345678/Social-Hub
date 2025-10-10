import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Database
    DATABASE_PATH = "data/travel_social.db"
    
    # API Settings
    API_HOST = "127.0.0.1"
    API_PORT = 8000
    DEBUG = True
    
    # Recommendation Settings
    MIN_INTERACTIONS_FOR_RECOMMENDATIONS = 3
    MAX_RECOMMENDATIONS = 20
    RECOMMENDATION_CACHE_TIME = 300  # 5 minutes
    
    # Travel specific settings
    POPULAR_DESTINATIONS = [
        "Paris", "Tokyo", "Bali", "New York", "London", "Bangkok", 
        "Dubai", "Singapore", "Rome", "Barcelona", "Amsterdam", 
        "Sydney", "Maldives", "Switzerland", "Iceland"
    ]
    
    TRAVEL_CATEGORIES = [
        "Adventure", "Beach", "Culture", "Food", "Nature", 
        "Photography", "Backpacking", "Luxury", "Solo Travel", 
        "Family", "Historical", "Wildlife", "Mountains", "Cities"
    ]