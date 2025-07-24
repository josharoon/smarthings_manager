#!/usr/bin/env python
"""
Command to list all the rooms in a SmartThings home.
"""

import asyncio
import os
import sys
from smart_things_controller import SmartThingsController
from config import get_token


async def list_rooms():
    """List all rooms in the SmartThings home."""
    # Get token from config
    token = get_token()
    
    # Initialize controller
    controller = SmartThingsController(token)
    
    # Get and print rooms
    await controller.list_rooms()


if __name__ == "__main__":
    try:
        # Handle the event loop properly for all Python versions
        if sys.version_info >= (3, 11):
            # Python 3.11+
            asyncio.run(list_rooms())
        else:
            # Python 3.10 and earlier
            loop = asyncio.get_event_loop()
            loop.run_until_complete(list_rooms())
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
