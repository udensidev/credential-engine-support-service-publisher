#!/bin/bash

# Clear the terminal for a fresh view
clear

# Print header
echo "Launching the University Support Service Publisher 🚀"
echo "-----------------------------------------------------"

# Step 0: Check Python Version (at least 3.8 recommended)
REQUIRED_PYTHON="3.8"
CURRENT_PYTHON=$(python3 --version 2>&1 | awk '{print $2}')

if [[ "$(printf '%s\n' "$REQUIRED_PYTHON" "$CURRENT_PYTHON" | sort -V | head -n1)" != "$REQUIRED_PYTHON" ]]; then
    echo "❌ Python $REQUIRED_PYTHON or higher is required. You have $CURRENT_PYTHON."
    exit 1
else
    echo "✅ Python version $CURRENT_PYTHON detected."
fi

# Step 0.1: Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 not found."
    echo "👉 Attempting to install pip3..."
    sudo apt update && sudo apt install python3-pip -y

    if ! command -v pip3 &> /dev/null; then
        echo "❌ Failed to install pip3 automatically. Please install manually."
        exit 1
    else
        echo "✅ pip3 installed successfully."
    fi
else
    echo "✅ pip3 is installed."
fi

# Step 1: Check if requirements are installed
echo "🔍 Checking Python dependencies..."

pip3 install --quiet -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ All dependencies installed successfully."
else
    echo "❌ Failed to install dependencies. Please check your Python environment."
    exit 1
fi

# Step 2: # Launch the app in the background
echo "⚙️ Starting the app in the background..."
python3 app.py &

# Give Flask server a few seconds to start
sleep 3

# Open default local browser link
echo "🌐 Opening your browser..."
if command -v xdg-open > /dev/null; then
    xdg-open "http://127.0.0.1:8000"
elif command -v open > /dev/null; then
    open "http://127.0.0.1:8000"
else
    echo "👉 Please manually open http://127.0.0.1:8000 in your browser."
fi