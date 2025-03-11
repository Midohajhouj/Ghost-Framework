#!/usr/bin/env bash
# -*- coding: utf-8 -*-
### BEGIN INIT INFO
# Provides:          ghost_framework
# Required-Start:    $network $remote_fs
# Required-Stop:     $remote_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Remote ADB Control Tool for Android Devices
# Description:       A tool to manage Android devices via ADB for debugging, file management, screen mirroring, and more.
# Author:            LIONMAD <https://github.com/Midohajhouj>
# Version:           V.2.0
# License:           MIT License - https://opensource.org/licenses/MIT
### END INIT INFO

# Standard Libraries
import os 
import sys 
import subprocess 
import logging
import re 
import asyncio 
from datetime import datetime  
import getpass 
import shutil 
import zipfile 
import gzip

# Third-Party Libraries
from cryptography.fernet import Fernet 
import keyring
from tqdm import tqdm 

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

# Secure key storage using keyring
SECURE_KEY = None
try:
    SECURE_KEY = keyring.get_password("ghost_framework", "secure_key")
    if not SECURE_KEY:
        SECURE_KEY = Fernet.generate_key().decode()
        keyring.set_password("ghost_framework", "secure_key", SECURE_KEY)
    cipher_suite = Fernet(SECURE_KEY.encode())
except Exception as e:
    logging.error(f"Failed to handle secure key storage: {e}")
    sys.exit(1)

# Password protection for the script
SCRIPT_PASSWORD = "ghost"  # Change this to a secure password

def authenticate():
    """Authenticate the user before allowing access to the script."""
    attempts = 3
    while attempts > 0:
        password = getpass.getpass(color_text("Enter password to access Ghost Framework: ", 'blue'))
        if password == SCRIPT_PASSWORD:
            return True
        else:
            attempts -= 1
            logging.error(f"Incorrect password. {attempts} attempts remaining.")
    logging.error("Too many failed attempts. Exiting.")
    sys.exit(1)

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
{color_text('[1]', 'green')} Show Connected Devices          {color_text('[15]', 'green')} Uninstall App
{color_text('[2]', 'green')} Connect to a Device             {color_text('[16]', 'green')} Show Device Info
{color_text('[3]', 'green')} Disconnect from a Device        {color_text('[17]', 'green')} Mirror Screen
{color_text('[4]', 'green')} Access Device Shell             {color_text('[18]', 'green')} Execute Custom Command
{color_text('[5]', 'green')} Install APK                     {color_text('[19]', 'green')} Interactive Shell
{color_text('[6]', 'green')} Install Multiple APKs           {color_text('[20]', 'green')} List Files on Device
{color_text('[7]', 'green')} Take Screenshot                 {color_text('[21]', 'green')} Delete File on Device
{color_text('[8]', 'green')} Record Screen                   {color_text('[22]', 'green')} Check Battery Health
{color_text('[9]', 'green')} List Installed Apps             {color_text('[23]', 'green')} Execute Script
{color_text('[10]', 'green')} Reboot Device                  {color_text('[24]', 'green')} Interactive File Browser
{color_text('[11]', 'green')} Backup Device                  {color_text('[25]', 'green')} Batch Push/Pull Files
{color_text('[12]', 'green')} Restore Device                 {color_text('[26]', 'green')} Connect via Wi-Fi ADB
{color_text('[13]', 'green')} Push File (Secure)             {color_text('[27]', 'green')} Compress/Decompress Files
{color_text('[14]', 'green')} Pull File (Secure)             {color_text('[28]', 'green')} View Device Logs (logcat)
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

def push_file_secure():
    """Push a file to the device securely."""
    device = select_device()
    if not device:
        return
    local_path = input(color_text("Enter local file path: ", 'blue'))
    remote_path = input(color_text("Enter remote file path: ", 'blue'))
    
    # Encrypt the file before pushing
    try:
        with open(local_path, 'rb') as file:
            file_data = file.read()
        encrypted_data = cipher_suite.encrypt(file_data)
        encrypted_file = local_path + ".enc"
        with open(encrypted_file, 'wb') as file:
            file.write(encrypted_data)
        
        output = adb_command(device, f"push {encrypted_file} {remote_path}")
        if "error" in output.lower():
            logging.error(output)
        else:
            logging.info(f"File pushed securely to {remote_path}")
        os.remove(encrypted_file)  # Clean up the encrypted file
    except Exception as e:
        logging.error(f"Error during secure file push: {e}")

def pull_file_secure():
    """Pull a file from the device securely."""
    device = select_device()
    if not device:
        return
    remote_path = input(color_text("Enter remote file path: ", 'blue'))
    local_path = input(color_text("Enter local file path: ", 'blue'))
    
    # Pull the encrypted file
    encrypted_file = local_path + ".enc"
    output = adb_command(device, f"pull {remote_path} {encrypted_file}")
    if "error" in output.lower():
        logging.error(output)
        return
    
    # Decrypt the file
    try:
        with open(encrypted_file, 'rb') as file:
            encrypted_data = file.read()
        decrypted_data = cipher_suite.decrypt(encrypted_data)
        with open(local_path, 'wb') as file:
            file.write(decrypted_data)
        logging.info(f"File pulled securely to {local_path}")
        os.remove(encrypted_file)  # Clean up the encrypted file
    except Exception as e:
        logging.error(f"Error during secure file pull: {e}")

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

def interactive_file_browser():
    """Interactive file browser for selecting files to push/pull."""
    device = select_device()
    if not device:
        return
    remote_path = input(color_text("Enter remote directory path: ", 'blue'))
    output = adb_command(device, f"shell ls {remote_path}")
    if "error" in output.lower():
        logging.error(output)
        return
    
    files = output.splitlines()
    print(color_text("Files in directory:", 'yellow'))
    for i, file in enumerate(files):
        print(f"{color_text(f'[{i + 1}]', 'green')} {file}")
    
    choice = input(color_text("Select a file: ", 'blue'))
    try:
        choice = int(choice) - 1
        if 0 <= choice < len(files):
            selected_file = files[choice]
            action = input(color_text("Do you want to (1) Push or (2) Pull this file? ", 'blue'))
            if action == '1':
                local_path = input(color_text("Enter local file path: ", 'blue'))
                output = adb_command(device, f"push {local_path} {remote_path}/{selected_file}")
                if "error" in output.lower():
                    logging.error(output)
                else:
                    logging.info(f"File pushed to {remote_path}/{selected_file}")
            elif action == '2':
                local_path = input(color_text("Enter local file path: ", 'blue'))
                output = adb_command(device, f"pull {remote_path}/{selected_file} {local_path}")
                if "error" in output.lower():
                    logging.error(output)
                else:
                    logging.info(f"File pulled to {local_path}")
            else:
                logging.error("Invalid action.")
        else:
            logging.error("Invalid selection.")
    except ValueError:
        logging.error("Invalid input.")

def batch_push_pull_files():
    """Batch push or pull multiple files."""
    device = select_device()
    if not device:
        return
    action = input(color_text("Do you want to (1) Push or (2) Pull files? ", 'blue'))
    if action not in ['1', '2']:
        logging.error("Invalid action.")
        return
    
    if action == '1':
        local_dir = input(color_text("Enter local directory path: ", 'blue'))
        remote_dir = input(color_text("Enter remote directory path: ", 'blue'))
        if not os.path.isdir(local_dir):
            logging.error("Local directory not found.")
            return
        
        files = os.listdir(local_dir)
        for file in tqdm(files, desc="Pushing files", unit="file"):
            local_path = os.path.join(local_dir, file)
            output = adb_command(device, f"push {local_path} {remote_dir}")
            if "error" in output.lower():
                logging.error(f"Failed to push {file}: {output}")
            else:
                logging.info(f"Pushed {file} to {remote_dir}")
    
    elif action == '2':
        remote_dir = input(color_text("Enter remote directory path: ", 'blue'))
        local_dir = input(color_text("Enter local directory path: ", 'blue'))
        if not os.path.isdir(local_dir):
            logging.error("Local directory not found.")
            return
        
        output = adb_command(device, f"shell ls {remote_dir}")
        if "error" in output.lower():
            logging.error(output)
            return
        
        files = output.splitlines()
        for file in tqdm(files, desc="Pulling files", unit="file"):
            output = adb_command(device, f"pull {remote_dir}/{file} {local_dir}")
            if "error" in output.lower():
                logging.error(f"Failed to pull {file}: {output}")
            else:
                logging.info(f"Pulled {file} to {local_dir}")

def connect_wifi_adb():
    """Connect to a device over Wi-Fi using ADB."""
    device = select_device()
    if not device:
        return
    ip = input(color_text("Enter device IP address: ", 'blue'))
    if not validate_ip(ip):
        logging.error("Invalid IP address.")
        return
    output = run_command(f"adb -s {device} tcpip 5555")
    if "restarting" in output.lower():
        logging.info("ADB daemon restarted in TCP mode.")
        output = run_command(f"adb -s {device} connect {ip}")
        if "connected" in output.lower():
            logging.info(f"Connected to {ip} over Wi-Fi.")
        else:
            logging.error(f"Failed to connect to {ip}.")
    else:
        logging.error("Failed to restart ADB in TCP mode.")

def compress_file(file_path, compress_type="zip"):
    """Compress a file using ZIP or GZIP."""
    try:
        if compress_type == "zip":
            with zipfile.ZipFile(f"{file_path}.zip", 'w') as zipf:
                zipf.write(file_path, os.path.basename(file_path))
            logging.info(f"File compressed as {file_path}.zip")
        elif compress_type == "gzip":
            with open(file_path, 'rb') as f_in:
                with gzip.open(f"{file_path}.gz", 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            logging.info(f"File compressed as {file_path}.gz")
        else:
            logging.error("Unsupported compression type.")
    except Exception as e:
        logging.error(f"Error compressing file: {e}")

def decompress_file(file_path):
    """Decompress a ZIP or GZIP file."""
    try:
        if file_path.endswith(".zip"):
            with zipfile.ZipFile(file_path, 'r') as zipf:
                zipf.extractall(os.path.dirname(file_path))
            logging.info(f"File decompressed from {file_path}")
        elif file_path.endswith(".gz"):
            with gzip.open(file_path, 'rb') as f_in:
                with open(file_path[:-3], 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            logging.info(f"File decompressed from {file_path}")
        else:
            logging.error("Unsupported file format.")
    except Exception as e:
        logging.error(f"Error decompressing file: {e}")

def view_device_logs():
    """View device logs (logcat) in real-time."""
    device = select_device()
    if not device:
        return
    print(color_text("Starting logcat... Press Ctrl+C to stop.", 'blue'))
    try:
        subprocess.run(f"adb -s {device} logcat", shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error viewing logs: {e}")
    except KeyboardInterrupt:
        logging.info("Logcat stopped.")

def main():
    """Main function to display menu and handle user input."""
    try:
        if not authenticate():
            return
        
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
                push_file_secure()
            elif choice == '14':
                pull_file_secure()
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
            elif choice == '24':
                interactive_file_browser()
            elif choice == '25':
                batch_push_pull_files()
            elif choice == '26':
                connect_wifi_adb()
            elif choice == '27':
                file_path = input(color_text("Enter file path to compress/decompress: ", 'blue'))
                action = input(color_text("Do you want to (1) Compress or (2) Decompress? ", 'blue'))
                if action == '1':
                    compress_type = input(color_text("Enter compression type (zip/gzip): ", 'blue'))
                    compress_file(file_path, compress_type)
                elif action == '2':
                    decompress_file(file_path)
                else:
                    logging.error("Invalid action.")
            elif choice == '28':
                view_device_logs()
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
