#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import logging
import re
import asyncio
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
      .-.
    .'   `.
   :0 0  :
   : o    `.
  :         ``.
 :             `.
:  :         .   `.
:   :          ` . `.
 `.. :            `. ``;
    `:;             `:'
       :              `.
        `.              `.     
          `'`'`'`---..,____`.
          
{color_text('Ghost Framework', 'blue')} - {color_text('Remote ADB Control Tool', 'yellow')}
    Coded by {color_text('LIONMAD', 'red')}
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
{color_text('[6]', 'green')} Install Multiple APKs
{color_text('[7]', 'green')} Take Screenshot
{color_text('[8]', 'green')} Record Screen
{color_text('[9]', 'green')} List Installed Apps
{color_text('[10]', 'green')} Reboot Device
{color_text('[11]', 'green')} Backup Device
{color_text('[12]', 'green')} Restore Device
{color_text('[13]', 'green')} Push File
{color_text('[14]', 'green')} Pull File
{color_text('[15]', 'green')} Uninstall App
{color_text('[16]', 'green')} Show Device Info
{color_text('[17]', 'green')} Mirror Screen
{color_text('[18]', 'green')} Execute Custom Command
{color_text('[19]', 'green')} Interactive Shell
{color_text('[20]', 'green')} List Files on Device
{color_text('[21]', 'green')} Delete File on Device
{color_text('[22]', 'green')} Check Battery Health
{color_text('[23]', 'green')} Execute Script
{color_text('[0]', 'red')} Exit
"""
    print(menu)

async def run_command_async(command):
    """Run a command asynchronously and return the output."""
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        logging.error(f"Error executing command: {stderr.decode().strip()}")
        return f"Error executing command: {stderr.decode().strip()}"
    
    logging.debug(f"Command executed: {command}")
    return stdout.decode().strip()

def run_command(command):
    """Run a command synchronously and return the output."""
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True, check=True)
        logging.debug(f"Command executed: {command}")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing command: {e.stderr}")
        return f"Error executing command: {e.stderr}"

def validate_ip(ip):
    """Validate an IP address."""
    pattern = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    return pattern.match(ip) is not None

def select_device():
    """Allow the user to select a specific device if multiple devices are connected."""
    devices_output = run_command("adb devices")
    devices = [line.split('\t')[0] for line in devices_output.splitlines()[1:] if line.endswith('\tdevice')]
    
    if not devices:
        logging.error("No devices connected.")
        return None
    elif len(devices) == 1:
        return devices[0]
    
    print(color_text("Connected devices:", 'yellow'))
    for i, device in enumerate(devices):
        print(f"{color_text(f'[{i + 1}]', 'green')} {device}")
    
    choice = input(color_text("Select a device: ", 'blue'))
    try:
        choice = int(choice) - 1
        if 0 <= choice < len(devices):
            return devices[choice]
        else:
            logging.error("Invalid selection.")
            return None
    except ValueError:
        logging.error("Invalid input.")
        return None

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
    if not validate_ip(ip):
        logging.error("Invalid IP address.")
        return
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
    device = select_device()
    if not device:
        return
    print(color_text(f"Entering ADB shell for device {device}...", 'blue'))
    try:
        subprocess.run(f"adb -s {device} shell", shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error accessing shell: {e}")

def adb_command(device, command):
    """Execute an ADB command on the specified device."""
    try:
        result = subprocess.run(f"adb -s {device} {command}", shell=True, text=True, capture_output=True, check=True)
        logging.debug(f"Command executed: {command}")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing command: {e.stderr}")
        return f"Error executing command: {e.stderr}"

def install_apk():
    """Install a single APK."""
    device = select_device()
    if not device:
        return
    apk_path = input(color_text("Enter path to APK: ", 'blue'))
    if not os.path.exists(apk_path):
        logging.error("APK file not found!")
        return
    
    try:
        logging.info(f"Installing APK: {apk_path}")
        output = adb_command(device, f"install {apk_path}")
        if "success" in output.lower():
            logging.info(f"APK installed successfully: {apk_path}")
        else:
            logging.error(f"Failed to install APK: {output}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

def install_multiple_apks():
    """Install multiple APKs in batch."""
    device = select_device()
    if not device:
        return
    apk_paths = input(color_text("Enter paths to APKs (comma-separated): ", 'blue')).split(',')
    for apk_path in apk_paths:
        apk_path = apk_path.strip()
        if not os.path.exists(apk_path):
            logging.error(f"APK file not found: {apk_path}")
            continue
        logging.info(f"Installing APK: {apk_path}")
        output = adb_command(device, f"install {apk_path}")
        if "success" in output.lower():
            logging.info(f"APK installed successfully: {apk_path}")
        else:
            logging.error(f"Failed to install APK: {output}")

def take_screenshot():
    """Take screenshot with timestamp-based file naming."""
    device = select_device()
    if not device:
        return
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_file = f"screenshot_{timestamp}.png"
    output = adb_command(device, f"exec-out screencap -p > {screenshot_file}")
    if os.path.exists(screenshot_file):
        logging.info(f"Screenshot saved as {screenshot_file}")
    else:
        logging.error("Failed to take screenshot.")

def record_screen():
    """Record the screen of the connected device."""
    device = select_device()
    if not device:
        return
    duration = input(color_text("Enter recording duration (seconds): ", 'blue'))
    try:
        duration = int(duration)
        if duration <= 0:
            raise ValueError("Duration must be a positive integer.")
    except ValueError as e:
        logging.error(f"Invalid duration: {e}")
        return

    logging.info(f"Recording for {duration} seconds...")
    output = adb_command(device, f"shell screenrecord --time-limit {duration} /sdcard/screenrecord.mp4 && pull /sdcard/screenrecord.mp4")
    if os.path.exists("screenrecord.mp4"):
        logging.info("Screen recording saved as screenrecord.mp4")
    else:
        logging.error("Failed to record screen.")

def list_installed_apps():
    """List all installed apps on the connected device."""
    device = select_device()
    if not device:
        return
    output = adb_command(device, "shell pm list packages")
    if "error" in output.lower():
        logging.error(output)
    else:
        print(color_text(output, 'yellow'))

def reboot_device():
    """Reboot the connected device."""
    device = select_device()
    if not device:
        return
    output = adb_command(device, "reboot")
    if "error" in output.lower():
        logging.error(output)
    else:
        logging.info("Device rebooted.")

def backup_device():
    """Backup device data with progress indicator."""
    device = select_device()
    if not device:
        return
    backup_file = input(color_text("Enter backup file name: ", 'blue'))
    print(color_text("Starting backup...", 'blue'))
    process = subprocess.Popen(f"adb -s {device} backup -all -f {backup_file}.ab", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(color_text(output.strip(), 'yellow'))
            print(color_text("Backup in progress...", 'blue'))
    
    if process.returncode == 0:
        logging.info(f"Backup saved as {backup_file}.ab")
    else:
        logging.error("Backup failed.")

def restore_device():
    """Restore device data."""
    device = select_device()
    if not device:
        return
    backup_file = input(color_text("Enter backup file name: ", 'blue'))
    output = adb_command(device, f"restore {backup_file}.ab")
    if "error" in output.lower():
        logging.error(output)
    else:
        logging.info(f"Restored from {backup_file}.ab")

def push_file():
    """Push a file to the device."""
    device = select_device()
    if not device:
        return
    local_path = input(color_text("Enter local file path: ", 'blue'))
    remote_path = input(color_text("Enter remote file path: ", 'blue'))
    output = adb_command(device, f"push {local_path} {remote_path}")
    if "error" in output.lower():
        logging.error(output)
    else:
        logging.info(f"File pushed to {remote_path}")

def pull_file():
    """Pull a file from the device."""
    device = select_device()
    if not device:
        return
    remote_path = input(color_text("Enter remote file path: ", 'blue'))
    local_path = input(color_text("Enter local file path: ", 'blue'))
    output = adb_command(device, f"pull {remote_path} {local_path}")
    if "error" in output.lower():
        logging.error(output)
    else:
        logging.info(f"File pulled to {local_path}")

def uninstall_app():
    """Uninstall an app from the device."""
    device = select_device()
    if not device:
        return
    package_name = input(color_text("Enter package name to uninstall: ", 'blue'))
    output = adb_command(device, f"uninstall {package_name}")
    if "success" in output.lower():
        logging.info(f"App {package_name} uninstalled successfully.")
    else:
        logging.error(f"Failed to uninstall app: {output}")

def show_device_info():
    """Show detailed device information."""
    device = select_device()
    if not device:
        return
    model = adb_command(device, "shell getprop ro.product.model")
    android_version = adb_command(device, "shell getprop ro.build.version.release")
    battery_level = adb_command(device, "shell dumpsys battery | grep level")
    logging.info(f"Model: {model}")
    logging.info(f"Android Version: {android_version}")
    logging.info(f"Battery Level: {battery_level}")

def mirror_screen():
    """Mirror the device screen to the computer."""
    device = select_device()
    if not device:
        return
    output = adb_command(device, "exec-out screenrecord --output-format=h264 - | ffplay -")
    if "error" in output.lower():
        logging.error(output)
    else:
        logging.info("Screen mirroring started.")

def execute_custom_command():
    """Execute a custom ADB command."""
    device = select_device()
    if not device:
        return
    command = input(color_text("Enter custom ADB command: ", 'blue'))
    output = adb_command(device, command)
    logging.info(output)

def interactive_shell():
    """Start an interactive ADB shell session."""
    device = select_device()
    if not device:
        return
    print(color_text(f"Starting interactive ADB shell for device {device}...", 'blue'))
    print(color_text("Type 'exit' to return to the main menu.", 'yellow'))
    while True:
        command = input(color_text("adb shell> ", 'blue'))
        if command.lower() == 'exit':
            break
        output = adb_command(device, f"shell {command}")
        print(color_text(output, 'yellow'))

def list_files_on_device():
    """List files in a specific directory on the device."""
    device = select_device()
    if not device:
        return
    remote_path = input(color_text("Enter remote directory path: ", 'blue'))
    output = adb_command(device, f"shell ls {remote_path}")
    if "error" in output.lower():
        logging.error(output)
    else:
        print(color_text(output, 'yellow'))

def delete_file_on_device():
    """Delete a file or directory on the device."""
    device = select_device()
    if not device:
        return
    remote_path = input(color_text("Enter remote file/directory path: ", 'blue'))
    output = adb_command(device, f"shell rm -rf {remote_path}")
    if "error" in output.lower():
        logging.error(output)
    else:
        logging.info(f"Deleted {remote_path}")

def check_battery_health():
    """Check the battery health and charging status."""
    device = select_device()
    if not device:
        return
    battery_health = adb_command(device, "shell dumpsys battery | grep health")
    charging_status = adb_command(device, "shell dumpsys battery | grep status")
    logging.info(f"Battery Health: {battery_health}")
    logging.info(f"Charging Status: {charging_status}")

def execute_script():
    """Execute a series of ADB commands from a script file."""
    device = select_device()
    if not device:
        return
    script_path = input(color_text("Enter path to script file: ", 'blue'))
    if not os.path.exists(script_path):
        logging.error("Script file not found!")
        return
    
    with open(script_path, 'r') as file:
        commands = file.readlines()
    
    for command in commands:
        command = command.strip()
        if command:
            logging.info(f"Executing command: {command}")
            output = adb_command(device, command)
            print(color_text(output, 'yellow'))

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
                install_multiple_apks()
            elif choice == '7':
                take_screenshot()
            elif choice == '8':
                record_screen()
            elif choice == '9':
                list_installed_apps()
            elif choice == '10':
                reboot_device()
            elif choice == '11':
                backup_device()
            elif choice == '12':
                restore_device()
            elif choice == '13':
                push_file()
            elif choice == '14':
                pull_file()
            elif choice == '15':
                uninstall_app()
            elif choice == '16':
                show_device_info()
            elif choice == '17':
                mirror_screen()
            elif choice == '18':
                execute_custom_command()
            elif choice == '19':
                interactive_shell()
            elif choice == '20':
                list_files_on_device()
            elif choice == '21':
                delete_file_on_device()
            elif choice == '22':
                check_battery_health()
            elif choice == '23':
                execute_script()
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
