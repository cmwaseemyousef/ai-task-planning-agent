"""
Unit tests for the AI Task Planning Agent
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.task_planner import TaskPlanningAgent
from tools.web_search import WebSearchTool
from tools.weather import WeatherTool
from database.database import DatabaseManager

class TestTaskPlanningAgent(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = TaskPlanningAgent()
    
    def test_agent_initialization(self):
        """Test agent initializes correctly"""
        self.assertIsInstance(self.agent.web_search, WebSearchTool)
        self.assertIsInstance(self.agent.weather_tool, WeatherTool)
    
    @patch('openai.OpenAI')
    def test_create_plan_basic(self, mock_openai):
        """Test basic plan creation"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''[
            {
                "step_number": 1,
                "title": "Test Step",
                "description": "Test description",
                "estimated_duration": "1 hour",
                "requires_research": false,
                "research_topics": []
            }
        ]'''
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Test plan creation
        plan = self.agent.create_plan("Test goal")
        
        self.assertEqual(plan['goal'], "Test goal")
        self.assertEqual(plan['total_steps'], 1)
        self.assertEqual(len(plan['steps']), 1)
    
    def test_extract_location(self):
        """Test location extraction"""
        text1 = "Plan a trip to Jaipur with cultural activities"
        location1 = self.agent._extract_location(text1)
        self.assertEqual(location1, "Jaipur")
        
        text2 = "No location mentioned here"
        location2 = self.agent._extract_location(text2)
        self.assertIsNone(location2)

class TestWebSearchTool(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.search_tool = WebSearchTool()
    
    def test_mock_search_results(self):
        """Test mock search functionality"""
        results = self.search_tool.search("Jaipur tourism")
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        
        # Check result structure
        result = results[0]
        self.assertIn('title', result)
        self.assertIn('snippet', result)
        self.assertIn('url', result)
        self.assertIn('source', result)

class TestWeatherTool(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.weather_tool = WeatherTool()
    
    def test_mock_weather_data(self):
        """Test mock weather functionality"""
        weather = self.weather_tool.get_current_weather("Jaipur")
        
        self.assertIsInstance(weather, dict)
        self.assertIn('location', weather)
        self.assertIn('temperature', weather)
        self.assertIn('description', weather)
        self.assertEqual(weather['source'], 'mock_data')
    
    def test_weather_forecast(self):
        """Test weather forecast functionality"""
        forecast = self.weather_tool.get_weather_forecast("Jaipur", days=3)
        
        self.assertIsInstance(forecast, dict)
        self.assertIn('daily_forecasts', forecast)
        self.assertEqual(len(forecast['daily_forecasts']), 3)

class TestDatabaseManager(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        # Use in-memory SQLite for testing
        self.db_manager = DatabaseManager("sqlite:///:memory:")
    
    def test_save_and_retrieve_plan(self):
        """Test saving and retrieving plans"""
        test_plan = {
            'goal': 'Test goal for database',
            'total_steps': 2,
            'estimated_total_duration': '2 hours',
            'steps': [
                {
                    'step_number': 1,
                    'title': 'First step',
                    'description': 'First step description'
                }
            ],
            'metadata': {
                'has_weather_info': False,
                'has_web_research': True
            }
        }
        
        # Save plan
        plan_id = self.db_manager.save_plan(test_plan)
        self.assertIsInstance(plan_id, int)
        
        # Retrieve plan
        retrieved_plan = self.db_manager.get_plan_by_id(plan_id)
        self.assertIsNotNone(retrieved_plan)
        self.assertEqual(retrieved_plan['plan_data']['goal'], test_plan['goal'])
    
    def test_search_plans(self):
        """Test plan search functionality"""
        # Save a test plan
        test_plan = {
            'goal': 'Learn Python programming',
            'total_steps': 1,
            'steps': [],
            'metadata': {}
        }
        
        plan_id = self.db_manager.save_plan(test_plan)
        
        # Search for the plan
        results = self.db_manager.search_plans("Python")
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]['id'], plan_id)

if __name__ == '__main__':
    unittest.main()