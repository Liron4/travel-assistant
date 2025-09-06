import os
import re
from langchain_openai import ChatOpenAI
from langchain.tools import tool
import requests

# Initialize the DeepSeek model via OpenRouter
def get_llm():
    """Initialize and return the DeepSeek LLM via OpenRouter"""
    return ChatOpenAI(
        model="openai/gpt-oss-20b:free",
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "http://localhost",
            "X-Title": "Travel Assistant",
        },
        temperature=0.7,
        max_tokens=2000
    )

@tool
def get_weather(location: str) -> str:
    """Get current weather information for a specific location. Use this when users ask about weather conditions."""
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            return "Weather service is not configured. Please set up an OpenWeatherMap API key."
        
        # OpenWeatherMap API call
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        weather_info = {
            "location": data["name"],
            "country": data["sys"]["country"],
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"]
        }
        
        return f"""Current weather in {weather_info['location']}, {weather_info['country']}:
Temperature: {weather_info['temperature']}°C (feels like {weather_info['feels_like']}°C)
Conditions: {weather_info['description']}
Humidity: {weather_info['humidity']}%
Wind Speed: {weather_info['wind_speed']} m/s"""
        
    except requests.exceptions.RequestException as e:
        return f"Sorry, I couldn't fetch weather data for {location}. Error: {str(e)}"
    except KeyError as e:
        return f"Sorry, I couldn't find weather data for {location}. Please check the location name."
    except Exception as e:
        return f"An error occurred while fetching weather data: {str(e)}"

def extract_location_from_weather_query(user_input: str) -> str:
    """Extract location from weather-related queries"""
    user_input_lower = user_input.lower()
    
    # Common patterns for location queries
    patterns = [
        r'weather (?:in|at|for|of) ([^?]+)',
        r'temperature (?:in|at|for|of) ([^?]+)',
        r'forecast (?:in|at|for|of) ([^?]+)',
        r'(?:how is|what is|what\'s) (?:the )?weather (?:like )?(?:in|at|for|of) ([^?]+)',
        r'(?:how is|what is|what\'s) (?:the )?temperature (?:in|at|for|of) ([^?]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, user_input_lower)
        if match:
            location = match.group(1).strip()
            # Clean up common words that might be included
            location = re.sub(r'\b(like|today|now|currently)\b', '', location).strip()
            return location
    
    # If no pattern matched, try to find location after common prepositions
    words = user_input.split()
    for i, word in enumerate(words):
        if word.lower() in ['in', 'at', 'for'] and i + 1 < len(words):
            # Take the next word(s) as location
            location_parts = []
            for j in range(i + 1, min(i + 3, len(words))):  # Take up to 2 words
                if words[j].lower() in ['?', 'today', 'now', 'currently', 'like']:
                    break
                location_parts.append(words[j].strip('?.,!'))
            if location_parts:
                return ' '.join(location_parts)
    
    return None

# Global LLM instance
_llm = None

def get_agent_response(user_input: str) -> str:
    """
    Get a response from the travel assistant
    
    Args:
        user_input: The user's message/question
    
    Returns:
        The agent's response as a string
    """
    global _llm
    
    try:
        # Initialize LLM if not already done
        if _llm is None:
            _llm = get_llm()
        
        # Check if user is asking for weather
        weather_keywords = ['weather', 'temperature', 'forecast', 'rain', 'sunny', 'cloudy', 'climate', 'conditions']
        if any(weather_word in user_input.lower() for weather_word in weather_keywords):
            location = extract_location_from_weather_query(user_input)
            
            if location:
                weather_info = get_weather(location)
                response = f"Let me get the current weather information for you!\n\n{weather_info}"
            else:
                response = "I'd be happy to help you with weather information! Could you please specify which location you'd like to know about? For example: 'What's the weather like in Paris?' or 'How's the temperature in Tokyo?'"
        
        else:
            # Handle general travel queries with the LLM
            system_prompt = """You are a helpful and knowledgeable Travel Assistant AI. Your role is to help users with all aspects of travel planning and travel-related questions.

Your capabilities include:
1. Providing travel advice and recommendations based on your knowledge
2. Helping with travel planning and itineraries  
3. Answering questions about destinations, cultures, and travel tips
4. Offering practical travel guidance
5. Getting real-time weather information when users ask about weather

Guidelines:
- Be friendly, helpful, and enthusiastic about travel
- Provide practical and actionable advice based on your training data
- If users ask about weather, suggest they ask specifically for weather information (e.g., "What's the weather like in Tokyo?")
- For current events or real-time information beyond weather, acknowledge that your knowledge has a cutoff date and suggest they check current sources
- Draw from your extensive knowledge of destinations, cultures, travel tips, and general travel advice
- Be encouraging and help users plan amazing trips

Remember: You have access to extensive travel knowledge and can provide real-time weather data when requested. Focus on being helpful with travel planning, destination advice, and general travel guidance."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
            
            response_obj = _llm.invoke(messages)
            response = response_obj.content
        
        return response
        
    except Exception as e:
        return f"I apologize, but I encountered an error while processing your request: {str(e)}. Please try rephrasing your question or try again later."
