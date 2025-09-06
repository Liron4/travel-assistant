"""
Weather Information Tool - LangChain Tool Definition

This module contains the weather information tool for the travel agent,
providing current weather and forecast data for travel destinations.
"""

import os
import requests
from datetime import datetime
from langchain_core.tools import tool

@tool
def get_weather_info(location: str, days: int = 3) -> str:
    """
    Get current weather and forecast for a travel destination.
    
    Args:
        location: City name or 'city, country' format
        days: Number of forecast days (1-5, default 3)
    
    Returns:
        Weather information including current conditions and forecast
    """
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            return "Weather service unavailable - API key not configured"
        
        # Get coordinates first
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct"
        geo_params = {"q": location, "limit": 1, "appid": api_key}
        geo_response = requests.get(geo_url, params=geo_params, timeout=10)
        
        if not geo_response.ok or not geo_response.json():
            return f"Location '{location}' not found"
        
        geo_data = geo_response.json()[0]
        lat, lon = geo_data["lat"], geo_data["lon"]
        city_name = geo_data.get("name", location)
        country = geo_data.get("country", "")
        
        # Get current weather and forecast
        weather_url = "https://api.openweathermap.org/data/2.5/forecast"
        weather_params = {
            "lat": lat,
            "lon": lon,
            "appid": api_key,
            "units": "metric"
        }
        weather_response = requests.get(weather_url, params=weather_params, timeout=10)
        
        if not weather_response.ok:
            return f"Weather data unavailable for {location}"
        
        data = weather_response.json()
        
        # Process current and forecast data
        current = data["list"][0]
        temp = current["main"]["temp"]
        feels_like = current["main"]["feels_like"]
        humidity = current["main"]["humidity"]
        description = current["weather"][0]["description"].title()
        wind_speed = current["wind"]["speed"]
        
        result = f"🌍 Weather for {city_name}"
        if country:
            result += f", {country}"
        result += f"\n\n🌡️ Current: {temp}°C (feels like {feels_like}°C)\n"
        result += f"☁️ Conditions: {description}\n"
        result += f"💨 Wind: {wind_speed} m/s\n"
        result += f"💧 Humidity: {humidity}%\n\n"
        
        # Add forecast
        result += f"📅 {days}-Day Forecast:\n"
        unique_days = {}
        for item in data["list"][:days*8]:  # 8 forecasts per day
            date = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")
            if date not in unique_days:
                temp_day = item["main"]["temp"]
                desc_day = item["weather"][0]["description"].title()
                unique_days[date] = f"• {date}: {temp_day}°C, {desc_day}"
        
        for forecast in list(unique_days.values())[:days]:
            result += f"{forecast}\n"
        
        return result
        
    except requests.RequestException:
        return f"Network error while fetching weather for {location}"
    except Exception as e:
        return f"Error getting weather data: {str(e)}"


# Weather tool for easy importing
WEATHER_TOOLS = [get_weather_info]
