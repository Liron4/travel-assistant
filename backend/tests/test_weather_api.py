import pytest
import os
import requests
from unittest.mock import patch, MagicMock
from app.services.weather_service import get_current_weather
from app.services.llm_service import get_weather


class TestWeatherAPI:
    """Essential tests for weather functionality"""
    
    def test_openweather_api_key_exists(self):
        """Test that OpenWeather API key is configured"""
        api_key = os.getenv("OPENWEATHER_API_KEY")
        assert api_key is not None, "OPENWEATHER_API_KEY environment variable is not set"
        assert api_key != "your_openweather_api_key_here", "Please set a valid OpenWeather API key"
        assert len(api_key) > 10, "API key seems too short to be valid"
    
    @patch('requests.get')
    def test_weather_service_success(self, mock_get):
        """Test successful weather API response"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "name": "Paris",
            "sys": {"country": "FR"},
            "main": {
                "temp": 15.5,
                "feels_like": 14.2,
                "humidity": 65
            },
            "weather": [{"description": "few clouds"}],
            "wind": {"speed": 3.2}
        }
        mock_get.return_value = mock_response
        
        result = get_current_weather("Paris")
        
        # Verify the API was called with correct parameters
        expected_url = f"http://api.openweathermap.org/data/2.5/weather?q=Paris&appid={os.getenv('OPENWEATHER_API_KEY')}&units=metric"
        mock_get.assert_called_once_with(expected_url, timeout=10)
        
        # Verify the response format
        assert result["success"] is True
        assert "Current weather in Paris, FR:" in result["formatted"]
        assert "15.5°C" in result["formatted"]
        assert "few clouds" in result["formatted"]
    
    @patch('requests.get')
    def test_weather_service_api_error(self, mock_get):
        """Test weather API error handling"""
        # Mock API error
        mock_get.side_effect = requests.exceptions.RequestException("API Error")
        
        result = get_current_weather("InvalidCity")
        
        assert "error" in result
        assert "Sorry, I couldn't fetch weather data" in result["error"]
        assert "InvalidCity" in result["error"]
    
    @patch('requests.get')
    def test_weather_service_invalid_location(self, mock_get):
        """Test handling of invalid location"""
        # Mock response with missing data
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {}  # Empty response
        mock_get.return_value = mock_response
        
        result = get_current_weather("NonExistentCity")
        
        assert "error" in result
        assert "Sorry, I couldn't find weather data" in result["error"]
        assert "NonExistentCity" in result["error"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
