#!/usr/bin/env python
"""
Test script to verify the functionality of device status checking.
"""
import asyncio
import sys
from smart_things_controller import SmartThingsController

# Replace with your SmartThings Personal Access Token
SMARTTHINGS_TOKEN = "46e99609-d0b5-46a2-bc3f-ede7386c4fb1"  # Use the same token as in main.py

async def test_device_status_functionality():
    """Test the device status functionality."""
    print("🧪 Testing device status functionality...")
    controller = SmartThingsController(SMARTTHINGS_TOKEN)
    
    # Test 1: Get all devices
    print("\n--- Test 1: Get all devices ---")
    devices = await controller.get_all_devices()
    if devices:
        print(f"✅ Successfully retrieved {len(devices)} device(s)")
    else:
        print("❌ Failed to retrieve devices or no devices available")
    
    # Test 2: Get offline devices
    print("\n--- Test 2: Get offline devices ---")
    offline_devices = await controller.get_offline_devices()
    print(f"Found {len(offline_devices)} offline device(s)")
    
    # Test 3: Get online devices
    print("\n--- Test 3: Get online devices ---")
    online_devices = await controller.get_online_devices()
    print(f"Found {len(online_devices)} online device(s)")
    
    # Test 4: Get device status report
    print("\n--- Test 4: Get device status report ---")
    try:
        report = await controller.get_device_status_report()
        print("✅ Status report generated successfully")
        print(f"Summary: {report['summary']}")
    except Exception as e:
        print(f"❌ Failed to generate status report: {e}")
    
    # Validate consistency
    if len(devices) != (len(online_devices) + len(offline_devices)):
        print("⚠️ Warning: The sum of online and offline devices doesn't match the total device count")
        print(f"Total: {len(devices)}, Online: {len(online_devices)}, Offline: {len(offline_devices)}")
    else:
        print("✅ Device count validation passed")

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(test_device_status_functionality())
        print("\n🏁 All tests completed!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)
