#!/usr/bin/env python
"""
Controls SmartThings water switch based on weather forecast using the Rules API.
Creates and manages watering rules based on daily weather conditions.
"""

import json
import os
import requests
from datetime import datetime, timedelta
import config
from weather_service import get_weather_forecast, save_forecast_to_file, interpret_weather_code

# Configuration
RULE_NAME_PREFIX = "Auto Watering"  # Used to identify our rules
API_BASE_URL = "https://api.smartthings.com/v1"
RULES_ENDPOINT = f"{API_BASE_URL}/rules"
DEVICES_ENDPOINT = f"{API_BASE_URL}/devices"

# Paths to rule templates
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIGHT_WATERING_TEMPLATE = os.path.join(SCRIPT_DIR, "rule_template_light_watering.json")
NORMAL_WATERING_TEMPLATE = os.path.join(SCRIPT_DIR, "rule_template_normal_watering.json")

# Temperature threshold for "hot" day classification (in Celsius)
HOT_TEMP_THRESHOLD = 25.0

# Location ID - we need this for the Rules API
LOCATION_ID = "0af498bc-50f4-4dd1-88c5-6bfc2b30b317"

class WateringController:
    """Controls SmartThings water switch based on weather forecast using Rules API."""
    
    def __init__(self, token=None, switch_device_id=None):
        """
        Initialize the watering controller.
        
        Args:
            token (str): SmartThings API token. If None, will use config.py
            switch_device_id (str): Device ID of the water switch. If None, will use config.py
        """
        self.token = token or config.get_token()
        
        # Default to None until config is updated - we'll handle this gracefully
        self.switch_device_id = switch_device_id
        
        if hasattr(config, 'WATER_SWITCH_DEVICE_ID'):
            self.switch_device_id = switch_device_id or config.WATER_SWITCH_DEVICE_ID
            
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
    def _time_to_minutes(self, time_str):
        """
        Convert time string in "HH:MM" format to minutes since midnight.
        
        Args:
            time_str (str): Time in format "HH:MM"
            
        Returns:
            int: Minutes since midnight
        """
        hour, minute = map(int, time_str.split(':'))
        return hour * 60 + minute
        
    def _load_rule_template(self, template_path, rule_name):
        """
        Load a rule template from a JSON file and customize it.
        
        Args:
            template_path (str): Path to the rule template JSON file
            rule_name (str): Name for the rule
            
        Returns:
            dict: Rule data or None if failed
        """
        try:
            with open(template_path, 'r') as f:
                rule_data = json.load(f)
                
            # Customize the rule with provided name and device ID
            rule_data['name'] = rule_name
            
            # Replace device ID in all actions
            for action in rule_data.get('actions', []):
                for then_action in action.get('then', []):
                    if 'command' in then_action and 'devices' in then_action['command']:
                        then_action['command']['devices'] = [self.switch_device_id]
            
            return rule_data
        except Exception as e:
            print(f"Error loading rule template {template_path}: {e}")
            return None
    
    def get_existing_rules(self):
        """
        Fetch all existing watering rules.
        
        Returns:
            list: List of rule objects that match our naming pattern
        """
        try:
            print("Fetching existing watering rules...")
            url = f"{RULES_ENDPOINT}?locationId={LOCATION_ID}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            rules_data = response.json()
            if 'items' not in rules_data:
                print("No rules found or unexpected API response format.")
                return []
                
            rules = rules_data.get("items", [])
            watering_rules = []
            
            for rule in rules:
                if rule.get("name", "").startswith(RULE_NAME_PREFIX):
                    watering_rules.append({
                        "id": rule.get("id"),
                        "name": rule.get("name")
                    })
            
            if watering_rules:
                print(f"Found {len(watering_rules)} existing watering rules:")
                for rule in watering_rules:
                    print(f" - {rule['name']} (ID: {rule['id']})")
            else:
                print("No existing watering rules found.")
                
            return watering_rules
            
        except requests.exceptions.RequestException as e:
            print(f"Error getting existing rules: {e}")
            return []
    
    def delete_rules(self, rule_ids):
        """
        Delete specified rules.
        
        Args:
            rule_ids (list): List of rule IDs to delete
            
        Returns:
            bool: True if all deletions were successful
        """
        success = True
        for rule_id in rule_ids:
            try:
                # Include locationId in URL as per API docs
                url = f"{RULES_ENDPOINT}/{rule_id}?locationId={LOCATION_ID}"
                response = requests.delete(url, headers=self.headers)
                response.raise_for_status()
                print(f"Successfully deleted rule: {rule_id}")
                
            except Exception as e:
                print(f"Error deleting rule {rule_id}: {e}")
                success = False
                
        return success
        
    def create_watering_rule(self, name, start_time, duration_minutes):
        """
        Create a rule to water at specified time for specified duration.
        
        Args:
            name (str): Name for the rule
            start_time (str): Time in format "HH:MM"
            duration_minutes (int): Duration in minutes
            
        Returns:
            str: ID of created rule, or None if failed
        """
        if not self.switch_device_id:
            print("Error: Water switch device ID not specified. Cannot create rule.")
            return None
            
        try:
            # Calculate end time
            hour, minute = map(int, start_time.split(":"))
            end_hour, end_minute = divmod(hour * 60 + minute + duration_minutes, 60)
            end_hour %= 24  # Handle overflow to next day
            end_time = f"{end_hour:02d}:{end_minute:02d}"
            
            # Create rule JSON - structure matches the SmartThings Rules API format
            rule_data = {
                "name": name,
                "actions": [
                    {
                        "every": {
                            "specific": {
                                "daysOfWeek": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                                "reference": "Midnight",
                                "offset": {
                                    "value": {
                                        "integer": self._time_to_minutes(start_time)
                                    },
                                    "unit": "Minute"
                                },
                                "timeZoneId": "Europe/London"
                            },
                            "actions": [
                                {
                                    "command": {
                                        "devices": [self.switch_device_id],
                                        "commands": [
                                            {
                                                "component": "main",
                                                "capability": "switch",
                                                "command": "on"
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "every": {
                            "specific": {
                                "daysOfWeek": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                                "reference": "Midnight",
                                "offset": {
                                    "value": {
                                        "integer": self._time_to_minutes(end_time)
                                    },
                                    "unit": "Minute"
                                },
                                "timeZoneId": "Europe/London"
                            },
                            "actions": [
                                {
                                    "command": {
                                        "devices": [self.switch_device_id],
                                        "commands": [
                                            {
                                                "component": "main",
                                                "capability": "switch",
                                                "command": "off"
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
            
            # Send the request to create the rule - locationId in URL as per API docs
            url = f"{RULES_ENDPOINT}?locationId={LOCATION_ID}"
            response = requests.post(url, headers=self.headers, json=rule_data)
            response.raise_for_status()
            
            rule_id = response.json().get("id")
            print(f"Successfully created rule: {name} (ID: {rule_id})")
            return rule_id
            
        except Exception as e:
            print(f"Error creating watering rule: {e}")
            return None
            
    def check_rain_in_days(self, forecast, days_ahead):
        """
        Check if rain is predicted within specified days ahead.
        
        Args:
            forecast (dict): Weather forecast data
            days_ahead (int): Number of days to check ahead
            
        Returns:
            bool: True if rain is predicted within specified days
        """
        today = datetime.now().date()
        days_to_check = [today + timedelta(days=i) for i in range(days_ahead)]
        dates_to_check = [d.isoformat() for d in days_to_check]
        
        print(f"Checking for rain in the next {days_ahead} days:")
        try:
            for day in forecast['daily_forecast']:
                if day['date'] in dates_to_check:
                    weather_code = day['weather_code']
                    precip_prob = day.get('precipitation_probability_max', 0)
                    
                    rain_predicted = interpret_weather_code(weather_code)
                    high_probability = precip_prob >= 50  # 50% or higher probability
                    
                    print(f" - {day['date']}: Weather Code: {weather_code}, Precipitation: {precip_prob}%, "
                          f"Rain Predicted: {'Yes' if rain_predicted else 'No'}")
                    
                    # Consider it raining only if weather code indicates rain AND probability is high enough
                    if rain_predicted and high_probability:
                        return True
            
            return False
        except Exception as e:
            print(f"Error checking rain forecast: {e}")
            return False
    
    def create_rules_based_on_weather(self):
        """
        Create watering rules based on weather forecast.
        
        Returns:
            bool: True if rules were created successfully
        """
        # Get weather forecast
        weather_data = get_weather_forecast()
        if not weather_data:
            print("Failed to get weather forecast. Cannot create rules.")
            return False
            
        forecast = save_forecast_to_file(weather_data)
        if not forecast:
            print("Failed to process weather forecast. Cannot create rules.")
            return False
        
        # Delete any existing watering rules first
        existing_rules = self.get_existing_rules()
        if existing_rules:
            rule_ids = [rule["id"] for rule in existing_rules]
            self.delete_rules(rule_ids)
        
        # Create unique rule name with date
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # Decision logic based on our three scenarios:
        
        # Scenario 1: Rain expected today - no watering (all rules already removed)
        rain_today = self.check_rain_in_days(forecast, 1)  # Check today only
        if rain_today:
            print("Rain expected today. No watering rules created.")
            return True
            
        # Scenario 2: Rain expected within 3 days - water for 5 mins at 10am
        rain_in_3_days = self.check_rain_in_days(forecast, 3)  # Check next 3 days
        if rain_in_3_days:
            print("Rain expected within 3 days. Creating 5-minute watering rule at 10:00 AM.")
            rule_name = f"{RULE_NAME_PREFIX} - Light Watering {today_str}"
            rule_id = self.create_watering_rule(rule_name, "10:00", 5)
            return rule_id is not None
            
        # Scenario 3: Rain not expected this week - water for 10 mins at 10am
        print("No rain expected this week. Creating 10-minute watering rule at 10:00 AM.")
        rule_name = f"{RULE_NAME_PREFIX} - Normal Watering {today_str}"
        rule_id = self.create_watering_rule(rule_name, "10:00", 10)
        return rule_id is not None
    
    def test_weather_logic(self, mock_weather=None):
        """
        Test the weather-based decision logic without creating rules.
        
        Args:
            mock_weather (dict): Optional mock weather data for testing
        
        Returns:
            str: Description of what would happen based on the weather
        """
        if not mock_weather:
            # Get real weather data
            weather_data = get_weather_forecast()
            if not weather_data:
                return "Failed to get weather forecast."
                
            forecast = save_forecast_to_file(weather_data)
            if not forecast:
                return "Failed to process weather forecast."
        else:
            forecast = mock_weather
        
        # Decision logic simulation based on our three scenarios
        rain_today = self.check_rain_in_days(forecast, 1)
        if rain_today:
            return "Rain expected today. No watering rules would be created."
            
        rain_in_3_days = self.check_rain_in_days(forecast, 3)
        if rain_in_3_days:
            return "Rain expected within 3 days. Would create 5-minute watering rule at 10:00 AM."
            
        return "No rain expected this week. Would create 10-minute watering rule at 10:00 AM."
            
    def run(self):
        """Main entry point to update watering rules based on weather."""
        print(f"=== Running Watering Controller - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
        
        if not self.switch_device_id:
            print("ERROR: Water switch device ID not configured.")
            print("Please update config.py with your WATER_SWITCH_DEVICE_ID.")
            return False
            
        result = self.create_rules_based_on_weather()
        print(f"Watering rule update {'completed successfully' if result else 'failed'}")
        return result


def test_api_access():
    """
    Test access to the SmartThings Rules API.
    Returns:
        bool: True if access is successful, False otherwise.
    """
    # Use the token from config.py
    token = config.get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("Testing access to SmartThings Rules API...")
    print(f"Token: {token[:8]}...{token[-4:]}") # Show partial token for verification
    
    try:
        # Test the Rules API with locationId parameter
        url = f"{RULES_ENDPOINT}?locationId={LOCATION_ID}"
        print(f"API Endpoint: {url}")
        
        response = requests.get(url, headers=headers)
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            rules_data = response.json()
            rule_count = len(rules_data.get("items", []))
            print(f"✅ SUCCESS: Successfully accessed Rules API. Found {rule_count} rules.")
            return True
        elif response.status_code == 403:
            print(f"❌ ERROR: Access denied (403 Forbidden). Your token does not have the required permissions.")
            print("Please make sure your token has the 'r:rules:*' scope enabled.")
            print(f"Response body: {response.text}")
            return False
        else:
            print(f"❌ ERROR: Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: Failed to access Rules API: {e}")
        return False
        


if __name__ == "__main__":
    # First test API access
    if test_api_access():
        # Test the weather logic (dry run)
        controller = WateringController()
        test_result = controller.test_weather_logic()
        print("\n=== Weather Logic Test (Dry Run) ===")
        print(test_result)
        
        print("\nWould you like to proceed with creating/updating rules? (y/n)")
        choice = input().strip().lower()
        
        if choice == 'y':
            # Check if we have a water switch device ID
            if not hasattr(config, 'WATER_SWITCH_DEVICE_ID') or not config.WATER_SWITCH_DEVICE_ID:
                print("Before proceeding, please enter your water switch device ID:")
                device_id = input().strip()
                if device_id:
                    controller.switch_device_id = device_id
                    controller.run()
                else:
                    print("No device ID provided. Aborting.")
            else:
                controller.run()
        else:
            print("Operation cancelled.")
    else:
        print("Cannot proceed due to API access issues.")
