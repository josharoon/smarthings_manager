"""
Batch actions for SmartThings devices.

This module provides classes to perform batch actions on SmartThings devices.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable
from devices import Device


class BatchAction(ABC):
    """Base class for batch actions on devices."""
    
    def __init__(self, name: str = None):
        """Initialize a batch action.
        
        Args:
            name: Optional name for this action
        """
        self.name = name or self.__class__.__name__
        self.results = {}
    
    @abstractmethod
    async def execute(self, devices: List[Device]) -> Dict[str, Any]:
        """Execute the action on the provided devices.
        
        Args:
            devices: List of Device objects to act upon
            
        Returns:
            Dictionary of results with device IDs as keys
        """
        pass
    
    def get_results(self) -> Dict[str, Any]:
        """Get the results of the last execution.
        
        Returns:
            Dictionary of results with device IDs as keys
        """
        return self.results
    
    def get_success_rate(self) -> float:
        """Calculate the success rate of the last execution.
        
        Returns:
            Percentage of successful operations (0-100)
        """
        if not self.results:
            return 0.0
            
        success_count = sum(1 for result in self.results.values() if result.get('success', False))
        return (success_count / len(self.results)) * 100


class SwitchAction(BatchAction):
    """Action to turn devices on or off."""
    
    def __init__(self, turn_on: bool = True, name: str = None):
        """Initialize a switch action.
        
        Args:
            turn_on: True to turn devices on, False to turn them off
            name: Optional name for this action
        """
        super().__init__(name or f"Switch{'On' if turn_on else 'Off'}")
        self.turn_on = turn_on
    
    async def execute(self, devices: List[Device]) -> Dict[str, Any]:
        """Execute the switch action on the provided devices.
        
        Args:
            devices: List of Device objects to act upon
            
        Returns:
            Dictionary of results with device IDs as keys
        """
        self.results = {}
        
        # Filter to only devices with switch capability
        switch_devices = [d for d in devices if d.has_capability("switch")]
        
        # Execute in parallel
        tasks = []
        for device in switch_devices:
            if self.turn_on:
                tasks.append(self._turn_on_device(device))
            else:
                tasks.append(self._turn_off_device(device))
                
        # Wait for all tasks to complete
        await asyncio.gather(*tasks)
        
        # Add skipped devices to results
        for device in devices:
            if device.device_id not in self.results:
                self.results[device.device_id] = {
                    'success': False,
                    'skipped': True,
                    'error': "Device does not have switch capability",
                    'name': device.name
                }
                
        return self.results
    
    async def _turn_on_device(self, device: Device):
        """Turn on a single device."""
        try:
            await device.turn_on()
            self.results[device.device_id] = {
                'success': True,
                'action': 'on',
                'name': device.name
            }
        except Exception as e:
            self.results[device.device_id] = {
                'success': False,
                'action': 'on',
                'error': str(e),
                'name': device.name
            }
    
    async def _turn_off_device(self, device: Device):
        """Turn off a single device."""
        try:
            await device.turn_off()
            self.results[device.device_id] = {
                'success': True,
                'action': 'off',
                'name': device.name
            }
        except Exception as e:
            self.results[device.device_id] = {
                'success': False,
                'action': 'off',
                'error': str(e),
                'name': device.name
            }


class RefreshAction(BatchAction):
    """Action to refresh device status."""
    
    def __init__(self, name: str = None):
        """Initialize a refresh action.
        
        Args:
            name: Optional name for this action
        """
        super().__init__(name or "RefreshDevices")
    
    async def execute(self, devices: List[Device]) -> Dict[str, Any]:
        """Execute the refresh action on the provided devices.
        
        Args:
            devices: List of Device objects to act upon
            
        Returns:
            Dictionary of results with device IDs as keys
        """
        self.results = {}
        
        # Execute in parallel
        tasks = []
        for device in devices:
            tasks.append(self._refresh_device(device))
                
        # Wait for all tasks to complete
        await asyncio.gather(*tasks)
                
        return self.results
    
    async def _refresh_device(self, device: Device):
        """Refresh a single device."""
        try:
            await device.refresh()
            self.results[device.device_id] = {
                'success': True,
                'action': 'refresh',
                'name': device.name
            }
        except Exception as e:
            self.results[device.device_id] = {
                'success': False,
                'action': 'refresh',
                'error': str(e),
                'name': device.name
            }


class LevelAction(BatchAction):
    """Action to set the level of dimmer devices."""
    
    def __init__(self, level: int, name: str = None):
        """Initialize a level action.
        
        Args:
            level: Level to set (0-100)
            name: Optional name for this action
        """
        if not (0 <= level <= 100):
            raise ValueError("Level must be between 0 and 100")
            
        super().__init__(name or f"SetLevel({level})")
        self.level = level
    
    async def execute(self, devices: List[Device]) -> Dict[str, Any]:
        """Execute the level action on the provided devices.
        
        Args:
            devices: List of Device objects to act upon
            
        Returns:
            Dictionary of results with device IDs as keys
        """
        self.results = {}
        
        # Filter to only devices with switchLevel capability
        level_devices = [d for d in devices if d.has_capability("switchLevel")]
        
        # Execute in parallel
        tasks = []
        for device in level_devices:
            tasks.append(self._set_level(device))
                
        # Wait for all tasks to complete
        await asyncio.gather(*tasks)
        
        # Add skipped devices to results
        for device in devices:
            if device.device_id not in self.results:
                self.results[device.device_id] = {
                    'success': False,
                    'skipped': True,
                    'error': "Device does not have switchLevel capability",
                    'name': device.name
                }
                
        return self.results
    
    async def _set_level(self, device: Device):
        """Set level for a single device."""
        try:
            await device.set_level(self.level)
            self.results[device.device_id] = {
                'success': True,
                'action': 'setLevel',
                'level': self.level,
                'name': device.name
            }
        except Exception as e:
            self.results[device.device_id] = {
                'success': False,
                'action': 'setLevel',
                'level': self.level,
                'error': str(e),
                'name': device.name
            }


class CustomAction(BatchAction):
    """Custom action that applies a user-provided function to each device."""
    
    def __init__(self, action_func: Callable[[Device], Any], name: str = None):
        """Initialize a custom action.
        
        Args:
            action_func: Function to apply to each device
            name: Optional name for this action
        """
        super().__init__(name or "CustomAction")
        self.action_func = action_func
    
    async def execute(self, devices: List[Device]) -> Dict[str, Any]:
        """Execute the custom action on the provided devices.
        
        Args:
            devices: List of Device objects to act upon
            
        Returns:
            Dictionary of results with device IDs as keys
        """
        self.results = {}
        
        # Execute in parallel
        tasks = []
        for device in devices:
            tasks.append(self._execute_action(device))
                
        # Wait for all tasks to complete
        await asyncio.gather(*tasks)
                
        return self.results
    
    async def _execute_action(self, device: Device):
        """Execute the custom action on a single device."""
        try:
            result = await self.action_func(device)
            self.results[device.device_id] = {
                'success': True,
                'action': 'custom',
                'result': result,
                'name': device.name
            }
        except Exception as e:
            self.results[device.device_id] = {
                'success': False,
                'action': 'custom',
                'error': str(e),
                'name': device.name
            }


class BatchActionRunner:
    """Runner for executing batch actions on device collections."""
    
    @staticmethod
    async def run_action(action: BatchAction, devices: List[Device]) -> Dict[str, Any]:
        """Run an action on a list of devices.
        
        Args:
            action: BatchAction object to run
            devices: List of Device objects to act upon
            
        Returns:
            Dictionary of results with device IDs as keys
        """
        return await action.execute(devices)
    
    @staticmethod
    def print_results(action: BatchAction):
        """Print the results of an action.
        
        Args:
            action: BatchAction object with results to print
        """
        results = action.get_results()
        success_count = sum(1 for r in results.values() if r.get('success', False))
        skip_count = sum(1 for r in results.values() if r.get('skipped', False))
        error_count = len(results) - success_count - skip_count
        
        print(f"\nAction: {action.name}")
        print(f"Total devices: {len(results)}")
        print(f"Successful: {success_count}")
        print(f"Skipped: {skip_count}")
        print(f"Errors: {error_count}")
        
        if error_count > 0:
            print("\nErrors:")
            for device_id, result in results.items():
                if not result.get('success', False) and not result.get('skipped', False):
                    print(f"  {result.get('name', device_id)}: {result.get('error', 'Unknown error')}")
