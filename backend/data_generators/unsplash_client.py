import os
import requests
import time
from typing import List, Dict, Optional
from dotenv import load_dotenv
import random

load_dotenv()

class UnsplashClient:
    def __init__(self, access_key: str = None):
        self.access_key = access_key or os.getenv("UNSPLASH_ACCESS_KEY")
        self.api_url = os.getenv("UNSPLASH_API_URL", "https://api.unsplash.com")
        self.headers = {
            "Authorization": f"Client-ID {self.access_key}",
            "Accept-Version": "v1"
        }
        self.rate_limit_delay = 1  # 1 second between requests to respect rate limits
    
    def search_photos(self, query: str, per_page: int = 30, page: int = 1) -> List[Dict]:
        """Search for photos on Unsplash"""
        url = f"{self.api_url}/search/photos"
        params = {
            "query": query,
            "per_page": min(per_page, 30),  # Max 30 per request
            "page": page,
            "orientation": "landscape"  # Better for social media posts
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            time.sleep(self.rate_limit_delay)  # Rate limiting
            
            if response.status_code == 200:
                data = response.json()
                return data.get("results", [])
            else:
                print(f"❌ Unsplash API error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching photos: {e}")
            return []
    
    def get_photo_data(self, photo: Dict) -> Dict:
        """Extract relevant photo data"""
        return {
            "id": photo.get("id"),
            "url": photo.get("urls", {}).get("regular"),
            "thumb_url": photo.get("urls", {}).get("thumb"),
            "description": photo.get("description") or photo.get("alt_description"),
            "author": photo.get("user", {}).get("name"),
            "author_username": photo.get("user", {}).get("username"),
            "download_url": photo.get("links", {}).get("download"),
            "width": photo.get("width"),
            "height": photo.get("height"),
            "color": photo.get("color")
        }
    
    def download_image(self, url: str, filepath: str) -> bool:
        """Download image from URL to local file"""
        try:
            response = requests.get(url, stream=True)
            time.sleep(self.rate_limit_delay)
            
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return True
            else:
                print(f"❌ Failed to download image: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error downloading image: {e}")
            return False

class IndianTravelImageGenerator:
    """Generate Indian travel-themed images using Unsplash"""
    
    def __init__(self, client: UnsplashClient = None):
        self.client = client or UnsplashClient()
        self.travel_keywords = [
            # Major destinations
            "taj mahal agra",
            "goa beach sunset",
            "kerala backwaters",
            "rajasthan palace",
            "mumbai skyline", 
            "delhi red fort",
            "bangalore garden",
            "chennai marina beach",
            "kolkata victoria memorial",
            "hyderabad charminar",
            
            # Activities and experiences
            "indian food street",
            "indian temple",
            "indian market spices",
            "indian festival holi",
            "indian mountains himalaya",
            "indian train journey",
            "indian sunset landscape",
            "indian coffee plantation",
            "indian desert camel",
            "indian river ganges",
            
            # Cultural elements
            "indian architecture",
            "indian culture dance",
            "indian traditional dress",
            "indian handicrafts",
            "indian tea garden",
            "indian yoga meditation",
            "indian wedding celebration",
            "indian boat ride",
            "indian wildlife tiger",
            "indian waterfall nature"
        ]
    
    def fetch_travel_images(self, target_count: int = 3000) -> List[Dict]:
        """Fetch travel images from Unsplash"""
        print(f"🔄 Fetching {target_count} travel images from Unsplash...")
        
        all_images = []
        images_per_keyword = target_count // len(self.travel_keywords) + 1
        
        for i, keyword in enumerate(self.travel_keywords):
            print(f"📸 Fetching images for '{keyword}' ({i+1}/{len(self.travel_keywords)})")
            
            # Calculate how many pages we need (30 images per page max)
            pages_needed = (images_per_keyword // 30) + 1
            
            for page in range(1, pages_needed + 1):
                photos = self.client.search_photos(keyword, per_page=30, page=page)
                
                for photo in photos:
                    if len(all_images) >= target_count:
                        break
                    
                    image_data = self.client.get_photo_data(photo)
                    image_data["keyword"] = keyword
                    image_data["category"] = self._categorize_keyword(keyword)
                    all_images.append(image_data)
                
                if len(all_images) >= target_count:
                    break
            
            if len(all_images) >= target_count:
                break
            
            # Progress update
            if (i + 1) % 5 == 0:
                print(f"✅ Fetched {len(all_images)} images so far...")
        
        print(f"✅ Total images fetched: {len(all_images)}")
        return all_images[:target_count]  # Ensure exact count
    
    def _categorize_keyword(self, keyword: str) -> str:
        """Categorize images based on keywords"""
        if any(place in keyword.lower() for place in ["taj mahal", "delhi", "mumbai", "goa", "kerala", "rajasthan"]):
            return "destination"
        elif any(food in keyword.lower() for food in ["food", "spices", "tea", "coffee"]):
            return "food"
        elif any(culture in keyword.lower() for culture in ["temple", "culture", "festival", "wedding", "dance"]):
            return "culture"
        elif any(nature in keyword.lower() for nature in ["mountain", "river", "waterfall", "nature", "wildlife"]):
            return "nature"
        elif any(activity in keyword.lower() for activity in ["train", "boat", "yoga", "market"]):
            return "activity"
        else:
            return "general"

# Profile picture generator
class ProfilePictureGenerator:
    def __init__(self):
        self.client = UnsplashClient()
        self.profile_keywords = [
            "indian person portrait",
            "indian man smiling",
            "indian woman portrait",
            "indian traveler backpack",
            "indian student young",
            "person hiking mountain",
            "person beach vacation",
            "professional headshot indian"
        ]
    
    def fetch_profile_pictures(self, count: int = 1000) -> List[Dict]:
        """Fetch profile pictures from Unsplash"""
        print(f"🔄 Fetching {count} profile pictures...")
        
        all_profiles = []
        images_per_keyword = count // len(self.profile_keywords) + 1
        
        for keyword in self.profile_keywords:
            photos = self.client.search_photos(keyword, per_page=30)
            
            for photo in photos:
                if len(all_profiles) >= count:
                    break
                
                profile_data = self.client.get_photo_data(photo)
                profile_data["keyword"] = keyword
                all_profiles.append(profile_data)
            
            if len(all_profiles) >= count:
                break
        
        print(f"✅ Profile pictures fetched: {len(all_profiles)}")
        return all_profiles[:count]