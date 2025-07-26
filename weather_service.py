#!/usr/bin/env python
"""
Fetches daily weather forecast data from the Open-Meteo API
and determines if it will rain tomorrow.
"""

import json
import os
from datetime import datetime, timedelta
import requests

# --- Configuration ---
# Location for Beckenham, UK
LATITUDE = 51.4084
LONGITUDE = -0.0241

# File to save the forecast data
OUTPUT_FILE = "weather_forecast.json"
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(PROJECT_DIR, OUTPUT_FILE)


def get_weather_forecast():
    """
    Fetches daily weather forecast data from the Open-Meteo API.

    Returns:
        dict: A dictionary containing the weather forecast data, or None on error.
    """
    print("Fetching 7-day weather forecast from Open-Meteo...")
    try:
        # The Open-Meteo API URL for a 7-day daily forecast
        # Request more detailed weather data for full forecast verification
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={LATITUDE}&longitude={LONGITUDE}"
            f"&daily=weather_code,precipitation_probability_max,temperature_2m_max,temperature_2m_min"
        )
        
        response = requests.get(url)
        # This will raise an exception if the request was not successful
        response.raise_for_status()
        
        print("Successfully fetched weather data.")
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Error: Could not fetch weather data from Open-Meteo API. {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def save_forecast_to_file(weather_data, filename="weather_forecast.json"):
    """
    Process weather data and save to file.
    
    Args:
        weather_data (dict): Raw weather data from the API
        filename (str): Name of file to save the processed forecast
        
    Returns:
        dict: Processed forecast data or None if processing fails
    """
    if not weather_data or 'daily' not in weather_data:
        print("No valid weather data to save.")
        return None
    
    # Check if required data is available
    required_fields = ['time', 'weather_code', 'temperature_2m_max', 'temperature_2m_min', 'precipitation_probability_max']
    for field in required_fields:
        if field not in weather_data['daily']:
            print(f"Missing required field in weather data: {field}")
            return None
    
    # Process the weather data into a more usable format
    daily_forecast = []
    
    # Extract the daily forecast data
    days = len(weather_data['daily']['time'])
    for i in range(days):
        daily_forecast.append({
            'date': weather_data['daily']['time'][i],
            'weather_code': weather_data['daily']['weather_code'][i],
            'temperature_max': weather_data['daily']['temperature_2m_max'][i],
            'temperature_min': weather_data['daily']['temperature_2m_min'][i],
            'precipitation_probability_max': weather_data['daily']['precipitation_probability_max'][i],
        })
    
    # Create a structured forecast object
    forecast = {
        'latitude': weather_data['latitude'],
        'longitude': weather_data['longitude'],
        'updated_at': datetime.now().isoformat(),
        'daily_forecast': daily_forecast
    }
    
    # Save the forecast to file
    try:
        with open(os.path.join(PROJECT_DIR, filename), 'w') as f:
            json.dump(forecast, f, indent=2)
        print(f"Weather forecast saved to {filename}")
    except Exception as e:
        print(f"Error saving forecast to file: {e}")
        return None
        
    return forecast


def interpret_weather_code(code):
    """
    Interprets the WMO weather code to determine if it indicates rain.
    
    Args:
        code (int): The WMO weather code
        
    Returns:
        bool: True if the weather code indicates rain, False otherwise
    """
    # Weather codes from Open-Meteo API
    # 51-59: Drizzle, 61-69: Rain, 80-82: Rain showers, 95-99: Thunderstorm
    rain_codes = list(range(51, 70)) + list(range(80, 83)) + list(range(95, 100))
    return code in rain_codes


def will_rain_tomorrow():
    """
    Checks if it's likely to rain tomorrow based on the saved forecast data.
    
    Returns:
        tuple: (bool, str) - Whether it will rain and a descriptive message
    """
    try:
        if not os.path.exists(OUTPUT_PATH):
            print("No weather forecast data found. Fetching fresh data...")
            weather_data = get_weather_forecast()
            if weather_data:
                forecast = save_forecast_to_file(weather_data)
                if not forecast:
                    return False, "Could not process weather data"
            else:
                return False, "Could not fetch weather data"
        
        # Read the saved forecast data
        with open(OUTPUT_PATH, 'r') as f:
            forecast = json.load(f)
        
        # Check if the data is current (less than 24 hours old)
        last_updated = datetime.fromisoformat(forecast['updated_at'])
        now = datetime.now()
        time_diff = now - last_updated
        
        # If data is older than 6 hours, fetch fresh data
        if time_diff.total_seconds() > 21600:  # 6 hours in seconds
            print("Weather data is outdated. Fetching fresh data...")
            weather_data = get_weather_forecast()
            if weather_data:
                forecast = save_forecast_to_file(weather_data)
                if not forecast:
                    return False, "Could not process updated weather data"
        
        # Get tomorrow's date in the format used by the API
        tomorrow = (datetime.now().date() + timedelta(days=1)).isoformat()
        
        # Find tomorrow's forecast
        for daily in forecast['daily_forecast']:
            if daily['date'] == tomorrow:
                weather_code = daily['weather_code']
                precip_prob = daily.get('precipitation_probability_max', 0)
                
                rain_predicted = interpret_weather_code(weather_code)
                high_probability = precip_prob >= 30  # Consider 30% or higher as significant rain chance
                
                if rain_predicted or high_probability:
                    reason = "weather conditions" if rain_predicted else "precipitation probability"
                    return True, f"Rain is expected tomorrow based on {reason}. Weather code: {weather_code}, Precipitation probability: {precip_prob}%"
                else:
                    return False, f"No rain expected tomorrow. Weather code: {weather_code}, Precipitation probability: {precip_prob}%"
        
        return False, "Could not find tomorrow's forecast in the data"
        
    except Exception as e:
        return False, f"Error checking rain forecast: {e}"


def get_weather_description(code):
    """Convert WMO weather code to human-readable description"""
    weather_descriptions = {
        0: "Clear sky",
        1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        56: "Light freezing drizzle", 57: "Dense freezing drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        66: "Light freezing rain", 67: "Heavy freezing rain",
        71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
        77: "Snow grains",
        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
        85: "Slight snow showers", 86: "Heavy snow showers",
        95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail"
    }
    return weather_descriptions.get(code, f"Unknown ({code})")


if __name__ == "__main__":
    # Always fetch fresh forecast data when run directly
    weather_data = get_weather_forecast()
    if weather_data:
        forecast = save_forecast_to_file(weather_data)
        
        if forecast:
            # Display full 7-day forecast
            print("\n--- 7-DAY WEATHER FORECAST ---")
            print(f"Location: {forecast['latitude']}, {forecast['longitude']}")
            print(f"Last updated: {forecast['updated_at']}")
            print("\nDAILY FORECAST:")
            print("-" * 80)
            print(f"{'DATE':<12} {'TEMP MIN/MAX':<15} {'PRECIP %':<10} {'CONDITION'}")
            print("-" * 80)
            
            for day in forecast['daily_forecast']:
                date = day['date']
                temp_min = day.get('temperature_min', 'N/A')
                temp_max = day.get('temperature_max', 'N/A')
                precip = day.get('precipitation_probability_max', 'N/A')
                weather_code = day['weather_code']
                condition = get_weather_description(weather_code)
                
                # Format the output row
                temp_range = f"{temp_min}°C / {temp_max}°C" if temp_min != 'N/A' else 'N/A'
                precip_str = f"{precip}%" if precip != 'N/A' else 'N/A'
                
                print(f"{date:<12} {temp_range:<15} {precip_str:<10} {condition}")
        else:
            print("Failed to process weather forecast data.")
    
    # Check if it will rain tomorrow
    will_rain, message = will_rain_tomorrow()
    print(f"\nRain prediction for tomorrow: {'Yes' if will_rain else 'No'}")
    print(message)
