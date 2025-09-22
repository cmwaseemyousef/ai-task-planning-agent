"""
Improved location extraction using spaCy NER
"""

import os
import logging
from typing import List, Optional, Set
from functools import lru_cache

try:
    import spacy
    from spacy import displacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    spacy = None

logger = logging.getLogger(__name__)

class LocationExtractor:
    """
    Enhanced location extraction using NLP and predefined location lists
    """
    
    def __init__(self):
        """Initialize the location extractor"""
        self.nlp = None
        self.indian_cities = self._load_indian_cities()
        self.world_cities = self._load_world_cities()
        
        if SPACY_AVAILABLE:
            self._initialize_spacy()
        else:
            logger.warning("spaCy not available, using fallback location extraction")
    
    def _initialize_spacy(self):
        """Initialize spaCy model"""
        try:
            # Try to load English model
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy English model loaded successfully")
        except OSError:
            logger.warning("spaCy English model not found, downloading...")
            try:
                spacy.cli.download("en_core_web_sm")
                self.nlp = spacy.load("en_core_web_sm")
                logger.info("spaCy English model downloaded and loaded")
            except Exception as e:
                logger.error(f"Failed to download spaCy model: {e}")
                self.nlp = None
    
    def _load_indian_cities(self) -> Set[str]:
        """Load comprehensive list of Indian cities"""
        return {
            # Major cities
            "mumbai", "delhi", "bangalore", "bengaluru", "hyderabad", "ahmedabad",
            "chennai", "kolkata", "pune", "jaipur", "surat", "lucknow", "kanpur",
            "nagpur", "indore", "thane", "bhopal", "visakhapatnam", "vizag",
            "patna", "vadodara", "ghaziabad", "ludhiana", "agra", "nashik",
            "faridabad", "meerut", "rajkot", "varanasi", "srinagar", "aurangabad",
            "dhanbad", "amritsar", "navi mumbai", "allahabad", "prayagraj",
            "ranchi", "howrah", "coimbatore", "jabalpur", "gwalior", "vijayawada",
            "jodhpur", "madurai", "raipur", "kota", "guwahati", "chandigarh",
            "thiruvananthapuram", "solapur", "hubballi", "tiruchirappalli",
            "tiruppur", "moradabad", "mysuru", "mysore", "bareilly", "aligarh",
            "tirupati", "gurgaon", "gurugram", "salem", "mira-bhayandar",
            "warangal", "guntur", "bhiwandi", "saharanpur", "gorakhpur",
            "bikaner", "amravati", "noida", "jamshedpur", "bhilai", "cuttack",
            "firozabad", "kochi", "cochin", "nellore", "bhavnagar", "dehradun",
            "durgapur", "asansol", "rourkela", "nanded", "kolhapur", "ajmer",
            "akola", "gulbarga", "jamnagar", "ujjain", "loni", "siliguri",
            "jhansi", "ulhasnagar", "jammu", "sangli-miraj & kupwad", "mangalore",
            "erode", "belgaum", "ambattur", "tirunelveli", "malegaon", "gaya",
            "jalgaon", "udaipur", "maheshtala",
            
            # Tourist destinations
            "goa", "kerala", "rajasthan", "kashmir", "ladakh", "shimla", "manali",
            "darjeeling", "ooty", "munnar", "kodaikanal", "mount abu", "rishikesh",
            "haridwar", "vaishno devi", "amarnath", "kedarnath", "badrinath",
            "golden temple", "red fort", "taj mahal", "ajanta", "ellora",
            "hampi", "khajuraho", "konark", "mahabalipuram", "sanchi",
            "bodh gaya", "pushkar", "mount abu", "ranthambore", "jim corbett",
            "sundarbans", "backwaters", "andaman", "nicobar", "lakshadweep"
        }
    
    def _load_world_cities(self) -> Set[str]:
        """Load list of major world cities and countries"""
        return {
            # Major international cities
            "london", "paris", "new york", "tokyo", "singapore", "dubai",
            "hong kong", "sydney", "melbourne", "toronto", "vancouver",
            "los angeles", "san francisco", "chicago", "boston", "seattle",
            "amsterdam", "berlin", "rome", "madrid", "barcelona", "zurich",
            "geneva", "vienna", "prague", "budapest", "moscow", "istanbul",
            "cairo", "cape town", "johannesburg", "nairobi", "lagos",
            "beijing", "shanghai", "seoul", "bangkok", "kuala lumpur",
            "jakarta", "manila", "ho chi minh", "hanoi", "phnom penh",
            "yangon", "kathmandu", "dhaka", "colombo", "male", "thimphu",
            
            # Countries
            "india", "usa", "uk", "canada", "australia", "germany", "france",
            "italy", "spain", "netherlands", "switzerland", "austria",
            "japan", "china", "south korea", "thailand", "singapore",
            "malaysia", "indonesia", "philippines", "vietnam", "cambodia",
            "myanmar", "nepal", "bhutan", "sri lanka", "maldives", "bangladesh"
        }
    
    @lru_cache(maxsize=256)
    def extract_locations(self, text: str) -> List[str]:
        """
        Extract locations from text using multiple methods
        
        Args:
            text (str): Input text to extract locations from
            
        Returns:
            List[str]: List of extracted locations
        """
        if not text or not text.strip():
            return []
        
        text = text.lower().strip()
        locations = set()
        
        # Method 1: spaCy NER
        if self.nlp:
            spacy_locations = self._extract_with_spacy(text)
            locations.update(spacy_locations)
        
        # Method 2: Keyword matching
        keyword_locations = self._extract_with_keywords(text)
        locations.update(keyword_locations)
        
        # Method 3: Pattern matching
        pattern_locations = self._extract_with_patterns(text)
        locations.update(pattern_locations)
        
        # Filter and prioritize results
        return self._filter_and_prioritize(list(locations), text)
    
    def _extract_with_spacy(self, text: str) -> List[str]:
        """Extract locations using spaCy NER"""
        if not self.nlp:
            return []
        
        try:
            doc = self.nlp(text)
            locations = []
            
            for ent in doc.ents:
                if ent.label_ in ["GPE", "LOC", "FACILITY"]:
                    location = ent.text.lower().strip()
                    if len(location) > 2:  # Filter out very short matches
                        locations.append(location)
            
            return locations
        except Exception as e:
            logger.error(f"Error in spaCy extraction: {e}")
            return []
    
    def _extract_with_keywords(self, text: str) -> List[str]:
        """Extract locations using keyword matching"""
        locations = []
        
        # Check Indian cities first (higher priority)
        for city in self.indian_cities:
            if city in text:
                locations.append(city)
        
        # Check world cities
        for city in self.world_cities:
            if city in text and city not in locations:
                locations.append(city)
        
        return locations
    
    def _extract_with_patterns(self, text: str) -> List[str]:
        """Extract locations using pattern matching"""
        import re
        
        locations = []
        
        # Pattern for "in [location]" or "to [location]"
        patterns = [
            r'\b(?:in|to|at|from|near|around)\s+([A-Za-z\s]+?)\b',
            r'\b([A-Za-z\s]+?)\s+(?:city|state|country|province|region)\b',
            r'\bvisit\s+([A-Za-z\s]+?)\b',
            r'\btrip\s+to\s+([A-Za-z\s]+?)\b'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                location = match.strip().lower()
                if len(location) > 2 and location not in locations:
                    # Validate against known locations
                    if (location in self.indian_cities or 
                        location in self.world_cities or
                        any(city in location for city in self.indian_cities)):
                        locations.append(location)
        
        return locations
    
    def _filter_and_prioritize(self, locations: List[str], original_text: str) -> List[str]:
        """Filter and prioritize extracted locations"""
        if not locations:
            # Fallback to default Indian cities if no location found
            return self._get_default_locations(original_text)
        
        # Remove duplicates while preserving order
        seen = set()
        filtered = []
        
        for loc in locations:
            if loc not in seen:
                seen.add(loc)
                filtered.append(loc)
        
        # Prioritize Indian cities
        indian_locs = [loc for loc in filtered if loc in self.indian_cities]
        other_locs = [loc for loc in filtered if loc not in self.indian_cities]
        
        # Return prioritized list (Indian cities first)
        result = indian_locs + other_locs
        
        # Limit to top 3 locations
        return result[:3]
    
    def _get_default_locations(self, text: str) -> List[str]:
        """Get default location based on text analysis"""
        # Check for travel/tourism keywords to suggest default Indian destinations
        tourism_keywords = {
            'food': 'delhi',
            'vegetarian': 'chennai',
            'seafood': 'mumbai',
            'palace': 'jaipur',
            'fort': 'jaipur',
            'beach': 'goa',
            'hill': 'shimla',
            'mountain': 'manali',
            'temple': 'varanasi',
            'culture': 'delhi',
            'heritage': 'agra'
        }
        
        for keyword, default_city in tourism_keywords.items():
            if keyword in text.lower():
                return [default_city]
        
        # Ultimate fallback
        return ['delhi']
    
    def get_primary_location(self, text: str) -> Optional[str]:
        """
        Get the primary/most relevant location from text
        
        Args:
            text (str): Input text
            
        Returns:
            Optional[str]: Primary location or None
        """
        locations = self.extract_locations(text)
        return locations[0] if locations else None
    
    def is_location_in_india(self, location: str) -> bool:
        """
        Check if a location is in India
        
        Args:
            location (str): Location name
            
        Returns:
            bool: True if location is in India
        """
        return location.lower() in self.indian_cities

# Global instance
location_extractor = LocationExtractor()