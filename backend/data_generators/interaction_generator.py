import random
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import math

class SocialInteractionGenerator:
    def __init__(self):
        # Indian travel-related comments (English/Hindi mix)
        self.comment_templates = {
            "positive": [
                "Wow! Absolutely stunning! 😍",
                "This looks amazing! Adding to my bucket list ✈️",
                "बहुत खुबसूरत! Beautiful capture! 📸",
                "I've been here too! Such an incredible place! ❤️",
                "Goals! When are you planning your next trip? 🗺️",
                "The colors in this photo are incredible! 🌈",
                "This made my day! Thank you for sharing 🙏",
                "Wanderlust activated! Where should I go next? 🎒",
                "Living your best life! So jealous! 😊",
                "Perfect shot! What camera did you use? 📷"
            ],
            "engaging": [
                "How was the weather there? Planning to visit soon! ☀️",
                "Any food recommendations for this place? 🍽️",
                "Which month did you visit? Want to plan accordingly 📅",
                "How many days would you recommend for this place? 🤔",
                "Solo trip या group के साथ? Looks like so much fun! 👥",
                "Budget-friendly tips for this destination? 💰",
                "Best time to visit? And any hidden gems nearby? 💎",
                "Transportation advice? How did you reach there? 🚗",
                "Any must-visit places you'd recommend around here? 📍",
                "What was the highlight of your trip? ⭐"
            ],
            "emoji_heavy": [
                "🔥🔥🔥 This is fire! 🔥🔥🔥",
                "❤️❤️❤️ Love this so much! ❤️❤️❤️",
                "🌟✨ Magical vibes! ✨🌟",
                "🙌🙌 Incredible! 🙌🙌",
                "💯💯 Perfect! 💯💯",
                "😍🤩 Obsessed with this view! 🤩😍",
                "🌈🦋 So peaceful and beautiful! 🦋🌈",
                "🎉🎊 Amazing adventure! 🎊🎉",
                "🏔️⛰️ Mountain lover approved! ⛰️🏔️",
                "🏖️🌊 Beach vibes! 🌊🏖️"
            ],
            "travel_buddy": [
                "OMG we need to plan a trip together! 👯‍♀️",
                "Next trip partner? I'm in! ✋",
                "Let's recreate this shot when I visit! 📸",
                "Taking notes for our upcoming trip! 📝",
                "You're the best travel guide! Thanks for the tips! 🗺️",
                "Squad goals! Missing our travel days 👨‍👩‍👧‍👦",
                "This brings back memories of our last trip! 💭",
                "Planning committee meeting soon? 😄",
                "Your posts always inspire my next destination! ✈️",
                "Travel buddy application submitted! 📋"
            ],
            "local_knowledge": [
                "I'm from here! So happy to see people enjoying our culture! 🏠",
                "Local tip: Visit early morning for the best photos! 🌅",
                "Pro tip from a local: Try the food at the small stalls nearby! 🍜",
                "Born and raised here! This place holds special memories ❤️",
                "As a local, I recommend visiting during [season] for best experience! 🗓️",
                "Hidden gem nearby: [Location]! Must visit next time! 💎",
                "Local secret: Best sunset view is from the hilltop! 🌄",
                "Glad you enjoyed our city! Come back soon! 🤗",
                "Try the local transport for authentic experience! 🚌",
                "Local photographer here! You captured it perfectly! 📸"
            ]
        }
    
    def generate_interactions(self, users: List[Dict], posts: List[Dict], target_count: int = 15000) -> Dict[str, List[Dict]]:
        """Generate likes, comments, and shares with realistic patterns"""
        print(f"🔄 Generating {target_count} social interactions...")
        
        # Calculate distribution (realistic social media engagement)
        likes_count = int(target_count * 0.50)  # 50% likes
        comments_count = int(target_count * 0.40)  # 40% comments
        shares_count = target_count - likes_count - comments_count  # 10% shares
        
        # Create user and post lookups for faster access
        user_lookup = {user["id"]: user for user in users}
        
        # Sort posts by creation date (newer posts get more engagement)
        sorted_posts = sorted(posts, key=lambda x: x["created_at"], reverse=True)
        
        # Apply 80/20 rule: 20% of posts get 80% of engagement
        viral_posts = sorted_posts[:int(len(posts) * 0.2)]  # Top 20%
        regular_posts = sorted_posts[int(len(posts) * 0.2):]  # Bottom 80%
        
        print("📊 Generating engagement patterns...")
        
        # Generate likes
        likes = self._generate_likes(users, viral_posts, regular_posts, likes_count, user_lookup)
        
        # Generate comments
        comments = self._generate_comments(users, viral_posts, regular_posts, comments_count, user_lookup)
        
        # Generate shares
        shares = self._generate_shares(users, viral_posts, regular_posts, shares_count, user_lookup)
        
        print(f"✅ Generated {len(likes)} likes, {len(comments)} comments, {len(shares)} shares")
        
        return {
            "likes": likes,
            "comments": comments,
            "shares": shares
        }
    
    def _generate_likes(self, users: List[Dict], viral_posts: List[Dict], regular_posts: List[Dict], 
                       count: int, user_lookup: Dict) -> List[Dict]:
        """Generate like interactions"""
        likes = []
        viral_likes = int(count * 0.8)  # 80% of likes go to viral posts
        regular_likes = count - viral_likes
        
        # Generate likes for viral posts
        likes.extend(self._create_likes_for_posts(viral_posts, users, viral_likes, user_lookup, is_viral=True))
        
        # Generate likes for regular posts
        likes.extend(self._create_likes_for_posts(regular_posts, users, regular_likes, user_lookup, is_viral=False))
        
        return likes
    
    def _create_likes_for_posts(self, posts: List[Dict], users: List[Dict], count: int, 
                               user_lookup: Dict, is_viral: bool) -> List[Dict]:
        """Create like interactions for given posts"""
        likes = []
        
        for i in range(count):
            post = random.choice(posts)
            
            # Apply geographic and interest-based clustering
            potential_users = self._get_potential_interactors(post, users, user_lookup)
            user = random.choice(potential_users if potential_users else users)
            
            # Ensure user doesn't like their own post
            if user["id"] == post["user_id"]:
                continue
            
            # Create like timestamp (after post creation, before now)
            like_time = self._generate_interaction_time(post["created_at"])
            
            likes.append({
                "user_id": user["id"],
                "post_id": post["id"],
                "created_at": like_time
            })
        
        return likes
    
    def _generate_comments(self, users: List[Dict], viral_posts: List[Dict], regular_posts: List[Dict], 
                          count: int, user_lookup: Dict) -> List[Dict]:
        """Generate comment interactions"""
        comments = []
        viral_comments = int(count * 0.8)  # 80% of comments go to viral posts
        regular_comments = count - viral_comments
        
        # Generate comments for viral posts
        comments.extend(self._create_comments_for_posts(viral_posts, users, viral_comments, user_lookup, is_viral=True))
        
        # Generate comments for regular posts
        comments.extend(self._create_comments_for_posts(regular_posts, users, regular_comments, user_lookup, is_viral=False))
        
        return comments
    
    def _create_comments_for_posts(self, posts: List[Dict], users: List[Dict], count: int, 
                                  user_lookup: Dict, is_viral: bool) -> List[Dict]:
        """Create comment interactions for given posts"""
        comments = []
        
        for i in range(count):
            post = random.choice(posts)
            
            # Apply geographic and interest-based clustering
            potential_users = self._get_potential_interactors(post, users, user_lookup)
            user = random.choice(potential_users if potential_users else users)
            
            # Ensure user doesn't comment on their own post
            if user["id"] == post["user_id"]:
                continue
            
            # Generate comment text
            comment_text = self._generate_comment_text(post, user, user_lookup)
            
            # Create comment timestamp
            comment_time = self._generate_interaction_time(post["created_at"])
            
            comments.append({
                "user_id": user["id"],
                "post_id": post["id"],
                "comment_text": comment_text,
                "created_at": comment_time,
                "updated_at": comment_time
            })
        
        return comments
    
    def _generate_shares(self, users: List[Dict], viral_posts: List[Dict], regular_posts: List[Dict], 
                        count: int, user_lookup: Dict) -> List[Dict]:
        """Generate share interactions"""
        shares = []
        viral_shares = int(count * 0.9)  # 90% of shares go to viral posts
        regular_shares = count - viral_shares
        
        # Generate shares for viral posts
        shares.extend(self._create_shares_for_posts(viral_posts, users, viral_shares, user_lookup, is_viral=True))
        
        # Generate shares for regular posts
        shares.extend(self._create_shares_for_posts(regular_posts, users, regular_shares, user_lookup, is_viral=False))
        
        return shares
    
    def _create_shares_for_posts(self, posts: List[Dict], users: List[Dict], count: int, 
                                user_lookup: Dict, is_viral: bool) -> List[Dict]:
        """Create share interactions for given posts"""
        shares = []
        
        for i in range(count):
            post = random.choice(posts)
            
            # Apply geographic and interest-based clustering
            potential_users = self._get_potential_interactors(post, users, user_lookup)
            user = random.choice(potential_users if potential_users else users)
            
            # Ensure user doesn't share their own post
            if user["id"] == post["user_id"]:
                continue
            
            # Create share timestamp
            share_time = self._generate_interaction_time(post["created_at"])
            
            shares.append({
                "user_id": user["id"],
                "post_id": post["id"],
                "created_at": share_time
            })
        
        return shares
    
    def _get_potential_interactors(self, post: Dict, users: List[Dict], user_lookup: Dict) -> List[Dict]:
        """Get users who are more likely to interact based on geographic and interest clustering"""
        post_author = user_lookup.get(post["user_id"])
        if not post_author:
            return []
        
        potential_users = []
        author_location = post_author.get("location", "")
        author_interests = post_author.get("travel_interests", [])
        
        for user in users:
            if user["id"] == post["user_id"]:  # Skip post author
                continue
            
            score = 0
            
            # Geographic clustering (same city/state gets higher score)
            user_location = user.get("location", "")
            if author_location and user_location:
                if author_location.split(",")[0].strip() in user_location:  # Same city
                    score += 3
                elif author_location.split(",")[-1].strip() in user_location:  # Same state
                    score += 2
            
            # Interest-based clustering
            user_interests = user.get("travel_interests", [])
            common_interests = set(author_interests) & set(user_interests)
            score += len(common_interests)
            
            # Travel style similarity
            if user.get("travel_style") == post_author.get("travel_style"):
                score += 1
            
            # Add user multiple times based on score (higher score = more likely to interact)
            for _ in range(max(1, score)):
                potential_users.append(user)
        
        return potential_users
    
    def _generate_comment_text(self, post: Dict, user: Dict, user_lookup: Dict) -> str:
        """Generate realistic comment text based on post and user context"""
        post_author = user_lookup.get(post["user_id"])
        user_location = user.get("location", "")
        post_location = post.get("location", "")
        
        # Determine comment type based on relationship and context
        comment_type = "positive"  # Default
        
        # Local knowledge comments (if user is from the same location)
        if post_location and user_location:
            if post_location.split(",")[0].strip().lower() in user_location.lower():
                comment_type = "local_knowledge"
            elif random.random() < 0.3:  # 30% chance for engaging questions
                comment_type = "engaging"
            elif random.random() < 0.2:  # 20% chance for travel buddy comments
                comment_type = "travel_buddy"
            elif random.random() < 0.15:  # 15% chance for emoji-heavy comments
                comment_type = "emoji_heavy"
        
        # Select and return comment
        templates = self.comment_templates[comment_type]
        return random.choice(templates)
    
    def _generate_interaction_time(self, post_created_at: datetime) -> datetime:
        """Generate realistic interaction timestamp after post creation"""
        # Interactions happen between post creation and now
        now = datetime.utcnow()
        time_since_post = (now - post_created_at).total_seconds()
        
        # Most interactions happen within first few days
        if time_since_post < 86400:  # Less than 1 day
            # 60% of interactions happen within first day
            interaction_delay = random.uniform(0, time_since_post * 0.6)
        elif time_since_post < 604800:  # Less than 1 week
            # 30% happen in first week
            interaction_delay = random.uniform(0, time_since_post * 0.8)
        else:
            # 10% happen later
            interaction_delay = random.uniform(0, time_since_post)
        
        return post_created_at + timedelta(seconds=interaction_delay)
    
    def update_post_counts(self, posts: List[Dict], interactions: Dict[str, List[Dict]]) -> List[Dict]:
        """Update post interaction counts based on generated interactions"""
        print("🔄 Updating post interaction counts...")
        
        # Create counters
        likes_count = {}
        comments_count = {}
        shares_count = {}
        
        # Count likes
        for like in interactions["likes"]:
            post_id = like["post_id"]
            likes_count[post_id] = likes_count.get(post_id, 0) + 1
        
        # Count comments
        for comment in interactions["comments"]:
            post_id = comment["post_id"]
            comments_count[post_id] = comments_count.get(post_id, 0) + 1
        
        # Count shares
        for share in interactions["shares"]:
            post_id = share["post_id"]
            shares_count[post_id] = shares_count.get(post_id, 0) + 1
        
        # Update posts
        for post in posts:
            post_id = post["id"]
            post["likes_count"] = likes_count.get(post_id, 0)
            post["comments_count"] = comments_count.get(post_id, 0)
            post["shares_count"] = shares_count.get(post_id, 0)
        
        print("✅ Post interaction counts updated")
        return posts