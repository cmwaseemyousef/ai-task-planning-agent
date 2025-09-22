# API Setup Guide

This guide explains how to set up the external APIs used by the AI Task Planning Agent.

## 🔑 Required API Keys

The application requires one mandatory API key and two optional ones:

### ✅ Required: OpenAI API Key
**Purpose**: Powers the AI agent for goal decomposition and planning
**Cost**: Pay-per-use (approximately $0.002 per request)

### ⚠️ Optional: Google Custom Search API
**Purpose**: Provides real web search results for plan enrichment
**Fallback**: Mock data with realistic examples
**Cost**: Free tier available (100 searches/day)

### ⚠️ Optional: OpenWeatherMap API
**Purpose**: Provides weather forecasts for location-based plans
**Fallback**: Mock weather data
**Cost**: Free tier available (1000 calls/day)

## 🚀 Setup Instructions

### 1. OpenAI API Key (Required)

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to **API Keys** section
4. Click **"Create new secret key"**
5. Copy the key and add to your `.env` file:
   ```env
   OPENAI_API_KEY=sk-your-key-here
   ```

**💡 Cost Optimization**:
- Uses GPT-3.5-turbo model (cheaper than GPT-4)
- Average cost per plan: $0.001-0.005
- Monthly cost for 100 plans: ~$0.50

### 2. Google Custom Search API (Optional)

#### Step 1: Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the **Custom Search API**

#### Step 2: Get API Key
1. Go to **APIs & Services > Credentials**
2. Click **Create Credentials > API Key**
3. Copy the API key

#### Step 3: Create Custom Search Engine
1. Go to [Google Custom Search](https://cse.google.com/)
2. Click **Add** to create a new search engine
3. Enter any website (you can edit later)
4. Get your **Search Engine ID** from the control panel

#### Step 4: Configure for Web Search
1. In your custom search engine settings
2. Go to **Setup > Basics**
3. Enable **Search the entire web**
4. Remove the specific site restriction

#### Step 5: Add to Environment
```env
SEARCH_API_KEY=your-google-api-key
SEARCH_ENGINE_ID=your-search-engine-id
```

**💡 Alternative**: If you skip this setup, the app will use realistic mock data that includes information about Indian cities, restaurants, and tourist attractions.

### 3. OpenWeatherMap API (Optional)

1. Go to [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for a free account
3. Navigate to **API Keys** section
4. Copy your default API key
5. Add to your `.env` file:
   ```env
   WEATHER_API_KEY=your-openweather-api-key
   ```

**💡 Alternative**: If you skip this setup, the app will use mock weather data with realistic forecasts for Indian cities.

## 🔧 Environment Configuration

Create a `.env` file in your project root:

```env
# Required - AI functionality
OPENAI_API_KEY=sk-your-openai-key-here

# Optional - Enhanced web search  
SEARCH_API_KEY=your-google-search-api-key
SEARCH_ENGINE_ID=your-search-engine-id

# Optional - Weather data
WEATHER_API_KEY=your-openweather-api-key

# Database (default: SQLite)
DATABASE_URL=sqlite:///./plans.db

# Server configuration  
HOST=localhost
PORT=8000
```

## 🧪 Testing API Setup

### Test OpenAI Connection
```python
import openai
from openai import OpenAI

client = OpenAI(api_key="your-key-here")
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello, AI!"}],
    max_tokens=50
)
print(response.choices[0].message.content)
```

### Test Google Search
```python
import requests

url = "https://www.googleapis.com/customsearch/v1"
params = {
    'key': 'your-api-key',
    'cx': 'your-search-engine-id', 
    'q': 'test search'
}
response = requests.get(url, params=params)
print(response.json())
```

### Test Weather API
```python
import requests

url = "http://api.openweathermap.org/data/2.5/weather"
params = {
    'q': 'Jaipur',
    'appid': 'your-api-key',
    'units': 'metric'
}
response = requests.get(url, params=params)
print(response.json())
```

## 🚨 Troubleshooting

### OpenAI API Issues
- **401 Unauthorized**: Check if API key is correct
- **429 Rate Limit**: You've exceeded usage limits
- **500 Server Error**: Try again later, OpenAI service issue

### Google Search Issues
- **403 Forbidden**: API key might be restricted
- **400 Bad Request**: Check search engine ID format
- **Daily limit exceeded**: Wait for quota reset

### Weather API Issues
- **401 Unauthorized**: Invalid API key
- **404 Not Found**: City name not recognized
- **429 Too Many Requests**: Rate limit exceeded

## 💰 Cost Management

### OpenAI Costs
- **GPT-3.5-turbo**: $0.0015 per 1K input tokens, $0.002 per 1K output tokens
- **Average plan**: 500-1000 tokens = $0.001-0.003 per plan
- **Monthly estimate**: 100 plans = ~$0.30

### Google Search Costs
- **Free tier**: 100 searches/day
- **Paid tier**: $5 per 1,000 additional queries
- **App usage**: 1-3 searches per plan

### Weather API Costs
- **Free tier**: 1,000 calls/day, 60 calls/minute
- **App usage**: 1 call per location-based plan
- **Very unlikely to exceed free limits**

## 🔒 Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for all secrets
3. **Restrict API key permissions** where possible
4. **Monitor usage** to detect unexpected spikes
5. **Rotate keys periodically** for security

## 🎯 Minimum Setup for Demo

To run the demo with **minimal setup**:

1. **Only get OpenAI API key** (required)
2. **Skip Google Search and Weather APIs**
3. **App will use mock data** for external information
4. **Still fully functional** for demonstration

The mock data includes realistic information about:
- Indian cities and tourist attractions
- Restaurant recommendations
- Weather forecasts
- Learning resources

This allows you to demonstrate the full functionality without setting up multiple APIs.