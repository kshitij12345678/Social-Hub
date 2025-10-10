import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple
import re

class ContentBasedRecommender:
    def __init__(self, db_manager):
        self.db = db_manager
        self.tfidf_vectorizer = None
        self.content_features_matrix = None
        self.posts_df = None
        self.location_similarity_matrix = None
        self.content_similarity_matrix = None
        
    def preprocess_text(self, text):
        """Clean and preprocess text for TF-IDF"""
        if not text:
            return ""
        
        # Remove emojis and special characters, keep Hindi words
        text = re.sub(r'[^\w\s]', ' ', text)
        # Convert to lowercase
        text = text.lower()
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def build_content_features(self):
        """Build content feature matrix using post captions, locations, and tags"""
        print("🔄 Building content feature matrix...")
        
        # Get all posts with their metadata
        posts_query = """
        SELECT 
            p.post_id,
            p.caption,
            p.user_id,
            p.post_type,
            p.travel_date,
            l.name as location_name,
            l.country,
            l.continent,
            l.category as location_category,
            GROUP_CONCAT(pt.tag_name, ' ') as tags,
            u.travel_style,
            u.location as user_location
        FROM posts p
        LEFT JOIN locations l ON p.location_id = l.location_id
        LEFT JOIN post_tags pt ON p.post_id = pt.post_id
        LEFT JOIN users u ON p.user_id = u.user_id
        GROUP BY p.post_id, p.caption, p.user_id, p.post_type, p.travel_date, 
                 l.name, l.country, l.continent, l.category, u.travel_style, u.location
        """
        
        posts_data = self.db.execute_query(posts_query)
        
        if not posts_data:
            print("❌ No posts found!")
            return None
        
        # Convert to DataFrame
        columns = ['post_id', 'caption', 'user_id', 'post_type', 'travel_date', 
                  'location_name', 'country', 'continent', 'location_category', 
                  'tags', 'travel_style', 'user_location']
        
        self.posts_df = pd.DataFrame(posts_data, columns=columns)
        
        # Create combined text features for each post
        content_features = []
        
        for _, post in self.posts_df.iterrows():
            # Combine different text features
            feature_text = []
            
            # Add caption (main content)
            if post['caption']:
                feature_text.append(self.preprocess_text(post['caption']))
            
            # Add location information (heavily weighted for better location matching)
            if post['location_name']:
                location_text = post['location_name'].lower()
                feature_text.extend([location_text] * 5)  # Increased weight for location
            
            if post['country']:
                country_text = post['country'].lower()
                feature_text.extend([country_text] * 3)  # Increased weight for country
            
            if post['continent']:
                continent_text = post['continent'].lower()
                feature_text.extend([continent_text] * 2)  # Weight continent
            
            if post['location_category']:
                category_text = post['location_category'].lower()
                feature_text.extend([category_text] * 4)  # Increased weight for category
            
            # Add tags (important for content similarity)
            if post['tags']:
                tags = post['tags'].lower().split()
                feature_text.extend(tags * 2)  # Weight tags 2x
            
            # Add travel style
            if post['travel_style']:
                feature_text.append(post['travel_style'].lower())
            
            # Add post type
            if post['post_type']:
                feature_text.append(post['post_type'].lower())
            
            # Join all features
            combined_text = ' '.join(feature_text)
            content_features.append(combined_text)
        
        # Create TF-IDF matrix
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),  # Include both unigrams and bigrams
            min_df=2,  # Ignore terms that appear in less than 2 documents
            max_df=0.8  # Ignore terms that appear in more than 80% of documents
        )
        
        self.content_features_matrix = self.tfidf_vectorizer.fit_transform(content_features)
        
        print(f"✅ Content features matrix created: {self.content_features_matrix.shape}")
        print(f"✅ TF-IDF vocabulary size: {len(self.tfidf_vectorizer.vocabulary_)}")
        
        return self.content_features_matrix
    
    def calculate_content_similarity(self):
        """Calculate cosine similarity between posts based on content"""
        if self.content_features_matrix is None:
            self.build_content_features()
            
        if self.content_features_matrix is None:
            return None
        
        print("🔄 Calculating content similarity matrix...")
        
        # Calculate cosine similarity
        self.content_similarity_matrix = cosine_similarity(self.content_features_matrix)
        
        print("✅ Content similarity matrix calculated")
        return self.content_similarity_matrix
    
    def find_similar_posts(self, post_id: int, n_similar: int = 10) -> List[Tuple[int, float]]:
        """Find most similar posts to the given post"""
        if self.content_similarity_matrix is None:
            self.calculate_content_similarity()
        
        # Find the index of the post in our DataFrame
        post_indices = self.posts_df[self.posts_df['post_id'] == post_id].index
        
        if len(post_indices) == 0:
            print(f"❌ Post {post_id} not found")
            return []
        
        post_idx = post_indices[0]
        
        # Get similarity scores for this post
        similarity_scores = self.content_similarity_matrix[post_idx]
        
        # Get indices of most similar posts (excluding the post itself)
        similar_indices = np.argsort(similarity_scores)[::-1][1:n_similar+1]
        
        # Return post IDs and similarity scores
        similar_posts = []
        for idx in similar_indices:
            similar_post_id = self.posts_df.iloc[idx]['post_id']
            similarity_score = similarity_scores[idx]
            similar_posts.append((int(similar_post_id), float(similarity_score)))
        
        return similar_posts
    
    def recommend_posts_content_based(self, user_id: int, n_recommendations: int = 10) -> List[Dict]:
        """Recommend posts based on content similarity to user's interaction history"""
        print(f"🔍 Finding content-based recommendations for user {user_id}...")
        
        if self.posts_df is None:
            self.build_content_features()
        
        # First validate user exists
        user_exists = self.db.execute_query(
            "SELECT COUNT(*) FROM users WHERE user_id = ?", 
            (user_id,)
        )[0][0]
        
        if user_exists == 0:
            print(f"❌ User {user_id} does not exist")
            return []
        
        # Get posts the user has interacted with (liked, commented, etc.)
        user_interactions_query = """
        SELECT DISTINCT i.post_id, i.interaction_type,
               p.caption, l.name as location_name, pt.tag_name
        FROM interactions i
        JOIN posts p ON i.post_id = p.post_id
        LEFT JOIN locations l ON p.location_id = l.location_id
        LEFT JOIN post_tags pt ON p.post_id = pt.post_id
        WHERE i.user_id = ?
        ORDER BY i.timestamp DESC
        """
        
        user_interactions = self.db.execute_query(user_interactions_query, (user_id,))
        
        if not user_interactions:
            print(f"❌ No interactions found for user {user_id}")
            return []  # Return empty list instead of popular posts
        
        # Get posts user has already seen
        seen_posts = set([interaction[0] for interaction in user_interactions])
        
        # Analyze user's location and category preferences
        user_location_preferences = {}
        user_category_preferences = {}
        user_country_preferences = {}
        
        for post_id, interaction_type, caption, location, tag in user_interactions:
            # Get post details for location analysis
            post_details = self.db.execute_query("""
                SELECT l.name, l.country, l.category 
                FROM posts p 
                JOIN locations l ON p.location_id = l.location_id 
                WHERE p.post_id = ?
            """, (post_id,))
            
            if post_details:
                loc_name, country, category = post_details[0]
                
                # Weight different interaction types
                interaction_weights = {
                    'like': 1.0,
                    'comment': 2.0,
                    'share': 3.0,
                    'save': 2.5
                }
                weight = interaction_weights.get(interaction_type, 1.0)
                
                # Build preference profiles
                if loc_name:
                    user_location_preferences[loc_name] = user_location_preferences.get(loc_name, 0) + weight
                if country:
                    user_country_preferences[country] = user_country_preferences.get(country, 0) + weight
                if category:
                    user_category_preferences[category] = user_category_preferences.get(category, 0) + weight
        
        # Find similar posts to user's interaction history
        similar_posts_scores = {}
        
        for post_id, interaction_type, caption, location, tag in user_interactions:
            interaction_weights = {
                'like': 1.0,
                'comment': 2.0,
                'share': 3.0,
                'save': 2.5
            }
            
            weight = interaction_weights.get(interaction_type, 1.0)
            similar_posts = self.find_similar_posts(post_id, n_similar=20)
            
            for similar_post_id, similarity_score in similar_posts:
                if similar_post_id not in seen_posts:
                    if similar_post_id not in similar_posts_scores:
                        similar_posts_scores[similar_post_id] = 0
                    
                    # Get location details for the recommended post
                    rec_post_details = self.db.execute_query("""
                        SELECT l.name, l.country, l.category 
                        FROM posts p 
                        JOIN locations l ON p.location_id = l.location_id 
                        WHERE p.post_id = ?
                    """, (similar_post_id,))
                    
                    location_bonus = 0
                    if rec_post_details:
                        rec_location, rec_country, rec_category = rec_post_details[0]
                        
                        # Boost score for preferred locations
                        if rec_location in user_location_preferences:
                            location_bonus += user_location_preferences[rec_location] * 0.3
                        
                        # Boost score for preferred countries
                        if rec_country in user_country_preferences:
                            location_bonus += user_country_preferences[rec_country] * 0.2
                        
                        # Boost score for preferred categories
                        if rec_category in user_category_preferences:
                            location_bonus += user_category_preferences[rec_category] * 0.4
                    
                    final_score = (similarity_score * weight) + location_bonus
                    similar_posts_scores[similar_post_id] += final_score
        
        # Sort by combined similarity score
        recommended_post_ids = sorted(
            similar_posts_scores.keys(),
            key=lambda x: similar_posts_scores[x],
            reverse=True
        )[:n_recommendations]
        
        # Get detailed information for recommended posts
        recommendations = []
        for post_id in recommended_post_ids:
            post_info = self._get_post_details(post_id)
            if post_info:
                post_info['similarity_score'] = similar_posts_scores[post_id]
                post_info['recommendation_reason'] = 'Similar to your interests'
                post_info['algorithm'] = 'content_based_filtering'
                recommendations.append(post_info)
        
        print(f"✅ Found {len(recommendations)} content-based recommendations")
        return recommendations
    
    def recommend_destinations_content_based(self, user_id: int, n_recommendations: int = 10) -> List[Dict]:
        """Recommend travel destinations based on user's content preferences"""
        print(f"🔍 Finding destination recommendations for user {user_id}...")
        
        # Validate user exists
        user_exists = self.db.execute_query(
            "SELECT COUNT(*) FROM users WHERE user_id = ?", 
            (user_id,)
        )[0][0]
        
        if user_exists == 0:
            print(f"❌ User {user_id} does not exist")
            return []
        
        # Get user's interaction history with location preferences
        user_location_query = """
        SELECT l.name, l.country, l.continent, l.category,
               COUNT(i.interaction_id) as interaction_count,
               AVG(CASE 
                   WHEN i.interaction_type = 'like' THEN 1.0
                   WHEN i.interaction_type = 'comment' THEN 2.0  
                   WHEN i.interaction_type = 'share' THEN 3.0
                   WHEN i.interaction_type = 'save' THEN 2.5
               END) as avg_engagement
        FROM interactions i
        JOIN posts p ON i.post_id = p.post_id
        JOIN locations l ON p.location_id = l.location_id
        WHERE i.user_id = ?
        GROUP BY l.name, l.country, l.continent, l.category
        ORDER BY interaction_count DESC, avg_engagement DESC
        """
        
        user_locations = self.db.execute_query(user_location_query, (user_id,))
        
        if not user_locations:
            return self._get_popular_destinations(n_recommendations)
        
        # Analyze user's location preferences with better weighting
        visited_locations = set([loc[0] for loc in user_locations])
        preferred_categories = {}
        preferred_continents = {}
        preferred_countries = {}
        
        # Calculate total engagement for normalization
        total_engagement = sum([count * engagement for _, _, _, _, count, engagement in user_locations if engagement])
        
        for location, country, continent, category, count, engagement in user_locations:
            engagement_weight = (count * engagement) / total_engagement if total_engagement > 0 else 1
            
            if category:
                preferred_categories[category] = preferred_categories.get(category, 0) + engagement_weight
            if continent:
                preferred_continents[continent] = preferred_continents.get(continent, 0) + engagement_weight
            if country:
                preferred_countries[country] = preferred_countries.get(country, 0) + engagement_weight
        
        # Get all locations not yet visited
        all_locations_query = """
        SELECT l.location_id, l.name, l.country, l.continent, l.category,
               l.latitude, l.longitude,
               COUNT(p.post_id) as post_count,
               AVG(subq.interaction_count) as avg_popularity
        FROM locations l
        LEFT JOIN posts p ON l.location_id = p.location_id
        LEFT JOIN (
            SELECT post_id, COUNT(interaction_id) as interaction_count
            FROM interactions
            GROUP BY post_id
        ) subq ON p.post_id = subq.post_id
        WHERE l.name NOT IN ({})
        GROUP BY l.location_id, l.name, l.country, l.continent, l.category, l.latitude, l.longitude
        HAVING post_count > 0
        ORDER BY avg_popularity DESC
        """.format(','.join(['?'] * len(visited_locations)))
        
        unvisited_locations = self.db.execute_query(all_locations_query, tuple(visited_locations))
        
        # Score locations based on user preferences
        destination_scores = []
        
        for loc_data in unvisited_locations:
            loc_id, name, country, continent, category, lat, lng, post_count, popularity = loc_data
            
            score = 0
            reasons = []
            
            # Score based on preferred categories (highest weight)
            if category and category in preferred_categories:
                category_score = preferred_categories[category]
                score += category_score * 4  # Increased weight for category matching
                reasons.append(f"You love {category.lower()} destinations")
            
            # Score based on preferred countries (medium-high weight)
            if country and country in preferred_countries:
                country_score = preferred_countries[country]
                score += country_score * 3
                reasons.append(f"You frequently visit {country}")
            
            # Score based on preferred continents (medium weight)
            if continent and continent in preferred_continents:
                continent_score = preferred_continents[continent]
                score += continent_score * 2
                reasons.append(f"You enjoy {continent} travel")
            
            # Bonus for nearby/similar regions to user's preferences
            if country == 'India' and 'India' in preferred_countries:
                score += preferred_countries['India'] * 1.5  # Boost Indian destinations for India lovers
                reasons.append("Perfect for Indian travel enthusiasts")
            
            # Add popularity bonus
            if popularity:
                score += min(popularity / 10, 1.0)  # Normalize popularity
            
            if score > 0:
                destination_scores.append({
                    'location_id': loc_id,
                    'name': name,
                    'country': country,
                    'continent': continent,
                    'category': category,
                    'latitude': lat,
                    'longitude': lng,
                    'post_count': post_count,
                    'popularity_score': popularity or 0,
                    'recommendation_score': score,
                    'reasons': reasons,
                    'algorithm': 'content_based_filtering'
                })
        
        # Sort by recommendation score and return top N
        destination_scores.sort(key=lambda x: x['recommendation_score'], reverse=True)
        
        print(f"✅ Found {len(destination_scores[:n_recommendations])} destination recommendations")
        return destination_scores[:n_recommendations]
    
    def _get_post_details(self, post_id: int) -> Dict:
        """Get detailed information for a post"""
        post_query = """
        SELECT p.post_id, p.caption, p.user_id, p.post_type,
               u.username, u.full_name,
               l.name as location_name, l.country,
               GROUP_CONCAT(pt.tag_name, ', ') as tags
        FROM posts p
        JOIN users u ON p.user_id = u.user_id
        LEFT JOIN locations l ON p.location_id = l.location_id
        LEFT JOIN post_tags pt ON p.post_id = pt.post_id
        WHERE p.post_id = ?
        GROUP BY p.post_id, p.caption, p.user_id, p.post_type, u.username, u.full_name, l.name, l.country
        """
        
        result = self.db.execute_query(post_query, (post_id,))
        
        if result:
            post_data = result[0]
            return {
                'post_id': post_data[0],
                'caption': post_data[1][:100] + "..." if post_data[1] and len(post_data[1]) > 100 else post_data[1],
                'author_id': post_data[2],
                'post_type': post_data[3],
                'author_username': post_data[4],
                'author_name': post_data[5],
                'location': post_data[6],
                'country': post_data[7],
                'tags': post_data[8]
            }
        
        return None
    
    def _get_popular_posts(self, n_posts: int) -> List[Dict]:
        """Get popular posts as fallback recommendations"""
        popular_posts_query = """
        SELECT p.post_id, COUNT(i.interaction_id) as interaction_count
        FROM posts p
        LEFT JOIN interactions i ON p.post_id = i.post_id
        GROUP BY p.post_id
        ORDER BY interaction_count DESC
        LIMIT ?
        """
        
        popular_posts = self.db.execute_query(popular_posts_query, (n_posts,))
        
        recommendations = []
        for post_id, count in popular_posts:
            post_info = self._get_post_details(post_id)
            if post_info:
                post_info['popularity_score'] = count
                post_info['recommendation_reason'] = 'Popular content'
                post_info['algorithm'] = 'popularity_based'
                recommendations.append(post_info)
        
        return recommendations
    
    def _get_popular_destinations(self, n_destinations: int) -> List[Dict]:
        """Get popular destinations as fallback recommendations"""
        popular_destinations_query = """
        SELECT l.location_id, l.name, l.country, l.continent, l.category,
               COUNT(p.post_id) as post_count,
               COUNT(i.interaction_id) as total_interactions
        FROM locations l
        LEFT JOIN posts p ON l.location_id = p.location_id
        LEFT JOIN interactions i ON p.post_id = i.post_id
        GROUP BY l.location_id, l.name, l.country, l.continent, l.category
        ORDER BY total_interactions DESC, post_count DESC
        LIMIT ?
        """
        
        popular_destinations = self.db.execute_query(popular_destinations_query, (n_destinations,))
        
        recommendations = []
        for dest_data in popular_destinations:
            loc_id, name, country, continent, category, post_count, interactions = dest_data
            recommendations.append({
                'location_id': loc_id,
                'name': name,
                'country': country,
                'continent': continent,
                'category': category,
                'post_count': post_count,
                'interaction_count': interactions,
                'recommendation_reason': 'Popular destination',
                'algorithm': 'popularity_based'
            })
        
        return recommendations

if __name__ == "__main__":
    # Test the content-based recommender
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
    
    from src.database.models import DatabaseManager
    
    db = DatabaseManager()
    recommender = ContentBasedRecommender(db)
    
    # Test with user ID 1
    print("🧪 Testing Content-Based Recommender...")
    
    # Build content features
    recommender.build_content_features()
    
    # Test recommendations
    post_recs = recommender.recommend_posts_content_based(1, 5)
    dest_recs = recommender.recommend_destinations_content_based(1, 5)
    
    print(f"\n📊 Content-Based Post Recommendations for User 1:")
    for i, rec in enumerate(post_recs, 1):
        print(f"{i}. {rec['caption']} (Location: {rec['location']}) - Score: {rec.get('similarity_score', 0):.3f}")
    
    print(f"\n🏞️ Content-Based Destination Recommendations for User 1:")
    for i, rec in enumerate(dest_recs, 1):
        print(f"{i}. {rec['name']}, {rec['country']} ({rec['category']}) - Score: {rec.get('recommendation_score', 0):.3f}")
        if rec.get('reasons'):
            print(f"   Reason: {', '.join(rec['reasons'])}")
    
    print("\n✅ Content-based filtering test complete!")