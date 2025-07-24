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
