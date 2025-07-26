#!/usr/bin/env python
"""
A simple script to test SmartThings API token validity.
"""
import asyncio
import aiohttp
import json
from pysmartthings import SmartThings

# Use the token from your main.py
from config import get_token
SMARTTHINGS_TOKEN = get_token()  # Get token from config

async def test_token():
    """Test if the SmartThings token is valid."""
    print("🔑 Testing SmartThings API token...")
    print(f"Token: {SMARTTHINGS_TOKEN[:5]}...{SMARTTHINGS_TOKEN[-5:]}")
    
    # Create a session with verbose logging
    headers = {
        "Authorization": f"Bearer {SMARTTHINGS_TOKEN}",
        "Accept": "application/json"
    }
    
    # Try multiple API endpoints to verify token
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            # First test with direct API call to SmartThings API
            print("\n1️⃣ Testing with direct API call...")
            async with session.get("https://api.smartthings.com/v1/devices") as response:
                print(f"Status: {response.status}")
                print(f"Headers: {response.headers}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"Success! Found {len(data.get('items', []))} devices")
                else:
                    error_text = await response.text()
                    print(f"Error response: {error_text}")
            
            # Now test with the pysmartthings library
            print("\n2️⃣ Testing with pysmartthings library...")
            api = SmartThings(request_timeout=20, _token=SMARTTHINGS_TOKEN, session=session)
            print("Library initialized")
            
            try:
                # Try to get devices directly
                devices = await api.get_devices()
                print(f"Success! Found {len(devices)} device(s)")
                
                if devices:
                    print("\n📱 First device details:")
                    device = devices[0]
                    print(f"  - Name: {device.label}")
                    print(f"  - Device ID: {device.device_id}")
                    print(f"  - Available attributes: {', '.join([a for a in dir(device) if not a.startswith('_')])}")
            except Exception as e:
                print(f"Library error: {str(e)}")
                print(f"Error type: {type(e).__name__}")
    
    except Exception as e:
        print(f"Connection error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_token())
