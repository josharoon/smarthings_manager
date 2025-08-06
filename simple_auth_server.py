# /media/josh/data1/smarrthings_controller/simple_auth_server.py

from flask import Flask, request
from typing import Optional
import codecs
import requests

# Import the official SmartApp SDK classes
from smartapp.interface import (
    ConfigurationRequest,
    ConfirmationRequest,
    EventRequest,
    EventType,
    InstallRequest,
    OauthCallbackRequest,
    SmartAppEventHandler,
    UninstallRequest,
    UpdateRequest,
    ConfigSection,
    SmartAppConfigPage,
    SmartAppDefinition,
    DeviceSetting,
)
from smartapp.dispatcher import SmartAppDispatcher
from smartapp.interface import SmartAppRequestContext

# --- 1. Define App Event Handler Class ---
# This class will handle all SmartThings lifecycle events.

class EventHandler(SmartAppEventHandler):
    """SmartApp event handler implementation."""
    
    def handle_confirmation(self, correlation_id: Optional[str], request: ConfirmationRequest) -> None:
        """Handle a CONFIRMATION lifecycle request"""
        print(f"CONFIRMATION request received: {request}")
        
        # Extract and log the confirmation URL
        confirmation_url = request.confirmation_data.confirmation_url
        app_id = request.confirmation_data.app_id
        print(f"App ID: {app_id}")
        print(f"Confirmation URL: {confirmation_url}")
        
        # Automatically make a GET request to the confirmation URL
        import requests
        try:
            print(f"Sending GET request to confirmation URL...")
            response = requests.get(confirmation_url)
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
        except Exception as e:
            print(f"Error making confirmation request: {e}")
        
    def handle_configuration(self, correlation_id: Optional[str], request: ConfigurationRequest) -> None:
        """Handle a CONFIGURATION lifecycle request."""
        print(f"CONFIGURATION request received: {request}")
        # No action needed as the dispatcher handles the configuration response
        
    def handle_install(self, correlation_id: Optional[str], request: InstallRequest) -> None:
        """Handle an INSTALL lifecycle request."""
        print(f"INSTALL event received: {request}")
        
        # Extract selected devices from the configuration
        try:
            # Get the auth token from the request
            auth_token = request.token()
            
            # Get the app ID
            app_id = request.app_id()
            
            # Get the selected devices
            sensor_devices = request.as_devices("sensors")
            light_devices = request.as_devices("lights")
            
            print(f"Selected sensor devices: {sensor_devices}")
            print(f"Selected light devices: {light_devices}")
            
            # Set up subscriptions to device events
            # In a real app, you would make API calls to SmartThings to create subscriptions
            # For example:
            # create_subscription(auth_token, app_id, device_id, capability, attribute)
            
            print("Device subscriptions would be set up here in a complete app")
        except Exception as e:
            print(f"Error in handle_install: {e}")
        
    def handle_update(self, correlation_id: Optional[str], request: UpdateRequest) -> None:
        """Handle an UPDATE lifecycle request."""
        print(f"UPDATE event received: {request}")
        # No action needed for a basic app, just acknowledge the event.
        
    def handle_uninstall(self, correlation_id: Optional[str], request: UninstallRequest) -> None:
        """Handle an UNINSTALL lifecycle request."""
        print(f"UNINSTALL event received: {request}")
        # No action needed, just acknowledge the event.
        
    def handle_oauth_callback(self, correlation_id: Optional[str], request: OauthCallbackRequest) -> None:
        """Handle an OAUTH_CALLBACK lifecycle request."""
        print(f"OAUTH_CALLBACK event received: {request}")
        # No action needed for a basic app
        
    def handle_event(self, correlation_id: Optional[str], request: EventRequest) -> None:
        """Handle an EVENT lifecycle request."""
        print(f"EVENT received: {request}")
        
        try:
            # Get the auth token to make API calls
            auth_token = request.token()
            
            # Process device events
            device_events = request.event_data.for_type(EventType.DEVICE_EVENT)
            if device_events:
                for event in device_events:
                    device_id = event.get("deviceId")
                    component_id = event.get("componentId")
                    capability = event.get("capability")
                    attribute = event.get("attribute")
                    value = event.get("value")
                    
                    print(f"Device event: device_id={device_id}, component={component_id}, "
                          f"capability={capability}, attribute={attribute}, value={value}")
                    
                    # Example: If a sensor turns on, turn on the lights
                    if attribute == "switch" and value == "on":
                        # In a real app, you would make API calls to control devices
                        # For example:
                        # control_device(auth_token, light_device_id, "switch", "on")
                        print(f"Would turn on lights in response to sensor {device_id} turning on")
                    
        except Exception as e:
            print(f"Error in handle_event: {e}")


# --- 2. Define SmartApp Definition ---
definition = SmartAppDefinition(
    id="josh_basic_app_v1",
    name="My First Python SmartApp",
    description="A basic webhook app built with Python and Flask.",
    target_url="https://e0d71a3c4664.ngrok-free.app/", # Your ngrok public URL
    permissions=["r:devices:*", "x:devices:*"],  # Read and execute device permissions
    config_pages=[
        SmartAppConfigPage(
            page_name="Device Selection",
            sections=[
                ConfigSection(
                    name="When these devices change...",
                    settings=[
                        DeviceSetting(
                            id="sensors",
                            name="Select sensors",
                            description="Select devices to monitor",
                            required=True,
                            multiple=True,
                            capabilities=["switch"],
                            permissions=["r"]
                        )
                    ]
                ),
                ConfigSection(
                    name="Then do this...",
                    settings=[
                        DeviceSetting(
                            id="lights",
                            name="Select lights",
                            description="Select lights to control",
                            required=True,
                            multiple=True,
                            capabilities=["switch"],
                            permissions=["r", "x"]
                        )
                    ]
                )
            ]
        )
    ],
)

# --- 3. Create Dispatcher with X.509 Certificate Verification ---
from smartapp.interface import SmartAppDispatcherConfig

# Create dispatcher config with explicit settings - disable signature verification during development
dispatcher_config = SmartAppDispatcherConfig(
    check_signatures=False,  # Disable signature verification for development/testing
    clock_skew_sec=300,     # Allow 5 minutes of clock skew
    keyserver_url="https://key.smartthings.com",  # SmartThings key server URL
    log_json=True,          # Log JSON data for debugging
)

# Create the dispatcher with our config
dispatcher = SmartAppDispatcher(
    definition=definition, 
    event_handler=EventHandler(),
    config=dispatcher_config
)

# --- 4. Set up Flask Web Server ---
app = Flask(__name__)

# Handle all POST requests at any path
@app.route("/", methods=["POST"])
@app.route("/<path:path>", methods=["POST"])
def webhook(path=""):
    """Handles all incoming webhook requests from SmartThings."""
    print(f"Received POST request at path: /{path}")
    # Convert Flask headers to a dictionary for the SDK
    headers = dict(request.headers)
    body = codecs.decode(request.data, "UTF-8")
    print(f"Request body: {body}")
    
    # Direct handling for confirmation requests to ensure they're processed
    try:
        import json
        data = json.loads(body)
        
        if data.get("lifecycle") == "CONFIRMATION":
            print("Detected CONFIRMATION lifecycle directly from request")
            confirmation_url = data.get("confirmationData", {}).get("confirmationUrl")
            app_id = data.get("confirmationData", {}).get("appId")
            
            if confirmation_url:
                print(f"App ID: {app_id}")
                print(f"Confirmation URL: {confirmation_url}")
                
                # Make GET request to confirmation URL
                try:
                    print(f"Sending GET request directly to confirmation URL: {confirmation_url}")
                    response = requests.get(confirmation_url)
                    print(f"Direct response status: {response.status_code}")
                    print(f"Direct response body: {response.text}")
                    
                    # Return a success response
                    return json.dumps({"targetUrl": definition.target_url})
                except Exception as e:
                    print(f"Error making direct confirmation request: {e}")
    except Exception as e:
        print(f"Error in direct confirmation handling: {e}")
    
    # Standard processing through the dispatcher
    context = SmartAppRequestContext(headers=headers, body=body)
    try:
        response_body = dispatcher.dispatch(context=context)
        return response_body
    except Exception as e:
        print(f"Error in dispatcher: {e}")
        # Fall back to a simple OK response if the dispatcher fails
        return "{}"

# Handle all GET requests at any path
@app.route("/", methods=["GET"])
@app.route("/<path:path>", methods=["GET"])
def info(path=""):
    """Provide a simple endpoint for testing the server."""
    print(f"Received GET request at path: /{path}")
    return "SmartThings webhook server is running. Use POST to interact with the SmartApp."


if __name__ == "__main__":
    print("Starting SmartApp server on port 8080...")
    app.run(host="0.0.0.0", port=8080, debug=True)