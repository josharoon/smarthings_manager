# Weather-Based Watering System Implementation Plan

## Objective
Automate watering rules for a SmartThings water switch using the SmartThings Rules API, based on daily weather forecasts.

## API Investigation
- **SmartThings Rules API**
  - Endpoint: `https://api.smartthings.com/v1/rules`
  - Requires Personal Access Token (PAT) with appropriate scopes
  - Supports GET (list rules), POST (create rule), DELETE (remove rule)

## Process Logic
1. **Collect Weather Forecast**
   - Use `weather_service.py` to fetch and process the daily forecast
2. **Decide Watering Action**
   - If rain is forecasted today:
     - Do nothing (no watering rules created)
   - Else if sunny and hot (high temperature):
     - Create two rules:
       - 20-minute watering at 7:00 AM
       - 30-minute watering at 10:00 PM
   - Else (normal dry day):
     - Create one rule:
       - 10-minute watering at 7:00 AM
3. **Update Rules**
   - Delete previous day's watering rules
   - Create new rules as needed

## Module Design: `watering_controller.py`
- **Class: WateringController**
  - `__init__()` - Initialize with SmartThings token and water switch device ID
  - `get_existing_rules()` - Fetch all existing watering rules
  - `delete_rules(rule_ids)` - Delete specified rules
  - `create_watering_rule(name, start_time, duration)` - Create rule to turn on water for specified duration
  - `create_rules_based_on_weather()` - Main logic to determine which rules to create
  - `run()` - Main entry point

## Configuration
- Add `WATER_SWITCH_DEVICE_ID` to `config.py` and `config.template.py`

## Testing Plan
- Run script manually and verify rule creation/deletion in SmartThings app
- Test with mock weather data for rainy, hot, and normal conditions

## Automation
- Schedule daily run via cron:
  - Example: `0 5 * * * cd /path/to/smartthings_controller && ./.venv/bin/python watering_controller.py >> watering.log 2>&1`

## Documentation
- Add README section describing the watering automation logic, configuration, and troubleshooting steps

---
This plan documents the approach for integrating weather-based watering automation with SmartThings using the Rules API. Refer to this file for implementation and testing checkpoints.
