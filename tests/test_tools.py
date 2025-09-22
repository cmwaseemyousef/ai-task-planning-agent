"""
Test cases for tools and utilities
"""

import pytest
from unittest.mock import patch, MagicMock
import requests

from tools.web_search import WebSearchTool
from tools.weather import WeatherTool
from tools.location_extractor import LocationExtractor, location_extractor
from tools.cache import SimpleCache, cached


class TestWebSearchTool:
    """Test cases for WebSearchTool"""
    
    @pytest.fixture
    def search_tool(self):
        """Create WebSearchTool instance"""
        return WebSearchTool()
    
    def test_search_with_mock_data(self, search_tool):
        """Test search with mock data (no API keys)"""
        with patch.object(search_tool, 'api_key', None):
            results = search_tool.search("Jaipur tourism")
            
            assert isinstance(results, list)
            assert len(results) > 0
            assert all('title' in result for result in results)
            assert all('snippet' in result for result in results)
            assert all(result['source'] == 'mock_data' for result in results)
    
    @patch('requests.get')
    def test_search_with_api(self, mock_get, search_tool):
        """Test search with API response"""
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'items': [
                {
                    'title': 'Jaipur Tourism Guide',
                    'snippet': 'Complete guide to Jaipur',
                    'link': 'https://example.com/jaipur'
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with patch.object(search_tool, 'api_key', 'test_key'):
            with patch.object(search_tool, 'search_engine_id', 'test_engine'):
                results = search_tool.search("Jaipur tourism")
                
                assert len(results) == 1
                assert results[0]['title'] == 'Jaipur Tourism Guide'
                assert results[0]['source'] == 'google_search'
    
    @patch('requests.get')
    def test_search_api_error(self, mock_get, search_tool):
        """Test search with API error (should fallback to mock)"""
        mock_get.side_effect = requests.RequestException("API Error")
        
        with patch.object(search_tool, 'api_key', 'test_key'):
            with patch.object(search_tool, 'search_engine_id', 'test_engine'):
                results = search_tool.search("Jaipur tourism")
                
                assert isinstance(results, list)
                assert all(result['source'] == 'mock_data' for result in results)
    
    def test_search_specific_info(self, search_tool):
        """Test specific information search"""
        results = search_tool.search_specific_info("Jaipur", "restaurants")
        
        assert isinstance(results, list)
        assert len(results) <= 3  # Limited results


class TestWeatherTool:
    """Test cases for WeatherTool"""
    
    @pytest.fixture
    def weather_tool(self):
        """Create WeatherTool instance"""
        return WeatherTool()
    
    def test_get_current_weather_mock(self, weather_tool):
        """Test current weather with mock data"""
        with patch.object(weather_tool, 'api_key', None):
            weather = weather_tool.get_current_weather("Jaipur")
            
            assert weather is not None
            assert weather['location'] == 'Jaipur'
            assert weather['source'] == 'mock_data'
            assert 'temperature' in weather
            assert 'description' in weather
    
    @patch('requests.get')
    def test_get_current_weather_api(self, mock_get, weather_tool):
        """Test current weather with API"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'name': 'Jaipur',
            'sys': {'country': 'IN'},
            'main': {'temp': 28, 'feels_like': 30, 'humidity': 45},
            'weather': [{'description': 'clear sky', 'main': 'Clear'}],
            'wind': {'speed': 3.5}
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with patch.object(weather_tool, 'api_key', 'test_key'):
            weather = weather_tool.get_current_weather("Jaipur")
            
            assert weather['location'] == 'Jaipur'
            assert weather['temperature'] == 28
            assert weather['source'] == 'openweathermap'
    
    def test_get_weather_forecast_mock(self, weather_tool):
        """Test weather forecast with mock data"""
        with patch.object(weather_tool, 'api_key', None):
            forecast = weather_tool.get_weather_forecast("Jaipur", days=3)
            
            assert forecast is not None
            assert forecast['location'] == 'Jaipur'
            assert forecast['forecast_days'] == 3
            assert len(forecast['daily_forecasts']) == 3
            assert forecast['source'] == 'mock_data'
    
    def test_weather_advice(self, weather_tool):
        """Test weather advice generation"""
        # Hot weather
        hot_weather = {'temperature': 35, 'description': 'clear sky'}
        advice = weather_tool.get_weather_advice(hot_weather)
        assert 'Hot weather' in advice
        
        # Rainy weather
        rainy_weather = {'temperature': 25, 'description': 'light rain'}
        advice = weather_tool.get_weather_advice(rainy_weather)
        assert 'Rain expected' in advice
        
        # Cold weather
        cold_weather = {'temperature': 10, 'description': 'clear sky'}
        advice = weather_tool.get_weather_advice(cold_weather)
        assert 'Cool weather' in advice


class TestLocationExtractor:
    """Test cases for LocationExtractor"""
    
    @pytest.fixture
    def extractor(self):
        """Create LocationExtractor instance"""
        return LocationExtractor()
    
    def test_extract_indian_cities(self, extractor):
        """Test extraction of Indian cities"""
        text = "I want to visit Jaipur and Mumbai for vacation"
        locations = extractor.extract_locations(text)
        
        assert 'jaipur' in locations
        assert 'mumbai' in locations
    
    def test_extract_with_context(self, extractor):
        """Test extraction with contextual phrases"""
        text = "Plan a trip to Delhi and visit Red Fort"
        locations = extractor.extract_locations(text)
        
        assert 'delhi' in locations
    
    def test_get_primary_location(self, extractor):
        """Test getting primary location"""
        text = "Travel to Goa for beaches and then Shimla for hills"
        primary = extractor.get_primary_location(text)
        
        assert primary is not None
        assert primary.lower() in ['goa', 'shimla']
    
    def test_is_location_in_india(self, extractor):
        """Test checking if location is in India"""
        assert extractor.is_location_in_india('jaipur') is True
        assert extractor.is_location_in_india('mumbai') is True
        assert extractor.is_location_in_india('london') is False
        assert extractor.is_location_in_india('new york') is False
    
    def test_extract_no_location(self, extractor):
        """Test extraction when no location is found"""
        text = "I want to learn programming"
        locations = extractor.extract_locations(text)
        
        # Should return default location
        assert len(locations) >= 1
    
    def test_global_instance(self):
        """Test global location_extractor instance"""
        locations = location_extractor.extract_locations("Visit beautiful Kerala")
        assert 'kerala' in locations


class TestCache:
    """Test cases for caching system"""
    
    @pytest.fixture
    def cache(self):
        """Create cache instance"""
        cache = SimpleCache(default_ttl=60)
        cache.clear()  # Start with empty cache
        return cache
    
    def test_cache_set_get(self, cache):
        """Test basic cache set and get"""
        cache.set("test_key", "test_value")
        value = cache.get("test_key")
        
        assert value == "test_value"
    
    def test_cache_miss(self, cache):
        """Test cache miss"""
        value = cache.get("nonexistent_key")
        assert value is None
    
    def test_cache_expiry(self, cache):
        """Test cache expiry"""
        cache.set("expire_key", "expire_value", ttl=0)  # Immediate expiry
        
        import time
        time.sleep(0.1)  # Wait for expiry
        
        value = cache.get("expire_key")
        assert value is None
    
    def test_cache_decorator(self):
        """Test cache decorator"""
        call_count = 0
        
        @cached(ttl=60)
        def test_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call
        result1 = test_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # Second call (should use cache)
        result2 = test_function(5)
        assert result2 == 10
        assert call_count == 1  # Should not increment
        
        # Different argument (should call function)
        result3 = test_function(10)
        assert result3 == 20
        assert call_count == 2
    
    def test_cache_disabled(self):
        """Test cache when disabled"""
        with patch('tools.cache.os.getenv', return_value='false'):
            disabled_cache = SimpleCache()
            
            disabled_cache.set("test_key", "test_value")
            value = disabled_cache.get("test_key")
            
            assert value is None  # Cache is disabled
    
    def test_cache_cleanup(self, cache):
        """Test cache cleanup of expired items"""
        cache.set("keep_key", "keep_value", ttl=60)
        cache.set("expire_key", "expire_value", ttl=0)
        
        import time
        time.sleep(0.1)
        
        cleaned = cache.cleanup_expired()
        assert cleaned >= 1
        
        # Verify expired item is gone but valid item remains
        assert cache.get("keep_key") == "keep_value"
        assert cache.get("expire_key") is None
    
    def test_cache_stats(self, cache):
        """Test cache statistics"""
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        stats = cache.get_stats()
        
        assert stats['enabled'] is True
        assert stats['total_items'] == 2
        assert 'default_ttl' in stats