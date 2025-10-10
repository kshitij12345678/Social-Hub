import random
from faker import Faker
from typing import List, Dict
import hashlib
from datetime import datetime, timedelta

# Initialize Faker with Indian locale
fake = Faker(['en_IN', 'hi_IN'])

class IndianUserGenerator:
    def __init__(self):
        self.indian_cities = [
            # Major cities
            {"name": "Mumbai", "state": "Maharashtra", "type": "major"},
            {"name": "Delhi", "state": "Delhi", "type": "major"},
            {"name": "Bangalore", "state": "Karnataka", "type": "major"},
            {"name": "Chennai", "state": "Tamil Nadu", "type": "major"},
            {"name": "Kolkata", "state": "West Bengal", "type": "major"},
            {"name": "Hyderabad", "state": "Telangana", "type": "major"},
            {"name": "Pune", "state": "Maharashtra", "type": "major"},
            {"name": "Ahmedabad", "state": "Gujarat", "type": "major"},
            
            # Smaller cities/towns
            {"name": "Goa", "state": "Goa", "type": "tourist"},
            {"name": "Jaipur", "state": "Rajasthan", "type": "tourist"},
            {"name": "Kochi", "state": "Kerala", "type": "tourist"},
            {"name": "Udaipur", "state": "Rajasthan", "type": "tourist"},
            {"name": "Agra", "state": "Uttar Pradesh", "type": "tourist"},
            {"name": "Varanasi", "state": "Uttar Pradesh", "type": "tourist"},
            {"name": "Mysore", "state": "Karnataka", "type": "small"},
            {"name": "Coimbatore", "state": "Tamil Nadu", "type": "small"},
            {"name": "Indore", "state": "Madhya Pradesh", "type": "small"},
            {"name": "Bhopal", "state": "Madhya Pradesh", "type": "small"},
            {"name": "Chandigarh", "state": "Punjab", "type": "small"},
            {"name": "Shimla", "state": "Himachal Pradesh", "type": "hill_station"}
        ]
        
        self.travel_styles = [
            "adventure", "luxury", "budget", "family", "solo", 
            "cultural", "nature", "photography", "food", "spiritual"
        ]
        
        self.indian_male_names = [
            "Arjun", "Rahul", "Amit", "Rohit", "Vikram", "Rajesh", "Suresh", "Kiran",
            "Arun", "Ravi", "Manoj", "Sanjay", "Ajay", "Vinod", "Deepak", "Ashok",
            "Nitin", "Sachin", "Anil", "Ramesh", "Rakesh", "Mukesh", "Dinesh", "Naresh",
            "Pradeep", "Sandeep", "Mahesh", "Yogesh", "Umesh", "Ganesh", "Jagdish", "Harish"
        ]
        
        self.indian_female_names = [
            "Priya", "Anjali", "Pooja", "Sunita", "Kavita", "Meera", "Seema", "Ritu",
            "Nisha", "Rekha", "Shweta", "Neha", "Asha", "Usha", "Maya", "Sita",
            "Radha", "Gita", "Lata", "Kiran", "Sushma", "Pushpa", "Lalita", "Savita",
            "Vandana", "Archana", "Suman", "Renu", "Manju", "Anju", "Ravi", "Devi"
        ]
        
        self.indian_surnames = [
            "Sharma", "Singh", "Kumar", "Gupta", "Agarwal", "Shah", "Patel", "Reddy",
            "Iyer", "Nair", "Rao", "Jain", "Bansal", "Malhotra", "Chopra", "Kapoor",
            "Verma", "Srivastava", "Mishra", "Pandey", "Tiwari", "Dubey", "Shukla", "Joshi",
            "Mehta", "Saxena", "Agrawal", "Goyal", "Mittal", "Arora", "Khurana", "Bhatia"
        ]
    
    def generate_users(self, count: int = 1000) -> List[Dict]:
        """Generate realistic Indian users"""
        print(f"🔄 Generating {count} Indian users...")
        
        users = []
        male_count = count // 2
        female_count = count - male_count
        
        # Generate male users
        for i in range(male_count):
            user = self._generate_male_user(i + 1)
            users.append(user)
        
        # Generate female users
        for i in range(female_count):
            user = self._generate_female_user(male_count + i + 1)
            users.append(user)
        
        # Shuffle to mix genders
        random.shuffle(users)
        
        print(f"✅ Generated {len(users)} users ({male_count} male, {female_count} female)")
        return users
    
    def _generate_male_user(self, user_id: int) -> Dict:
        """Generate a male user profile"""
        first_name = random.choice(self.indian_male_names)
        last_name = random.choice(self.indian_surnames)
        city = random.choice(self.indian_cities)
        
        return self._create_user_profile(user_id, first_name, last_name, city, "male")
    
    def _generate_female_user(self, user_id: int) -> Dict:
        """Generate a female user profile"""
        first_name = random.choice(self.indian_female_names)
        last_name = random.choice(self.indian_surnames)
        city = random.choice(self.indian_cities)
        
        return self._create_user_profile(user_id, first_name, last_name, city, "female")
    
    def _create_user_profile(self, user_id: int, first_name: str, last_name: str, city: Dict, gender: str) -> Dict:
        """Create a complete user profile"""
        full_name = f"{first_name} {last_name}"
        
        # Generate unique email with user_id to ensure uniqueness
        email_domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]
        username = f"{first_name.lower()}{last_name.lower()}{user_id}"
        domain = random.choice(email_domains)
        email = f"{username}@{domain}"
        
        # Generate travel bio
        travel_interests = random.sample(self.travel_styles, random.randint(2, 4))
        bio_templates = [
            f"🌍 Travel enthusiast | {' & '.join(travel_interests)} | From {city['name']}",
            f"📸 Capturing memories across India | Love {' and '.join(travel_interests)} travel",
            f"✈️ Wanderlust soul | {city['name']} based | Passionate about {' '.join(travel_interests)} adventures",
            f"🗺️ Exploring incredible India | {' | '.join(travel_interests)} | {city['name']} 📍",
            f"🎒 Travel blogger | {' enthusiast | '.join(travel_interests)} | Born in {city['name']}"
        ]
        
        # User age and account creation
        age = random.randint(18, 45)
        days_ago = random.randint(30, 365)  # Account created in last year
        created_at = datetime.utcnow() - timedelta(days=days_ago)
        
        return {
            "id": user_id,
            "full_name": full_name,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": "password123",  # Default password for all users
            "hashed_password": self._hash_password("password123"),
            "bio": random.choice(bio_templates),
            "location": f"{city['name']}, {city['state']}",
            "city_type": city['type'],
            "age": age,
            "gender": gender,
            "travel_style": random.choice(self.travel_styles),
            "travel_interests": travel_interests,
            "auth_provider": "local",
            "is_active": True,
            "created_at": created_at,
            "updated_at": created_at,
            "profile_picture_url": None  # Will be set later with Unsplash images
        }
    
    def _hash_password(self, password: str) -> str:
        """Hash password for database storage"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def assign_profile_pictures(self, users: List[Dict], profile_pictures: List[Dict]) -> List[Dict]:
        """Assign profile pictures to users"""
        print("🔄 Assigning profile pictures to users...")
        
        # Shuffle profile pictures for random assignment
        random.shuffle(profile_pictures)
        
        for i, user in enumerate(users):
            if i < len(profile_pictures):
                user["profile_picture_url"] = profile_pictures[i]["url"]
                user["profile_picture_thumb"] = profile_pictures[i]["thumb_url"]
        
        print("✅ Profile pictures assigned")
        return users

class UserInterestGenerator:
    """Generate user interests for recommendation system"""
    
    def __init__(self):
        self.interest_categories = {
            "destination": [
                "beaches", "mountains", "cities", "temples", "palaces", "forts",
                "backwaters", "deserts", "hill_stations", "national_parks"
            ],
            "activity": [
                "photography", "trekking", "camping", "water_sports", "heritage_tours",
                "food_tours", "wildlife_safari", "adventure_sports", "cultural_shows", "meditation"
            ],
            "style": [
                "luxury", "budget", "solo", "family", "group", "romantic",
                "adventure", "cultural", "spiritual", "eco_friendly"
            ]
        }
    
    def generate_user_interests(self, user: Dict) -> List[Dict]:
        """Generate interests for a user based on their profile"""
        interests = []
        
        # Generate interests based on travel style
        travel_style = user.get("travel_style", "cultural")
        city_type = user.get("city_type", "major")
        
        # Add destination interests based on city type
        if city_type == "tourist":
            interests.extend(self._create_interests(user["id"], "destination", ["temples", "palaces", "heritage"], high_weight=True))
        elif city_type == "major":
            interests.extend(self._create_interests(user["id"], "destination", ["cities", "museums", "food_tours"]))
        elif city_type == "hill_station":
            interests.extend(self._create_interests(user["id"], "destination", ["mountains", "nature", "trekking"]))
        
        # Add activity interests based on travel style
        if travel_style == "adventure":
            interests.extend(self._create_interests(user["id"], "activity", ["trekking", "camping", "adventure_sports"], high_weight=True))
        elif travel_style == "cultural":
            interests.extend(self._create_interests(user["id"], "activity", ["heritage_tours", "cultural_shows", "temples"]))
        elif travel_style == "photography":
            interests.extend(self._create_interests(user["id"], "activity", ["photography", "wildlife_safari"], high_weight=True))
        
        # Add style interests
        interests.extend(self._create_interests(user["id"], "style", [travel_style], high_weight=True))
        
        # Add some random interests for diversity
        for category, values in self.interest_categories.items():
            random_interests = random.sample(values, random.randint(1, 3))
            interests.extend(self._create_interests(user["id"], category, random_interests))
        
        return interests
    
    def _create_interests(self, user_id: int, interest_type: str, values: List[str], high_weight: bool = False) -> List[Dict]:
        """Create interest records"""
        interests = []
        base_weight = 2.0 if high_weight else 1.0
        
        for value in values:
            weight = base_weight + random.uniform(-0.5, 0.5)  # Add some randomness
            interests.append({
                "user_id": user_id,
                "interest_type": interest_type,
                "interest_value": value,
                "weight": max(0.1, weight)  # Ensure positive weight
            })
        
        return interests