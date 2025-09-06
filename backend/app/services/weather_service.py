import os
import requests
from typing import Dict, Any

def get_current_weather(location: str) -> Dict[str, Any]:
    """
    Get current weather information for a specific location using OpenWeatherMap API
    
    Args:
        location: The location to get weather for
    
    Returns:
        Dictionary containing weather information or error details
    """
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            return {
                "error": "Weather service is not configured. Please set up an OpenWeatherMap API key."
            }
        
        # OpenWeatherMap API call
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            "success": True,
            "location": data["name"],
            "country": data["sys"]["country"],
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"],
            "formatted": f"""Current weather in {data['name']}, {data['sys']['country']}:
Temperature: {data['main']['temp']}°C (feels like {data['main']['feels_like']}°C)
Conditions: {data['weather'][0]['description']}
Humidity: {data['main']['humidity']}%
Wind Speed: {data['wind']['speed']} m/s"""
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "error": f"Sorry, I couldn't fetch weather data for {location}. Error: {str(e)}"
        }
    except KeyError as e:
        return {
            "error": f"Sorry, I couldn't find weather data for {location}. Please check the location name."
        }
    except Exception as e:
        return {
            "error": f"An error occurred while fetching weather data: {str(e)}"
        }
