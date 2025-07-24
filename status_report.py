#!/usr/bin/env python
"""
A script to generate a report of online and offline SmartThings devices.
"""
import asyncio
import argparse
from smart_things_controller import SmartThingsController
from devices import Device
from config import get_token

async def generate_status_report(offline_only=False, online_only=False):
    """
    Generate and print a report of online and offline SmartThings devices.
    
    Args:
        offline_only: If True, only show offline devices
        online_only: If True, only show online devices
    """
    token = get_token()
    controller = SmartThingsController(token)
    
    try:
        print("📊 Generating SmartThings Device Status Report...")
        
        # First check if we can connect to the API
        devices = await controller.get_all_devices()
        if not devices and "Authentication failed" in str(devices):
            print("\n🚨 ERROR: Authentication failed with SmartThings API")
            print("Please check your Personal Access Token in the script.")
            print("You can generate a new token from the SmartThings Developer Portal.")
            return
            
        status_report = await controller.get_device_status_report()
        
        # Print summary
        summary = status_report["summary"]
        print("\n=== SUMMARY ===")
        print(f"Total Devices: {summary['total']}")
        print(f"Online: {summary['online_count']} ({summary['online_percentage']}%)")
        print(f"Offline: {summary['offline_count']} ({100 - summary['online_percentage']}%)")
        
        # Print online devices if not in offline_only mode
        if not offline_only:
            print("\n=== ONLINE DEVICES ===")
            if not status_report["online"]:
                print("No online devices found.")
            else:
                for device in status_report["online"]:
                    health_info = f" - Health: {device.health_state}" if device.health_state else ""
                    print(f"🟢 {device.name} ({device.device_id}){health_info}")
        
        # Print offline devices if not in online_only mode
        if not online_only:
            print("\n=== OFFLINE DEVICES ===")
            if not status_report["offline"]:
                print("No offline devices found.")
            else:
                for device in status_report["offline"]:
                    health_info = f" - Health: {device.health_state}" if device.health_state else ""
                    print(f"🔴 {device.name} ({device.device_id}){health_info}")

    except Exception as e:
        print(f"Error generating status report: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a SmartThings device status report')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--offline', action='store_true', help='Show only offline devices')
    group.add_argument('--online', action='store_true', help='Show only online devices')
    
    args = parser.parse_args()
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(generate_status_report(offline_only=args.offline, online_only=args.online))
