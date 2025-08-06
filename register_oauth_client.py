#!/usr/bin/env python3
"""
SmartThings API Client Registration Helper

This script helps you register your OAuth client with SmartThings
by providing the correct settings and instructions.
"""

import config
import webbrowser
import json

def print_registration_instructions():
    """Print detailed instructions for registering an OAuth client."""
    
    client_id = config.get_client_id()
    client_secret = config.get_client_secret()
    
    print("=== SmartThings API Client Registration Helper ===")
    print("\nTo use OAuth 2.0 with SmartThings, you need to register a client application.")
    print("Follow these steps:")
    
    print("\n1. Go to the SmartThings Developer Workspace:")
    print("   https://developer.smartthings.com/workspace/projects")
    
    print("\n2. Click 'Add Project' and select 'API Access'")
    
    print("\n3. Fill in the required information:")
    print("   - Project Name: 'SmartThings Controller' (or any name you prefer)")
    print("   - Description: 'Python application to control SmartThings devices'")
    
    print("\n4. In the OAuth section, add this exact redirect URI:")
    print("   http://localhost:8000/oauth/callback")
    
    print("\n5. For scopes, select all of the following:")
    for scope in [
        "r:devices:*",
        "w:devices:*",
        "x:devices:*",
        "r:scenes:*", 
        "x:scenes:*",
        "r:locations:*"
    ]:
        print(f"   - {scope}")
    
    print("\n6. Complete the registration process")
    
    print("\n7. After registration, copy the Client ID and Client Secret")
    print("   to your config.py file or set them as environment variables:")
    print("   export SMARTTHINGS_CLIENT_ID='your_client_id'")
    print("   export SMARTTHINGS_CLIENT_SECRET='your_client_secret'")
    
    print("\nCurrent Configuration:")
    print(f"Client ID: {client_id}")
    print(f"Client Secret: {'*' * 8 if client_secret else 'Not set'}")
    
    # Open the developer workspace in a browser
    choice = input("\nWould you like to open the SmartThings Developer Portal now? (y/n): ")
    if choice.lower() == 'y':
        print("Opening browser to SmartThings Developer Portal...")
        webbrowser.open("https://developer.smartthings.com/workspace/projects")
    
if __name__ == "__main__":
    print_registration_instructions()
