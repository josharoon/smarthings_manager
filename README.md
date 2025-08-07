# SmartThings Controller

A Python application to control SmartThings devices.

## Setup

1. Clone this repository
2. Activate the virtual environment:
   ```bash
   # On Linux/macOS
   source .venv/bin/activate
   
   # On Windows
   .venv\Scripts\activate
   ```
3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up your SmartThings API token:
   - Create a SmartThings Personal Access Token in the [SmartThings Developer Workspace](https://account.smartthings.com/tokens)
   - Use the token in one of the following ways:
     - Set as environment variable: `export SMARTTHINGS_TOKEN="your-token-here"`
     - Pass directly to commands with the `--token` parameter
     - Edit the default token in the script files

## Usage

### Main Application

Run the main application to see all your devices:
```bash
python main.py
```

### Device Status Report

Generate a report of online and offline devices:
```bash
python status_report.py
```

Show only offline devices:
```bash
python status_report.py --offline
```

Show only online devices:
```bash
python status_report.py --online
```

### Device Filtering

The filtering system allows you to find devices based on multiple criteria:

```bash
# Show devices in a specific room
./filter_cli.py --room "Living Room"

# Show offline devices
./filter_cli.py --offline

# Show offline devices in a specific room
./filter_cli.py --offline --room "Living Room"

# Filter by name (substring match)
./filter_cli.py --name "sensor"

# Show devices with battery below a threshold
./filter_cli.py --battery-below 30

# Save filtered devices to a collection
./filter_cli.py --offline --save "offline-devices"

# Load a saved collection
./filter_cli.py --load "offline-devices"

# List all saved collections
./filter_cli.py --list-collections

# Delete a collection
./filter_cli.py --delete-collection "offline-devices"

# Display additional information
./filter_cli.py --offline --show-ids --summary
```

### Batch Actions

Execute actions on multiple devices at once:

```bash
# Turn on all lights in the living room
./batch_action_cli.py --filter --room "Living Room" --turn-on

# Turn off all offline devices from a saved collection
./batch_action_cli.py --collection "offline-devices" --turn-off

# Set brightness level for all lights in a room
./batch_action_cli.py --filter --room "Bedroom" --set-level 50

# Refresh status of all devices
./batch_action_cli.py --filter --refresh
```

## SmartApp Mode (for Watering Controller)

The watering controller can be run as a persistent SmartApp, which is the recommended approach for automated, long-running tasks. This avoids the need for 24-hour Personal Access Tokens and allows for a more robust, event-driven architecture.

### How It Works

The SmartApp is a web server that responds to lifecycle events from the SmartThings platform. When you install the app, it schedules a daily job to check the weather and create or delete watering rules accordingly.

### Running the SmartApp Server

1.  **Install Dependencies:**
    Make sure you have all the required dependencies installed:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Server:**
    Start the SmartApp server:
    ```bash
    python watering_app.py
    ```
    The server will run on `localhost:8000` by default.

3.  **Expose to the Internet:**
    For SmartThings to be able to send webhooks to your server, it needs to be accessible from the public internet. For local development, you can use a tool like [ngrok](https://ngrok.com/) to create a secure tunnel to your local server.
    ```bash
    ngrok http 8000
    ```
    ngrok will provide you with a public URL (e.g., `https://your-unique-id.ngrok.io`). You will use this URL when you register your SmartApp in the SmartThings Developer Workspace.

4.  **Register the SmartApp:**
    In the SmartThings Developer Workspace, create a new SmartApp and select "Webhook App" as the hosting type. Use the ngrok URL as your webhook URL.

5.  **Installation:**
    Once the app is registered, you can install it using the SmartThings mobile app. During the installation, you will be prompted to select your location and the water switch you want to control.

## Configuration

### Directory Structure

Collections of devices are saved in the `~/.smartthings/collections` directory by default. You can modify this location in the script files if needed.

### Adding Custom Filters and Actions

To extend the functionality:

- Add new filter types in `filters.py` by creating new classes that inherit from `DeviceFilter`
- Add new batch actions in `actions.py` by creating new classes that inherit from `BatchAction`

## Development

This project uses a Python virtual environment to manage dependencies.

### Project Structure

- `smart_things_controller.py`: Core controller for SmartThings API
- `devices.py`: Device class definitions and capabilities
- `filters.py`: Filtering system for devices
- `device_collection.py`: Collection management for devices
- `actions.py`: Batch actions implementation
- `filter_cli.py`: Command-line interface for filtering
- `batch_action_cli.py`: Command-line interface for batch actions
- `status_report.py`: Simple status reporting tool
