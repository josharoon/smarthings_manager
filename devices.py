import aiohttp

class Device:
    """
    Represents a generic SmartThings device.
    """
    def __init__(self, st_device, health_state=None):
        self._st_device = st_device
        self._health_state = health_state

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