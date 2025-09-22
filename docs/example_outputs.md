# Example Plan Outputs

This document contains example outputs from the AI Task Planning Agent for the assignment goals.

## Example 1: Vegetarian Food Tour in Hyderabad

**Goal**: "Plan a 2-day vegetarian food tour in Hyderabad"

**Generated Plan**:

```json
{
  "goal": "Plan a 2-day vegetarian food tour in Hyderabad",
  "created_at": "2025-09-20T10:00:00",
  "total_steps": 6,
  "estimated_total_duration": "2 days, 4 hours",
  "steps": [
    {
      "step_number": 1,
      "title": "Day 1 Morning: Traditional South Indian Breakfast",
      "description": "Start with authentic Hyderabadi breakfast items like Dosa, Idli, and Vada at famous local restaurants in Banjara Hills area",
      "estimated_duration": "2 hours",
      "requires_research": true,
      "web_research": [
        {
          "title": "Best Vegetarian Restaurants in Hyderabad",
          "snippet": "Top vegetarian dining spots in Hyderabad including traditional South Indian, North Indian, and fusion cuisine.",
          "source": "mock_data"
        }
      ]
    },
    {
      "step_number": 2,
      "title": "Day 1 Afternoon: Local Street Food Experience", 
      "description": "Explore Charminar area for vegetarian street food like Pani Puri, Bhel Puri, and local snacks",
      "estimated_duration": "3 hours",
      "requires_research": true,
      "web_research": [
        {
          "title": "Hyderabad Vegetarian Food Tour",
          "snippet": "Explore the diverse vegetarian food scene including famous Hyderabadi biryani variants, dosas, and sweets.",
          "source": "mock_data"
        }
      ]
    }
  ],
  "metadata": {
    "has_weather_info": true,
    "has_web_research": true,
    "research_topics": ["Hyderabad vegetarian restaurants", "vegetarian food tour"]
  }
}
```

## Example 2: Python Learning Study Routine

**Goal**: "Organise a 5-step daily study routine for learning Python"

**Generated Plan**:

```json
{
  "goal": "Organise a 5-step daily study routine for learning Python",
  "created_at": "2025-09-20T10:30:00",
  "total_steps": 5,
  "estimated_total_duration": "3 hours, 30 minutes",
  "steps": [
    {
      "step_number": 1,
      "title": "Morning Theory Session (30 min)",
      "description": "Study Python concepts, syntax, and fundamentals using online resources or textbooks",
      "estimated_duration": "30 minutes",
      "requires_research": true,
      "web_research": [
        {
          "title": "Python Learning Roadmap for Beginners",
          "snippet": "Complete guide to learning Python programming from basics to advanced concepts with practical projects.",
          "source": "mock_data"
        }
      ]
    },
    {
      "step_number": 2,
      "title": "Hands-on Coding Practice (45 min)",
      "description": "Practice coding exercises on platforms like HackerRank, LeetCode, or Python.org tutorials",
      "estimated_duration": "45 minutes",
      "requires_research": true
    }
  ]
}
```

## Example 3: Vizag Weekend Plan

**Goal**: "Create a weekend plan in Vizag with beach, hiking, and seafood"

**Generated Plan**:

```json
{
  "goal": "Create a weekend plan in Vizag with beach, hiking, and seafood",
  "created_at": "2025-09-20T11:00:00", 
  "total_steps": 4,
  "estimated_total_duration": "2 days, 6 hours",
  "steps": [
    {
      "step_number": 1,
      "title": "Saturday Morning: Beach Activities at RK Beach",
      "description": "Start the weekend with sunrise viewing and beach activities at Ramakrishna Beach, including water sports if available",
      "estimated_duration": "4 hours",
      "requires_research": true,
      "web_research": [
        {
          "title": "Vizag Weekend Guide - Beaches and Hills",
          "snippet": "Perfect weekend getaway with beautiful beaches, Araku Valley hills, and fresh seafood experiences.",
          "source": "mock_data"
        }
      ],
      "weather_info": {
        "location": "Vizag",
        "country": "IN",
        "daily_forecasts": [
          {
            "date": "2025-09-21",
            "max_temp": 27,
            "min_temp": 21,
            "description": "partly cloudy"
          }
        ],
        "source": "mock_data"
      }
    },
    {
      "step_number": 2,
      "title": "Saturday Evening: Seafood Dinner",
      "description": "Experience fresh seafood at local coastal restaurants with traditional Andhra preparations",
      "estimated_duration": "2 hours",
      "web_research": [
        {
          "title": "Best Seafood Restaurants in Visakhapatnam", 
          "snippet": "Top seafood dining spots along the coast with fresh catches and traditional Andhra preparations.",
          "source": "mock_data"
        }
      ]
    }
  ],
  "metadata": {
    "has_weather_info": true,
    "has_web_research": true,
    "research_topics": ["Vizag beaches", "hiking in Vizag", "seafood restaurants"]
  }
}
```

## Key Features Demonstrated

### 1. Goal Decomposition
- Each goal is broken down into logical, sequential steps
- Steps include specific timing and duration estimates
- Activities are organized by day/time for travel plans

### 2. External Information Integration
- **Web Research**: Relevant information from search results
- **Weather Data**: Location-based weather forecasts for outdoor activities
- **Mock Data**: Fallback system when APIs are unavailable

### 3. Structured Output
- Consistent JSON format for all plans
- Metadata tracking for features used
- Clear step numbering and descriptions

### 4. Contextual Intelligence
- Location-aware planning (beaches in Vizag, food in Hyderabad)
- Activity-appropriate timing (morning beach visits, evening dining)
- Weather consideration for outdoor activities

These examples demonstrate the agent's ability to create practical, actionable plans that users can follow to achieve their goals.