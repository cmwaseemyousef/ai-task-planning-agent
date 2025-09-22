#!/usr/bin/env python3
"""
Test the mock agent functionality
"""

import sys
sys.path.append('.')

from agent.mock_agent import MockTaskPlanningAgent

def test_mock_agent():
    agent = MockTaskPlanningAgent()
    
    # Test with assignment example
    goal = "Plan a 2-day vegetarian food tour in Hyderabad"
    plan = agent.create_plan(goal)
    
    print("🎯 Mock Agent Test Results:")
    print("=" * 50)
    print(f"Goal: {plan['goal']}")
    print(f"Total Steps: {plan['total_steps']}")
    print(f"Duration: {plan['estimated_total_duration']}")
    print(f"Has Research: {plan['metadata']['has_web_research']}")
    print(f"AI Provider: {plan['metadata']['ai_provider']}")
    
    print("\n📝 First Step:")
    first_step = plan['steps'][0]
    print(f"  {first_step['step_number']}. {first_step['title']}")
    print(f"     {first_step['description'][:100]}...")
    
    if first_step.get('web_research'):
        print(f"     🔍 Found {len(first_step['web_research'])} research results")

if __name__ == "__main__":
    test_mock_agent()