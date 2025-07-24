#!/usr/bin/env python
"""
A script to debug device status in SmartThings.
"""
import asyncio
import aiohttp
from pysmartthings import SmartThings
import json

# Use the verified token
SMARTTHINGS_TOKEN = "46e99609-d0b5-46a2-bc3f-ede7386c4fb1"

async def debug_device_status():
    """Debug device status information from the SmartThings API."""
    print("🔍 Debugging device status...")
    
    async with aiohttp.ClientSession() as session:
        # Initialize the SmartThings API client
        api = SmartThings(request_timeout=20, _token=SMARTTHINGS_TOKEN, session=session)
        
        # Get all devices
        devices = await api.get_devices()
        
        if not devices:
            print("No devices found.")
            return
            
        print(f"Found {len(devices)} devices")
        
        # Get the first device for detailed inspection
        device = devices[0]
        print(f"\n=== Detailed inspection of device: {device.label} ({device.device_id}) ===")
        
        # List all non-private attributes
        print("\n1. All attributes:")
        for attr in [a for a in dir(device) if not a.startswith('_')]:
            try:
                value = getattr(device, attr)
                if not callable(value):
                    print(f"  - {attr}: {value}")
            except Exception as e:
                print(f"  - {attr}: <Error: {e}>")
                
        # Check for status attribute
        print("\n2. Status attribute:")
        if hasattr(device, 'status'):
            print("  Status attribute exists.")
            status = device.status
            print("  Status type:", type(status))
            
            # List all status attributes
            print("\n3. Status attributes:")
            for attr in [a for a in dir(status) if not a.startswith('_')]:
                try:
                    value = getattr(status, attr)
                    if not callable(value):
                        print(f"  - {attr}: {value}")
                except Exception as e:
                    print(f"  - {attr}: <Error: {e}>")
        else:
            print("  Status attribute does not exist!")
            
        # Try to get status via API call
        print("\n4. Getting device status via direct API call:")
        try:
            headers = {
                "Authorization": f"Bearer {SMARTTHINGS_TOKEN}",
                "Accept": "application/json"
            }
            async with session.get(f"https://api.smartthings.com/v1/devices/{device.device_id}/status") as response:
                if response.status == 200:
                    status_data = await response.json()
                    print(f"  API Status Response: {json.dumps(status_data, indent=2)[:1000]}...")
                else:
                    print(f"  API Status Error: {response.status}")
                    print(f"  Error Response: {await response.text()}")
        except Exception as e:
            print(f"  API Status Error: {e}")
            
        # Try to get health status 
        print("\n5. Getting device health status:")
        try:
            headers = {
                "Authorization": f"Bearer {SMARTTHINGS_TOKEN}",
                "Accept": "application/json"
            }
            async with session.get(f"https://api.smartthings.com/v1/devices/{device.device_id}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    print(f"  API Health Response: {json.dumps(health_data, indent=2)}")
                else:
                    print(f"  API Health Error: {response.status}")
                    print(f"  Error Response: {await response.text()}")
        except Exception as e:
            print(f"  API Health Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_device_status())
