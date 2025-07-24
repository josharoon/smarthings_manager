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

## Development

This project uses a Python virtual environment to manage dependencies.
