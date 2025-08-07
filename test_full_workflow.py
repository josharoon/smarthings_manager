#!/usr/bin/env python3
"""
Dry-run test of the watering controller.
This script tests the full workflow without actually creating or deleting rules.
"""

from watering_controller import WateringController
import json
from datetime import datetime

def test_full_workflow():
    """Test the full workflow with the current weather data"""
    
    print("\n=== Watering Controller Full Workflow Test ===")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    controller = WateringController()
    
    # Step 1: Check API access
    print("\nStep 1: Testing API access...")
    from watering_controller import test_api_access
    import config
    token = config.get_token()
    location_id = config.LOCATION_ID if hasattr(config, 'LOCATION_ID') else None
    if not test_api_access(token, location_id):
        print("API access test failed. Cannot continue.")
        return
    
    # Step 2: Check existing rules
    print("\nStep 2: Getting existing rules...")
    existing_rules = controller.get_existing_rules()
    
    # Step 3: Test weather logic
    print("\nStep 3: Testing weather logic...")
    weather_result = controller.test_weather_logic()
    print(f"Weather logic result: {weather_result}")
    
    # Step 4: Test rule template loading
    print("\nStep 4: Testing rule template loading...")
    from watering_controller import LIGHT_WATERING_TEMPLATE, NORMAL_WATERING_TEMPLATE
    
    print(f"Light watering template: {LIGHT_WATERING_TEMPLATE}")
    light_rule = controller._load_rule_template(LIGHT_WATERING_TEMPLATE, "Test Light Rule")
    print(f"Light rule loaded successfully: {'Yes' if light_rule else 'No'}")
    if light_rule:
        print(f"Rule name: {light_rule.get('name')}")
        print(f"Device ID in rule: {light_rule.get('actions', [])[0].get('then', [])[0].get('command', {}).get('devices', [])}")
    
    print(f"\nNormal watering template: {NORMAL_WATERING_TEMPLATE}")
    normal_rule = controller._load_rule_template(NORMAL_WATERING_TEMPLATE, "Test Normal Rule")
    print(f"Normal rule loaded successfully: {'Yes' if normal_rule else 'No'}")
    if normal_rule:
        print(f"Rule name: {normal_rule.get('name')}")
        print(f"Device ID in rule: {normal_rule.get('actions', [])[0].get('then', [])[0].get('command', {}).get('devices', [])}")
    
    print("\nTest completed. No rules were created or deleted.")

if __name__ == "__main__":
    test_full_workflow()
