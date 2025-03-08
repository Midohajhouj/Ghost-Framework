# <p align="center"> **👻 Ghost Framework**

<p align="center">  
  <img src="https://img.shields.io/github/v/release/Midohajhouj/Ghost-Framework?label=Version&color=a80505">  
  <img src="https://img.shields.io/github/stars/Midohajhouj/Ghost-Framework?style=flat&label=Stars&color=a80505">  
  <img src="https://img.shields.io/github/repo-size/Midohajhouj/Ghost-Framework?label=Size&color=a80505">  
  <img src="https://img.shields.io/github/languages/top/Midohajhouj/Ghost-Framework?color=a80505">  
</p>  

**Ghost Framework** is a powerful **Remote ADB Control Tool** designed to streamline interactions with Android devices. It offers advanced capabilities like screen mirroring, real-time log analysis, and batch file operations, all through a convenient command-line interface. Whether you're a developer or security expert, **Ghost Framework** will help you efficiently manage Android devices for testing, development, and troubleshooting.

---

## 🎯 Features

- **📱 Device Management**: Seamlessly connect, disconnect, and interact with Android devices via ADB (Android Debug Bridge).
- **🛠 Advanced Tools**: Supports installing/uninstalling APKs, backing up and restoring data, managing files (push/pull), and more.
- **📜 Interactive Menu**: An intuitive, color-coded terminal interface for easy navigation.
- **🔍 Detailed Logs**: Logs all actions with timestamps for better debugging, stored in `ghost_framework.log`.
- **🔒 Secure File Transfer**: Includes encryption/decryption for files transferred between the computer and the Android device.
- **📦 Batch Operations**: Perform multiple actions simultaneously with batch file operations.
- **📊 Device Info**: Get comprehensive device details such as model, Android version, battery health, CPU usage, and RAM stats.
- **📹 Screen Mirroring**: View the Android device's screen on your computer in real-time.
- **📜 Logcat Viewer**: Monitor system logs in real-time to capture debugging information or analyze crashes.
- **⚡ Wi-Fi ADB**: Manage Android devices wirelessly over Wi-Fi, eliminating the need for USB cables.
- **💾 Data Backup & Restore**: Protect your data by backing up and restoring app data, system settings, and other important information.

---

### 🔧 Setup & Usage

1. **Clone the Repository**:
```bash
git clone https://github.com/Midohajhouj/Ghost-Framework.git
cd Ghost-Framework
chmod +x *
./install.sh

2. **Run the Tool**:
After installation, launch Ghost Framework with:
```bash
ghost
```

Default password: **ghost** (please change this for security purposes).

---

## 🗼 Terminal Preview
```bash
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
          
Ghost Framework - Remote ADB Control Tool  
Coded by LIONMAD  

[1] Show Connected Devices  
[2] Connect to a Device  
[3] Install an APK  
[4] Backup Data  
[5] View Device Info  
[6] Screen Mirroring  
[7] Pull Files  
[8] Push Files  
[9] Wi-Fi ADB  
[0] Exit

```

---

## 💂 Logs

All logs are saved in ghost_framework.log for detailed debugging. The log file records:

Connection Attempts: Details on successful/failed connections to devices.

Executed Commands: Lists all commands run by the user.

Device Information: Shows connected device data.

Errors and Successes: Provides logs on issues or successful operations.



---

## 🤝 Contribution

Contributions are welcome! Whether you're submitting bug fixes, suggesting new features, or improving the documentation, feel free to open an issue or submit a pull request. Make sure to follow the project's Code of Conduct and contribution guidelines.


---

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.


---

### <p align="center"> Coded by <a href="https://github.com/Midohajhouj">LIONMAD</a> </p>

