#!/bin/bash

# This script installs the Ghost Framework tool on your system.

# Step 1: Copy the Python script to /usr/local/bin/ (or any directory in PATH)
echo "Copying Ghost Framework to /usr/local/bin/..."
cp ghost.py /usr/local/bin/ghost
# Step 2: Make the script executable
echo "Making the Ghost Framework script executable..."
chmod +x /usr/local/bin/ghost

# Step 3: Verify installation
echo "Installation complete. Verifying Ghost command..."

if command -v ghost &>/dev/null; then
    echo "ghost command is now available!"
    echo "You can now run ghost for usage instructions."
else
    echo "Something went wrong. Ghost command is not available."
    exit 1
fi
