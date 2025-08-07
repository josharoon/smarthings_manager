from flask import Flask, request, jsonify
import yaml
from apscheduler.schedulers.background import BackgroundScheduler
import json
import os
import requests
from watering_controller import WateringController

app = Flask(__name__)

INSTALLATIONS_FILE = "installations.json"
installations = {}

def load_installations():
    global installations
    if os.path.exists(INSTALLATIONS_FILE):
        with open(INSTALLATIONS_FILE, "r") as f:
            installations = json.load(f)

def save_installations():
    with open(INSTALLATIONS_FILE, "w") as f:
        json.dump(installations, f, indent=4)

scheduler = BackgroundScheduler()
scheduler.start()

import sys

def run_watering_check(installed_app_id):
    """Run the daily watering check for a given installation."""
    print(f"Running daily watering check for {installed_app_id}")
    sys.stdout.flush()
    if installed_app_id not in installations:
        print(f"Error: Installation {installed_app_id} not found.")
        sys.stdout.flush()
        return

    installation = installations[installed_app_id]

    controller = WateringController(
        token=installation["auth_token"],
        switch_device_id=installation["water_switch_id"],
        location_id=installation["location_id"]
    )

    controller.create_rules_based_on_weather()

def handle_install(data):
    install_data = data.get("installData", {})
    print(f"Install data: {install_data}")
    sys.stdout.flush()
    installed_app = install_data.get("installedApp", {})
    print(f"Installed app: {installed_app}")
    sys.stdout.flush()
    installed_app_id = installed_app.get("installedAppId")
    auth_token = install_data.get("authToken")
    refresh_token = install_data.get("refreshToken")
    location_id = installed_app.get("locationId")

    # Get the selected water switch from the config
    water_switch_config = installed_app.get("config", {}).get("water_switch", [])
    water_switch_id = None
    if water_switch_config and water_switch_config[0].get("valueType") == "DEVICE":
        water_switch_id = water_switch_config[0].get("deviceConfig", {}).get("deviceId")

    if not all([installed_app_id, auth_token, location_id, water_switch_id]):
        return jsonify({"statusCode": 400, "message": "Missing required installation data"})

    installations[installed_app_id] = {
        "auth_token": auth_token,
        "refresh_token": refresh_token,
        "location_id": location_id,
        "water_switch_id": water_switch_id
    }
    save_installations()

    # Schedule daily job
    scheduler.add_job(
        run_watering_check,
        "cron",
        hour=5, # Run at 5 AM
        args=[installed_app_id],
        id=installed_app_id,
        replace_existing=True
    )

    return jsonify({"installData": {}})


def handle_update(data):
    # For now, treat update the same as install
    return handle_install(data)

def handle_uninstall(data):
    uninstall_data = data.get("uninstallData", {})
    installed_app_id = uninstall_data.get("installedApp", {}).get("installedAppId")

    if not installed_app_id or installed_app_id not in installations:
        return jsonify({"statusCode": 400, "message": "Invalid installation ID"})

    installation = installations[installed_app_id]

    # Clean up rules
    controller = WateringController(
        token=installation["auth_token"],
        switch_device_id=installation["water_switch_id"],
        location_id=installation["location_id"]
    )
    existing_rules = controller.get_existing_rules()
    if existing_rules:
        rule_ids = [rule["id"] for rule in existing_rules]
        controller.delete_rules(rule_ids)

    # Remove scheduled job
    scheduler.remove_job(installed_app_id, ignore_if_missing=True)

    # Remove installation data
    del installations[installed_app_id]
    save_installations()

    return jsonify({"uninstallData": {}})

def handle_configuration(data):
    config_phase = data.get("configurationData", {}).get("phase")
    if config_phase == "INITIALIZE":
        return initialize_response()
    elif config_phase == "PAGE":
        return page_response(data)
    else:
        # Should not happen
        return jsonify({"statusCode": 400, "message": "Invalid configuration phase"})

def initialize_response():
    return jsonify({
        "configurationData": {
            "initialize": {
                "name": "Weather-Based Watering",
                "description": "Automatically water your garden based on the weather forecast.",
                "id": "watering-app",
                "permissions": [
                    "r:devices:*",
                    "w:devices:*",
                    "r:rules:*",
                    "w:rules:*"
                ],
                "firstPageId": "mainPage"
            }
        }
    })

def page_response(data):
    page_id = data.get("configurationData", {}).get("pageId")
    if page_id == "mainPage":
        return main_page_response()
    else:
        # Should not happen
        return jsonify({"statusCode": 400, "message": "Invalid page ID"})

def main_page_response():
    return jsonify({
        "configurationData": {
            "page": {
                "pageId": "mainPage",
                "name": "Configure Your Watering System",
                "nextPageId": None, # This is the last page
                "previousPageId": None, # This is the first page
                "complete": True,
                "sections": [
                    {
                        "name": "Select Your Location",
                        "settings": [
                            {
                                "id": "location",
                                "name": "SmartThings Location",
                                "description": "Select the location for this SmartApp.",
                                "type": "LOCATION",
                                "required": True
                            }
                        ]
                    },
                    {
                        "name": "Select Your Water Switch",
                        "settings": [
                            {
                                "id": "water_switch",
                                "name": "Water Switch",
                                "description": "Select the switch that controls your watering system.",
                                "type": "DEVICE",
                                "required": True,
                                "multiple": False,
                                "capabilities": ["switch"],
                                "permissions": ["r", "w", "x"]
                            }
                        ]
                    }
                ]
            }
        }
    })

def verify_signature(request):
    # Placeholder for signature verification
    return True

@app.route("/", methods=["POST"])
def handle_request():
    if not verify_signature(request):
        return "Unauthorized", 401

    try:
        data = request.get_json()
        lifecycle = data.get("lifecycle")
        print(f"Received {lifecycle} event")
        sys.stdout.flush()

        if lifecycle == "PING":
            challenge = data.get("pingData", {}).get("challenge")
            return jsonify({"statusCode": 200, "pingData": {"challenge": challenge}})
        elif lifecycle == "CONFIRMATION":
            confirmation_url = data.get("confirmationData", {}).get("confirmationUrl")
            if confirmation_url:
                print(f"Confirmation URL: {confirmation_url}")
                try:
                    requests.get(confirmation_url)
                    print("Confirmation request sent.")
                except Exception as e:
                    print(f"Error sending confirmation request: {e}")
            return jsonify({"statusCode": 200})
        elif lifecycle == "CONFIGURATION":
            return handle_configuration(data)
        elif lifecycle == "INSTALL":
            return handle_install(data)
        elif lifecycle == "UPDATE":
            return handle_update(data)
        elif lifecycle == "UNINSTALL":
            return handle_uninstall(data)
        else:
            print(f"Received unhandled event: {data}")
            return jsonify({"statusCode": 200})
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"statusCode": 500, "message": "Internal Server Error"})

if __name__ == "__main__":
    load_installations()
    # Reschedule jobs for existing installations
    for app_id in installations:
        scheduler.add_job(
            run_watering_check,
            "cron",
            hour=5, # Run at 5 AM
            args=[app_id],
            id=app_id,
            replace_existing=True
        )
    app.run(port=8000, debug=False)
