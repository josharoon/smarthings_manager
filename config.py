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

# Update these with the values from your SmartThings Developer Portal
# after registering your OAuth client
CLIENT_ID = "8fb08d03-3558-4137-bd10-2ad3d334aede"
CLIENT_SECRET ="c831168a-cd51-4c12-bfe1-98223f7ec482"

# Get the token from environment variable or use the default
def get_token():
    """Get the SmartThings API token from environment or default."""
    return os.environ.get('SMARTTHINGS_TOKEN', DEFAULT_TOKEN)

def get_client_id():
    """Get the SmartThings API client ID from environment or default."""
    return os.environ.get('SMARTTHINGS_CLIENT_ID', CLIENT_ID)

def get_client_secret():
    """Get the SmartThings API client secret from environment or default."""
    return os.environ.get('SMARTTHINGS_CLIENT_SECRET', CLIENT_SECRET)

# Directory for storing device collections
COLLECTIONS_DIR = os.path.expanduser("~/.smartthings/collections")

# Water switch device ID for the watering controller
# Replace with your actual water switch device ID
WATER_SWITCH_DEVICE_ID = "15e4656c-34c1-46cb-9cc2-2a68eb45cd85"

# Location ID for the watering controller
# Replace with your actual location ID
LOCATION_ID = "0af498bc-50f4-4dd1-88c5-6bfc2b30b317"
