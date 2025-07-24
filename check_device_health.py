#!/usr/bin/env python
"""
Updated script to check device health from SmartThings API
"""
import asyncio
import aiohttp
from pysmartthings import SmartThings
import json

# Use the verified token
SMARTTHINGS_TOKEN = "46e99609-d0b5-46a2-bc3f-ede7386c4fb1"

async def check_device_health(device_id):
    """
    Check the health of a device directly via the SmartThings API.
    
    Args:
        device_id: The SmartThings device ID to check
        
    Returns:
        dict: The health status or None if unavailable
    """
    headers = {
        "Authorization": f"Bearer {SMARTTHINGS_TOKEN}",
        "Accept": "application/json"
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            async with session.get(f"https://api.smartthings.com/v1/devices/{device_id}/health") as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            print(f"Error getting device health: {e}")
            return None

async def check_all_devices_health():
    """Check the health status of all devices."""
    async with aiohttp.ClientSession() as session:
        api = SmartThings(request_timeout=20, _token=SMARTTHINGS_TOKEN, session=session)
        devices = await api.get_devices()
        
        if not devices:
            print("No devices found.")
            return
            
        print(f"Checking health of {len(devices)} devices...")
        
        # Check a few devices for health status
        online_count = 0
        offline_count = 0
        unknown_count = 0
        
        # Just check a few devices to avoid rate limits
        sample_devices = devices[:5]
        
        for device in sample_devices:
            health = await check_device_health(device.device_id)
            print(f"\nDevice: {device.label} ({device.device_id})")
            
            if health:
                state = health.get('state', 'UNKNOWN')
                print(f"Health State: {state}")
                
                if state == "ONLINE":
                    online_count += 1
                elif state == "OFFLINE":
                    offline_count += 1
                else:
                    unknown_count += 1
            else:
                print("Health information unavailable")
                unknown_count += 1
                
        print(f"\nSample Results: {online_count} online, {offline_count} offline, {unknown_count} unknown")

if __name__ == "__main__":
    asyncio.run(check_all_devices_health())
