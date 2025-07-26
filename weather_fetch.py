#!/usr/bin/env python
"""
Fetches daily weather forecast data from the Open-Meteo API
and saves it to a JSON file for use by other scripts in the project.
"""

import json
import os
from datetime import datetime
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
        # We request the weather_code to simplify determining the weather conditions.
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={LATITUDE}&longitude={LONGITUDE}&daily=weather_code"
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


def save_forecast_to_file(forecast_data):
    """
    Saves the processed weather forecast to a JSON file.

    Args:
        forecast_data (dict): The weather forecast data to save.
    """
    if not forecast_data or 'daily' not in forecast_data:
        print("No forecast data to save.")
        return

    try:
        # Create a more structured and easy-to-use format
        processed_forecast = {
            "latitude": forecast_data.get("latitude"),
            "longitude": forecast_data.get("longitude"),
            "updated_at": datetime.now().isoformat(),
            "daily_forecast": []
        }
        
        # Combine the time and weather_code lists into a list of daily objects
        daily_data = forecast_data['daily']
        for i, date in enumerate(daily_data.get('time', [])):
            processed_forecast["daily_forecast"].append({
                "date": date,
                "weather_code": daily_data['weather_code'][i]
            })

        # Save the structured data to the output file
        with open(OUTPUT_PATH, 'w') as f:
            json.dump(processed_forecast, f, indent=4)
            
        print(f"Successfully saved weather forecast to: {OUTPUT_PATH}")

    except (IOError, KeyError, TypeError) as e:
        print(f"Error: Could not save forecast data to file. {e}")


if __name__ == "__main__":
    weather_data = get_weather_forecast()
    if weather_data:
        save_forecast_to_file(weather_data)
