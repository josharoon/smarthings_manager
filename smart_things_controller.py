import asyncio
import aiohttp
from pysmartthings import SmartThings
import inspect

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
        """
        devices = await self.get_all_devices()
        if devices:
            print(f"Device attributes: {dir(devices[0])}")
            print(f"Device attribute values:")
            for attr in dir(devices[0]):
                if not attr.startswith('__'):
                    try:
                        print(f"{attr}: {getattr(devices[0], attr)}")
                    except Exception as e:
                        print(f"{attr}: <error: {e}>")
        # Placeholder for correct offline check
        return []

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