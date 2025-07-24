#!/usr/bin/env python
"""
Command-line interface for filtering devices and managing device collections.
"""

import argparse
import asyncio
import os
import sys
import json
from smart_things_controller import SmartThingsController
from filters import (
    StatusFilter, RoomFilter, NameFilter, BatteryLevelFilter, 
    CapabilityFilter, TypeFilter, FilterGroup
)
from device_collection import DeviceCollection
from config import get_token, COLLECTIONS_DIR

# Ensure collections directory exists
os.makedirs(COLLECTIONS_DIR, exist_ok=True)


async def run_cli():
    """Run the command-line interface."""
    parser = argparse.ArgumentParser(
        description="Filter SmartThings devices and manage device collections"
    )
    
    # Authentication options
    auth_group = parser.add_argument_group('Authentication')
    auth_group.add_argument(
        '--token', 
        help='SmartThings API token (overrides environment variable)'
    )
    
    # Filter options
    filter_group = parser.add_argument_group('Filters')
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
    filter_group.add_argument(
        '--battery-below', 
        type=int,
        help='Filter for devices with battery level below threshold'
    )
    filter_group.add_argument(
        '--battery-above', 
        type=int,
        help='Filter for devices with battery level above threshold'
    )
    filter_group.add_argument(
        '--capability', 
        help='Filter by device capability'
    )
    filter_group.add_argument(
        '--type', 
        help='Filter by device type'
    )
    
    # Collection management
    collection_group = parser.add_argument_group('Collection Management')
    collection_group.add_argument(
        '--save', 
        metavar='NAME',
        help='Save filtered devices to a named collection'
    )
    collection_group.add_argument(
        '--load', 
        metavar='NAME',
        help='Load a saved collection'
    )
    collection_group.add_argument(
        '--list-collections', 
        action='store_true',
        help='List all saved collections'
    )
    collection_group.add_argument(
        '--delete-collection', 
        metavar='NAME',
        help='Delete a saved collection'
    )
    
    # Output options
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument(
        '--count-only', 
        action='store_true',
        help='Only show the count of matching devices'
    )
    output_group.add_argument(
        '--show-ids', 
        action='store_true',
        help='Include device IDs in output'
    )
    output_group.add_argument(
        '--show-room', 
        action='store_true',
        help='Include room information in output'
    )
    output_group.add_argument(
        '--summary', 
        action='store_true',
        help='Show summary statistics of matching devices'
    )
    
    args = parser.parse_args()
    
    # Handle collection listing separately
    if args.list_collections:
        list_collections()
        return
        
    # Handle collection deletion separately
    if args.delete_collection:
        delete_collection(args.delete_collection)
        return
    
    # Get token from args or from config
    token = args.token or get_token()
    
    # Initialize controller
    controller = SmartThingsController(token)
    
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
        
    if args.battery_below:
        filters.append(BatteryLevelFilter(args.battery_below, operator="<"))
        
    if args.battery_above:
        filters.append(BatteryLevelFilter(args.battery_above, operator=">"))
        
    if args.capability:
        filters.append(CapabilityFilter(args.capability))
        
    if args.type:
        filters.append(TypeFilter(args.type))
    
    # Combine all filters with AND logic
    filter_group = FilterGroup(filters, operator="and") if filters else None
    
    # Get devices either from filter or load from collection
    if args.load:
        collection_path = get_collection_path(args.load)
        if not os.path.exists(collection_path):
            print(f"Collection not found: {args.load}")
            return
            
        print(f"Loading collection from {collection_path}...")
        collection = DeviceCollection.load(collection_path, controller, load_devices=True)
        
        # Load the devices asynchronously
        print("Loading devices from collection...")
        devices = await collection.load_devices()
        
        # Apply additional filters if specified
        if filter_group and filters:
            print(f"Applying filters to loaded collection...")
            devices = [d for d in devices if filter_group.matches(d)]
    else:
        print("Fetching and filtering devices...")
        devices = await controller.find_devices(filter_group)
    
    # Save to collection if requested
    if args.save:
        collection = DeviceCollection(args.save, devices)
        collection_path = get_collection_path(args.save)
        saved_path = collection.save(collection_path)
        print(f"Saved {len(devices)} devices to collection: {args.save} ({saved_path})")
    
    # Display results
    if args.count_only:
        print(f"Found {len(devices)} matching devices")
    else:
        print(f"\nMatching devices ({len(devices)}):")
        for device in devices:
            # Format device information for display
            info = device.name
            
            if args.show_ids:
                info += f" ({device.device_id})"
                
            if args.show_room:
                room = device.room or "No Room"
                info += f" [Room: {room}]"
                
            status = "🟢 Online" if device.is_online() else "🔴 Offline"
            print(f"{status}: {info}")
    
    # Show summary if requested
    if args.summary and devices:
        print("\nSummary:")
        
        # Get online/offline summary
        online_summary = DeviceCollection("", devices).get_online_offline_summary()
        print(f"Online: {online_summary['online_count']} ({online_summary['online_percentage']}%)")
        print(f"Offline: {online_summary['offline_count']} ({online_summary['offline_percentage']}%)")
        
        # Get device types
        type_counts = DeviceCollection("", devices).get_device_types()
        if type_counts:
            print("\nDevice Types:")
            for device_type, count in type_counts.items():
                print(f"  {device_type}: {count}")


def get_collection_path(name):
    """Get the full path to a collection file."""
    # Convert spaces to underscores and ensure .json extension
    filename = f"{name.lower().replace(' ', '_')}"
    if not filename.endswith('.json'):
        filename += '.json'
    
    return os.path.join(COLLECTIONS_DIR, filename)


def list_collections():
    """List all saved collections."""
    print(f"Looking for collections in: {COLLECTIONS_DIR}")
    if not os.path.exists(COLLECTIONS_DIR):
        print("No saved collections found. Directory doesn't exist.")
        return
    
    collection_files = [f for f in os.listdir(COLLECTIONS_DIR) if f.endswith('.json')]
    
    if not collection_files:
        print("No saved collections found. No .json files in directory.")
        return
    
    print(f"Found {len(collection_files)} saved collections:")
    
    for i, filename in enumerate(sorted(collection_files), 1):
        # Load collection metadata
        path = os.path.join(COLLECTIONS_DIR, filename)
        print(f"Loading collection from: {path}")
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            
            name = data.get("name", filename.replace(".json", ""))
            device_count = data.get("device_count", 0)
            device_ids = data.get("device_ids", [])
            print(f"{i}. {name} - {len(device_ids)} devices")
        except Exception as e:
            print(f"{i}. {filename} - Error: {e}")


def delete_collection(name):
    """Delete a saved collection."""
    collection_path = get_collection_path(name)
    
    if not os.path.exists(collection_path):
        print(f"Collection not found: {name}")
        return
    
    try:
        os.remove(collection_path)
        print(f"Deleted collection: {name}")
    except Exception as e:
        print(f"Failed to delete collection: {e}")


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
