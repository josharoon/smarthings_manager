# Device Filtering and Batch Actions: Implementation Plan

## Overview

Adding the ability to filter devices by multiple criteria and perform batch actions on the filtered devices would significantly enhance the SmartThings Controller's functionality. This feature would allow users to find specific devices (e.g., offline devices in a particular room) and execute actions on them as a group.

## Step-by-Step Implementation Plan

### Phase 1: Implement Enhanced Device Filtering System

#### Step 1: Define Filter Criteria Classes
1. Create a new file `filters.py` to implement a flexible filtering system
2. Design a base `DeviceFilter` class with a standard interface
3. Implement specific filter classes for different criteria:
   - `RoomFilter`: Filter devices by room name
   - `StatusFilter`: Filter devices by online/offline status
   - `BatteryLevelFilter`: Filter devices by battery percentage
   - `CapabilityFilter`: Filter devices by their capabilities
   - `NameFilter`: Filter devices by name (exact, contains, regex)
   - `TypeFilter`: Filter devices by device type

#### Step 2: Implement Filter Combination Logic
1. Add methods to combine filters with logical operators (AND, OR, NOT)
2. Create a `FilterGroup` class that applies multiple filters with specified logic
3. Implement a fluent interface for building complex filter chains

#### Step 3: Extend the SmartThingsController Class
1. Add a new `find_devices()` method that accepts filter criteria
2. Update existing methods to leverage the new filtering system
3. Add helper methods for common filter combinations

### Phase 2: Create a Device Collection System

#### Step 4: Implement a DeviceCollection Class
1. Create a new file `device_collection.py`
2. Design a `DeviceCollection` class to manage groups of devices
3. Add methods for:
   - Adding/removing devices
   - Applying filters to create sub-collections
   - Checking collection properties (size, types of devices, etc.)

#### Step 5: Add Persistence for Device Collections
1. Implement methods to save collections to disk
2. Add functionality to load saved collections
3. Create a naming/tagging system for collections

### Phase 3: Implement Batch Actions

#### Step 6: Define the Action Framework
1. Create a new file `actions.py`
2. Design a base `DeviceAction` class with a standard interface
3. Implement specific action classes:
   - `SwitchAction`: Turn devices on/off
   - `RefreshAction`: Refresh device status
   - `DeleteAction`: Delete devices from SmartThings
   - Additional actions based on device capabilities

#### Step 7: Add Batch Execution to Device Collections
1. Add methods to execute actions on all devices in a collection
2. Implement error handling for failed actions
3. Create a system for reporting action results

### Phase 4: Build a Command-Line Interface

#### Step 8: Create a Command-Line Tool
1. Create a new file `filter_cli.py`
2. Implement command-line arguments for filtering devices
3. Add support for saving filtered devices to named collections
4. Implement commands for executing batch actions on collections

#### Step 9: Design a Query Language
1. Create a simple query language for complex filtering
2. Implement a parser for the query language
3. Add examples and documentation

### Phase 5: User Experience and Documentation

#### Step 10: Add User-Friendly Features
1. Add progress indicators for long-running operations
2. Implement confirmation prompts for destructive actions
3. Add informative error messages

#### Step 11: Update Documentation
1. Update the README with examples of filtering and batch actions
2. Create a new documentation file specifically for filtering capabilities
3. Add docstrings to all new classes and methods

## Example Usage Scenarios

Once implemented, this system would enable commands like:

```bash
# Find all offline devices in the Living Room
python filter_cli.py --room "Living Room" --offline

# Save offline smoke detectors to a collection
python filter_cli.py --offline --device-type "smoke detector" --save-as "offline_smoke_detectors"

# Turn on all lights in the bedroom
python filter_cli.py --room "Bedroom" --capability "switch" --action switch-on

# Refresh all devices with battery below 20%
python filter_cli.py --battery-below 20 --action refresh

# Load a saved collection and turn devices off
python filter_cli.py --load offline_smoke_detectors.json --action switch-off
```

## Timeline Estimate

- **Phase 1 (Filtering System)**: 3-4 days
- **Phase 2 (Device Collection)**: 2-3 days
- **Phase 3 (Batch Actions)**: 3-4 days
- **Phase 4 (CLI)**: 2-3 days
- **Phase 5 (Documentation & Refinement)**: 1-2 days

**Total**: Approximately 2-3 weeks for full implementation

## First Milestone

To deliver value quickly, we'll implement Phase 1 and parts of Phase 4 first. This provides a functional filtering system with CLI access, allowing search for devices with multiple criteria before the full batch action framework is in place.
