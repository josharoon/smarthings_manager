#!/usr/bin/env python3
"""
Daily watering controller script to be run by cron.
Updates watering rules based on current weather forecast.
"""

import sys
import logging
from datetime import datetime
from watering_controller import WateringController, test_api_access

# Configure logging
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/media/josh/data1/smarrthings_controller/watering.log')
    ]
)
logger = logging.getLogger(__name__)

def run_daily_update():
    """Run daily update of watering rules based on weather forecast"""
    
    logger.info("=== SmartThings Watering Controller - Daily Update ===")
    logger.info(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test API access first
    if not test_api_access():
        logger.error("Failed to access SmartThings API. Cannot continue.")
        return False
    
    # Initialize controller and run
    controller = WateringController()
    
    if not controller.switch_device_id:
        logger.error("No water switch device ID configured. Cannot continue.")
        logger.error("Please set WATER_SWITCH_DEVICE_ID in config.py")
        return False
    
    # Show existing rules
    existing_rules = controller.get_existing_rules()
    
    # Create new rules based on weather
    success = controller.create_rules_based_on_weather()
    
    if success:
        logger.info("Daily watering rules update completed successfully")
    else:
        logger.error("Daily watering rules update failed")
    
    return success

if __name__ == "__main__":
    run_daily_update()
