#!/usr/bin/env python
"""
Test script for the watering controller's interaction with the SmartThings Rules API.
This script tests creating, retrieving, and deleting rules using the actual API.
"""

import json
import time
import requests
from datetime import datetime
import config
from watering_controller import RULE_NAME_PREFIX, RULES_ENDPOINT, LOCATION_ID

# Test configuration
TEST_RULE_PREFIX = f"{RULE_NAME_PREFIX} - TEST"
TEST_DEVICE_ID = "09d78e71-e601-4f0c-89ef-066014f840e4"  # A known basic-switch device

def test_rules_api():
    """
    Run comprehensive tests against the SmartThings Rules API.
    """
    token = config.get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # We can track pass/fail counts here if needed, but for now, let's just run the flow.
    print("=" * 70)
    print(f"SMARTTHINGS RULES API TEST - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    print("\n📡 TEST 1: API Connection")
    if not test_api_connection(headers):
        print("❌ CRITICAL: API Connection failed. Aborting all tests.")
        return

    print("\n📝 TEST 2: Create Multiple Rule Types")
    created_rule_ids = test_create_rules(headers)

    if not created_rule_ids:
        print("\n⚠️  No rules were created successfully. Skipping retrieval and deletion tests.")
    else:
        print("\n🔍 TEST 3: Retrieve Created Rules")
        test_retrieve_rules(headers, created_rule_ids)

        print("\n🗑️ TEST 4: Delete Created Rules (Cleanup)")
        test_delete_rules(headers, created_rule_ids)
    
    print("\n" + "=" * 70)
    print("TESTING COMPLETE.")
    print("=" * 70)


def test_api_connection(headers):
    try:
        url = f"{RULES_ENDPOINT}?locationId={LOCATION_ID}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        print("✅ SUCCESS: Connected to Rules API")
        return True
    except requests.exceptions.HTTPError as e:
        print(f"❌ ERROR: Connection failed. Status: {e.response.status_code}, Response: {e.response.text[:200]}...")
        return False

def test_create_rules(headers):
    """
    Attempts to create a series of rules with increasing complexity.
    It will not abort if one rule fails to create.
    """
    created_rule_ids = {}
    url = f"{RULES_ENDPOINT}?locationId={LOCATION_ID}"

    # --- Load all rule payloads from JSON files ---
    with open("command_only_action.json", "r") as f:
        command_only_payload = json.load(f)
        command_only_payload["name"] = f"{TEST_RULE_PREFIX}-1-COMMAND-ONLY-{int(time.time())}"

    with open("device_state_if_action.json", "r") as f:
        device_state_if_payload = json.load(f)
        device_state_if_payload["name"] = f"{TEST_RULE_PREFIX}-2-DEVICE-IF-{int(time.time())}"

    with open("time_schedule_if_action.json", "r") as f:
        time_schedule_if_payload = json.load(f)
        time_schedule_if_payload["name"] = f"{TEST_RULE_PREFIX}-3-TIME-IF-{int(time.time())}"

    rule_tests = [
        {
            "name": "1-Command-Only",
            "payload": command_only_payload
        },
        {
            "name": "2-Device-State-IF",
            "payload": device_state_if_payload
        },
        {
            "name": "3-Time-Schedule-IF",
            "payload": time_schedule_if_payload
        }
    ]

    # --- Loop through tests and attempt to create each rule ---
    for test in rule_tests:
        print("-" * 30)
        print(f"Attempting to create rule: '{test['name']}'")
        try:
            response = requests.post(url, headers=headers, json=test['payload'])
            response.raise_for_status()
            rule_id = response.json().get("id")
            created_rule_ids[test['name']] = rule_id
            print(f"✅ SUCCESS: Created rule with ID: {rule_id}")
        except requests.exceptions.HTTPError as e:
            print(f"❌ FAILED to create rule '{test['name']}'. Status: {e.response.status_code}")
            print(f"   Response: {e.response.text}")

    return created_rule_ids


def test_retrieve_rules(headers, created_rule_ids):
    try:
        print("Retrieving rules to verify creation...")
        url = f"{RULES_ENDPOINT}?locationId={LOCATION_ID}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        all_rule_ids_from_api = {rule.get("id") for rule in response.json().get("items", [])}
        
        all_found = True
        for rule_type, rule_id in created_rule_ids.items():
            is_found = rule_id in all_rule_ids_from_api
            print(f"VERIFYING: Found '{rule_type}' rule (ID: {rule_id}): {'✅ Found' if is_found else '❌ NOT FOUND'}")
            if not is_found:
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"❌ ERROR: Exception during rule retrieval: {e}")
        return False

def test_delete_rules(headers, rule_ids):
    success = True
    print("Attempting to delete all successfully created rules...")
    for rule_type, rule_id in rule_ids.items():
        if not rule_id: continue
        try:
            url = f"{RULES_ENDPOINT}/{rule_id}?locationId={LOCATION_ID}"
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            print(f"✅ SUCCESS: Deleted '{rule_type}' rule.")
        except Exception as e:
            print(f"❌ ERROR: Failed to delete '{rule_type}' rule {rule_id}. Reason: {e}")
            success = False
    return success

if __name__ == "__main__":
    test_rules_api()