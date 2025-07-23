class Device:
    """
    Represents a generic SmartThings device.
    """
    def __init__(self, st_device):
        self._st_device = st_device

    @property
    def name(self):
        return self._st_device.label

    @property
    def device_id(self):
        return self._st_device.device_id

    def is_online(self):
        return self._st_device.status.is_online

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