"""
Pytest configuration and fixtures
"""

import pytest
import os
import tempfile
from unittest.mock import patch

# Set test environment
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["LOG_LEVEL"] = "WARNING"
os.environ["ENABLE_CACHE"] = "false"

@pytest.fixture(scope="session")
def test_env():
    """Set up test environment"""
    original_env = os.environ.copy()
    
    # Override environment variables for testing
    test_vars = {
        "TESTING": "true",
        "DATABASE_URL": "sqlite:///:memory:",
        "LOG_LEVEL": "WARNING",
        "ENABLE_CACHE": "false",
        "OPENAI_API_KEY": "test_key",
        "WEATHER_API_KEY": None,
        "SEARCH_API_KEY": None
    }
    
    for key, value in test_vars.items():
        if value is not None:
            os.environ[key] = value
        elif key in os.environ:
            del os.environ[key]
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)

@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def sample_plan_data():
    """Sample plan data for testing"""
    return {
        "goal": "Test plan for visiting Jaipur",
        "total_steps": 2,
        "estimated_total_duration": "1 day",
        "steps": [
            {
                "step_number": 1,
                "title": "Visit Amber Fort",
                "description": "Explore the historic Amber Fort",
                "estimated_duration": "3 hours",
                "requires_research": True,
                "research_topics": ["Amber Fort", "Jaipur history"]
            },
            {
                "step_number": 2,
                "title": "Local Food Tour",
                "description": "Try traditional Rajasthani cuisine",
                "estimated_duration": "2 hours",
                "requires_research": True,
                "research_topics": ["Rajasthani food", "Jaipur restaurants"]
            }
        ],
        "metadata": {
            "has_weather_info": False,
            "has_web_research": True,
            "research_topics": ["Amber Fort", "Jaipur history", "Rajasthani food"]
        }
    }

@pytest.fixture
def mock_weather_response():
    """Mock weather API response"""
    return {
        "location": "Jaipur",
        "country": "IN",
        "temperature": 28,
        "feels_like": 30,
        "humidity": 45,
        "description": "clear sky",
        "main": "Clear",
        "wind_speed": 3.5,
        "source": "openweathermap"
    }

@pytest.fixture
def mock_search_response():
    """Mock search API response"""
    return [
        {
            "title": "Jaipur Tourism Guide",
            "snippet": "Complete guide to visiting Jaipur with all major attractions",
            "url": "https://example.com/jaipur-guide",
            "source": "google_search"
        },
        {
            "title": "Best Places to Visit in Jaipur",
            "snippet": "Top attractions and activities in the Pink City",
            "url": "https://example.com/jaipur-places",
            "source": "google_search"
        }
    ]

# Configure logging for tests
import logging
logging.getLogger().setLevel(logging.WARNING)