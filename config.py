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
DEFAULT_TOKEN = "6fe689cd-dc58-45d1-8ebe-04f8d9ec71a5"

# Get the token from environment variable or use the default
def get_token():
    """Get the SmartThings API token from environment or default."""
    return os.environ.get('SMARTTHINGS_TOKEN', DEFAULT_TOKEN)

# Directory for storing device collections
COLLECTIONS_DIR = os.path.expanduser("~/.smartthings/collections")
