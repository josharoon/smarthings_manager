import asyncio
import aiohttp
from pysmartthings import SmartThings
import inspect
from devices import Device

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

    async def get_all_devices(self):
        """
        Retrieves all devices from the SmartThings account.
        
        Returns:
            list: A list of Device objects from the pysmartthings API response.
        """
        async with aiohttp.ClientSession() as session:
            api = SmartThings(request_timeout=10, _token=self._token, session=session)
            print("✅ SmartThings API object initialized.")
            try:
                devices = await api.get_devices()
                print(f"DEBUG: Retrieved devices using get_devices(), type(devices): {type(devices)}, type(devices[0]): {type(devices[0]) if devices else 'N/A'}")
                if devices:
                    # Show details about the first device to help with debugging
                    first_device = devices[0]
                    print(f"First device: {first_device.label} ({first_device.device_id})")
                    print(f"Available attributes: {', '.join([a for a in dir(first_device) if not a.startswith('_')])}")
                    # Check if the device has the attributes we need
                    if hasattr(first_device, 'capabilities'):
                        print(f"Capabilities: {first_device.capabilities}")
                    if hasattr(first_device, 'status'):
                        print(f"Status attributes: {', '.join([a for a in dir(first_device.status) if not a.startswith('_')])}")
                
                await self._refresh_devices(devices)
                return devices
            except Exception as e:
                print(f"DEBUG: get_devices() failed: {e}")
            print("DEBUG: No valid device retrieval method found.")
            return []

    async def _refresh_devices(self, devices):
        """Refreshes the status of all devices."""
        print("🔄 Refreshing device statuses...")
        # Only refresh if device has a 'refresh' method
        refresh_tasks = [device.refresh() for device in devices if hasattr(device, 'refresh')]
        if refresh_tasks:
            await asyncio.gather(*refresh_tasks)
        print("...Done.")

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