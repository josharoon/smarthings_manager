#!/bin/bash

# This script helps set up the SmartThings token as an environment variable
# and tests the token to verify it works

echo "🔧 SmartThings Token Setup"
echo "=========================="

# Check if a token was provided as an argument
if [ -z "$1" ]; then
    echo "❌ No token provided!"
    echo "Usage: ./setup_token.sh YOUR_SMARTTHINGS_TOKEN"
    echo "You can get a token by following the instructions in docs/get_smartthings_token.md"
    exit 1
fi

# Save the token to a .env file
echo "SMARTTHINGS_TOKEN=$1" > .env
echo "✅ Token saved to .env file"

# Export the token as an environment variable for the current session
export SMARTTHINGS_TOKEN=$1
echo "✅ Token exported as environment variable"

# Run the token check script
echo -e "\n🔍 Testing token..."
python check_token.py

# Final instructions
echo -e "\n📝 Next steps:"
echo "1. Add this line to your .gitignore file to keep your token safe:"
echo "   .env"
echo "2. To use this token in future sessions, run:"
echo "   source .env"
echo "3. Now you can run your SmartThings scripts:"
echo "   python status_report.py"
