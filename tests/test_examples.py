"""
Test the AI Task Planning Agent with example goals
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.task_planner import TaskPlanningAgent
from database.database import DatabaseManager
import json

def test_agent_with_examples():
    """Test the agent with the provided example goals"""
    
    # Initialize components
    agent = TaskPlanningAgent()
    db_manager = DatabaseManager()
    
    # Example goals from the assignment
    example_goals = [
        "Plan a 2-day vegetarian food tour in Hyderabad",
        "Organise a 5-step daily study routine for learning Python", 
        "Create a weekend plan in Vizag with beach, hiking, and seafood"
    ]
    
    print("🤖 Testing AI Task Planning Agent")
    print("=" * 50)
    
    for i, goal in enumerate(example_goals, 1):
        print(f"\n📋 Test {i}: {goal}")
        print("-" * 30)
        
        try:
            # Generate plan
            plan_data = agent.create_plan(goal)
            
            # Save to database
            plan_id = db_manager.save_plan(plan_data)
            
            # Display results
            print(f"✅ Plan created successfully (ID: {plan_id})")
            print(f"📊 Steps: {plan_data['total_steps']}")
            print(f"⏱️  Duration: {plan_data['estimated_total_duration']}")
            print(f"🔍 Has Research: {plan_data['metadata']['has_web_research']}")
            print(f"🌤️  Has Weather: {plan_data['metadata']['has_weather_info']}")
            
            # Show first few steps
            for j, step in enumerate(plan_data['steps'][:2], 1):
                print(f"\n  Step {j}: {step['title']}")
                print(f"  📝 {step['description'][:100]}...")
                
                if step.get('web_research'):
                    print(f"  🔍 Found {len(step['web_research'])} research results")
                
                if step.get('weather_info'):
                    print(f"  🌤️  Weather info for {step['weather_info']['location']}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Test database operations
    print(f"\n📊 Database Statistics")
    print("-" * 30)
    stats = db_manager.get_plan_statistics()
    print(f"Total plans: {stats['total_plans']}")
    print(f"Recent plans: {stats['recent_plans']}")
    
    # Test search
    print(f"\n🔍 Search Test: 'Python'")
    print("-" * 30)
    search_results = db_manager.search_plans("Python")
    for result in search_results:
        print(f"- {result['goal'][:60]}... (ID: {result['id']})")

if __name__ == "__main__":
    test_agent_with_examples()