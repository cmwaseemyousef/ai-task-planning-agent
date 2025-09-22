"""
Mock AI Agent for demonstration when OpenAI API is not available
"""

from typing import List, Dict
import json
from datetime import datetime

from tools.web_search import WebSearchTool
from tools.weather import WeatherTool
from tools.location_extractor import location_extractor

class MockTaskPlanningAgent:
    """Mock version of the AI agent for demo purposes"""
    
    def __init__(self):
        """Initialize the mock agent with tools"""
        self.web_search = WebSearchTool()
        self.weather_tool = WeatherTool()
        
    def create_plan(self, goal: str) -> Dict:
        """
        Create a mock plan based on predefined templates
        """
        print(f"Processing goal: {goal}")
        
        # Generate plan based on goal keywords
        base_plan = self._generate_mock_plan(goal)
        
        # Enrich with external information
        enriched_plan = self._enrich_plan(base_plan)
        
        # Structure the final plan
        final_plan = self._structure_plan(goal, enriched_plan)
        
        return final_plan
    
    def _generate_mock_plan(self, goal: str) -> List[Dict]:
        """Generate mock plan based on goal keywords"""
        
        goal_lower = goal.lower()
        
        if "jaipur" in goal_lower and "trip" in goal_lower:
            return [
                {
                    "step_number": 1,
                    "title": "Day 1: Explore Historic Forts and Palaces",
                    "description": "Visit Amber Fort in the morning, explore the magnificent architecture and take elephant rides. Afternoon visit to City Palace and Jantar Mantar observatory.",
                    "estimated_duration": "8 hours",
                    "requires_research": True,
                    "research_topics": ["Amber Fort Jaipur", "City Palace timings", "Jaipur attractions"]
                },
                {
                    "step_number": 2,
                    "title": "Day 2: Local Markets and Cultural Food",
                    "description": "Morning visit to Johari Bazaar for jewelry shopping, followed by traditional Rajasthani lunch. Evening at Chokhi Dhani for cultural performances.",
                    "estimated_duration": "7 hours",
                    "requires_research": True,
                    "research_topics": ["Jaipur markets", "Rajasthani food", "cultural activities"]
                },
                {
                    "step_number": 3,
                    "title": "Day 3: Hawa Mahal and Local Experiences",
                    "description": "Early morning photography at Hawa Mahal, visit local handicraft workshops, and enjoy sunset at Nahargarh Fort with panoramic city views.",
                    "estimated_duration": "6 hours",
                    "requires_research": True,
                    "research_topics": ["Hawa Mahal photography", "Nahargarh Fort sunset"]
                }
            ]
        
        elif "hyderabad" in goal_lower and "vegetarian" in goal_lower:
            return [
                {
                    "step_number": 1,
                    "title": "Day 1 Morning: Traditional South Indian Breakfast",
                    "description": "Start with authentic breakfast at Ram Ki Bandi or similar local spots. Try dosa varieties, idli, vada, and filter coffee.",
                    "estimated_duration": "3 hours",
                    "requires_research": True,
                    "research_topics": ["Hyderabad vegetarian breakfast", "best dosa places"]
                },
                {
                    "step_number": 2,
                    "title": "Day 1 Evening: Charminar Street Food",
                    "description": "Explore vegetarian street food around Charminar including pani puri, bhel puri, and local sweets like double ka meetha.",
                    "estimated_duration": "4 hours",
                    "requires_research": True,
                    "research_topics": ["Charminar vegetarian food", "Hyderabad street food"]
                },
                {
                    "step_number": 3,
                    "title": "Day 2: Vegetarian Biryani and Traditional Cuisine",
                    "description": "Experience famous vegetarian biryani at Paradise or Bawarchi, followed by traditional Andhra thali at a local restaurant.",
                    "estimated_duration": "5 hours",
                    "requires_research": True,
                    "research_topics": ["vegetarian biryani Hyderabad", "Andhra vegetarian restaurants"]
                }
            ]
        
        elif "python" in goal_lower and "study" in goal_lower:
            return [
                {
                    "step_number": 1,
                    "title": "Morning Theory Session (30 minutes)",
                    "description": "Study Python fundamentals including syntax, variables, data types, and basic operations using online resources or documentation.",
                    "estimated_duration": "30 minutes",
                    "requires_research": True,
                    "research_topics": ["Python basics tutorial", "Python syntax guide"]
                },
                {
                    "step_number": 2,
                    "title": "Hands-on Coding Practice (45 minutes)",
                    "description": "Practice coding exercises on platforms like HackerRank, LeetCode, or Python.org tutorials focusing on basic problem solving.",
                    "estimated_duration": "45 minutes",
                    "requires_research": True,
                    "research_topics": ["Python coding practice", "beginner Python exercises"]
                },
                {
                    "step_number": 3,
                    "title": "Project Work (60 minutes)",
                    "description": "Work on a small practical project like a calculator, to-do list, or simple game to apply learned concepts.",
                    "estimated_duration": "60 minutes",
                    "requires_research": True,
                    "research_topics": ["beginner Python projects", "Python project ideas"]
                },
                {
                    "step_number": 4,
                    "title": "Review and Documentation (20 minutes)",
                    "description": "Review the day's learning, document key concepts, and plan tomorrow's topics based on progress.",
                    "estimated_duration": "20 minutes",
                    "requires_research": False,
                    "research_topics": []
                },
                {
                    "step_number": 5,
                    "title": "Community Engagement (15 minutes)",
                    "description": "Engage with Python community through forums, Discord, or Stack Overflow to ask questions and help others.",
                    "estimated_duration": "15 minutes",
                    "requires_research": True,
                    "research_topics": ["Python community forums", "Python Discord servers"]
                }
            ]
        
        elif "vizag" in goal_lower or "visakhapatnam" in goal_lower:
            return [
                {
                    "step_number": 1,
                    "title": "Saturday Morning: Beach Activities at RK Beach",
                    "description": "Start with sunrise viewing at Ramakrishna Beach, enjoy water sports, beach volleyball, and morning walk along the coastline.",
                    "estimated_duration": "4 hours",
                    "requires_research": True,
                    "research_topics": ["RK Beach activities", "Vizag water sports"]
                },
                {
                    "step_number": 2,
                    "title": "Saturday Afternoon: Kailasagiri Hill Hiking",
                    "description": "Take cable car or hike up to Kailasagiri Hill for panoramic views of the city and coast. Visit Shiva Parvati statue.",
                    "estimated_duration": "3 hours",
                    "requires_research": True,
                    "research_topics": ["Kailasagiri hiking trails", "Vizag hill stations"]
                },
                {
                    "step_number": 3,
                    "title": "Saturday Evening: Seafood Dinner",
                    "description": "Experience fresh seafood at local coastal restaurants with traditional Andhra preparations like fish curry and prawn fry.",
                    "estimated_duration": "2 hours",
                    "requires_research": True,
                    "research_topics": ["best seafood restaurants Vizag", "Andhra fish curry"]
                },
                {
                    "step_number": 4,
                    "title": "Sunday: Araku Valley Day Trip",
                    "description": "Take scenic train journey or drive to Araku Valley for coffee plantations, tribal culture, and valley views.",
                    "estimated_duration": "10 hours",
                    "requires_research": True,
                    "research_topics": ["Araku Valley tour", "Vizag to Araku train"]
                }
            ]
        
        else:
            # Generic plan for unknown goals
            return [
                {
                    "step_number": 1,
                    "title": "Research and Planning",
                    "description": f"Conduct thorough research about: {goal}. Gather information from reliable sources and create a preliminary plan.",
                    "estimated_duration": "1 hour",
                    "requires_research": True,
                    "research_topics": [goal]
                },
                {
                    "step_number": 2,
                    "title": "Implementation Phase 1",
                    "description": "Begin the first phase of executing your plan with the most important and foundational tasks.",
                    "estimated_duration": "2 hours",
                    "requires_research": True,
                    "research_topics": [f"{goal} implementation", f"how to {goal}"]
                },
                {
                    "step_number": 3,
                    "title": "Review and Adjust",
                    "description": "Review progress, gather feedback, and make necessary adjustments to your approach for better results.",
                    "estimated_duration": "30 minutes",
                    "requires_research": False,
                    "research_topics": []
                }
            ]
    
    def _enrich_plan(self, base_plan: List[Dict]) -> List[Dict]:
        """Enrich plan steps with external information"""
        enriched_steps = []
        
        for step in base_plan:
            enriched_step = step.copy()
            
            if step.get("requires_research", False):
                research_topics = step.get("research_topics", [])
                
                # Gather web search information
                web_info = []
                for topic in research_topics:
                    search_results = self.web_search.search(topic)
                    if search_results:
                        web_info.extend(search_results[:2])  # Top 2 results per topic
                
                enriched_step["web_research"] = web_info
                
                # Add weather information if location-related
                if any(keyword in step["description"].lower() 
                       for keyword in ["trip", "travel", "visit", "weather", "outdoor", "beach", "hiking"]):
                    
                    text_for_extraction = step["description"] + " " + " ".join(research_topics)
                    location = location_extractor.get_primary_location(text_for_extraction)
                    if location:
                        weather_info = self.weather_tool.get_weather_forecast(location)
                        enriched_step["weather_info"] = weather_info
                        enriched_step["detected_location"] = location
            
            enriched_steps.append(enriched_step)
        
        return enriched_steps
    
    def _extract_location(self, text: str) -> str:
        """Extract location from text using improved NER"""
        location = location_extractor.get_primary_location(text)
        return location if location else "Delhi"  # Default fallback
    
    def _structure_plan(self, goal: str, enriched_steps: List[Dict]) -> Dict:
        """Structure the final plan with metadata"""
        
        return {
            "id": None,
            "goal": goal,
            "created_at": datetime.now().isoformat(),
            "total_steps": len(enriched_steps),
            "estimated_total_duration": self._calculate_total_duration(enriched_steps),
            "steps": enriched_steps,
            "metadata": {
                "has_weather_info": any("weather_info" in step for step in enriched_steps),
                "has_web_research": any("web_research" in step for step in enriched_steps),
                "research_topics": self._extract_all_research_topics(enriched_steps),
                "ai_provider": "mock_ai_for_demo"
            }
        }
    
    def _calculate_total_duration(self, steps: List[Dict]) -> str:
        """Calculate total estimated duration"""
        total_minutes = 0
        
        for step in steps:
            duration_str = step.get("estimated_duration", "30 minutes")
            import re
            numbers = re.findall(r'\d+', duration_str)
            if numbers:
                if "hour" in duration_str.lower():
                    total_minutes += int(numbers[0]) * 60
                elif "day" in duration_str.lower():
                    total_minutes += int(numbers[0]) * 24 * 60
                else:
                    total_minutes += int(numbers[0])
        
        if total_minutes >= 1440:
            days = total_minutes // 1440
            hours = (total_minutes % 1440) // 60
            return f"{days} days, {hours} hours"
        elif total_minutes >= 60:
            hours = total_minutes // 60
            minutes = total_minutes % 60
            return f"{hours} hours, {minutes} minutes"
        else:
            return f"{total_minutes} minutes"
    
    def _extract_all_research_topics(self, steps: List[Dict]) -> List[str]:
        """Extract all research topics from steps"""
        topics = []
        for step in steps:
            topics.extend(step.get("research_topics", []))
        return list(set(topics))