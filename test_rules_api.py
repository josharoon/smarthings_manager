#!/usr/bin/env python
"""
A simple script to test if a SmartThings API token has permissions
to read rules, including the required locationId.
"""

import asyncio
import aiohttp
from config import get_token

async def get_first_location_id(session, token):
    """Fetches the ID of the first available location."""
    print("Fetching location ID...")
    locations_url = "https://api.smartthings.com/v1/locations"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        async with session.get(locations_url, headers=headers) as response:
            response.raise_for_status()
            locations_data = await response.json()
            if locations_data.get('items'):
                location_id = locations_data['items'][0]['locationId']
                print(f"Found Location ID: {location_id}")
                return location_id
            else:
                print("No locations found for this account.")
                return None
    except Exception as e:
        print(f"Failed to get location ID: {e}")
        return None

async def test_rules_permission():
    """
    Tests if the provided SmartThings token can read the Rules API.
    """
    token = get_token()
    if not token or "YOUR_SMARTTHINGS_API_TOKEN" in token:
        print("🚨 ERROR: SmartThings token not found or is set to the default.")
        return

    print("🔑 Testing SmartThings token against the Rules API...")

    async with aiohttp.ClientSession() as session:
        # 1. Get the Location ID first
        location_id = await get_first_location_id(session, token)
        if not location_id:
            print("Could not proceed without a Location ID.")
            return

        # 2. Now, test the Rules API with the locationId
        headers = {"Authorization": f"Bearer {token}"}
        rules_url = f"https://api.smartthings.com/v1/rules?locationId={location_id}"
        
        print(f"\nQuerying Rules API with URL: {rules_url}")

        try:
            async with session.get(rules_url, headers=headers) as response:
                status = response.status
                
                if status == 200:
                    print("\n✅ SUCCESS: Token is valid and has permission to read rules.")
                    data = await response.json()
                    rule_count = len(data.get('items', []))
                    print(f"Found {rule_count} rule(s) in your location.")

                elif status == 401:
                    print("\n❌ FAILED: Authentication failed (401 Unauthorized).")

                elif status == 403:
                    print("\n❌ FAILED: Permission denied (403 Forbidden).")
                    print("The token is valid, but something is still wrong (check scopes or location).")
                
                else:
                    error_text = await response.text()
                    print(f"\n❌ FAILED: Received unexpected status code {status}.")
                    print(f"Response: {error_text[:200]}...")

        except Exception as e:
            print(f"\n❌ FAILED: An unexpected error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(test_rules_permission())