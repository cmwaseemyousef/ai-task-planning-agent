"""
Weather Tool for getting contextual weather information
Uses OpenWeatherMap API
"""

import requests
import os
import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from dotenv import load_dotenv
from .cache import cached

load_dotenv()

class WeatherTool:
    def __init__(self):
        """Initialize weather tool with API credentials"""
        self.api_key = os.getenv("WEATHER_API_KEY")
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.logger = logging.getLogger(__name__)
    
    @cached(ttl=1800, key_prefix="weather_current_")
    def get_current_weather(self, location: str) -> Optional[Dict]:
        """
        Get current weather for a location
        
        Args:
            location (str): City name or coordinates
            
        Returns:
            Dict: Current weather information
        """
        if not self.api_key:
            self.logger.warning("Weather API key not configured. Using mock data.")
            return self._get_mock_current_weather(location)
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'location': data['name'],
                'country': data['sys']['country'],
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'],
                'main': data['weather'][0]['main'],
                'wind_speed': data['wind']['speed'],
                'timestamp': datetime.now().isoformat(),
                'source': 'openweathermap'
            }
            
        except requests.RequestException as e:
            self.logger.error(f"Weather API error: {e}")
            return self._get_mock_current_weather(location)
        except Exception as e:
            self.logger.error(f"Unexpected weather error: {e}")
            return self._get_mock_current_weather(location)
    
    @cached(ttl=3600, key_prefix="weather_forecast_")
    def get_weather_forecast(self, location: str, days: int = 5) -> Optional[Dict]:
        """
        Get weather forecast for a location
        
        Args:
            location (str): City name
            days (int): Number of days for forecast (max 5)
            
        Returns:
            Dict: Weather forecast information
        """
        if not self.api_key:
            self.logger.warning("Weather API key not configured. Using mock data.")
            return self._get_mock_forecast(location, days)
        
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': min(days * 8, 40)  # API returns 3-hour intervals, max 40 calls
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Process forecast data into daily summaries
            daily_forecasts = self._process_forecast_data(data['list'])
            
            return {
                'location': data['city']['name'],
                'country': data['city']['country'],
                'forecast_days': len(daily_forecasts),
                'daily_forecasts': daily_forecasts,
                'timestamp': datetime.now().isoformat(),
                'source': 'openweathermap'
            }
            
        except requests.RequestException as e:
            self.logger.error(f"Weather forecast API error: {e}")
            return self._get_mock_forecast(location, days)
        except Exception as e:
            self.logger.error(f"Unexpected forecast error: {e}")
            return self._get_mock_forecast(location, days)
    
    def _process_forecast_data(self, forecast_list: List[Dict]) -> List[Dict]:
        """Process 3-hour forecast data into daily summaries"""
        daily_data = {}
        
        for item in forecast_list:
            date = datetime.fromtimestamp(item['dt']).date()
            date_str = date.isoformat()
            
            if date_str not in daily_data:
                daily_data[date_str] = {
                    'date': date_str,
                    'temperatures': [],
                    'descriptions': [],
                    'humidity': [],
                    'wind_speeds': []
                }
            
            daily_data[date_str]['temperatures'].append(item['main']['temp'])
            daily_data[date_str]['descriptions'].append(item['weather'][0]['description'])
            daily_data[date_str]['humidity'].append(item['main']['humidity'])
            daily_data[date_str]['wind_speeds'].append(item['wind']['speed'])
        
        # Create daily summaries
        daily_forecasts = []
        for date_str, data in sorted(daily_data.items()):
            daily_forecasts.append({
                'date': date_str,
                'max_temp': max(data['temperatures']),
                'min_temp': min(data['temperatures']),
                'avg_temp': sum(data['temperatures']) / len(data['temperatures']),
                'avg_humidity': sum(data['humidity']) / len(data['humidity']),
                'avg_wind_speed': sum(data['wind_speeds']) / len(data['wind_speeds']),
                'description': max(set(data['descriptions']), key=data['descriptions'].count)
            })
        
        return daily_forecasts
    
    def _get_mock_current_weather(self, location: str) -> Dict:
        """Return mock current weather data"""
        location_weather = {
            'jaipur': {'temp': 28, 'desc': 'clear sky', 'humidity': 45},
            'hyderabad': {'temp': 26, 'desc': 'partly cloudy', 'humidity': 60},
            'vizag': {'temp': 24, 'desc': 'overcast clouds', 'humidity': 75},
            'visakhapatnam': {'temp': 24, 'desc': 'overcast clouds', 'humidity': 75}
        }
        
        weather_data = location_weather.get(
            location.lower(), 
            {'temp': 25, 'desc': 'partly cloudy', 'humidity': 55}
        )
        
        return {
            'location': location.title(),
            'country': 'IN',
            'temperature': weather_data['temp'],
            'feels_like': weather_data['temp'] + 2,
            'humidity': weather_data['humidity'],
            'description': weather_data['desc'],
            'main': weather_data['desc'].split()[0].title(),
            'wind_speed': 3.5,
            'timestamp': datetime.now().isoformat(),
            'source': 'mock_data'
        }
    
    def _get_mock_forecast(self, location: str, days: int) -> Dict:
        """Return mock forecast data"""
        base_temp = self._get_mock_current_weather(location)['temperature']
        
        daily_forecasts = []
        for i in range(days):
            date = (datetime.now().date() + timedelta(days=i)).isoformat()
            temp_variation = [-2, 1, -1, 2, 0][i % 5]
            
            daily_forecasts.append({
                'date': date,
                'max_temp': base_temp + temp_variation + 3,
                'min_temp': base_temp + temp_variation - 2,
                'avg_temp': base_temp + temp_variation,
                'avg_humidity': 55 + (i * 5),
                'avg_wind_speed': 3.5,
                'description': ['clear sky', 'partly cloudy', 'overcast clouds', 'light rain', 'clear sky'][i % 5]
            })
        
        return {
            'location': location.title(),
            'country': 'IN',
            'forecast_days': days,
            'daily_forecasts': daily_forecasts,
            'timestamp': datetime.now().isoformat(),
            'source': 'mock_data'
        }
    
    def get_weather_advice(self, weather_data: Dict) -> str:
        """Generate weather-based advice for planning"""
        if not weather_data:
            return "Weather information not available."
        
        current = weather_data.get('daily_forecasts', [{}])[0] if 'daily_forecasts' in weather_data else weather_data
        
        temp = current.get('temperature', current.get('avg_temp', 25))
        desc = current.get('description', 'clear')
        
        advice = []
        
        if temp > 30:
            advice.append("Hot weather expected - plan indoor activities during peak hours")
        elif temp < 15:
            advice.append("Cool weather - carry warm clothing")
        
        if 'rain' in desc.lower():
            advice.append("Rain expected - carry umbrella and plan indoor alternatives")
        elif 'clear' in desc.lower():
            advice.append("Clear skies - perfect for outdoor activities")
        
        return "; ".join(advice) if advice else "Pleasant weather conditions expected"