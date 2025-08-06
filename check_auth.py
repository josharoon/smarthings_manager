#!/usr/bin/env python3
"""
Test OAuth Authentication for SmartThings Controller.

This script checks if valid OAuth tokens are available and displays their status.
"""

import oauth_manager
import json
import sys
from datetime import datetime, timedelta

def main():
    """
    Check authentication status and display token information.
    """
    print("=== SmartThings OAuth Authentication Status ===\n")
    
    if not oauth_manager.is_authenticated():
        print("❌ Not authenticated.")
        print("Please run setup_oauth.py to authenticate with SmartThings.")
        sys.exit(1)
    
    # Load token data
    token_data = oauth_manager.load_tokens()
    
    if not token_data:
        print("❌ Token file exists but is invalid or empty.")
        sys.exit(1)
    
    # Calculate token age and expiry
    timestamp = token_data.get('timestamp', 0)
    creation_time = datetime.fromtimestamp(timestamp)
    expires_in = token_data.get('expires_in', 86400)  # Default to 24 hours
    expiry_time = creation_time + timedelta(seconds=expires_in)
    now = datetime.now()
    
    print("✅ Authentication is set up correctly.")
    print(f"\nAccess Token: {token_data.get('access_token', '')[:10]}...{token_data.get('access_token', '')[-5:] if token_data.get('access_token') else ''}")
    print(f"Refresh Token: {token_data.get('refresh_token', '')[:5]}...{token_data.get('refresh_token', '')[-5:] if token_data.get('refresh_token') else ''}")
    print(f"\nToken created: {creation_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Token expires: {expiry_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if token is expired
    if now > expiry_time:
        print("\n⚠️ Access token has expired!")
        choice = input("Do you want to refresh the token now? (y/n): ")
        if choice.lower() == 'y':
            try:
                new_token = oauth_manager.refresh_access_token()
                print("\n✅ Token refreshed successfully.")
                print(f"New access token: {new_token[:10]}...{new_token[-5:]}")
            except Exception as e:
                print(f"\n❌ Failed to refresh token: {e}")
    else:
        time_left = expiry_time - now
        hours, remainder = divmod(time_left.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        print(f"\nAccess token valid for: {int(hours)} hours, {int(minutes)} minutes, {int(seconds)} seconds")
    
    print("\nYou can now use the SmartThings Controller with OAuth authentication.")

if __name__ == "__main__":
    main()
