#!/bin/bash
# This script sets up a cron job for daily watering controller updates

# Get script directory
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")

# Create crontab entry for daily execution at 6:00 AM
CRON_ENTRY="0 6 * * * cd $SCRIPT_DIR && $SCRIPT_DIR/daily_watering_update.py >> $SCRIPT_DIR/watering_cron.log 2>&1"

# Check if entry already exists
if crontab -l 2>/dev/null | grep -q "daily_watering_update.py"; then
    echo "Cron job already exists for watering controller."
else
    # Add to crontab
    (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
    echo "Cron job added: Watering controller will run daily at 6:00 AM."
fi

echo "Cron setup complete."
