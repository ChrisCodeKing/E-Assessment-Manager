#!/bin/bash

# Check if a virtual environment exists
if [ ! -d "venv" ]; then
  echo "No virtual environment found. Creating one..."
  python3 -m venv .venv
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Display the current date and time
echo "Starting script at: $(date)"

# install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Build the main.spec using pyinstaller with -y option
echo "Building main.spec with pyinstaller..."
pyinstaller -y main.spec

# Check if pyinstaller succeeded
if [ $? -ne 0 ]; then
  echo "PyInstaller build failed. Exiting."
  exit 1
fi

# Run the generated executable and display its process ID (PID)
echo "Starting main executable..."
./dist/main/main &
SCRIPT_PID=$!
echo "Started main executable with PID: $SCRIPT_PID"

# Function to check memory usage in MB
check_memory_usage() {
  echo "Memory usage (in MB):"
  ps -p $SCRIPT_PID -o rss= | awk '{printf "%.2f MB\n", $1/1024}'
}

# Continuously check memory usage every x seconds
# while kill -0 $SCRIPT_PID 2> /dev/null; do
#   check_memory_usage
#   sleep 1
# done

# Optionally, wait for the script to finish and display an exit message
wait $SCRIPT_PID
echo "Process finished at: $(date)"