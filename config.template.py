"""
Configuration module for SmartThings Controller (TEMPLATE).

This is a template of the config.py file. Copy this to config.py
and update the DEFAULT_TOKEN with your SmartThings API token.

NOTE: config.py is excluded from git in .gitignore to prevent
accidentally committing your API token.
"""

import os

# SmartThings API token
# Precedence:
# 1. Environment variable SMARTTHINGS_TOKEN
# 2. Value in this file
DEFAULT_TOKEN = "YOUR_SMARTTHINGS_API_TOKEN"

# Get the token from environment variable or use the default
def get_token():
    """Get the SmartThings API token from environment or default."""
    return os.environ.get('SMARTTHINGS_TOKEN', DEFAULT_TOKEN)

# Directory for storing device collections
COLLECTIONS_DIR = os.path.expanduser("~/.smartthings/collections")
