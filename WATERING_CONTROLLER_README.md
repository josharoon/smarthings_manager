# Weather-Based SmartThings Watering Controller

This module automatically controls your watering system based on weather forecasts from Open-Meteo.

## How It Works

1. The system fetches the latest weather forecast for your configured location
2. Based on the forecast for today, it:
   - If rain is expected: No watering rules are created
   - If hot weather (>25°C): Creates two watering rules - 20 minutes at 7 AM and 30 minutes at 10 PM
   - Otherwise: Creates one watering rule - 10 minutes at 7 AM
3. Any existing watering rules are deleted before new ones are created

## Setup

1. Configure your water switch device ID in `config.py`:
   ```python
   WATER_SWITCH_DEVICE_ID = "your-device-id-here"
   ```

2. Ensure your SmartThings token has the correct permissions:
   - `r:rules:*` - Read rules
   - `w:rules:*` - Write rules
   - `r:devices:*` - Read devices

3. Run the watering controller:
   ```bash
   python watering_controller.py
   ```

## Automation

To automate this process, add a cron job to run the script daily:

```bash
# Run daily at 5:00 AM
0 5 * * * cd /path/to/smartthings_controller && ./.venv/bin/python watering_controller.py >> watering.log 2>&1
```

## Troubleshooting

- Check `watering.log` for any errors
- Verify your SmartThings token has the required permissions
- Make sure your water switch device ID is correct
- Verify that the location ID in the script matches your SmartThings location
