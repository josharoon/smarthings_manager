#!/usr/bin/env python3
"""
OAuth Configuration Validator

This script verifies your OAuth client configuration by making test requests
to the SmartThings API. Use this to troubleshoot 403 Forbidden errors.
"""

import requests
import json
import sys
import config

def test_client_configuration():
    """Test the OAuth client configuration by attempting to make API requests."""
    
    client_id = config.get_client_id()
    client_secret = config.get_client_secret()
    
    print("=== SmartThings OAuth Configuration Validator ===")
    print(f"Client ID: {client_id}")
    print(f"Client Secret: {'*' * 8}")
    
    # Test 1: Check if we can make a basic request to SmartThings API
    print("\nTest 1: Checking SmartThings API availability...")
    try:
        response = requests.get("https://api.smartthings.com/")
        print(f"  Status: {response.status_code}")
        print("  API endpoint is reachable.")
    except Exception as e:
        print(f"  Error: Could not connect to SmartThings API: {e}")
    
    # Test 2: Check if the client ID is valid
    # We'll attempt to start an OAuth flow (it will fail without proper redirect)
    # but the error should be different than 403 if the client ID is valid
    print("\nTest 2: Checking Client ID validity...")
    auth_url = "https://api.smartthings.com/oauth/authorize"
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': 'http://localhost:8000/oauth/callback',
        'scope': 'r:devices:*'
    }
    
    try:
        response = requests.get(auth_url, params=params, allow_redirects=False)
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 403:
            print("  Error: Client ID appears to be invalid or not configured correctly.")
            print("  The SmartThings API returned a 403 Forbidden error.")
            print("  Please check your client ID and make sure it's correctly registered in the Developer Portal.")
        elif response.status_code == 302 or response.status_code == 301:
            print("  Success: Client ID appears to be valid.")
            print("  The request was properly redirected to the authorization page.")
        else:
            print(f"  Unexpected response code: {response.status_code}")
            print("  This might indicate an issue with the SmartThings API or your configuration.")
    except Exception as e:
        print(f"  Error during client ID test: {e}")
    
    # Test 3: Check common redirect URI issues
    print("\nTest 3: Common redirect URI problems...")
    print("  Important: Your redirect URI must be EXACTLY as registered in the Developer Portal.")
    print("  Current redirect URI: http://localhost:8000/oauth/callback")
    print("  Common issues:")
    print("  - Trailing slashes (e.g., /oauth/callback/ vs /oauth/callback)")
    print("  - HTTP vs HTTPS")
    print("  - Different port number")
    print("  - Case sensitivity in some parts")
    print("  - Special characters that need encoding")
    
    print("\nNext steps:")
    print("1. Verify the redirect URI in your SmartThings Developer Portal matches EXACTLY:")
    print("   http://localhost:8000/oauth/callback")
    print("2. Ensure all requested scopes are allowed for your client application")
    print("3. Check if your application is properly registered and approved")
    
if __name__ == "__main__":
    test_client_configuration()
