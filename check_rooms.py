#!/usr/bin/env python
"""
Test script to check room information for devices
"""
import asyncio
from smart_things_controller import SmartThingsController
from config import get_token

async def main():
    controller = SmartThingsController(get_token())
    print("Getting devices...")
    st_devices = await controller.get_all_devices()
    print(f"Got {len(st_devices)} devices")
    
    # Check first few devices for room information
    for i, st_device in enumerate(st_devices[:5]):
        print(f"\nDevice {i+1}: {st_device.label}")
        print(f"  Has room attr: {hasattr(st_device, 'room')}")
        
        room_value = None
        if hasattr(st_device, 'room'):
            room_value = st_device.room
            if room_value:
                print(f"  Room name: {room_value.name if hasattr(room_value, 'name') else 'No name attribute'}")
            else:
                print("  Room value is None")
        else:
            print("  No room attribute")
        
        print(f"  Dir(st_device): {dir(st_device)}")
        
        # Create a Device object to check the room property
        from devices import Device
        device = Device(st_device)
        print(f"  Wrapper room property: {device.room}")
    
    # Check SmartThingsController.get_device_room
    print("\nTesting controller.get_device_room")
    for i, st_device in enumerate(st_devices[:5]):
        from devices import Device
        device = Device(st_device)
        room = controller.get_device_room(device)
        print(f"Device {st_device.label}: Room={room}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Operation cancelled.")
    except Exception as e:
        print(f"Error: {e}")
