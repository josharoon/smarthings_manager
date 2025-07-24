#!/usr/bin/env python
"""
Command-line interface for running batch actions on SmartThings devices.
"""

import argparse
import asyncio
import os
import sys
from typing import List
from smart_things_controller import SmartThingsController
from filters import StatusFilter, RoomFilter, NameFilter, FilterGroup
from device_collection import DeviceCollection
from actions import SwitchAction, RefreshAction, LevelAction, BatchActionRunner
from config import get_token, COLLECTIONS_DIR

# Ensure collections directory exists
os.makedirs(COLLECTIONS_DIR, exist_ok=True)


async def run_cli():
    """Run the command-line interface."""
    parser = argparse.ArgumentParser(
        description="Run batch actions on SmartThings devices"
    )
    
    # Authentication options
    auth_group = parser.add_argument_group('Authentication')
    auth_group.add_argument(
        '--token', 
        help='SmartThings API token (overrides environment variable)'
    )
    
    # Target selection (devices or collection)
    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument(
        '--collection', 
        help='Use a saved device collection'
    )
    target_group.add_argument(
        '--filter', 
        action='store_true',
        help='Use filter options to select devices'
    )
    
    # Filter options (when --filter is used)
    filter_group = parser.add_argument_group('Filters (used with --filter)')
    filter_group.add_argument(
        '--name', 
        help='Filter by device name (substring match)'
    )
    filter_group.add_argument(
        '--room', 
        help='Filter by room name'
    )
    filter_group.add_argument(
        '--online', 
        action='store_true',
        help='Filter for online devices'
    )
    filter_group.add_argument(
        '--offline', 
        action='store_true',
        help='Filter for offline devices'
    )
    
    # Action options (required)
    action_group = parser.add_argument_group('Actions (one required)')
    action_options = action_group.add_mutually_exclusive_group(required=True)
    action_options.add_argument(
        '--turn-on', 
        action='store_true',
        help='Turn devices on'
    )
    action_options.add_argument(
        '--turn-off', 
        action='store_true',
        help='Turn devices off'
    )
    action_options.add_argument(
        '--set-level', 
        type=int, 
        metavar='LEVEL',
        help='Set devices to specified level (0-100)'
    )
    action_options.add_argument(
        '--refresh', 
        action='store_true',
        help='Refresh device status'
    )
    
    args = parser.parse_args()
    
    # Get token from args or from config
    token = args.token or get_token()
    
    # Initialize controller
    controller = SmartThingsController(token)
    
    # Get devices either from collection or by filtering
    if args.collection:
        collection_path = get_collection_path(args.collection)
        if not os.path.exists(collection_path):
            print(f"Collection not found: {args.collection}")
            return
            
        print(f"Loading collection from {collection_path}...")
        collection = DeviceCollection.load(collection_path, controller, load_devices=True)
        
        # Load the devices asynchronously
        print("Loading devices from collection...")
        devices = await collection.load_devices()
        print(f"Loaded {len(devices)} devices from collection.")
    else:  # Using filters
        # Build filter group based on provided arguments
        filters = []
        
        if args.name:
            filters.append(NameFilter(args.name, mode="contains"))
            
        if args.room:
            filters.append(RoomFilter(args.room))
            
        if args.online and not args.offline:
            filters.append(StatusFilter(is_online=True))
            
        if args.offline and not args.online:
            filters.append(StatusFilter(is_online=False))
        
        # Combine all filters with AND logic
        filter_group = FilterGroup(filters, operator="and") if filters else None
        
        print("Fetching and filtering devices...")
        devices = await controller.find_devices(filter_group)
        print(f"Found {len(devices)} matching devices.")
    
    # Check if we found any devices
    if not devices:
        print("No devices found matching the criteria. Exiting.")
        return
    
    # Display devices before action
    print("\nDevices selected for action:")
    for i, device in enumerate(devices, 1):
        status = "Online" if device.is_online() else "Offline"
        print(f"{i}. {device.name} ({status})")
    
    # Ask for confirmation
    if not confirm_action():
        print("Action cancelled.")
        return
    
    # Create and run the action
    action = create_action(args)
    if action:
        print(f"\nExecuting {action.name} on {len(devices)} devices...")
        await BatchActionRunner.run_action(action, devices)
        BatchActionRunner.print_results(action)
    else:
        print("No valid action specified.")


def create_action(args):
    """Create the appropriate action based on arguments."""
    if args.turn_on:
        return SwitchAction(turn_on=True)
    elif args.turn_off:
        return SwitchAction(turn_on=False)
    elif args.set_level is not None:
        level = max(0, min(100, args.set_level))  # Ensure level is 0-100
        return LevelAction(level=level)
    elif args.refresh:
        return RefreshAction()
    
    return None


def get_collection_path(name):
    """Get the full path to a collection file."""
    # Convert spaces to underscores and ensure .json extension
    filename = f"{name.lower().replace(' ', '_')}"
    if not filename.endswith('.json'):
        filename += '.json'
    
    return os.path.join(COLLECTIONS_DIR, filename)


def confirm_action():
    """Ask user to confirm the action."""
    while True:
        response = input("\nDo you want to continue with this action? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' or 'n'")


if __name__ == "__main__":
    try:
        # Handle the event loop properly for all Python versions
        if sys.version_info >= (3, 11):
            # Python 3.11+
            asyncio.run(run_cli())
        else:
            # Python 3.10 and earlier
            loop = asyncio.get_event_loop()
            loop.run_until_complete(run_cli())
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
