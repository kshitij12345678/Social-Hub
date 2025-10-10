import sys
import os
import asyncio
from typing import List, Dict
import random
from datetime import datetime, timedelta

# Add backend to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from sqlalchemy.orm import Session
    from database import get_db, User, Post, Like, Comment, Share, Location, Follow, UserInterest, PostTag
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you're in the backend directory and have activated the virtual environment")
    sys.exit(1)

# Import all our generators
from data_generators.unsplash_client import UnsplashClient, IndianTravelImageGenerator
from data_generators.user_generator import IndianUserGenerator
from data_generators.post_generator import IndianTravelPostGenerator
from data_generators.interaction_generator import SocialInteractionGenerator
from data_generators.location_generator import IndianLocationGenerator

class SyntheticDataOrchestrator:
    def __init__(self, unsplash_access_key: str = None):
        """Initialize the data generation orchestrator"""
        self.unsplash_client = UnsplashClient(unsplash_access_key) if unsplash_access_key else None
        self.image_generator = IndianTravelImageGenerator(self.unsplash_client) if unsplash_access_key else None
        self.user_generator = IndianUserGenerator()
        self.post_generator = IndianTravelPostGenerator()
        self.interaction_generator = SocialInteractionGenerator()
        self.location_generator = IndianLocationGenerator()
        
        # Configuration
        self.target_users = 1000
        self.target_posts = 3000
        self.target_interactions = 15000
        
        # Storage for generated data
        self.generated_users = []
        self.generated_locations = []
        self.generated_posts = []
        
        print("🚀 Synthetic Data Orchestrator initialized!")
        print(f"📊 Target: {self.target_users} users, {self.target_posts} posts, {self.target_interactions} interactions")
        
    async def clear_existing_data(self, db: Session):
        """Clear all existing data from database tables"""
        print("\n🧹 Clearing existing data...")
        
        try:
            # Delete in order of dependencies
            db.query(PostTag).delete()
            db.query(UserInterest).delete()
            db.query(Share).delete()
            db.query(Comment).delete()
            db.query(Like).delete()
            db.query(Follow).delete()
            db.query(Post).delete()
            db.query(Location).delete()
            db.query(User).delete()
            
            db.commit()
            print("✅ All existing data cleared successfully")
            
        except Exception as e:
            print(f"❌ Error clearing data: {e}")
            db.rollback()
            raise
    
    async def generate_locations(self, db: Session):
        """Generate and insert location data"""
        print("\n📍 Generating locations...")
        
        try:
            locations_data = self.location_generator.generate_locations()
            
            for location_data in locations_data:
                location = Location(
                    name=location_data["name"],
                    country=location_data["country"],
                    continent=location_data["continent"],
                    latitude=location_data["latitude"],
                    longitude=location_data["longitude"],
                    category=location_data["category"]
                )
                db.add(location)
                self.generated_locations.append(location)
            
            db.commit()
            print(f"✅ Generated {len(locations_data)} locations")
            
        except Exception as e:
            print(f"❌ Error generating locations: {e}")
            db.rollback()
            raise
    
    async def generate_users(self, db: Session):
        """Generate and insert user data"""
        print(f"\n👥 Generating {self.target_users} users...")
        
        try:
            users_data = self.user_generator.generate_users(self.target_users)
            
            for i, user_data in enumerate(users_data):
                user = User(
                    full_name=user_data["full_name"],
                    email=user_data["email"],
                    bio=user_data["bio"],
                    profile_picture_url=user_data.get("profile_picture_url", "https://via.placeholder.com/150"),
                    google_id=f"synthetic_google_{i+1}",
                    auth_provider="GOOGLE",
                    location=user_data.get("location", "India"),
                    travel_style=user_data.get("travel_style", "explorer"),
                    is_active=True,
                    created_at=user_data["created_at"]
                )
                db.add(user)
                self.generated_users.append(user)
                
                if (i + 1) % 100 == 0:
                    print(f"  📝 Generated {i + 1}/{self.target_users} users...")
            
            db.commit()
            print(f"✅ Generated {len(users_data)} users")
            
        except Exception as e:
            print(f"❌ Error generating users: {e}")
            db.rollback()
            raise
    
    async def generate_user_interests(self, db: Session):
        """Generate user interests for better recommendations"""
        print("\n🎯 Generating user interests...")
        
        try:
            interests = [
                "Adventure Travel", "Beach Holidays", "Mountain Trekking", "Cultural Tours",
                "Food Tourism", "Photography", "Wildlife Safari", "Spiritual Journey",
                "Historical Sites", "Luxury Travel", "Budget Travel", "Solo Travel",
                "Family Vacation", "Honeymoon", "Backpacking", "Pilgrimage",
                "Temple Visits", "Palace Tours", "Desert Safari", "Backwater Cruise",
                "Hill Station", "Tea Gardens", "Waterfalls", "National Parks"
            ]
            
            user_interests_created = 0
            
            for user in self.generated_users:
                # Each user gets 3-7 random interests
                num_interests = random.randint(3, 7)
                user_interests = random.sample(interests, num_interests)
                
                for interest in user_interests:
                    user_interest = UserInterest(
                        user_id=user.id,
                        interest_type="travel",
                        interest_value=interest,
                        weight=random.uniform(0.3, 1.0)  # Interest strength
                    )
                    db.add(user_interest)
                    user_interests_created += 1
            
            db.commit()
            print(f"✅ Generated {user_interests_created} user interests")
            
        except Exception as e:
            print(f"❌ Error generating user interests: {e}")
            db.rollback()
            raise
    
    async def generate_follows(self, db: Session):
        """Generate follow relationships between users"""
        print("\n🤝 Generating follow relationships...")
        
        try:
            follows_created = 0
            
            for user in self.generated_users:
                # Each user follows 20-100 other users
                num_follows = random.randint(20, 100)
                
                # Get potential users to follow (excluding self)
                potential_follows = [u for u in self.generated_users if u.id != user.id]
                users_to_follow = random.sample(potential_follows, min(num_follows, len(potential_follows)))
                
                for followed_user in users_to_follow:
                    # Check if follow relationship already exists
                    existing_follow = db.query(Follow).filter_by(
                        follower_id=user.id,
                        following_id=followed_user.id
                    ).first()
                    
                    if not existing_follow:
                        follow = Follow(
                            follower_id=user.id,
                            following_id=followed_user.id,
                            created_at=datetime.now() - timedelta(days=random.randint(1, 365))
                        )
                        db.add(follow)
                        follows_created += 1
            
            db.commit()
            
            # Note: follower/following counts will be calculated in verification
            # as the current User model doesn't have these fields
            
            db.commit()
            print(f"✅ Generated {follows_created} follow relationships")
            
        except Exception as e:
            print(f"❌ Error generating follows: {e}")
            db.rollback()
            raise
    
    async def generate_posts(self, db: Session):
        """Generate posts with images from Unsplash"""
        print(f"\n📸 Generating {self.target_posts} posts...")
        
        try:
            # Convert users to expected format for post generator
            users_data = []
            for user in self.generated_users:
                users_data.append({
                    "id": user.id,
                    "full_name": user.full_name,
                    "location": user.location
                })
            
            # Generate post data
            posts_data = self.post_generator.generate_posts(
                users=users_data,
                images=[],  # Will be populated with Unsplash images below
                count=self.target_posts
            )
            
            # Try Unsplash with fallback to placeholder images
            if self.image_generator and self.unsplash_client and self.unsplash_client.access_key:
                try:
                    print("🖼️  Downloading travel images from Unsplash...")
                    images = self.image_generator.fetch_travel_images(min(100, self.target_posts))  # Limit to 100 for faster testing
                    
                    if images:
                        print(f"✅ Successfully fetched {len(images)} images from Unsplash")
                        # Match images with posts
                        for i, post_data in enumerate(posts_data):
                            if i < len(images):
                                post_data["image_url"] = images[i]["url"]
                                post_data["image_description"] = images[i]["description"]
                            else:
                                post_data["image_url"] = f"https://picsum.photos/800/600?random={i}"
                                post_data["image_description"] = "Travel destination"
                    else:
                        print("⚠️  No images fetched from Unsplash, using placeholders")
                        for i, post_data in enumerate(posts_data):
                            post_data["image_url"] = f"https://picsum.photos/800/600?random={i}"
                            post_data["image_description"] = "Travel destination"
                        
                except Exception as e:
                    print(f"⚠️  Unsplash API failed: {e}")
                    print("📷 Falling back to placeholder images")
                    for i, post_data in enumerate(posts_data):
                        post_data["image_url"] = f"https://picsum.photos/800/600?random={i}"
                        post_data["image_description"] = "Travel destination"
            else:
                print("📷 Using placeholder images (no valid Unsplash API key)")
                for i, post_data in enumerate(posts_data):
                    post_data["image_url"] = f"https://picsum.photos/800/600?random={i}"
                    post_data["image_description"] = "Travel destination"
            
            # Create posts in database
            for i, post_data in enumerate(posts_data):
                # Get random location
                location = random.choice(self.generated_locations) if self.generated_locations else None
                
                post = Post(
                    user_id=post_data["user_id"],
                    caption=post_data["caption"],
                    image_url=post_data["image_url"],
                    location_id=location.id if location else None,
                    likes_count=0,  # Will be updated after generating likes
                    comments_count=0,  # Will be updated after generating comments
                    shares_count=0,   # Will be updated after generating shares
                    created_at=post_data["created_at"]
                )
                db.add(post)
                self.generated_posts.append(post)
                
                if (i + 1) % 500 == 0:
                    print(f"  📝 Generated {i + 1}/{self.target_posts} posts...")
            
            db.commit()
            
            # Note: post counts will be calculated in verification
            # as the current User model doesn't have post_count field
            
            db.commit()
            print(f"✅ Generated {len(posts_data)} posts")
            
        except Exception as e:
            print(f"❌ Error generating posts: {e}")
            db.rollback()
            raise
    
    async def generate_post_tags(self, db: Session):
        """Generate tags for posts"""
        print("\n🏷️  Generating post tags...")
        
        try:
            tags = [
                "travel", "india", "incredibleindia", "wanderlust", "explore",
                "adventure", "nature", "culture", "heritage", "photography",
                "travelgram", "instatravel", "vacation", "holiday", "tourism",
                "mountains", "beaches", "temples", "forts", "palaces",
                "backwaters", "desert", "wildlife", "spirituality", "food"
            ]
            
            tags_created = 0
            
            for post in self.generated_posts:
                # Each post gets 3-8 random tags
                num_tags = random.randint(3, 8)
                post_tags = random.sample(tags, num_tags)
                
                for tag in post_tags:
                    post_tag = PostTag(
                        post_id=post.id,
                        tag_name=tag
                    )
                    db.add(post_tag)
                    tags_created += 1
            
            db.commit()
            print(f"✅ Generated {tags_created} post tags")
            
        except Exception as e:
            print(f"❌ Error generating post tags: {e}")
            db.rollback()
            raise
    
    async def generate_interactions(self, db: Session):
        """Generate likes, comments, and shares"""
        print(f"\n💬 Generating {self.target_interactions} interactions...")
        
        try:
            # Convert users and posts to expected format
            users_data = [{"id": user.id, "full_name": user.full_name, "location": user.location} for user in self.generated_users]
            posts_data = [{"id": post.id, "user_id": post.user_id, "created_at": post.created_at} for post in self.generated_posts]
            
            interactions_data = self.interaction_generator.generate_interactions(
                users=users_data,
                posts=posts_data,
                target_count=self.target_interactions
            )
            
            likes_created = 0
            comments_created = 0
            shares_created = 0
            
            # Process likes
            for like_data in interactions_data["likes"]:
                # Check if like already exists
                existing_like = db.query(Like).filter_by(
                    user_id=like_data["user_id"],
                    post_id=like_data["post_id"]
                ).first()
                
                if not existing_like:
                    like = Like(
                        user_id=like_data["user_id"],
                        post_id=like_data["post_id"],
                        created_at=like_data["created_at"]
                    )
                    db.add(like)
                    likes_created += 1
            
            # Process comments
            for comment_data in interactions_data["comments"]:
                comment = Comment(
                    user_id=comment_data["user_id"],
                    post_id=comment_data["post_id"],
                    comment_text=comment_data["comment_text"],
                    created_at=comment_data["created_at"]
                )
                db.add(comment)
                comments_created += 1
            
            # Process shares
            for share_data in interactions_data["shares"]:
                share = Share(
                    user_id=share_data["user_id"],
                    post_id=share_data["post_id"],
                    created_at=share_data["created_at"]
                )
                db.add(share)
                shares_created += 1
            
            db.commit()
            
            # Update post interaction counts
            for post in self.generated_posts:
                likes_count = db.query(Like).filter_by(post_id=post.id).count()
                comments_count = db.query(Comment).filter_by(post_id=post.id).count()
                shares_count = db.query(Share).filter_by(post_id=post.id).count()
                
                post.likes_count = likes_count
                post.comments_count = comments_count
                post.shares_count = shares_count
            
            db.commit()
            
            total_interactions = likes_created + comments_created + shares_created
            print(f"✅ Generated {total_interactions} interactions:")
            print(f"   👍 {likes_created} likes")
            print(f"   💬 {comments_created} comments")
            print(f"   🔄 {shares_created} shares")
            
        except Exception as e:
            print(f"❌ Error generating interactions: {e}")
            db.rollback()
            raise
    
    async def run_full_generation(self, clear_existing: bool = True, use_unsplash: bool = True):
        """Run the complete data generation process"""
        print("🎬 Starting complete synthetic data generation...")
        start_time = datetime.now()
        
        # Get database session
        db = next(get_db())
        
        try:
            if clear_existing:
                await self.clear_existing_data(db)
            
            # Step 1: Generate locations
            await self.generate_locations(db)
            
            # Step 2: Generate users
            await self.generate_users(db)
            
            # Step 3: Generate user interests
            await self.generate_user_interests(db)
            
            # Step 4: Generate follow relationships
            await self.generate_follows(db)
            
            # Step 5: Generate posts
            await self.generate_posts(db)
            
            # Step 6: Generate post tags
            await self.generate_post_tags(db)
            
            # Step 7: Generate interactions
            await self.generate_interactions(db)
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            print(f"\n🎉 Synthetic Data Generation Complete!")
            print(f"⏱️  Total time: {duration}")
            print(f"📊 Generated:")
            print(f"   👥 {len(self.generated_users)} users")
            print(f"   📍 {len(self.generated_locations)} locations")
            print(f"   📸 {len(self.generated_posts)} posts")
            print(f"   💫 ~{self.target_interactions} interactions")
            
        except Exception as e:
            print(f"❌ Fatal error during generation: {e}")
            raise
        finally:
            db.close()

# Main execution
async def main():
    """Main function to run synthetic data generation"""
    print("🚀 Instagram-like Social Media Platform - Synthetic Data Generator")
    print("=" * 70)
    
    # Configuration
    UNSPLASH_ACCESS_KEY = "3JKKttBpcVcb5mf54ukd7RZVX3Zs2KrFSMIQ3ozUkEM"  # Correct access key from dashboard
    
    # Initialize orchestrator
    orchestrator = SyntheticDataOrchestrator(
        unsplash_access_key=UNSPLASH_ACCESS_KEY
    )
    
    # Run complete generation
    await orchestrator.run_full_generation(
        clear_existing=True,
        use_unsplash=True
    )
    
    print("\n✅ All synthetic data generated successfully!")
    print("🔍 Run verification script to validate the data...")

if __name__ == "__main__":
    asyncio.run(main())