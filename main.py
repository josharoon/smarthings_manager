import asyncio
from smart_things_controller import SmartThingsController
from devices import Device, Switch, BatteryDevice
from config import get_token


async def main():
    """
    Main function to run the SmartThings application.
    """
    token = get_token()
    controller = SmartThingsController(token)
    
    try:
        # Get all raw device objects from the API
        all_st_devices = await controller.get_all_devices()
        if not all_st_devices:
            print("No devices found or unable to retrieve devices.")
            return

        # --- 1. List All Registered Devices ---
        print(f"\n--- All Registered Devices ({len(all_st_devices)}) ---")
        all_devices = []
        for d in all_st_devices:
            try:
                device = Device(d)
                all_devices.append(device)
                print(device)
            except Exception as e:
                print(f"Error processing device: {e}")
        
        # --- 2. Find Offline Devices ---
        print("\n--- Offline Devices ---")
        offline_devices = [d for d in all_devices if not d.is_online()]
        if not offline_devices:
            print("All devices are online.")
        else:
            for device in offline_devices:
                print(device)
        
        # --- 3. Report on Battery Levels ---
        print("\n--- 🔋 Battery-Powered Devices ---")
        battery_devices = []
        for d in all_st_devices:
            try:
                if hasattr(d, 'capabilities') and "battery" in d.capabilities:
                    battery_devices.append(BatteryDevice(d))
            except Exception as e:
                print(f"Error checking battery capability: {e}")
        
        if not battery_devices:
            print("No devices with battery reporting found.")
        else:
            for device in battery_devices:
                print(device)

        # --- 4. Control and Report on Switches ---
        print("\n--- 💡 Switches ---")
        switches = []
        for d in all_st_devices:
            try:
                if (hasattr(d, 'capabilities') and "switch" in d.capabilities and 
                    hasattr(d, 'status') and hasattr(d.status, 'is_online') and d.status.is_online):
                    switches.append(Switch(d))
            except Exception as e:
                print(f"Error checking switch capability: {e}")
        
        if not switches:
            print("No online switches found.")
        else:
            # Report on all switches
            for switch in switches:
                print(f"Switch Found: {switch}")
            
            # Example: Toggle the first switch found
            first_switch = switches[0]
            print(f"\n>>> Controlling '{first_switch.name}'...")
            current_state = first_switch.state
            print(f"Current state is {current_state.upper()}. Toggling now...")
            if current_state == 'on':
                await first_switch.turn_off()
            else:
                await first_switch.turn_on()
            
            # Refresh status to confirm the change
            await first_switch._st_device.refresh()
            print(f"✅ New state: {Switch(first_switch._st_device)}")


    except ConnectionError as e:
        print(f"Connection Error: {e}")
    except TypeError as e:
        print(f"Type Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


import asyncio

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except RuntimeError:
        # For environments where a loop is already running (e.g., Jupyter)
        asyncio.ensure_future(main())