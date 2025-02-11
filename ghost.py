#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import logging
from datetime import datetime

# Set up logging with more detail (timestamp, log level, message)
logging.basicConfig(
    level=logging.DEBUG,  # Use DEBUG level for more detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("ghost_framework.log"), logging.StreamHandler()]
)

# Color definitions for terminal outputs
COLORS = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "bold": "\033[1m",
    "end": "\033[0m",
}

def color_text(text, color):
    """Return text wrapped in color codes."""
    return f"{COLORS.get(color, '')}{text}{COLORS['end']}"

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner():
    """Display the Ghost Framework banner."""
    banner = f"""
{color_text('Ghost Framework', 'red')} - {color_text('Remote ADB Control Tool', 'yellow')}
    Coded by {color_text('MIDO', 'green')}
"""
    logging.info(banner)

def show_menu():
    """Display the main menu options."""
    menu = f"""
{color_text('[1]', 'green')} Show Connected Devices
{color_text('[2]', 'green')} Connect to a Device
{color_text('[3]', 'green')} Disconnect from a Device
{color_text('[4]', 'green')} Access Device Shell
{color_text('[5]', 'green')} Install APK
{color_text('[6]', 'green')} Take Screenshot
{color_text('[7]', 'green')} Record Screen
{color_text('[8]', 'green')} List Installed Apps
{color_text('[9]', 'green')} Reboot Device
{color_text('[0]', 'red')} Exit
"""
    print(menu)

def run_command(command):
    """Enhanced error handling and return command output."""
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True, check=True)
        logging.debug(f"Command executed: {command}")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing command: {e.stderr}")
        return f"Error executing command: {e.stderr}"

def show_connected_devices():
    """Show all connected devices."""
    output = run_command("adb devices")
    if "error" in output.lower():
        logging.error(output)
    else:
        print(color_text(output, 'yellow'))

def connect_device():
    """Connect to a device using its IP address."""
    ip = input(color_text("Enter device IP: ", 'blue'))
    output = run_command(f"adb connect {ip}")
    if "connected" in output.lower():
        logging.info(output)
    else:
        logging.error(output)

def disconnect_device():
    """Disconnect from all connected devices."""
    output = run_command("adb disconnect")
    if "disconnected" in output.lower():
        logging.info(output)
    else:
        logging.error(output)

def access_shell():
    """Access the shell of a connected device."""
    print(color_text("Entering ADB shell...", 'blue'))
    try:
        subprocess.run("adb shell", shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error accessing shell: {e}")

def install_apk():
    """Enhanced APK installation with better error checking and multiple app executions."""
    apk_path = input(color_text("Enter path to APK: ", 'blue'))
    if not os.path.exists(apk_path):
        logging.error("APK file not found!")
        return
    
    logging.info(f"Installing APK: {apk_path}")
    output = run_command(f"adb install {apk_path}")
    if "success" in output.lower():
        logging.info(f"APK installed successfully: {apk_path}")
        
        # Extract the package name from the APK
        package_name = run_command(f"aapt dump badging {apk_path} | grep package:\ name").split("name='")[1].split("'")[0]
        logging.info(f"Package name extracted: {package_name}")

        # Prompt user for the number of times to launch the app
        try:
            times = int(input(color_text("How many times do you want to launch the app? ", 'blue')))
            if times <= 0:
                raise ValueError("Number of times must be positive.")
            for i in range(times):
                logging.info(f"Launching app {i + 1}/{times}...")
                run_command(f"adb shell am start -n {package_name}/.MainActivity")  # Adjust MainActivity to actual activity name if needed
                logging.info(f"App launched {i + 1} time(s)")
        except ValueError as e:
            logging.error(f"Invalid input for launch count: {e}")
        
    else:
        logging.error(f"Failed to install APK: {output}")

def take_screenshot():
    """Take screenshot with timestamp-based file naming."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_file = f"screenshot_{timestamp}.png"
    output = run_command(f"adb exec-out screencap -p > {screenshot_file}")
    if os.path.exists(screenshot_file):
        logging.info(f"Screenshot saved as {screenshot_file}")
    else:
        logging.error("Failed to take screenshot.")

def record_screen():
    """Record the screen of the connected device."""
    duration = input(color_text("Enter recording duration (seconds): ", 'blue'))
    try:
        duration = int(duration)
        if duration <= 0:
            raise ValueError("Duration must be a positive integer.")
    except ValueError as e:
        logging.error(f"Invalid duration: {e}")
        return

    logging.info(f"Recording for {duration} seconds...")
    output = run_command(f"adb shell screenrecord --time-limit {duration} /sdcard/screenrecord.mp4 && adb pull /sdcard/screenrecord.mp4")
    if os.path.exists("screenrecord.mp4"):
        logging.info("Screen recording saved as screenrecord.mp4")
    else:
        logging.error("Failed to record screen.")

def list_installed_apps():
    """List all installed apps on the connected device."""
    output = run_command("adb shell pm list packages")
    if "error" in output.lower():
        logging.error(output)
    else:
        print(color_text(output, 'yellow'))

def reboot_device():
    """Reboot the connected device."""
    output = run_command("adb reboot")
    if "error" in output.lower():
        logging.error(output)
    else:
        logging.info("Device rebooted.")

def main():
    """Main function to display menu and handle user input."""
    try:
        while True:
            clear_screen()
            show_banner()
            show_menu()

            choice = input(color_text("Select an option: ", 'blue'))

            if choice == '1':
                show_connected_devices()
            elif choice == '2':
                connect_device()
            elif choice == '3':
                disconnect_device()
            elif choice == '4':
                access_shell()
            elif choice == '5':
                install_apk()
            elif choice == '6':
                take_screenshot()
            elif choice == '7':
                record_screen()
            elif choice == '8':
                list_installed_apps()
            elif choice == '9':
                reboot_device()
            elif choice == '0':
                logging.info("Exiting Ghost Framework. Goodbye!")
                break
            else:
                logging.error("Invalid option. Please try again.")

            input(color_text("Press Enter to continue...", 'blue'))
    
    except KeyboardInterrupt:
        logging.error("Exiting Ghost Framework. Goodbye!")
        sys.exit(0)  # Exit cleanly

if __name__ == "__main__":
    main()
