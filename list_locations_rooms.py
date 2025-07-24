#!/usr/bin/env python
"""
Script to list all locations and rooms from the SmartThings API.
"""

import asyncio
import aiohttp
import json
import os
import sys
from config import get_token

SMARTTHINGS_API_BASE = "https://api.smartthings.com/v1"

async def get_locations(token):
    """
    Get all locations from the SmartThings API.
    
    Args:
        token: The SmartThings API token
        
    Returns:
        list: A list of location objects
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        url = f"{SMARTTHINGS_API_BASE}/locations"
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('items', [])
            else:
                print(f"Error fetching locations: {response.status}")
                return []

async def get_rooms(token, location_id):
    """
    Get all rooms for a location from the SmartThings API.
    
    Args:
        token: The SmartThings API token
        location_id: The location ID
        
    Returns:
        list: A list of room objects
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        url = f"{SMARTTHINGS_API_BASE}/locations/{location_id}/rooms"
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('items', [])
            else:
                print(f"Error fetching rooms: {response.status}")
                return []

async def get_devices_in_room(token, room_id):
    """
    Get all devices in a room from the SmartThings API.
    
    Args:
        token: The SmartThings API token
        room_id: The room ID
        
    Returns:
        list: A list of device objects
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        url = f"{SMARTTHINGS_API_BASE}/devices?roomId={room_id}"
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('items', [])
            else:
                print(f"Error fetching devices in room: {response.status}")
                return []

async def main():
    """Main function to list locations and rooms."""
    token = get_token()
    
    # Get all locations
    print("Fetching locations...")
    locations = await get_locations(token)
    
    if not locations:
        print("No locations found.")
        return
    
    print(f"\nFound {len(locations)} locations:\n")
    
    # For each location, get the rooms
    for location in locations:
        location_id = location.get('locationId')
        location_name = location.get('name', 'Unknown')
        print(f"Location: {location_name} ({location_id})")
        
        print(f"  Fetching rooms for {location_name}...")
        rooms = await get_rooms(token, location_id)
        
        if not rooms:
            print("  No rooms found.")
            continue
        
        print(f"  Found {len(rooms)} rooms:")
        
        # For each room, get the devices
        for room in rooms:
            room_id = room.get('roomId')
            room_name = room.get('name', 'Unknown')
            print(f"    Room: {room_name} ({room_id})")
            
            print(f"      Fetching devices in {room_name}...")
            devices = await get_devices_in_room(token, room_id)
            
            if not devices:
                print(f"      No devices found in {room_name}")
                continue
            
            print(f"      Found {len(devices)} devices in {room_name}:")
            for device in devices:
                device_id = device.get('deviceId')
                device_name = device.get('name', 'Unknown')
                device_type = device.get('deviceTypeName', 'Unknown')
                print(f"        {device_name} ({device_id}) - Type: {device_type}")

if __name__ == "__main__":
    try:
        # Handle the event loop properly for all Python versions
        if sys.version_info >= (3, 11):
            # Python 3.11+
            asyncio.run(main())
        else:
            # Python 3.10 and earlier
            loop = asyncio.get_event_loop()
            loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
