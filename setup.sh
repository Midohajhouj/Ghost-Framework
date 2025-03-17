#!/bin/bash

# Define colors for stylish output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display a stylish header
header() {
    clear
    echo -e "${BLUE}"
    echo -e "${NC}"
    echo -e "${YELLOW}Ghost Framework - Remote ADB Control Tool${NC}"
    echo -e "${YELLOW}Coded by MIDØ${NC}"
    echo -e "${BLUE}===========================================${NC}"
    echo
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install dependencies
install_dependencies() {
    echo -e "${YELLOW}[*] Installing dependencies...${NC}"
    if command_exists apt-get; then
        sudo apt-get update -y >/dev/null 2>&1
        sudo apt-get install -y adb android-tools-adb android-tools-fastboot ffmpeg >/dev/null 2>&1
    elif command_exists yum; then
        sudo yum install -y android-tools ffmpeg >/dev/null 2>&1
    elif command_exists brew; then
        brew install android-platform-tools ffmpeg >/dev/null 2>&1
    else
        echo -e "${RED}[!] Unsupported package manager. Please install adb and ffmpeg manually.${NC}"
        exit 1
    fi

    # Install Python dependencies
    echo -e "${YELLOW}[*] Installing Python dependencies...${NC}"
    sudo apt install pip -y
    pip install cryptography keyring tqdm keyrings.alt --break-system-packages >/dev/null 2>&1
    echo -e "${GREEN}[+] Dependencies installed successfully!${NC}"
}

# Function to download ghost.py if it doesn't exist
download_ghost_py() {
    if [ ! -f "ghost.py" ]; then
        echo -e "${YELLOW}[*] ghost.py not found. Downloading from external source...${NC}"
        curl -o ghost.py "https://raw.githubusercontent.com/Midohajhouj/Ghost-Framework/refs/heads/main/ghost.py"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}[+] ghost.py downloaded successfully!${NC}"
        else
            echo -e "${RED}[!] Failed to download ghost.py. Please check your internet connection or download it manually.${NC}"
            exit 1
        fi
    fi
}

# Function to make ghost.py executable
make_executable() {
    echo -e "${YELLOW}[*] Making ghost.py executable...${NC}"
    chmod +x ghost.py
    echo -e "${GREEN}[+] ghost.py is now executable!${NC}"
}

# Function to create a symlink for easy access
create_symlink() {
    echo -e "${YELLOW}[*] Creating symlink for easy access...${NC}"
    sudo cp "$(pwd)/ghost.py" /usr/local/bin/ghost
    echo -e "${GREEN}[+] Symlink created! You can now run 'ghost' from anywhere.${NC}"
}

# Main installation function
main() {
    header
    echo -e "${YELLOW}[*] Starting installation of Ghost Framework...${NC}"

    # Download ghost.py if it doesn't exist
    download_ghost_py

    # Install dependencies
    install_dependencies

    # Make ghost.py executable
    make_executable

    # Create symlink
    create_symlink

    echo -e "${GREEN}[+] Installation complete!${NC}"
    echo -e "${BLUE}===========================================${NC}"
    echo -e "${YELLOW}To start Ghost Framework, simply type 'ghost' in your terminal.
    passwd : ghost${NC}"
    echo
}

# Run the main function
main
