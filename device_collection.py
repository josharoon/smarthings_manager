#!/usr/bin/env python
"""
Device collection management for SmartThings Controller.

This module provides classes for managing collections of SmartThings devices,
including saving and loading device collections to/from disk.
"""

import json
import os
from pathlib import Path
from devices import Device


class DeviceCollection:
    """
    A collection of SmartThings devices.
    
    This class provides methods for managing groups of devices, applying filters,
    and persisting collections to disk.
    """
    
    def __init__(self, name="", devices=None):
        """
        Initialize a device collection.
        
        Args:
            name: A name for this collection
            devices: List of Device objects (optional)
        """
        self.name = name
        self.devices = devices if devices is not None else []
        self.device_ids = []
        # Controller will be set later if loading from saved collection
        self.controller = None
    
    def add(self, device):
        """
        Add a device to the collection.
        
        Args:
            device: The Device object to add
            
        Returns:
            bool: True if the device was added, False if it was already in the collection
        """
        # Check if the device is already in the collection
        device_ids = [d.device_id for d in self.devices]
        if device.device_id in device_ids:
            return False
            
        self.devices.append(device)
        return True
    
    def remove(self, device_or_id):
        """
        Remove a device from the collection.
        
        Args:
            device_or_id: A Device object or device ID string
            
        Returns:
            bool: True if the device was removed, False if it wasn't in the collection
        """
        # Handle either Device object or device ID string
        device_id = device_or_id.device_id if hasattr(device_or_id, 'device_id') else device_or_id
        
        for i, device in enumerate(self.devices):
            if device.device_id == device_id:
                self.devices.pop(i)
                return True
                
        return False
    
    def filter(self, device_filter):
        """
        Create a new collection with filtered devices.
        
        Args:
            device_filter: A DeviceFilter instance to apply
            
        Returns:
            DeviceCollection: A new collection with matching devices
        """
        filtered_devices = [d for d in self.devices if device_filter.matches(d)]
        return DeviceCollection(f"{self.name} (filtered)", filtered_devices)
    
    def save(self, filename=None, directory=None):
        """
        Save this collection to disk.
        
        Args:
            filename: The filename to save as (default: based on collection name)
            directory: The directory to save in (default: current directory)
            
        Returns:
            str: The path to the saved file
        """
        if not self.name and not filename:
            raise ValueError("Collection must have a name or filename must be provided")
            
        # Determine the filename if not provided
        if not filename:
            # Convert the name to a valid filename (replace spaces, etc.)
            filename = f"{self.name.lower().replace(' ', '_')}.json"
            
        # Determine the full path
        if directory:
            # Create the directory if it doesn't exist
            os.makedirs(directory, exist_ok=True)
            path = os.path.join(directory, filename)
        else:
            path = filename
            
        # Extract device IDs for storage
        device_ids = [device.device_id for device in self.devices]
        
        # Save to JSON file
        with open(path, 'w') as f:
            json.dump({
                "name": self.name,
                "device_count": len(device_ids),
                "device_ids": device_ids
            }, f, indent=2)
            
        return path
    
    @classmethod
    def load(cls, filename, controller=None, load_devices=True):
        """
        Load a collection from disk.
        
        Args:
            filename: The file to load from
            controller: SmartThingsController instance (required if load_devices=True)
            load_devices: Whether to load the actual device objects (requires controller)
            
        Returns:
            DeviceCollection: The loaded collection
        """
        # Check that the file exists
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Collection file not found: {filename}")
            
        with open(filename, 'r') as f:
            data = json.load(f)
            
        name = data.get("name", Path(filename).stem)
        device_ids = data.get("device_ids", [])
        
        # Create the collection
        collection = cls(name)
        
        # Load the devices if requested and controller is provided
        if load_devices and controller and device_ids:
            # We need to use asyncio to load devices
            import asyncio
            import sys
            
            # Store the device IDs for now, actual loading will happen outside
            collection.device_ids = device_ids
            collection.controller = controller
            
            # We'll leave devices as an empty list for now
            # The actual loading will be done by the calling code
            collection.devices = []
            
        return collection
        
    async def load_devices(self):
        """
        Asynchronously load devices from stored device IDs.
        
        This method should be called from an async context after loading
        a collection that has device_ids but no devices loaded yet.
        
        Returns:
            List[Device]: The loaded devices
        """
        if not self.device_ids or not self.controller:
            print("No device IDs or controller available")
            return []
            
        import asyncio
        
        print(f"Attempting to load {len(self.device_ids)} devices...")
        
        # Instead of loading individual devices, let's just get all devices 
        # and filter by the IDs we want
        try:
            # Get all devices first
            st_devices = await self.controller.get_all_devices()
            
            # Create device wrapper objects
            all_devices = []
            for st_device in st_devices:
                device = Device(st_device)
                health_state = await self.controller.get_device_health(device.device_id)
                if health_state:
                    device.health_state = health_state
                all_devices.append(device)
            
            # Create a set of device IDs for faster lookup
            collection_device_ids = set(self.device_ids)
            
            # Filter devices to only those in our collection
            self.devices = [d for d in all_devices if d.device_id in collection_device_ids]
            
            print(f"Successfully loaded {len(self.devices)} devices from collection")
            return self.devices
        except Exception as e:
            print(f"Error loading devices: {e}")
            return []
    
    def get_device_types(self):
        """
        Get a summary of device types in this collection.
        
        Returns:
            dict: A dictionary mapping device types to counts
        """
        type_counts = {}
        
        for device in self.devices:
            # Try to get the device type
            if hasattr(device, 'type'):
                device_type = device.type
            elif hasattr(device, '_st_device') and hasattr(device._st_device, 'type'):
                device_type = str(device._st_device.type)
            else:
                device_type = "unknown"
                
            # Update the counts
            if device_type in type_counts:
                type_counts[device_type] += 1
            else:
                type_counts[device_type] = 1
                
        return type_counts
    
    def get_online_offline_summary(self):
        """
        Get a summary of online/offline devices in this collection.
        
        Returns:
            dict: A dictionary with online/offline counts and percentages
        """
        online_count = 0
        offline_count = 0
        
        for device in self.devices:
            if device.is_online():
                online_count += 1
            else:
                offline_count += 1
                
        total = len(self.devices)
        online_percentage = round((online_count / total) * 100, 1) if total > 0 else 0
        offline_percentage = round((offline_count / total) * 100, 1) if total > 0 else 0
        
        return {
            "total": total,
            "online_count": online_count,
            "offline_count": offline_count,
            "online_percentage": online_percentage,
            "offline_percentage": offline_percentage
        }
    
    def __len__(self):
        """
        Get the number of devices in this collection.
        
        Returns:
            int: The number of devices
        """
        return len(self.devices)
    
    def __iter__(self):
        """
        Iterate over the devices in this collection.
        
        Returns:
            iterator: An iterator over the devices
        """
        return iter(self.devices)
    
    def __getitem__(self, index):
        """
        Get a device by index.
        
        Args:
            index: The index of the device
            
        Returns:
            Device: The device at the specified index
        """
        return self.devices[index]
    
    def __str__(self):
        """
        Get a string representation of this collection.
        
        Returns:
            str: A string describing this collection
        """
        return f"DeviceCollection '{self.name}' with {len(self.devices)} devices"
