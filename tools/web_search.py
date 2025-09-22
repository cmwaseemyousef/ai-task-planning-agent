"""
Web Search Tool for gathering external information
Uses Google Custom Search API
"""

import requests
import os
import logging
from typing import List, Dict, Optional
from dotenv import load_dotenv
from .cache import cached

load_dotenv()

class WebSearchTool:
    def __init__(self):
        """Initialize web search tool with API credentials"""
        self.api_key = os.getenv("SEARCH_API_KEY")
        self.search_engine_id = os.getenv("SEARCH_ENGINE_ID")
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.logger = logging.getLogger(__name__)
    
    @cached(ttl=3600, key_prefix="web_search_")
    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        Search the web for information related to the query
        
        Args:
            query (str): Search query
            num_results (int): Number of results to return
            
        Returns:
            List[Dict]: Search results with title, snippet, and URL
        """
        if not self.api_key or not self.search_engine_id:
            self.logger.warning("Search API credentials not configured. Using mock data.")
            return self._get_mock_results(query)
        
        try:
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': min(num_results, 10)  # API limit is 10
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get('items', []):
                results.append({
                    'title': item.get('title', ''),
                    'snippet': item.get('snippet', ''),
                    'url': item.get('link', ''),
                    'source': 'google_search'
                })
            
            return results
            
        except requests.RequestException as e:
            self.logger.error(f"Search API error: {e}")
            return self._get_mock_results(query)
        except Exception as e:
            self.logger.error(f"Unexpected search error: {e}")
            return self._get_mock_results(query)
    
    def _get_mock_results(self, query: str) -> List[Dict]:
        """
        Return mock search results when API is not available
        This helps with development and testing
        """
        query_lower = query.lower()
        
        if "jaipur" in query_lower:
            return [
                {
                    'title': 'Jaipur Tourism - Top Attractions',
                    'snippet': 'Discover the Pink City of India with its magnificent palaces, forts, and vibrant culture. Visit Amber Fort, City Palace, and Hawa Mahal.',
                    'url': 'https://example.com/jaipur-tourism',
                    'source': 'mock_data'
                },
                {
                    'title': 'Best Food in Jaipur - Traditional Rajasthani Cuisine',
                    'snippet': 'Experience authentic Rajasthani flavors with dal bati churma, laal maas, and ghewar. Top restaurants and street food spots.',
                    'url': 'https://example.com/jaipur-food',
                    'source': 'mock_data'
                },
                {
                    'title': 'Jaipur Travel Guide - 3 Day Itinerary',
                    'snippet': 'Complete 3-day travel guide covering all major attractions, local markets, and cultural experiences in Jaipur.',
                    'url': 'https://example.com/jaipur-guide',
                    'source': 'mock_data'
                }
            ]
        
        elif "hyderabad" in query_lower and "vegetarian" in query_lower:
            return [
                {
                    'title': 'Best Vegetarian Restaurants in Hyderabad',
                    'snippet': 'Top vegetarian dining spots in Hyderabad including traditional South Indian, North Indian, and fusion cuisine.',
                    'url': 'https://example.com/hyderabad-veg',
                    'source': 'mock_data'
                },
                {
                    'title': 'Hyderabad Vegetarian Food Tour',
                    'snippet': 'Explore the diverse vegetarian food scene including famous Hyderabadi biryani variants, dosas, and sweets.',
                    'url': 'https://example.com/hyderabad-veg-tour',
                    'source': 'mock_data'
                }
            ]
        
        elif "vizag" in query_lower or "visakhapatnam" in query_lower:
            return [
                {
                    'title': 'Vizag Weekend Guide - Beaches and Hills',
                    'snippet': 'Perfect weekend getaway with beautiful beaches, Araku Valley hills, and fresh seafood experiences.',
                    'url': 'https://example.com/vizag-weekend',
                    'source': 'mock_data'
                },
                {
                    'title': 'Best Seafood Restaurants in Visakhapatnam',
                    'snippet': 'Top seafood dining spots along the coast with fresh catches and traditional Andhra preparations.',
                    'url': 'https://example.com/vizag-seafood',
                    'source': 'mock_data'
                }
            ]
        
        elif "python" in query_lower and "study" in query_lower:
            return [
                {
                    'title': 'Python Learning Roadmap for Beginners',
                    'snippet': 'Complete guide to learning Python programming from basics to advanced concepts with practical projects.',
                    'url': 'https://example.com/python-roadmap',
                    'source': 'mock_data'
                },
                {
                    'title': 'Daily Python Study Routine - Best Practices',
                    'snippet': 'Effective daily study techniques for mastering Python including coding practice, projects, and resources.',
                    'url': 'https://example.com/python-study',
                    'source': 'mock_data'
                }
            ]
        
        else:
            return [
                {
                    'title': f'Search Results for: {query}',
                    'snippet': f'General information and resources related to {query}. This is mock data for development purposes.',
                    'url': 'https://example.com/search',
                    'source': 'mock_data'
                }
            ]
    
    @cached(ttl=1800, key_prefix="web_search_specific_")
    def search_specific_info(self, topic: str, info_type: str) -> List[Dict]:
        """
        Search for specific type of information about a topic
        
        Args:
            topic (str): The main topic
            info_type (str): Type of info (restaurants, attractions, tips, etc.)
            
        Returns:
            List[Dict]: Focused search results
        """
        query = f"{topic} {info_type}"
        return self.search(query, num_results=3)