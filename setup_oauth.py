#!/usr/bin/env python3
"""
Setup OAuth Authentication for SmartThings Controller.

This script initiates the OAuth 2.0 authorization flow for SmartThings API.
It starts the OAuth login process and redirects to your webhook server
for handling the callback.

Run this script to authenticate your application with SmartThings.
"""

import sys
import webbrowser
import oauth_manager

def main():
    """
    Main function to set up OAuth authentication.
    """
    print("=== SmartThings OAuth Setup ===")
    
    # Check if already authenticated
    if oauth_manager.is_authenticated():
        print("\nYou already have valid authentication tokens.")
        choice = input("Do you want to re-authenticate? (y/n): ")
        
        if choice.lower() != 'y':
            print("Setup canceled. Using existing authentication.")
            return
        
        # Clear existing tokens
        oauth_manager.clear_tokens()
        print("Existing tokens cleared.")
    
    print("\nStarting authentication process...")
    print("A browser window will open. Please follow these steps:")
    print("1. Log in with your Samsung/SmartThings account if prompted.")
    print("2. Review and grant the requested permissions to the application.")
    print("3. Select the locations you want to authorize.")
    print("4. After successful authorization, your webhook server will receive the authentication code.")
    
    # Webhook server URL using your ngrok tunnel
    webhook_url = "https://c78ea69ef759.ngrok-free.app/oauth/callback"
    
    # Generate authorization URL
    state = "setup_" + oauth_manager.os.urandom(8).hex()
    auth_url = oauth_manager.generate_auth_url(
        redirect_uri=webhook_url,
        state=state
    )
    
    print(f"\nOpening authorization URL in your browser...")
    print(f"Authorization URL: {auth_url}")
    
    # Open browser to the authorization URL
    webbrowser.open(auth_url)
    
    print("\nAfter you complete the authorization process, your webhook server should")
    print("receive the OAuth callback. Once this happens, run your application.")
    
    print("\nNOTE: This script doesn't check for authentication success because")
    print("the callback will go to your webhook server instead of this script.")
    print("Your webhook server should handle saving the tokens using oauth_manager.exchange_code_for_tokens().")

if __name__ == "__main__":
    main()
