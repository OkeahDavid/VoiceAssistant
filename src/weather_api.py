"""
Weather API Integration
Handles communication with the weather API
"""
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class WeatherAPI:
    def __init__(self, api_url: str = "https://api.responsible-nlp.net/weather.php"):
        """
        Initialize Weather API client
        
        Args:
            api_url: Base URL for the weather API
        """
        self.api_url = api_url
        
    def get_weather(self, place: str) -> Optional[Dict]:
        """
        Get weather forecast for a place
        
        Args:
            place: City/location name
            
        Returns:
            Dictionary containing weather data or None if error
        """
        try:
            response = requests.post(self.api_url, data={"place": place})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather: {e}")
            return None
    
    def get_weather_for_day(self, place: str, day: str) -> Optional[Dict]:
        """
        Get weather for a specific day
        
        Args:
            place: City/location name
            day: Day name (e.g., "monday", "tuesday") or "today", "tomorrow"
            
        Returns:
            Weather data for that day or None
        """
        weather_data = self.get_weather(place)
        if not weather_data or "forecast" not in weather_data:
            return None
        
        # Normalize day name
        day = day.lower()
        
        # Handle "today" and "tomorrow"
        if day == "today":
            day = datetime.now().strftime("%A").lower()
        elif day == "tomorrow":
            day = (datetime.now() + timedelta(days=1)).strftime("%A").lower()
        
        # Find the forecast for the requested day
        for forecast in weather_data["forecast"]:
            if forecast["day"].lower() == day:
                return {
                    "place": weather_data["place"],
                    "day": forecast["day"],
                    "temperature": forecast["temperature"],
                    "weather": forecast["weather"]
                }
        
        return None
    
    def will_it_rain(self, place: str, day: Optional[str] = None) -> bool:
        """
        Check if it will rain on a specific day
        
        Args:
            place: City/location name
            day: Day name or None for any day in forecast
            
        Returns:
            True if rain is forecasted, False otherwise
        """
        if day:
            weather = self.get_weather_for_day(place, day)
            if weather:
                return "rain" in weather["weather"].lower()
            return False
        else:
            weather_data = self.get_weather(place)
            if not weather_data or "forecast" not in weather_data:
                return False
            
            # Check if any day has rain
            for forecast in weather_data["forecast"]:
                if "rain" in forecast["weather"].lower():
                    return True
            return False
    
    def format_weather_response(self, weather_data: Dict) -> str:
        """
        Format weather data into a human-readable response
        
        Args:
            weather_data: Weather data dictionary
            
        Returns:
            Formatted string
        """
        if not weather_data:
            return "I couldn't retrieve the weather information."
        
        if "forecast" in weather_data:
            # Full forecast
            place = weather_data["place"]
            response = f"Here's the weather forecast for {place}:\n"
            for forecast in weather_data["forecast"]:
                day = forecast["day"].capitalize()
                temp_min = forecast["temperature"]["min"]
                temp_max = forecast["temperature"]["max"]
                weather = forecast["weather"]
                response += f"{day}: {weather}, temperature between {temp_min}°C and {temp_max}°C.\n"
            return response.strip()
        else:
            # Single day forecast
            day = weather_data.get("day", "").capitalize()
            place = weather_data.get("place", "")
            temp_min = weather_data["temperature"]["min"]
            temp_max = weather_data["temperature"]["max"]
            weather = weather_data["weather"]
            return f"On {day} in {place}, the weather will be {weather} with temperatures between {temp_min}°C and {temp_max}°C."


if __name__ == "__main__":
    # Test Weather API
    api = WeatherAPI()
    
    print("Testing Weather API...\n")
    
    # Test 1: Get weather for Marburg
    print("1. Weather in Marburg:")
    weather = api.get_weather("Marburg")
    if weather:
        print(api.format_weather_response(weather))
    
    print("\n2. Weather on Friday in Frankfurt:")
    weather = api.get_weather_for_day("Frankfurt", "friday")
    if weather:
        print(api.format_weather_response(weather))
    
    print("\n3. Will it rain in Marburg on Saturday?")
    will_rain = api.will_it_rain("Marburg", "saturday")
    print(f"Will it rain: {will_rain}")
