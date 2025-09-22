"""
Core AI Agent for Task Planning
Handles breaking down goals into actionable steps using LLM
"""

from typing import List, Dict, Optional
import openai
from openai import OpenAI
import json
import os
from datetime import datetime
from dotenv import load_dotenv

from tools.web_search import WebSearchTool
from tools.weather import WeatherTool
from tools.location_extractor import location_extractor
from database.models import Plan, PlanStep

load_dotenv()

class TaskPlanningAgent:
    def __init__(self):
        """Initialize the AI agent with LLM and tools"""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.web_search = WebSearchTool()
        self.weather_tool = WeatherTool()
        
    def create_plan(self, goal: str) -> Dict:
        """
        Main method to create a plan from a natural language goal
        
        Args:
            goal (str): Natural language description of the goal
            
        Returns:
            Dict: Complete plan with enriched steps
        """
        print(f"Processing goal: {goal}")
        
        # Step 1: Break down goal into actionable steps
        base_plan = self._generate_base_plan(goal)
        
        # Step 2: Enrich steps with external information
        enriched_plan = self._enrich_plan(base_plan)
        
        # Step 3: Structure the final plan
        final_plan = self._structure_plan(goal, enriched_plan)
        
        return final_plan
    
    def _generate_base_plan(self, goal: str) -> List[Dict]:
        """Generate basic plan steps using LLM"""
        
        prompt = f"""
        You are an expert task planning assistant. Given a goal, break it down into clear, actionable steps.
        
        Goal: {goal}
        
        Please provide a structured plan with the following format:
        - Each step should be specific and actionable
        - Include timing estimates where relevant
        - Consider dependencies between steps
        - Include any research or information gathering needs
        
        Return your response as a JSON array of steps, where each step has:
        - "step_number": integer
        - "title": brief title of the step
        - "description": detailed description
        - "estimated_duration": time estimate
        - "requires_research": boolean if external info is needed
        - "research_topics": array of topics to research (if applicable)
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful task planning assistant. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            # Extract JSON from the response
            json_start = content.find('[')
            json_end = content.rfind(']') + 1
            json_content = content[json_start:json_end]
            
            steps = json.loads(json_content)
            return steps
            
        except Exception as e:
            print(f"Error generating base plan: {e}")
            # Fallback basic structure
            return [
                {
                    "step_number": 1,
                    "title": "Break down the goal",
                    "description": f"Research and plan for: {goal}",
                    "estimated_duration": "30 minutes",
                    "requires_research": True,
                    "research_topics": [goal]
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
                        web_info.extend(search_results[:3])  # Top 3 results per topic
                
                enriched_step["web_research"] = web_info
                
                # Add weather information if location-related
                if any(keyword in step["description"].lower() 
                       for keyword in ["trip", "travel", "visit", "weather", "outdoor", "beach", "hiking"]):
                    
                    # Extract location using improved NER
                    text_for_extraction = step["description"] + " " + " ".join(research_topics)
                    location = location_extractor.get_primary_location(text_for_extraction)
                    if location:
                        weather_info = self.weather_tool.get_weather_forecast(location)
                        enriched_step["weather_info"] = weather_info
                        enriched_step["detected_location"] = location
            
            enriched_steps.append(enriched_step)
        
        return enriched_steps
    
    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location using improved NER (deprecated - use location_extractor)"""
        # Use the new location extractor
        return location_extractor.get_primary_location(text)
    
    def _structure_plan(self, goal: str, enriched_steps: List[Dict]) -> Dict:
        """Structure the final plan with metadata"""
        
        return {
            "id": None,  # Will be set by database
            "goal": goal,
            "created_at": datetime.now().isoformat(),
            "total_steps": len(enriched_steps),
            "estimated_total_duration": self._calculate_total_duration(enriched_steps),
            "steps": enriched_steps,
            "metadata": {
                "has_weather_info": any("weather_info" in step for step in enriched_steps),
                "has_web_research": any("web_research" in step for step in enriched_steps),
                "research_topics": self._extract_all_research_topics(enriched_steps)
            }
        }
    
    def _calculate_total_duration(self, steps: List[Dict]) -> str:
        """Calculate total estimated duration"""
        # Simple implementation - could be more sophisticated
        total_minutes = 0
        
        for step in steps:
            duration_str = step.get("estimated_duration", "30 minutes")
            # Extract numbers from duration string
            import re
            numbers = re.findall(r'\d+', duration_str)
            if numbers:
                if "hour" in duration_str.lower():
                    total_minutes += int(numbers[0]) * 60
                elif "day" in duration_str.lower():
                    total_minutes += int(numbers[0]) * 24 * 60
                else:  # assume minutes
                    total_minutes += int(numbers[0])
        
        if total_minutes >= 1440:  # More than a day
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
        return list(set(topics))  # Remove duplicates