#!/usr/bin/env python
"""
Script to generate a summary report of all SmartThings devices.
"""

import asyncio
import sys
import json
from smart_things_controller import SmartThingsController
from config import get_token

async def main():
    """Generate a summary report of all devices."""
    token = get_token()
    controller = SmartThingsController(token)
    
    print("Generating SmartThings device summary report...")
    print("=============================================\n")
    
    # Get all devices
    devices = await controller.get_all_devices()
    
    if not devices:
        print("No devices found.")
        return
    
    # Create device wrappers
    from devices import Device
    device_objects = [Device(d) for d in devices]
    
    # Get health status for all devices
    print("Checking health status for all devices...")
    for device in device_objects:
        health_state = await controller.get_device_health(device.device_id)
        if health_state:
            device.health_state = health_state
    
    # Count by status
    online_devices = [d for d in device_objects if d.is_online()]
    offline_devices = [d for d in device_objects if not d.is_online()]
    
    print(f"\nTotal Devices: {len(device_objects)}")
    print(f"Online: {len(online_devices)} ({round(len(online_devices)/len(device_objects)*100, 1)}%)")
    print(f"Offline: {len(offline_devices)} ({round(len(offline_devices)/len(device_objects)*100, 1)}%)")
    
    # Count by device type
    device_types = {}
    for device in device_objects:
        device_type = device.device_type
        if device_type in device_types:
            device_types[device_type] += 1
        else:
            device_types[device_type] = 1
    
    print("\nDevice Types:")
    for device_type, count in device_types.items():
        print(f"  {device_type}: {count}")
    
    # Count by room
    room_counts = {}
    for device in device_objects:
        room = device.room or "Unassigned"
        if room in room_counts:
            room_counts[room] += 1
        else:
            room_counts[room] = 1
    
    print("\nDevices by Room:")
    for room, count in sorted(room_counts.items()):
        print(f"  {room}: {count}")
    
    # List offline devices
    if offline_devices:
        print("\nOffline Devices:")
        for i, device in enumerate(offline_devices, 1):
            room_info = f" (in {device.room})" if device.room else ""
            print(f"  {i}. {device.name}{room_info}")
    
    # Battery levels
    battery_devices = []
    for device in device_objects:
        battery_level = device.battery_level
        if battery_level is not None:
            battery_devices.append((device, battery_level))
    
    if battery_devices:
        print("\nBattery Levels:")
        for device, level in sorted(battery_devices, key=lambda x: x[1]):
            status = "🟢" if device.is_online() else "🔴"
            print(f"  {status} {device.name}: {level}%")

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
