import asyncio
import aiohttp
from pysmartthings import SmartThings
import inspect
from devices import Device
from filters import DeviceFilter, FilterGroup

class SmartThingsController:
    """
    A controller to interact with the SmartThings API.
    """
    def __init__(self, token):
        """
        Initializes the SmartThingsController.

        Args:
            token (str): The SmartThings Personal Access Token.
        """
        self._token = token
        self._cached_locations = None
        self._cached_rooms = None
        self._room_id_to_name = {}

    async def get_all_devices(self):
        """
        Retrieves all devices from the SmartThings account.
        
        Returns:
            list: A list of Device objects from the pysmartthings API response.
        """
        # Try using the pysmartthings API first
        try:
            async with aiohttp.ClientSession() as session:
                api = SmartThings(request_timeout=10, _token=self._token, session=session)
                print("✅ SmartThings API object initialized.")
                
                devices = await api.get_devices()
                if devices:
                    print(f"Found {len(devices)} devices using pysmartthings API.")
                    await self._refresh_devices(devices)
                    return devices
        except Exception as e:
            print(f"Warning: pysmartthings API failed: {e}")
            
        # Fall back to direct REST API call
        print("Falling back to direct REST API call...")
        
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json"
        }
        
        try:
            st_devices = []
            async with aiohttp.ClientSession(headers=headers) as session:
                url = "https://api.smartthings.com/v1/devices"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        devices_data = data.get('items', [])
                        
                        if devices_data:
                            print(f"Retrieved {len(devices_data)} devices from REST API.")
                            
                            # Create pysmartthings Device objects from the data
                            for device_data in devices_data:
                                from pysmartthings import Device as STDevice
                                st_device = STDevice(None)
                                st_device.device_id = device_data.get('deviceId')
                                st_device.name = device_data.get('name')
                                st_device.label = device_data.get('label') or device_data.get('name')
                                st_device.device_type_id = device_data.get('deviceTypeId')
                                st_device.device_type_name = device_data.get('deviceTypeName')
                                st_device.room_id = device_data.get('roomId')
                                # Add location data if available
                                if 'location' in device_data:
                                    st_device.location_id = device_data['location'].get('locationId')
                                # Add capabilities
                                st_device.capabilities = [
                                    cap.get('id') for cap in device_data.get('components', [{}])[0].get('capabilities', [])
                                ]
                                st_devices.append(st_device)
                            
                            return st_devices
                        else:
                            print("No devices found in REST API response.")
                    else:
                        print(f"Error fetching devices from REST API: {response.status}")
        except Exception as e:
            print(f"Error with REST API call: {e}")
            
        print("Could not retrieve devices by any method.")
        return []

    async def _refresh_devices(self, devices):
        """Refreshes the status of all devices."""
        print("🔄 Refreshing device statuses...")
        # Only refresh if device has a 'refresh' method
        refresh_tasks = [device.refresh() for device in devices if hasattr(device, 'refresh')]
        if refresh_tasks:
            await asyncio.gather(*refresh_tasks)
        print("...Done.")
        
    async def get_locations(self):
        """
        Fetches all locations from the SmartThings API.
        
        Returns:
            dict: A dictionary of location objects keyed by location ID
        """
        if self._cached_locations:
            return self._cached_locations
            
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json"
        }
        
        locations = {}
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                url = "https://api.smartthings.com/v1/locations"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        for location in data.get('items', []):
                            location_id = location.get('locationId')
                            locations[location_id] = location
                        
                        print(f"Retrieved {len(locations)} locations from SmartThings API.")
                        self._cached_locations = locations
                        return locations
                    else:
                        print(f"Error fetching locations: {response.status}")
        except Exception as e:
            print(f"Error getting locations: {e}")
            
        return {}
        
    async def get_rooms(self, location_id=None):
        """
        Fetches all rooms from the SmartThings API, optionally filtered by location.
        
        Args:
            location_id (str, optional): The location ID to filter rooms by
            
        Returns:
            dict: A dictionary mapping room IDs to room objects
        """
        # Return cached rooms if available
        if self._cached_rooms:
            return self._cached_rooms
            
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json"
        }
        
        rooms = {}
        
        # If no location_id is provided, get all locations first
        locations = {}
        if location_id:
            locations[location_id] = {"locationId": location_id}
        else:
            locations = await self.get_locations()
            
        # For each location, get its rooms
        for loc_id in locations:
            try:
                async with aiohttp.ClientSession(headers=headers) as session:
                    url = f"https://api.smartthings.com/v1/locations/{loc_id}/rooms"
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            location_rooms = data.get('items', [])
                            
                            # Add location information to each room
                            for room in location_rooms:
                                room_id = room.get('roomId')
                                rooms[room_id] = {
                                    **room,
                                    "locationId": loc_id
                                }
                        else:
                            print(f"Error fetching rooms for location {loc_id}: {response.status}")
            except Exception as e:
                print(f"Error getting rooms for location {loc_id}: {e}")
                
        # Cache the rooms
        self._cached_rooms = rooms
        
        # Create a mapping from room ID to room name for easier access
        self._room_id_to_name = {
            room_id: room.get('name', 'Unknown Room') 
            for room_id, room in rooms.items()
        }
        
        print(f"Retrieved {len(rooms)} rooms from SmartThings API.")
        return rooms
        
    def get_room_name(self, room_id):
        """
        Gets the room name for a given room ID.
        
        Args:
            room_id (str): The room ID to get the name for
            
        Returns:
            str: The room name, or None if the room ID is not found
        """
        return self._room_id_to_name.get(room_id)

    async def list_all_devices(self):
        """
        Returns a list of all Device objects from SmartThings.
        """
        devices = await self.get_all_devices()
        if devices:
            print(f"Device attributes: {dir(devices[0])}")
        return devices

    async def get_offline_devices(self):
        """
        Returns a list of Device objects that are offline.
        
        Returns:
            list: A list of Device objects that are currently offline.
        """
        devices = await self.get_all_devices()
        offline_devices = []
        
        for device in devices:
            try:
                if hasattr(device, 'status') and hasattr(device.status, 'is_online') and not device.status.is_online:
                    offline_devices.append(device)
            except Exception as e:
                print(f"Error checking online status for device {getattr(device, 'label', 'Unknown')}: {e}")
        
        return offline_devices
        
    async def get_online_devices(self):
        """
        Returns a list of Device objects that are online.
        
        Returns:
            list: A list of Device objects that are currently online.
        """
        devices = await self.get_all_devices()
        online_devices = []
        
        for device in devices:
            try:
                if hasattr(device, 'status') and hasattr(device.status, 'is_online') and device.status.is_online:
                    online_devices.append(device)
            except Exception as e:
                print(f"Error checking online status for device {getattr(device, 'label', 'Unknown')}: {e}")
        
        return online_devices
        
    async def get_device_health(self, device_id):
        """
        Get the health status of a specific device.
        
        Args:
            device_id: The device ID to check
            
        Returns:
            str: The health state ('ONLINE', 'OFFLINE', or None if unknown)
        """
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                url = f"https://api.smartthings.com/v1/devices/{device_id}/health"
                async with session.get(url) as response:
                    if response.status == 200:
                        health_data = await response.json()
                        return health_data.get('state', None)
        except Exception as e:
            print(f"Error checking health for device {device_id}: {e}")
        
        return None
        
    async def get_device_status_report(self):
        """
        Generates a comprehensive report of all devices and their online/offline status.
        
        Returns:
            dict: A dictionary containing lists of online and offline devices, and a summary.
        """
        devices = await self.get_all_devices()
        online_devices = []
        offline_devices = []
        
        print(f"Checking health status for {len(devices)} devices...")
        for st_device in devices:
            # First create the device object
            device = Device(st_device)
            
            # Then check its health
            health_state = await self.get_device_health(device.device_id)
            if health_state:
                device.health_state = health_state
                
            # Categorize based on online status
            if device.is_online():
                online_devices.append(device)
            else:
                offline_devices.append(device)
        
        return {
            "online": online_devices,
            "offline": offline_devices,
            "summary": {
                "total": len(devices),
                "online_count": len(online_devices),
                "offline_count": len(offline_devices),
                "online_percentage": round((len(online_devices) / len(devices)) * 100 if devices else 0, 1)
            }
        }
        
    async def find_devices(self, device_filter=None):
        """
        Find devices that match the specified filter criteria.
        
        Args:
            device_filter: A DeviceFilter instance or FilterGroup to apply
                          If None, all devices are returned
                          
        Returns:
            list: A list of Device objects that match the filter criteria
        """
        # Get all devices first
        st_devices = await self.get_all_devices()
        
        # Get rooms mapping
        await self.get_rooms()
        
        # Create device wrapper objects
        devices = [Device(st_device) for st_device in st_devices]
        
        # Apply health state to all devices and add room information
        for device in devices:
            # Add health state
            health_state = await self.get_device_health(device.device_id)
            if health_state:
                device.health_state = health_state
                
            # Add room information if available
            if hasattr(device._st_device, 'room_id') and device._st_device.room_id:
                room_name = self.get_room_name(device._st_device.room_id)
                if room_name:
                    # Store the room name directly in the device for access via the room property
                    device._room_name = room_name
        
        # If no filter specified, return all devices
        if device_filter is None:
            return devices
            
        # Apply the filter and return matching devices
        return [device for device in devices if device_filter.matches(device)]
        
    async def get_device_by_id(self, device_id):
        """
        Get a specific device by its ID.
        
        Args:
            device_id: The SmartThings device ID
            
        Returns:
            Device: The device object or None if not found
        """
        # Get all devices (potentially optimize this later)
        st_devices = await self.get_all_devices()
        
        # Make sure rooms are loaded
        await self.get_rooms()
        
        # Find the device with matching ID
        for st_device in st_devices:
            if st_device.device_id == device_id:
                device = Device(st_device)
                
                # Add health state
                health_state = await self.get_device_health(device_id)
                if health_state:
                    device.health_state = health_state
                    
                # Add room information if available
                if hasattr(st_device, 'room_id') and st_device.room_id:
                    room_name = self.get_room_name(st_device.room_id)
                    if room_name:
                        device._room_name = room_name
                        
                return device
                
        return None

    async def delete_devices(self, device_ids):
        """
        Deletes devices from SmartThings by their device_id.
        
        Args:
            device_ids (list): List of device_id strings to delete.
        
        Returns:
            dict: Results of deletion for each device_id.
        """
        results = {}
        async with aiohttp.ClientSession() as session:
            api = SmartThings(request_timeout=10, _token=self._token, session=session)
            print(f"SmartThings methods: {dir(api)}")
            for device_id in device_ids:
                try:
                    await api.delete_device(device_id)
                    results[device_id] = 'Deleted'
                    print(f"Deleted device: {device_id}")
                except Exception as e:
                    results[device_id] = f"Failed: {e}"
                    print(f"Failed to delete device {device_id}: {e}")
        return results
        
    async def list_rooms(self):
        """
        List all rooms found in the SmartThings account by analyzing device assignments.
        """
        # Get all devices first
        st_devices = await self.get_all_devices()
        
        # Extract room information from devices
        rooms = {}
        devices_by_room = {}
        
        for st_device in st_devices:
            try:
                if hasattr(st_device, 'room') and st_device.room:
                    room_name = st_device.room.name
                    room_id = st_device.room.room_id
                    
                    # Add to rooms dictionary
                    if room_id not in rooms:
                        rooms[room_id] = {
                            'name': room_name,
                            'id': room_id,
                        }
                    
                    # Add device to room's device list
                    if room_name not in devices_by_room:
                        devices_by_room[room_name] = []
                    devices_by_room[room_name].append(st_device.label)
            except Exception as e:
                print(f"Error extracting room for device {getattr(st_device, 'label', 'Unknown')}: {e}")
                
        # Print results
        print("\n=== Rooms in SmartThings ===")
        
        if not rooms:
            print("No rooms found. Devices may not be assigned to rooms.")
            return
            
        for room_id, room_info in sorted(rooms.items(), key=lambda x: x[1]['name']):
            room_name = room_info['name']
            device_count = len(devices_by_room.get(room_name, []))
            print(f"Room: {room_name} ({device_count} devices)")
            
            # Optionally list devices in each room
            if device_count > 0:
                for device_name in sorted(devices_by_room[room_name]):
                    print(f"  • {device_name}")
                    
        total_rooms = len(rooms)
        total_devices_with_rooms = sum(len(devices) for devices in devices_by_room.values())
        
        print(f"\nTotal rooms: {total_rooms}")
        print(f"Total devices with room assignments: {total_devices_with_rooms}")
        print(f"Total devices without room assignments: {len(st_devices) - total_devices_with_rooms}")
        print(f"\nTotal rooms: {total_rooms}")
        
    def get_device_room(self, device):
        """
        Get the room name for a device.
        
        Args:
            device: The device to get the room for
            
        Returns:
            str: The room name or None if not found
        """
        try:
            if hasattr(device, 'room') and device.room:
                return device.room.name
            elif hasattr(device, '_st_device') and hasattr(device._st_device, 'room'):
                return device._st_device.room.name if device._st_device.room else None
        except Exception as e:
            print(f"Error getting room for device {device.name}: {e}")
        
        return None