import random
from typing import List, Dict
from datetime import datetime, timedelta
import json

class IndianTravelPostGenerator:
    def __init__(self):
        # Indian travel captions with English/Hindi mix
        self.caption_templates = {
            "destination": [
                "Finally made it to {location}! 🏛️ The architecture is absolutely breathtaking! #IncredibleIndia #Travel",
                "Exploring the beauty of {location} ✨ Every corner tells a story! #Wanderlust #IndianHeritage",
                "{location} मे बहुत खुबसूरती है! 😍 Such amazing vibes here! #TravelDiaries #India",
                "Dream destination ✅ {location} exceeded all expectations! #BucketList #TravelGoals",
                "Lost in the beauty of {location} 🌅 Nature at its finest! #NatureLovers #IndianTravel",
                "Memories being made at {location} 📸 Can't get enough of this place! #Memories #Travel",
                "{location} का नज़ारा देखते ही बनता है! Absolutely stunning views! #Views #IncredibleIndia"
            ],
            "food": [
                "Street food adventures in {location} 🍽️ The flavors are incredible! #IndianFood #Foodie",
                "Tasting the authentic flavors of {location} 😋 Every bite is pure bliss! #LocalFood #FoodLover",
                "{location} का खाना लाजवाब है! Best food experience ever! #FoodDiary #IndianCuisine",
                "Food coma incoming! 🤤 {location}'s cuisine is out of this world! #FoodieLife #Travel",
                "Spice level: {location} 🌶️ My taste buds are dancing! #SpicyFood #IndianFlavors",
                "From street vendors to local restaurants, {location} has it all! #LocalEats #FoodTravel"
            ],
            "culture": [
                "Experiencing the rich culture of {location} 🎭 Traditions that never fade! #Culture #Heritage",
                "Festival vibes in {location} 🎉 Colors, music, and pure joy! #Festival #IndianCulture",
                "{location} की संस्कृति अमूल्य है! Such rich traditions! #Traditions #CulturalHeritage",
                "Art, music, and dance - {location} has it all! 🎨 #Arts #Culture #India",
                "Temple hopping in {location} 🛕 Spiritual energy everywhere! #Temples #Spiritual",
                "Local markets of {location} are a photographer's paradise! 📸 #Markets #LocalLife"
            ],
            "nature": [
                "Nature therapy at {location} 🌿 Fresh air and stunning views! #Nature #Peace",
                "Sunrise at {location} hit different! 🌅 Starting the day with gratitude! #Sunrise #Nature",
                "{location} की प्राकृतिक सुंदरता अद्भुत है! Mother nature's masterpiece! #NaturePhotography #Beauty",
                "Trekking through {location} 🥾 Adventure and nature combined! #Trekking #Adventure",
                "Waterfall therapy at {location} 💦 Nothing beats the sound of cascading water! #Waterfalls #Nature",
                "Wildlife spotting in {location} 🐅 Nature never ceases to amaze! #Wildlife #NatureLovers"
            ],
            "activity": [
                "Adventure mode: ON! 🎒 {location} is perfect for thrill seekers! #Adventure #Adrenaline",
                "Boat ride through {location} ⛵ Peaceful and scenic! #BoatRide #Serenity",
                "Photography walk in {location} 📷 Every frame is Instagram-worthy! #Photography #Travel",
                "Yoga session with a view in {location} 🧘‍♀️ Mind, body, and soul alignment! #Yoga #Wellness",
                "Train journey to {location} 🚂 The journey is as beautiful as the destination! #TrainTravel #Journey",
                "Shopping spree in {location} 🛍️ Found some amazing local handicrafts! #Shopping #LocalCrafts"
            ]
        }
        
        # Indian travel hashtags
        self.hashtags = {
            "popular": [
                "#IncredibleIndia", "#IndianTravel", "#Wanderlust", "#TravelDiaries", 
                "#ExploreIndia", "#TravelGram", "#Instatravel", "#TravelAddict"
            ],
            "destination": [
                "#TajMahal", "#Goa", "#Kerala", "#Rajasthan", "#Mumbai", "#Delhi", 
                "#Bangalore", "#Chennai", "#Kolkata", "#Hyderabad", "#Heritage", "#Monument"
            ],
            "activity": [
                "#Adventure", "#Trekking", "#Photography", "#Foodie", "#Culture", 
                "#Festival", "#Nature", "#Wildlife", "#Spiritual", "#Beach", "#Mountains"
            ],
            "mood": [
                "#Blessed", "#Grateful", "#Peaceful", "#Amazing", "#Stunning", "#Beautiful",
                "#Incredible", "#Breathtaking", "#Memorable", "#Perfect", "#Love", "#Joy"
            ]
        }
        
        # Location mapping for posts
        self.location_keywords = {
            "taj mahal agra": {"location": "Agra, Uttar Pradesh", "category": "destination"},
            "goa beach sunset": {"location": "Goa", "category": "nature"},
            "kerala backwaters": {"location": "Alleppey, Kerala", "category": "nature"},
            "rajasthan palace": {"location": "Udaipur, Rajasthan", "category": "destination"},
            "mumbai skyline": {"location": "Mumbai, Maharashtra", "category": "destination"},
            "delhi red fort": {"location": "Delhi", "category": "destination"},
            "bangalore garden": {"location": "Bangalore, Karnataka", "category": "nature"},
            "indian food street": {"location": "Old Delhi", "category": "food"},
            "indian temple": {"location": "Varanasi, Uttar Pradesh", "category": "culture"},
            "indian market spices": {"location": "Jodhpur, Rajasthan", "category": "culture"},
            "indian festival holi": {"location": "Mathura, Uttar Pradesh", "category": "culture"},
            "indian mountains himalaya": {"location": "Manali, Himachal Pradesh", "category": "nature"},
            "indian train journey": {"location": "Indian Railways", "category": "activity"},
            "indian desert camel": {"location": "Jaisalmer, Rajasthan", "category": "activity"},
            "indian river ganges": {"location": "Rishikesh, Uttarakhand", "category": "nature"}
        }
    
    def generate_posts(self, users: List[Dict], images: List[Dict], count: int = 3000) -> List[Dict]:
        """Generate social media posts with images and captions"""
        print(f"🔄 Generating {count} travel posts...")
        
        posts = []
        
        for i in range(count):
            # Select random user and image
            user = random.choice(users)
            
            # Handle empty images list
            if images:
                image = random.choice(images)
            else:
                # Create placeholder image data
                image = {
                    "url": f"https://picsum.photos/800/600?random={i}",
                    "keyword": "indian travel",
                    "description": "Travel destination"
                }
            
            # Generate post content
            post = self._create_post(i + 1, user, image)
            posts.append(post)
            
            # Progress update
            if (i + 1) % 500 == 0:
                print(f"✅ Generated {i + 1} posts...")
        
        print(f"✅ Total posts generated: {len(posts)}")
        return posts
    
    def _create_post(self, post_id: int, user: Dict, image: Dict) -> Dict:
        """Create a single post"""
        # Determine post category and location
        keyword = image.get("keyword", "indian travel")
        location_info = self.location_keywords.get(keyword, {
            "location": user["location"], 
            "category": "general"
        })
        
        category = location_info["category"]
        location = location_info["location"]
        
        # Generate caption
        caption = self._generate_caption(category, location, user)
        
        # Generate timestamp (last 6 months)
        days_ago = random.randint(1, 180)  # 6 months
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        
        created_at = datetime.utcnow() - timedelta(
            days=days_ago, 
            hours=hours_ago, 
            minutes=minutes_ago
        )
        
        # Determine post type
        post_type = "photo"  # Most posts are photos
        if random.random() < 0.1:  # 10% chance of video
            post_type = "video"
        
        return {
            "id": post_id,
            "user_id": user["id"],
            "caption": caption,
            "image_url": image["url"],
            "video_url": image["url"] if post_type == "video" else None,
            "image_description": image.get("description", ""),
            "image_author": image.get("author", ""),
            "location": location,
            "travel_date": created_at - timedelta(days=random.randint(0, 30)),  # Travel happened before post
            "post_type": post_type,
            "likes_count": 0,  # Will be updated by interactions
            "comments_count": 0,
            "shares_count": 0,
            "created_at": created_at,
            "updated_at": created_at,
            "category": category,
            "keyword": keyword
        }
    
    def _generate_caption(self, category: str, location: str, user: Dict) -> str:
        """Generate realistic caption with location and hashtags"""
        # Select caption template based on category
        templates = self.caption_templates.get(category, self.caption_templates["destination"])
        template = random.choice(templates)
        
        # Replace location placeholder
        caption = template.format(location=location)
        
        # Add relevant hashtags
        hashtags = []
        
        # Add popular hashtags (always include some)
        hashtags.extend(random.sample(self.hashtags["popular"], random.randint(2, 4)))
        
        # Add category-specific hashtags
        if category in ["destination", "nature", "culture"]:
            hashtags.extend(random.sample(self.hashtags["destination"], random.randint(1, 3)))
        
        # Add activity hashtags
        hashtags.extend(random.sample(self.hashtags["activity"], random.randint(1, 3)))
        
        # Add mood hashtags
        hashtags.extend(random.sample(self.hashtags["mood"], random.randint(1, 2)))
        
        # Add user's travel style as hashtag
        user_style = user.get("travel_style", "").title()
        if user_style:
            hashtags.append(f"#{user_style}Travel")
        
        # Remove duplicates and limit to 8-12 hashtags
        unique_hashtags = list(set(hashtags))
        selected_hashtags = random.sample(unique_hashtags, min(len(unique_hashtags), random.randint(8, 12)))
        
        # Add hashtags to caption
        hashtag_string = " ".join(selected_hashtags)
        final_caption = f"{caption}\n\n{hashtag_string}"
        
        return final_caption
    
    def assign_locations_to_posts(self, posts: List[Dict], locations: List[Dict]) -> List[Dict]:
        """Assign location IDs to posts based on location names"""
        print("🔄 Assigning location IDs to posts...")
        
        # Create location lookup
        location_lookup = {}
        for loc in locations:
            location_lookup[loc["name"]] = loc["id"]
        
        # Assign location IDs
        for post in posts:
            post_location = post.get("location", "")
            
            # Try to find matching location
            location_id = None
            for loc_name, loc_id in location_lookup.items():
                if loc_name.lower() in post_location.lower():
                    location_id = loc_id
                    break
            
            post["location_id"] = location_id
        
        print("✅ Location IDs assigned to posts")
        return posts

class PostTagGenerator:
    """Generate tags for posts based on content and category"""
    
    def __init__(self):
        self.category_tags = {
            "destination": ["heritage", "monument", "architecture", "historical", "landmark"],
            "food": ["cuisine", "local_food", "street_food", "restaurant", "traditional"],
            "culture": ["festival", "tradition", "art", "music", "dance", "temple"],
            "nature": ["landscape", "scenic", "wildlife", "adventure", "peaceful"],
            "activity": ["experience", "adventure", "fun", "activity", "memorable"]
        }
        
        self.location_tags = {
            "agra": ["taj_mahal", "mughal", "unesco"],
            "goa": ["beach", "coastal", "portuguese"],
            "kerala": ["backwaters", "tropical", "coconut"],
            "rajasthan": ["desert", "royal", "palace", "fort"],
            "mumbai": ["bollywood", "financial_capital", "street_food"],
            "delhi": ["capital", "history", "mughal", "street_food"],
            "bangalore": ["garden_city", "technology", "pleasant_weather"]
        }
    
    def generate_post_tags(self, post: Dict) -> List[Dict]:
        """Generate tags for a post"""
        tags = []
        post_id = post["id"]
        category = post.get("category", "general")
        location = post.get("location", "").lower()
        
        # Add category-based tags
        if category in self.category_tags:
            category_tags = random.sample(self.category_tags[category], random.randint(1, 3))
            for tag in category_tags:
                tags.append({"post_id": post_id, "tag_name": tag})
        
        # Add location-based tags
        for loc_key, loc_tags in self.location_tags.items():
            if loc_key in location:
                location_tags = random.sample(loc_tags, random.randint(1, 2))
                for tag in location_tags:
                    tags.append({"post_id": post_id, "tag_name": tag})
                break
        
        # Add general travel tags
        general_tags = ["travel", "india", "photography", "memories"]
        selected_general = random.sample(general_tags, random.randint(1, 2))
        for tag in selected_general:
            tags.append({"post_id": post_id, "tag_name": tag})
        
        return tags