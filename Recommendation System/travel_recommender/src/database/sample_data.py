import random
import sqlite3
from faker import Faker
from datetime import datetime, timedelta
from src.database.models import DatabaseManager

# Set up Faker for Indian data
fake = Faker('en_IN')

class TravelDataGenerator:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        # Indian travel destinations - mix of domestic and popular international spots for Indians
        self.destinations = [
            # Popular Indian destinations
            ("Goa", "India", "Asia", 15.2993, 74.1240, "beach"),
            ("Kerala Backwaters", "India", "Asia", 9.9312, 76.2673, "nature"),
            ("Rajasthan", "India", "Asia", 27.0238, 74.2179, "historical"),
            ("Kashmir", "India", "Asia", 34.0837, 74.7973, "mountain"),
            ("Mumbai", "India", "Asia", 19.0760, 72.8777, "city"),
            ("Delhi", "India", "Asia", 28.7041, 77.1025, "city"),
            ("Manali", "India", "Asia", 32.2432, 77.1892, "mountain"),
            ("Rishikesh", "India", "Asia", 30.0869, 78.2676, "spiritual"),
            ("Agra", "India", "Asia", 27.1767, 78.0081, "historical"),
            ("Hampi", "India", "Asia", 15.3350, 76.4600, "historical"),
            ("Ladakh", "India", "Asia", 34.1526, 77.5770, "mountain"),
            ("Udaipur", "India", "Asia", 24.5854, 73.7125, "historical"),
            
            # Popular international destinations for Indians
            ("Dubai", "UAE", "Asia", 25.2048, 55.2708, "city"),
            ("Thailand", "Thailand", "Asia", 15.8700, 100.9925, "beach"),
            ("Singapore", "Singapore", "Asia", 1.3521, 103.8198, "city"),
            ("London", "UK", "Europe", 51.5074, -0.1278, "city"),
            ("Paris", "France", "Europe", 48.8566, 2.3522, "city"),
            ("Maldives", "Maldives", "Asia", 3.2028, 73.2207, "beach"),
            ("Nepal", "Nepal", "Asia", 28.1667, 84.2500, "mountain"),
            ("Sri Lanka", "Sri Lanka", "Asia", 7.8731, 80.7718, "beach")
        ]
        
        # Indian travel tags and interests
        self.travel_tags = [
            "Adventure", "Beach", "Culture", "Food", "Nature", "Photography",
            "Backpacking", "Luxury", "Solo Travel", "Family", "Historical",
            "Wildlife", "Mountains", "Cities", "Sunset", "Architecture",
            "Spiritual", "Temples", "Heritage", "Festivals", "Street Food",
            "Bollywood", "Royal", "Ayurveda", "Yoga", "Monsoon"
        ]
        
        self.travel_styles = ["Adventure", "Luxury", "Budget", "Family", "Solo", "Couples", "Friends", "Spiritual"]
        
        # Indian names for more authentic profiles
        self.indian_first_names = [
            "Arjun", "Priya", "Rahul", "Ananya", "Rohan", "Kavya", "Aman", "Shreya",
            "Vikram", "Riya", "Aditya", "Neha", "Karan", "Pooja", "Siddharth", "Meera",
            "Aryan", "Isha", "Varun", "Divya", "Nikhil", "Sakshi", "Akash", "Tanvi"
        ]
        
        self.indian_last_names = [
            "Sharma", "Gupta", "Singh", "Kumar", "Patel", "Shah", "Agarwal", "Jain",
            "Mehta", "Malhotra", "Khanna", "Verma", "Agnihotri", "Bansal", "Chopra"
        ]
        
        self.indian_cities = [
            "Mumbai", "Delhi", "Bangalore", "Pune", "Chennai", "Hyderabad", 
            "Kolkata", "Ahmedabad", "Jaipur", "Chandigarh", "Gurgaon", "Noida"
        ]
        
    def generate_locations(self):
        """Generate location data"""
        print("🌍 Generating locations...")
        
        for name, country, continent, lat, lng, category in self.destinations:
            query = """
                INSERT OR IGNORE INTO locations (name, country, continent, latitude, longitude, category)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            self.db.execute_insert(query, (name, country, continent, lat, lng, category))
        
        print(f"✅ Generated {len(self.destinations)} locations")
    
    def generate_users(self, num_users: int = 100):
        """Generate Indian travel enthusiast users"""
        print(f"👥 Generating {num_users} Indian travel enthusiasts...")
        
        for i in range(num_users):
            # Create Indian usernames and names
            first_name = random.choice(self.indian_first_names)
            last_name = random.choice(self.indian_last_names)
            username = f"{first_name.lower()}_{last_name.lower()}_{random.randint(10, 99)}"
            
            # Indian email domains
            email_domains = ["gmail.com", "yahoo.co.in", "hotmail.com", "rediffmail.com"]
            email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 99)}@{random.choice(email_domains)}"
            
            full_name = f"{first_name} {last_name}"
            bio = self.generate_indian_travel_bio()
            location = random.choice(self.indian_cities)
            travel_style = random.choice(self.travel_styles)
            
            query = """
                INSERT INTO users (username, email, full_name, bio, location, travel_style)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            
            self.db.execute_insert(query, (username, email, full_name, bio, location, travel_style))
        
        print(f"✅ Generated {num_users} Indian users")
    
    def generate_indian_travel_bio(self):
        """Generate realistic Indian travel bios"""
        bio_templates = [
            "✈️ Travel junkie | 📸 Capturing India's beauty | �🇳 {states} states explored",
            "🎒 Wanderlust | �️ Spiritual seeker | Currently exploring {location}",
            "🌅 Sunrise chaser | 🏔️ Mountain lover | From {city} with love ❤️",
            "📷 Travel photographer | 🌺 Culture enthusiast | Heritage explorer",
            "🏖️ Beach bum | 🥥 Goa vibes | 🌊 Salt in hair, sand in toes",
            "🛕 Temple hopper | 🎭 Festival lover | Living the desi dream",
            "🍛 Foodie traveler | 🚂 Train journeys | Discovering incredible India",
            "🧘‍♀️ Yoga enthusiast | 🕉️ Spiritual wanderer | Peace seeker",
            "👫 Travel with squad | � Making memories | Life's a journey!",
            "💫 Solo female traveler | 🦋 Breaking stereotypes | Fearless explorer"
        ]
        
        template = random.choice(bio_templates)
        states = random.randint(8, 28)  # India has 28 states
        location = random.choice([dest[0] for dest in self.destinations if dest[1] == "India"])
        city = random.choice(self.indian_cities)
        
        return template.format(states=states, location=location, city=city)
    
    def generate_posts(self, num_posts: int = 500):
        """Generate travel posts"""
        print(f"📸 Generating {num_posts} travel posts...")
        
        users = self.db.execute_query("SELECT user_id FROM users")
        locations = self.db.execute_query("SELECT location_id, name FROM locations")
        
        for i in range(num_posts):
            user_id = random.choice(users)[0]
            location_id, location_name = random.choice(locations)
            
            caption = self.generate_indian_travel_caption(location_name)
            post_type = random.choices(['photo', 'video'], weights=[0.8, 0.2])[0]
            
            # Random travel date in the past 2 years
            travel_date = fake.date_between(start_date='-2y', end_date='today')
            
            query = """
                INSERT INTO posts (user_id, caption, location_id, travel_date, post_type)
                VALUES (?, ?, ?, ?, ?)
            """
            
            post_id = self.db.execute_insert(query, (user_id, caption, location_id, travel_date, post_type))
            
            # Add random tags to posts
            num_tags = random.randint(1, 4)
            selected_tags = random.sample(self.travel_tags, num_tags)
            
            for tag in selected_tags:
                tag_query = "INSERT OR IGNORE INTO post_tags (post_id, tag_name) VALUES (?, ?)"
                self.db.execute_insert(tag_query, (post_id, tag))
        
        print(f"✅ Generated {num_posts} posts with tags")
    
    def generate_indian_travel_caption(self, location_name):
        """Generate realistic Indian travel captions"""
        caption_templates = [
            f"Magical sunset at {location_name}! 🌅 India never fails to amaze ✨ #IncredibleIndia",
            f"Just reached {location_name} and I'm speechless! 😍 #wanderlust #IndianTravel",
            f"The beauty of {location_name} is beyond imagination... 📸 #traveldiaries #India",
            f"Living my best life in {location_name}! Tag someone who needs to see this! 🌍",
            f"Missing {location_name} already... Next trip planning mode ON! ✈️ #TravelBug",
            f"Food, culture, heritage - {location_name} has my heart! �🏛️ #IndianCulture",
            f"Solo trip to {location_name}! Sometimes you need to get lost to find yourself 🙏",
            f"Squad trip to {location_name}! These memories will last forever! 👥 #FriendsTrip",
            f"Spiritual vibes at {location_name} 🕉️ Feeling blessed and grateful 🙏",
            f"Heritage walk in {location_name}! Our history is so rich 🏛️ #ProudIndian",
            f"Street food hunting in {location_name}! Foodie heaven 🍛 #StreetFood",
            f"Festival season in {location_name}! Colors everywhere 🎨 #IndianFestival"
        ]
        
        return random.choice(caption_templates)
    
    def generate_interactions(self, num_interactions: int = 2000):
        """Generate user interactions"""
        print(f"❤️ Generating {num_interactions} interactions...")
        
        users = self.db.execute_query("SELECT user_id FROM users")
        posts = self.db.execute_query("SELECT post_id, user_id FROM posts")
        
        interaction_types = ['like', 'comment', 'share', 'save']
        weights = [0.6, 0.25, 0.1, 0.05]  # Likes are most common
        
        for i in range(num_interactions):
            user_id = random.choice(users)[0]
            post_id, post_owner = random.choice(posts)
            
            # Users don't interact with their own posts (mostly)
            if user_id == post_owner and random.random() < 0.9:
                continue
            
            interaction_type = random.choices(interaction_types, weights=weights)[0]
            comment_text = None
            
            if interaction_type == 'comment':
                comment_text = self.generate_indian_travel_comment()
            
            # Random timestamp in the past month
            timestamp = fake.date_time_between(start_date='-1M', end_date='now')
            
            query = """
                INSERT OR IGNORE INTO interactions 
                (user_id, post_id, interaction_type, comment_text, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """
            
            self.db.execute_insert(query, (user_id, post_id, interaction_type, comment_text, timestamp))
        
        print(f"✅ Generated interactions")
    
    def generate_indian_travel_comment(self):
        """Generate realistic Indian travel comments"""
        comments = [
            "Wow yaar, this looks amazing! 😍",
            "Adding this to my bucket list bro! ✈️",
            "I was there last month, such a beautiful place!",
            "Total goals! 🌟 Which camera you used?",
            "Bhai kaise find kiya ye spot?",
            "Incredible shot! 📸 Instagram worthy!",
            "Living vicariously through your travels! Next time saath le jana",
            "Need to visit ASAP! 🗺️ Planning next month",
            "This is why I love our incredible India! 🇮�",
            "Jealous! When are you going back? Mai bhi aaunga",
            "Mast hai yaar! 🔥",
            "Kitna kharcha hua total?",
            "Solo gaya ya group trip tha?",
            "Weather kaisa tha? Planning same time pe jaane ka",
            "Bhai tu to photographer hai! Teaching session de de"
        ]
        return random.choice(comments)
    
    def generate_follows(self, num_follows: int = 800):
        """Generate follow relationships"""
        print(f"👥 Generating {num_follows} follow relationships...")
        
        users = [row[0] for row in self.db.execute_query("SELECT user_id FROM users")]
        
        for i in range(num_follows):
            follower = random.choice(users)
            following = random.choice(users)
            
            # Don't follow yourself
            if follower == following:
                continue
            
            query = """
                INSERT OR IGNORE INTO follows (follower_id, following_id)
                VALUES (?, ?)
            """
            
            self.db.execute_insert(query, (follower, following))
        
        print(f"✅ Generated follow relationships")
    
    def generate_user_interests(self):
        """Generate user travel interests based on their interactions"""
        print("🎯 Generating user interests...")
        
        users = self.db.execute_query("SELECT user_id FROM users")
        
        for user_id, in users:
            # Add destination interests
            destinations = random.sample([dest[0] for dest in self.destinations], random.randint(3, 8))
            for dest in destinations:
                query = """
                    INSERT OR IGNORE INTO user_interests 
                    (user_id, interest_type, interest_value, weight)
                    VALUES (?, ?, ?, ?)
                """
                weight = random.uniform(0.3, 1.0)
                self.db.execute_insert(query, (user_id, 'destination', dest, weight))
            
            # Add activity interests
            activities = random.sample(self.travel_tags, random.randint(3, 6))
            for activity in activities:
                query = """
                    INSERT OR IGNORE INTO user_interests 
                    (user_id, interest_type, interest_value, weight)
                    VALUES (?, ?, ?, ?)
                """
                weight = random.uniform(0.4, 1.0)
                self.db.execute_insert(query, (user_id, 'activity', activity, weight))
        
        print("✅ Generated user interests")
    
    def generate_all(self):
        """Generate complete sample dataset"""
        print("🚀 Starting data generation for Travel Instagram...")
        
        self.generate_locations()
        self.generate_users(100)
        self.generate_posts(500)
        self.generate_interactions(2000)
        self.generate_follows(800)
        self.generate_user_interests()
        
        print("\n✅ Sample data generation complete!")
        print("📊 Dataset summary:")
        
        # Print summary stats
        stats = {
            'Users': self.db.execute_query("SELECT COUNT(*) FROM users")[0][0],
            'Posts': self.db.execute_query("SELECT COUNT(*) FROM posts")[0][0],
            'Interactions': self.db.execute_query("SELECT COUNT(*) FROM interactions")[0][0],
            'Follows': self.db.execute_query("SELECT COUNT(*) FROM follows")[0][0],
            'Locations': self.db.execute_query("SELECT COUNT(*) FROM locations")[0][0],
        }
        
        for key, value in stats.items():
            print(f"   {key}: {value}")

if __name__ == "__main__":
    db = DatabaseManager()
    generator = TravelDataGenerator(db)
    generator.generate_all()