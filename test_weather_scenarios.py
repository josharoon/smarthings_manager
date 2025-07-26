#!/usr/bin/env python3
"""
Test script for watering controller with simulated weather data.
"""

import json
from datetime import datetime, timedelta
from watering_controller import WateringController

def create_mock_forecast(rain_today=False, rain_in_3_days=False):
    """Create a mock weather forecast with specified rain conditions"""
    
    today = datetime.now().date()
    daily_forecast = []
    
    for i in range(7):  # 7-day forecast
        date = today + timedelta(days=i)
        date_str = date.isoformat()
        
        # Default good weather
        weather_code = 0  # Clear sky
        precip_prob = 0
        
        # Add rain based on parameters
        if i == 0 and rain_today:
            weather_code = 61  # Rain
            precip_prob = 50
        elif i == 2 and rain_in_3_days:  # Day 3
            weather_code = 61  # Rain
            precip_prob = 50
            
        daily_forecast.append({
            'date': date_str,
            'weather_code': weather_code,
            'temperature_max': 22,
            'temperature_min': 15,
            'precipitation_probability_max': precip_prob
        })
    
    return {
        'latitude': 51.4084,
        'longitude': -0.0241,
        'updated_at': datetime.now().isoformat(),
        'daily_forecast': daily_forecast
    }

def test_with_mock_forecast(scenario_name, rain_today=False, rain_in_3_days=False):
    """Test watering controller logic with mock forecast"""
    
    print(f"\n=== Testing Scenario: {scenario_name} ===")
    
    # Create mock forecast
    mock_forecast = create_mock_forecast(rain_today, rain_in_3_days)
    
    # Create controller
    controller = WateringController()
    
    # Test logic
    result = controller.test_weather_logic(mock_forecast)
    print(f"Weather Logic Result: {result}")
    
    return result

if __name__ == "__main__":
    print("Testing watering controller with different weather scenarios\n")
    
    # Scenario 1: Rain today
    test_with_mock_forecast("Rain Today", rain_today=True)
    
    # Scenario 2: Rain in 3 days
    test_with_mock_forecast("Rain in 3 Days", rain_in_3_days=True)
    
    # Scenario 3: No rain in next week
    test_with_mock_forecast("No Rain This Week")
