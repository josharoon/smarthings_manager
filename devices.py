import aiohttp
from typing import List, Dict, Any, Optional

class Device:
    """
    Represents a generic SmartThings device.
    """
    def __init__(self, st_device, health_state=None):
        self._st_device = st_device
        self._health_state = health_state
        self._room_name = None  # This will be set by the controller

    @property
    def name(self):
        return self._st_device.label

    @property
    def device_id(self):
        return self._st_device.device_id
        
    @property
    def health_state(self):
        return self._health_state
        
    @health_state.setter
    def health_state(self, state):
        self._health_state = state

    def is_online(self):
        try:
            # First check if we have a health state
            if self._health_state:
                return self._health_state == "ONLINE"
                
            # Fallback to the component check
            if hasattr(self._st_device, 'components') and self._st_device.components:
                # For now, let's assume the device is online if we can access its components
                return True
            return False
        except Exception as e:
            print(f"Error checking online status for {self.name}: {e}")
            return False
            
    async def check_health(self, token):
        """
        Check device health from the SmartThings API.
        
        Args:
            token: SmartThings API token
            
        Returns:
            bool: True if device is online, False otherwise
        """
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                url = f"https://api.smartthings.com/v1/devices/{self.device_id}/health"
                async with session.get(url) as response:
                    if response.status == 200:
                        health_data = await response.json()
                        self._health_state = health_data.get('state', None)
                        return self._health_state == "ONLINE"
        except Exception as e:
            print(f"Error checking health for {self.name}: {e}")
        
        return self.is_online()  # Fall back to the component check

    def __str__(self):
        status = "🟢 Online" if self.is_online() else "🔴 Offline"
        return f"{self.name} ({self.device_id}) - Status: {status}"
        
    def has_capability(self, capability: str) -> bool:
        """
        Check if the device has a specific capability.
        
        Args:
            capability: The capability to check for
            
        Returns:
            bool: True if the device has the capability, False otherwise
        """
        try:
            return capability in self._st_device.capabilities
        except Exception:
            return False
    
    async def refresh(self) -> bool:
        """
        Refresh the device state.
        
        Returns:
            bool: True if refresh was successful, False otherwise
        """
        try:
            if hasattr(self._st_device, 'refresh'):
                await self._st_device.refresh()
            return True
        except Exception as e:
            print(f"Error refreshing device {self.name}: {e}")
            return False
            
    async def turn_on(self) -> None:
        """
        Turn on the device if it has a switch capability.
        
        Returns:
            None
        """
        if self.has_capability("switch"):
            await self._st_device.switch_on()
        else:
            raise ValueError(f"Device {self.name} does not have switch capability")
            
    async def turn_off(self) -> None:
        """
        Turn off the device if it has a switch capability.
        
        Returns:
            None
        """
        if self.has_capability("switch"):
            await self._st_device.switch_off()
        else:
            raise ValueError(f"Device {self.name} does not have switch capability")
            
    async def set_level(self, level: int) -> None:
        """
        Set the level of the device if it has a switchLevel capability.
        
        Args:
            level: The level to set (0-100)
            
        Returns:
            None
        """
        if not (0 <= level <= 100):
            raise ValueError("Level must be between 0 and 100")
            
        if self.has_capability("switchLevel"):
            await self._st_device.set_level(level)
        else:
            raise ValueError(f"Device {self.name} does not have switchLevel capability")
            
    @property
    def room(self) -> Optional[str]:
        """
        Get the room name for the device.
        
        Returns:
            str or None: The room name if available, None otherwise
        """
        # First check if we have a room name set directly by the controller
        if self._room_name is not None:
            return self._room_name
            
        # Try to get the room name from the device if available
        try:
            # Check if the device has room and room.name attributes
            if hasattr(self._st_device, 'room') and self._st_device.room:
                return self._st_device.room.name
        except Exception:
            pass
            
        # Check for room_id only (common in REST API responses)
        try:
            if hasattr(self._st_device, 'room_id') and self._st_device.room_id:
                # We can't resolve the name here without the controller,
                # but at least we know it has a room
                return f"Room ID: {self._st_device.room_id}"
        except Exception:
            pass
            
        return None
            
    @property
    def device_type(self) -> str:
        """
        Get the device type.
        
        Returns:
            str: The device type
        """
        try:
            return self._st_device.type
        except Exception:
            return "unknown"
            
    @property
    def battery_level(self) -> Optional[int]:
        """
        Get the battery level if the device has a battery.
        
        Returns:
            int or None: The battery level if available, None otherwise
        """
        if self.has_capability("battery"):
            try:
                return self._st_device.status.battery
            except Exception:
                pass
        return None


class Switch(Device):
    """
    Represents a device with switch capabilities.
    """
    def __init__(self, st_device):
        super().__init__(st_device)
        if "switch" not in self._st_device.capabilities:
            raise TypeError("Device does not have 'switch' capability.")

    @property
    def state(self):
        return self._st_device.status.switch

    async def turn_on(self):
        await self._st_device.switch_on()
        print(f"💡 Turned ON: {self.name}")

    async def turn_off(self):
        await self._st_device.switch_off()
        print(f"⚫ Turned OFF: {self.name}")

    def __str__(self):
        base_str = super().__str__()
        return f"{base_str} - State: {self.state.upper()}"


class BatteryDevice(Device):
    """
    Represents a device with battery reporting capabilities.
    """
    def __init__(self, st_device):
        super().__init__(st_device)
        if "battery" not in self._st_device.capabilities:
            raise TypeError("Device does not have 'battery' capability.")

    @property
    def battery_level(self):
        return self._st_device.status.battery

    def __str__(self):
        base_str = super().__str__()
        return f"{base_str} - 🔋 Battery: {self.battery_level}%"