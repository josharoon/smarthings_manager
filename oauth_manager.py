"""
OAuth Manager for SmartThings API.

This module handles the OAuth 2.0 flow for SmartThings API authentication:
- Generating authorization URLs
- Handling the callback from SmartThings
- Exchanging the code for access and refresh tokens
- Storing tokens securely
- Refreshing access tokens when they expire

References:
- SmartThings OAuth documentation: https://developer.smartthings.com/docs/authorization/
"""

import os
import json
import time
import requests
from urllib.parse import urlencode
import config

# Constants for OAuth flow
AUTH_URL = "https://api.smartthings.com/oauth/authorize"
TOKEN_URL = "https://api.smartthings.com/oauth/token"
TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tokens.json")

# Define default scopes for the application
# Adjust these based on your application's needs
DEFAULT_SCOPES = [
    "r:devices:*",  # Read all devices
    "w:devices:*",  # Write to all devices
    "x:devices:*",  # Execute commands on all devices
    "r:scenes:*",   # Read all scenes
    "x:scenes:*",   # Execute scenes
    "r:locations:*" # Read all locations
]

def generate_auth_url(redirect_uri, scopes=None, state=None):
    """
    Generate the SmartThings OAuth authorization URL.
    
    Args:
        redirect_uri (str): The URI to redirect to after authorization
        scopes (list, optional): List of permission scopes to request. Defaults to DEFAULT_SCOPES.
        state (str, optional): A value to maintain state between the request and callback.
        
    Returns:
        str: The authorization URL to redirect the user to
    """
    if scopes is None:
        scopes = DEFAULT_SCOPES
        
    params = {
        'client_id': config.get_client_id(),
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'scope': ' '.join(scopes)
    }
    
    if state:
        params['state'] = state
        
    return f"{AUTH_URL}?{urlencode(params)}"

def exchange_code_for_tokens(code, redirect_uri):
    """
    Exchange the authorization code for access and refresh tokens.
    
    Args:
        code (str): The authorization code received from SmartThings
        redirect_uri (str): The redirect URI used in the authorization request
        
    Returns:
        dict: The token response containing access_token, refresh_token, etc.
    """
    client_id = config.get_client_id()
    client_secret = config.get_client_secret()
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri
    }
    
    response = requests.post(TOKEN_URL, headers=headers, data=data)
    
    if response.status_code != 200:
        raise Exception(f"Failed to exchange code for tokens: {response.text}")
        
    token_data = response.json()
    
    # Add current timestamp to the token data
    token_data['timestamp'] = time.time()
    
    # Store tokens securely
    save_tokens(token_data)
    
    return token_data

def save_tokens(token_data):
    """
    Save tokens to a file.
    
    Args:
        token_data (dict): The token data to save
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    
    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_data, f)
        
    # Set restrictive permissions
    os.chmod(TOKEN_FILE, 0o600)

def load_tokens():
    """
    Load tokens from the file.
    
    Returns:
        dict: The token data or None if file doesn't exist or is invalid
    """
    try:
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading tokens: {e}")
    
    return None

def refresh_access_token():
    """
    Refresh the access token using the refresh token.
    
    Returns:
        str: The new access token
    """
    token_data = load_tokens()
    
    if not token_data or 'refresh_token' not in token_data:
        raise Exception("No refresh token available. Please re-authenticate.")
    
    client_id = config.get_client_id()
    client_secret = config.get_client_secret()
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': token_data['refresh_token'],
        'client_id': client_id,
        'client_secret': client_secret
    }
    
    response = requests.post(TOKEN_URL, headers=headers, data=data)
    
    if response.status_code != 200:
        raise Exception(f"Failed to refresh access token: {response.text}")
    
    new_token_data = response.json()
    
    # Preserve the refresh token if not returned in response
    if 'refresh_token' not in new_token_data and 'refresh_token' in token_data:
        new_token_data['refresh_token'] = token_data['refresh_token']
    
    # Add current timestamp
    new_token_data['timestamp'] = time.time()
    
    # Store updated tokens
    save_tokens(new_token_data)
    
    return new_token_data['access_token']

def get_valid_access_token():
    """
    Get a valid access token, refreshing if necessary.
    
    Returns:
        str: A valid access token
    """
    token_data = load_tokens()
    
    if not token_data:
        raise Exception("No tokens available. Please authenticate first.")
    
    # Check if token is expired (considering a 5-minute buffer)
    current_time = time.time()
    token_age = current_time - token_data.get('timestamp', 0)
    expires_in = token_data.get('expires_in', 86400)  # Default to 24 hours
    
    # If token is expired or will expire in the next 5 minutes
    if token_age > (expires_in - 300):
        print("Access token expired or about to expire. Refreshing...")
        return refresh_access_token()
    
    return token_data['access_token']

def is_authenticated():
    """
    Check if we have valid authentication tokens.
    
    Returns:
        bool: True if we have tokens that appear valid, False otherwise
    """
    token_data = load_tokens()
    if not token_data:
        return False
    
    # Check if we have both required tokens
    if 'access_token' not in token_data or 'refresh_token' not in token_data:
        return False
    
    return True

def clear_tokens():
    """
    Clear stored tokens.
    """
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
        
def handle_webhook_callback(data):
    """
    Process the webhook callback data from SmartThings.
    
    This function is meant to be called from your webhook server when it 
    receives a callback with the OAuth code.
    
    Args:
        data (dict): The JSON data received in the webhook callback
        
    Returns:
        bool: True if authentication was successful, False otherwise
    """
    try:
        # Extract the code and state from the webhook data
        if data.get('lifecycle') == 'OAUTH_CALLBACK':
            code = data.get('oauthCallbackData', {}).get('code')
            redirect_uri = data.get('callbackUrls', {}).get('oauthCallback')
            
            if not code or not redirect_uri:
                print("Error: Missing code or redirect_uri in webhook data")
                return False
            
            # Exchange the code for tokens
            token_data = exchange_code_for_tokens(code, redirect_uri)
            return True
        return False
    except Exception as e:
        print(f"Error processing webhook callback: {e}")
        return False
