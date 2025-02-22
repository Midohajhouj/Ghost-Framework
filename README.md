# Ghost Framework

Ghost Framework is a powerful **Remote ADB Control Tool** designed to help users interact with Android devices efficiently. The framework allows you to perform a variety of tasks such as connecting to devices, managing apps, taking screenshots, recording the screen, and much more — all via an intuitive command-line interface.

---

## 🎯 Features
- 📱 **Device Management**: Connect, disconnect, and interact with Android devices over ADB.
- 🛠 **Advanced Tools**: Install/uninstall apps, backup/restore data, mirror screens, and more.
- 🌈 **Interactive Menu**: User-friendly interface with colorful terminal outputs.
- 🔍 **Detailed Logs**: Debugging made easy with timestamped logs.

---

## 🚀 Getting Started

### Prerequisites
1. **Python 3.6+** installed on your system.
2. [**ADB (Android Debug Bridge)**](https://developer.android.com/studio/command-line/adb) installed and configured in your system's PATH.
3. **Required Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🔧 Setup & Usage

### Clone the Repository
```bash
git clone https://github.com/your-username/ghost-framework.git
cd ghost-framework
```

### Run the Tool
```bash
python3 ghost_framework.py
```

---

## 📜 Main Menu Options

| **Option** | **Action**                   |
|------------|------------------------------|
| 1          | Show Connected Devices       |
| 2          | Connect to a Device          |
| 3          | Disconnect from a Device     |
| 4          | Access Device Shell          |
| 5          | Install APK                  |
| 6          | Take Screenshot              |
| 7          | Record Screen                |
| 8          | List Installed Apps          |
| 9          | Reboot Device                |
| 10         | Backup Device Data           |
| 11         | Restore Device Data          |
| 12         | Push File                    |
| 13         | Pull File                    |
| 14         | Uninstall App                |
| 15         | Show Device Info             |
| 16         | Mirror Device Screen         |
| 17         | Execute Custom ADB Command   |
| 0          | Exit                         |

---

## 🗼 Terminal Preview

```plaintext
Ghost Framework - Remote ADB Control Tool
Coded by MIDO777

[1] Show Connected Devices
[2] Connect to a Device
...
[0] Exit
```

---

## 💂 Logs

All logs are saved in `ghost_framework.log` for easy debugging and analysis.

---

## 🤝 Contribution
Contributions are welcome! Feel free to submit a pull request or open an issue for suggestions.

---

## 📄 License
This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author
Coded with ❤️ by **MIDO777**.

