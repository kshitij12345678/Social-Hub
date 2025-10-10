from typing import List, Dict

class IndianLocationGenerator:
    def __init__(self):
        self.indian_locations = [
            # Major Tourist Destinations
            {"name": "Taj Mahal", "city": "Agra", "state": "Uttar Pradesh", "country": "India", 
             "continent": "Asia", "latitude": 27.1751, "longitude": 78.0421, "category": "monument"},
            
            {"name": "Red Fort", "city": "Delhi", "state": "Delhi", "country": "India", 
             "continent": "Asia", "latitude": 28.6562, "longitude": 77.2410, "category": "historical"},
             
            {"name": "Hawa Mahal", "city": "Jaipur", "state": "Rajasthan", "country": "India", 
             "continent": "Asia", "latitude": 26.9239, "longitude": 75.8267, "category": "palace"},
             
            {"name": "City Palace", "city": "Udaipur", "state": "Rajasthan", "country": "India", 
             "continent": "Asia", "latitude": 24.5764, "longitude": 73.6833, "category": "palace"},
             
            {"name": "Amber Fort", "city": "Jaipur", "state": "Rajasthan", "country": "India", 
             "continent": "Asia", "latitude": 26.9855, "longitude": 75.8513, "category": "fort"},
             
            # Beaches
            {"name": "Baga Beach", "city": "Goa", "state": "Goa", "country": "India", 
             "continent": "Asia", "latitude": 15.5557, "longitude": 73.7517, "category": "beach"},
             
            {"name": "Calangute Beach", "city": "Goa", "state": "Goa", "country": "India", 
             "continent": "Asia", "latitude": 15.5435, "longitude": 73.7550, "category": "beach"},
             
            {"name": "Marina Beach", "city": "Chennai", "state": "Tamil Nadu", "country": "India", 
             "continent": "Asia", "latitude": 13.0500, "longitude": 80.2824, "category": "beach"},
             
            {"name": "Juhu Beach", "city": "Mumbai", "state": "Maharashtra", "country": "India", 
             "continent": "Asia", "latitude": 19.0990, "longitude": 72.8262, "category": "beach"},
             
            # Hill Stations
            {"name": "Mall Road", "city": "Shimla", "state": "Himachal Pradesh", "country": "India", 
             "continent": "Asia", "latitude": 31.1048, "longitude": 77.1734, "category": "hill_station"},
             
            {"name": "Rohtang Pass", "city": "Manali", "state": "Himachal Pradesh", "country": "India", 
             "continent": "Asia", "latitude": 32.2432, "longitude": 77.2487, "category": "mountain"},
             
            {"name": "Tiger Hill", "city": "Darjeeling", "state": "West Bengal", "country": "India", 
             "continent": "Asia", "latitude": 26.9954, "longitude": 88.2596, "category": "hill_station"},
             
            {"name": "Doddabetta Peak", "city": "Ooty", "state": "Tamil Nadu", "country": "India", 
             "continent": "Asia", "latitude": 11.4064, "longitude": 76.7337, "category": "hill_station"},
             
            # Backwaters & Nature
            {"name": "Alleppey Backwaters", "city": "Alleppey", "state": "Kerala", "country": "India", 
             "continent": "Asia", "latitude": 9.4981, "longitude": 76.3388, "category": "backwaters"},
             
            {"name": "Kumarakom", "city": "Kottayam", "state": "Kerala", "country": "India", 
             "continent": "Asia", "latitude": 9.6186, "longitude": 76.4301, "category": "backwaters"},
             
            {"name": "Munnar Tea Gardens", "city": "Munnar", "state": "Kerala", "country": "India", 
             "continent": "Asia", "latitude": 10.0889, "longitude": 77.0595, "category": "nature"},
             
            # Temples
            {"name": "Golden Temple", "city": "Amritsar", "state": "Punjab", "country": "India", 
             "continent": "Asia", "latitude": 31.6200, "longitude": 74.8765, "category": "temple"},
             
            {"name": "Meenakshi Temple", "city": "Madurai", "state": "Tamil Nadu", "country": "India", 
             "continent": "Asia", "latitude": 9.9195, "longitude": 78.1193, "category": "temple"},
             
            {"name": "Jagannath Temple", "city": "Puri", "state": "Odisha", "country": "India", 
             "continent": "Asia", "latitude": 19.8135, "longitude": 85.8312, "category": "temple"},
             
            {"name": "Kashi Vishwanath", "city": "Varanasi", "state": "Uttar Pradesh", "country": "India", 
             "continent": "Asia", "latitude": 25.3109, "longitude": 83.0090, "category": "temple"},
             
            # Cities & Urban Areas
            {"name": "Gateway of India", "city": "Mumbai", "state": "Maharashtra", "country": "India", 
             "continent": "Asia", "latitude": 18.9220, "longitude": 72.8347, "category": "monument"},
             
            {"name": "India Gate", "city": "Delhi", "state": "Delhi", "country": "India", 
             "continent": "Asia", "latitude": 28.6129, "longitude": 77.2295, "category": "monument"},
             
            {"name": "Charminar", "city": "Hyderabad", "state": "Telangana", "country": "India", 
             "continent": "Asia", "latitude": 17.3616, "longitude": 78.4747, "category": "monument"},
             
            {"name": "Victoria Memorial", "city": "Kolkata", "state": "West Bengal", "country": "India", 
             "continent": "Asia", "latitude": 22.5448, "longitude": 88.3426, "category": "monument"},
             
            # National Parks & Wildlife
            {"name": "Jim Corbett National Park", "city": "Nainital", "state": "Uttarakhand", "country": "India", 
             "continent": "Asia", "latitude": 29.5319, "longitude": 78.7460, "category": "national_park"},
             
            {"name": "Ranthambore National Park", "city": "Sawai Madhopur", "state": "Rajasthan", "country": "India", 
             "continent": "Asia", "latitude": 26.0173, "longitude": 76.5026, "category": "national_park"},
             
            {"name": "Kaziranga National Park", "city": "Jorhat", "state": "Assam", "country": "India", 
             "continent": "Asia", "latitude": 26.5775, "longitude": 93.1633, "category": "national_park"},
             
            # Desert
            {"name": "Thar Desert", "city": "Jaisalmer", "state": "Rajasthan", "country": "India", 
             "continent": "Asia", "latitude": 26.9157, "longitude": 70.9083, "category": "desert"},
             
            {"name": "Sam Sand Dunes", "city": "Jaisalmer", "state": "Rajasthan", "country": "India", 
             "continent": "Asia", "latitude": 26.8945, "longitude": 70.6075, "category": "desert"},
             
            # Religious & Spiritual
            {"name": "Rishikesh", "city": "Rishikesh", "state": "Uttarakhand", "country": "India", 
             "continent": "Asia", "latitude": 30.0869, "longitude": 78.2676, "category": "spiritual"},
             
            {"name": "Haridwar", "city": "Haridwar", "state": "Uttarakhand", "country": "India", 
             "continent": "Asia", "latitude": 29.9457, "longitude": 78.1642, "category": "spiritual"},
             
            {"name": "Bodh Gaya", "city": "Gaya", "state": "Bihar", "country": "India", 
             "continent": "Asia", "latitude": 24.6958, "longitude": 84.9917, "category": "spiritual"},
             
            # Modern Cities
            {"name": "Cyber City", "city": "Gurgaon", "state": "Haryana", "country": "India", 
             "continent": "Asia", "latitude": 28.4595, "longitude": 77.0266, "category": "city"},
             
            {"name": "Electronic City", "city": "Bangalore", "state": "Karnataka", "country": "India", 
             "continent": "Asia", "latitude": 12.8456, "longitude": 77.6603, "category": "city"},
             
            {"name": "Banjara Hills", "city": "Hyderabad", "state": "Telangana", "country": "India", 
             "continent": "Asia", "latitude": 17.4126, "longitude": 78.4482, "category": "city"},
             
            # Waterfalls
            {"name": "Jog Falls", "city": "Shimoga", "state": "Karnataka", "country": "India", 
             "continent": "Asia", "latitude": 14.2291, "longitude": 74.8104, "category": "waterfall"},
             
            {"name": "Athirappilly Falls", "city": "Thrissur", "state": "Kerala", "country": "India", 
             "continent": "Asia", "latitude": 10.2851, "longitude": 76.5664, "category": "waterfall"},
             
            {"name": "Dudhsagar Falls", "city": "Goa", "state": "Goa", "country": "India", 
             "continent": "Asia", "latitude": 15.3144, "longitude": 74.3144, "category": "waterfall"},
             
            # Islands
            {"name": "Havelock Island", "city": "Port Blair", "state": "Andaman and Nicobar Islands", "country": "India", 
             "continent": "Asia", "latitude": 12.0067, "longitude": 93.0019, "category": "island"},
             
            {"name": "Neil Island", "city": "Port Blair", "state": "Andaman and Nicobar Islands", "country": "India", 
             "continent": "Asia", "latitude": 11.8369, "longitude": 93.0248, "category": "island"},
             
            # Food & Cultural Hubs
            {"name": "Chandni Chowk", "city": "Delhi", "state": "Delhi", "country": "India", 
             "continent": "Asia", "latitude": 28.6506, "longitude": 77.2334, "category": "market"},
             
            {"name": "Colaba Causeway", "city": "Mumbai", "state": "Maharashtra", "country": "India", 
             "continent": "Asia", "latitude": 18.9067, "longitude": 72.8147, "category": "market"},
             
            {"name": "Brigade Road", "city": "Bangalore", "state": "Karnataka", "country": "India", 
             "continent": "Asia", "latitude": 12.9716, "longitude": 77.5946, "category": "market"},
             
            # Lakes
            {"name": "Dal Lake", "city": "Srinagar", "state": "Jammu and Kashmir", "country": "India", 
             "continent": "Asia", "latitude": 34.1218, "longitude": 74.8092, "category": "lake"},
             
            {"name": "Vembanad Lake", "city": "Kochi", "state": "Kerala", "country": "India", 
             "continent": "Asia", "latitude": 9.5975, "longitude": 76.3967, "category": "lake"},
             
            {"name": "Chilika Lake", "city": "Puri", "state": "Odisha", "country": "India", 
             "continent": "Asia", "latitude": 19.7179, "longitude": 85.3184, "category": "lake"}
        ]
    
    def generate_locations(self) -> List[Dict]:
        """Generate comprehensive list of Indian travel locations"""
        print(f"🔄 Generating {len(self.indian_locations)} Indian travel locations...")
        
        locations = []
        
        for i, location_data in enumerate(self.indian_locations):
            location = {
                "id": i + 1,
                "name": location_data["name"],
                "city": location_data["city"],
                "state": location_data["state"], 
                "country": location_data["country"],
                "continent": location_data["continent"],
                "latitude": location_data["latitude"],
                "longitude": location_data["longitude"],
                "category": location_data["category"],
                "full_location": f"{location_data['name']}, {location_data['city']}, {location_data['state']}"
            }
            locations.append(location)
        
        print(f"✅ Generated {len(locations)} locations across {len(set(loc['category'] for loc in locations))} categories")
        return locations
    
    def get_location_by_name(self, location_name: str) -> Dict:
        """Find location by name (partial match)"""
        location_name_lower = location_name.lower()
        
        for location_data in self.indian_locations:
            if (location_name_lower in location_data["name"].lower() or 
                location_name_lower in location_data["city"].lower()):
                return location_data
        
        return None
    
    def get_locations_by_category(self, category: str) -> List[Dict]:
        """Get all locations of a specific category"""
        return [loc for loc in self.indian_locations if loc["category"] == category]
    
    def get_locations_by_state(self, state: str) -> List[Dict]:
        """Get all locations in a specific state"""
        return [loc for loc in self.indian_locations if loc["state"].lower() == state.lower()]