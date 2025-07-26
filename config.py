"""
Configuration module for SmartThings Controller.

This module provides configuration settings for the SmartThings Controller.
The token should be set via environment variable, but a default is provided here.
"""

import os

# SmartThings API token
# Precedence:
# 1. Environment variable SMARTTHINGS_TOKEN
# 2. Value in this file
DEFAULT_TOKEN = "7b1d7a5b-aec8-4e04-a7c7-e7e56763a1fe"

# Get the token from environment variable or use the default
def get_token():
    """Get the SmartThings API token from environment or default."""
    return os.environ.get('SMARTTHINGS_TOKEN', DEFAULT_TOKEN)

# Directory for storing device collections
COLLECTIONS_DIR = os.path.expanduser("~/.smartthings/collections")

# Water switch device ID for the watering controller
# Replace with your actual water switch device ID
WATER_SWITCH_DEVICE_ID = "15e4656c-34c1-46cb-9cc2-2a68eb45cd85"
