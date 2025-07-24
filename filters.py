#!/usr/bin/env python
"""
Device filtering system for SmartThings Controller.

This module provides a flexible filtering system for finding devices that match
specific criteria. Filters can be combined using logical operators (AND, OR, NOT)
to create complex queries.
"""


class DeviceFilter:
    """
    Base class for device filters.
    
    All filter classes should inherit from this base class and implement
    the matches() method.
    """
    
    def matches(self, device):
        """
        Check if a device matches this filter's criteria.
        
        Args:
            device: The device object to check against this filter
            
        Returns:
            bool: True if the device matches, False otherwise
        """
        raise NotImplementedError("Subclasses must implement matches() method")
    
    def __and__(self, other):
        """
        Combine this filter with another using AND logic.
        
        Args:
            other: Another DeviceFilter instance
            
        Returns:
            AndFilter: A new filter that requires both filters to match
        """
        return AndFilter(self, other)
    
    def __or__(self, other):
        """
        Combine this filter with another using OR logic.
        
        Args:
            other: Another DeviceFilter instance
            
        Returns:
            OrFilter: A new filter that requires either filter to match
        """
        return OrFilter(self, other)
    
    def __invert__(self):
        """
        Negate this filter (NOT logic).
        
        Returns:
            NotFilter: A new filter that inverts the result of this filter
        """
        return NotFilter(self)


class AndFilter(DeviceFilter):
    """
    A filter that combines two other filters with AND logic.
    Both filters must match for this filter to match.
    """
    
    def __init__(self, filter1, filter2):
        """
        Initialize with two filters to combine with AND logic.
        
        Args:
            filter1: First DeviceFilter instance
            filter2: Second DeviceFilter instance
        """
        self.filter1 = filter1
        self.filter2 = filter2
    
    def matches(self, device):
        """
        Check if a device matches both filters.
        
        Args:
            device: The device to check
            
        Returns:
            bool: True if the device matches both filters, False otherwise
        """
        return self.filter1.matches(device) and self.filter2.matches(device)


class OrFilter(DeviceFilter):
    """
    A filter that combines two other filters with OR logic.
    Either filter must match for this filter to match.
    """
    
    def __init__(self, filter1, filter2):
        """
        Initialize with two filters to combine with OR logic.
        
        Args:
            filter1: First DeviceFilter instance
            filter2: Second DeviceFilter instance
        """
        self.filter1 = filter1
        self.filter2 = filter2
    
    def matches(self, device):
        """
        Check if a device matches either filter.
        
        Args:
            device: The device to check
            
        Returns:
            bool: True if the device matches either filter, False otherwise
        """
        return self.filter1.matches(device) or self.filter2.matches(device)


class NotFilter(DeviceFilter):
    """
    A filter that negates another filter (NOT logic).
    Matches when the wrapped filter does not match.
    """
    
    def __init__(self, filter_to_negate):
        """
        Initialize with a filter to negate.
        
        Args:
            filter_to_negate: The DeviceFilter instance to negate
        """
        self.filter_to_negate = filter_to_negate
    
    def matches(self, device):
        """
        Check if a device does NOT match the wrapped filter.
        
        Args:
            device: The device to check
            
        Returns:
            bool: True if the device does NOT match the wrapped filter
        """
        return not self.filter_to_negate.matches(device)


class StatusFilter(DeviceFilter):
    """
    Filter devices by their online/offline status.
    """
    
    def __init__(self, is_online=True):
        """
        Initialize with the desired online status.
        
        Args:
            is_online: If True, matches online devices. If False, matches offline devices.
        """
        self.is_online = is_online
    
    def matches(self, device):
        """
        Check if a device matches the desired online status.
        
        Args:
            device: The device to check
            
        Returns:
            bool: True if the device's online status matches the filter
        """
        try:
            return device.is_online() == self.is_online
        except Exception:
            # If we can't determine online status, consider it a non-match
            return False


class RoomFilter(DeviceFilter):
    """
    Filter devices by room name.
    """
    
    def __init__(self, room_name, case_sensitive=False):
        """
        Initialize with the room name to match.
        
        Args:
            room_name: The name of the room to filter by
            case_sensitive: If True, perform case-sensitive matching
        """
        self.room_name = room_name if case_sensitive else room_name.lower()
        self.case_sensitive = case_sensitive
    
    def matches(self, device):
        """
        Check if a device is in the specified room.
        
        Args:
            device: The device to check
            
        Returns:
            bool: True if the device is in the specified room
        """
        try:
            # Get the room from the device using the room property
            room_name = device.room
            
            # If we couldn't get the room name or it's None, return False
            if not room_name:
                return False
                
            # Apply case sensitivity
            if not self.case_sensitive:
                room_name = room_name.lower()
                pattern = self.room_name.lower()
            else:
                pattern = self.room_name
            
            # Match either exact match or substring
            return pattern == room_name or pattern in room_name
                
        except Exception as e:
            print(f"Error in RoomFilter: {e}")
            return False


class NameFilter(DeviceFilter):
    """
    Filter devices by name.
    """
    
    def __init__(self, name_pattern, mode="contains", case_sensitive=False):
        """
        Initialize with the name pattern and matching mode.
        
        Args:
            name_pattern: The name or pattern to filter by
            mode: The matching mode - "exact", "contains", or "startswith"
            case_sensitive: If True, perform case-sensitive matching
        """
        self.pattern = name_pattern if case_sensitive else name_pattern.lower()
        self.mode = mode
        self.case_sensitive = case_sensitive
    
    def matches(self, device):
        """
        Check if a device's name matches the pattern according to the specified mode.
        
        Args:
            device: The device to check
            
        Returns:
            bool: True if the device's name matches the pattern
        """
        try:
            name = device.name
            if not self.case_sensitive:
                name = name.lower()
                
            if self.mode == "exact":
                return name == self.pattern
            elif self.mode == "contains":
                return self.pattern in name
            elif self.mode == "startswith":
                return name.startswith(self.pattern)
            else:
                return False
        except Exception:
            return False


class BatteryLevelFilter(DeviceFilter):
    """
    Filter devices by battery level.
    """
    
    def __init__(self, level, operator="<="):
        """
        Initialize with the battery level threshold and comparison operator.
        
        Args:
            level: The battery level threshold (percentage)
            operator: The comparison operator - "<=", "<", ">=", ">", "=="
        """
        self.level = level
        self.operator = operator
    
    def matches(self, device):
        """
        Check if a device's battery level matches the criteria.
        
        Args:
            device: The device to check
            
        Returns:
            bool: True if the device's battery level matches the criteria
        """
        try:
            # Try to get battery level from the device
            battery_level = getattr(device, "battery_level", None)
            
            # If not available directly, try from the _st_device
            if battery_level is None and hasattr(device, "_st_device"):
                st_device = device._st_device
                if hasattr(st_device, "status") and hasattr(st_device.status, "battery"):
                    battery_level = st_device.status.battery
            
            if battery_level is None:
                return False
                
            if self.operator == "<=":
                return battery_level <= self.level
            elif self.operator == "<":
                return battery_level < self.level
            elif self.operator == ">=":
                return battery_level >= self.level
            elif self.operator == ">":
                return battery_level > self.level
            elif self.operator == "==":
                return battery_level == self.level
            else:
                return False
        except Exception:
            return False


class CapabilityFilter(DeviceFilter):
    """
    Filter devices by capability.
    """
    
    def __init__(self, capability):
        """
        Initialize with the capability to filter by.
        
        Args:
            capability: The capability name to filter by (e.g., "switch", "battery")
        """
        self.capability = capability
    
    def matches(self, device):
        """
        Check if a device has the specified capability.
        
        Args:
            device: The device to check
            
        Returns:
            bool: True if the device has the specified capability
        """
        try:
            # Try different ways to check for capabilities
            
            # 1. Check if device has a capabilities attribute directly
            if hasattr(device, "capabilities"):
                return self.capability in device.capabilities
                
            # 2. Check if the SmartThings device has capabilities
            if hasattr(device, "_st_device") and hasattr(device._st_device, "capabilities"):
                return self.capability in device._st_device.capabilities
                
            # 3. Check if the device inherits from a class that implies the capability
            if self.capability == "switch" and hasattr(device, "turn_on") and hasattr(device, "turn_off"):
                return True
                
            if self.capability == "battery" and hasattr(device, "battery_level"):
                return True
                
            return False
        except Exception:
            return False


class TypeFilter(DeviceFilter):
    """
    Filter devices by their type.
    """
    
    def __init__(self, device_type, case_sensitive=False):
        """
        Initialize with the device type to filter by.
        
        Args:
            device_type: The device type to filter by
            case_sensitive: If True, perform case-sensitive matching
        """
        self.device_type = device_type if case_sensitive else device_type.lower()
        self.case_sensitive = case_sensitive
    
    def matches(self, device):
        """
        Check if a device is of the specified type.
        
        Args:
            device: The device to check
            
        Returns:
            bool: True if the device is of the specified type
        """
        try:
            # Try different ways to check for device type
            
            # 1. Check if device has a type attribute directly
            if hasattr(device, "type"):
                device_type = device.type
                if not self.case_sensitive:
                    device_type = device_type.lower()
                return device_type == self.device_type
                
            # 2. Check the SmartThings device type
            if hasattr(device, "_st_device") and hasattr(device._st_device, "type"):
                device_type = device._st_device.type
                if not self.case_sensitive:
                    device_type = str(device_type).lower()
                return device_type == self.device_type
                
            # 3. Check if the device name contains the type as a fallback
            name = getattr(device, "name", "").lower()
            return self.device_type in name.lower()
        except Exception:
            return False


class FilterGroup:
    """
    A group of filters with a specified logical operation.
    
    This allows for creating more complex filter combinations.
    """
    
    def __init__(self, filters=None, operator="and"):
        """
        Initialize with a list of filters and a logical operator.
        
        Args:
            filters: List of DeviceFilter instances
            operator: The logical operator to apply - "and" or "or"
        """
        self.filters = filters or []
        self.operator = operator.lower()
    
    def add_filter(self, filter_obj):
        """
        Add a filter to the group.
        
        Args:
            filter_obj: A DeviceFilter instance to add
        """
        self.filters.append(filter_obj)
    
    def matches(self, device):
        """
        Check if a device matches the filter group according to the logical operator.
        
        Args:
            device: The device to check
            
        Returns:
            bool: True if the device matches the filter group
        """
        if not self.filters:
            return True  # Empty filter group matches everything
            
        if self.operator == "and":
            return all(f.matches(device) for f in self.filters)
        elif self.operator == "or":
            return any(f.matches(device) for f in self.filters)
        else:
            raise ValueError(f"Unknown operator: {self.operator}")
