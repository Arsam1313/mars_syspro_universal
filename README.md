# 🍕 DineSysPro - Restaurant Order Management System

Professional POS printer integration and order management system for restaurants.

## ✨ Features

- 🖨️ **Multi-Printer Support**: USB, LAN (Network), Bluetooth
- 📄 **Paper Sizes**: 58mm and 80mm thermal printers
- 🇸🇪 **Swedish Characters**: Full support for åäöÅÄÖ
- 🔊 **Sound Alerts**: Customizable alerts for new orders, internet loss, low battery
- ⚙️ **Easy Configuration**: User-friendly settings interface
- 🌐 **WebView Integration**: Seamless integration with web-based order systems
- 🖥️ **Cross-Platform**: Works on macOS, Windows, and Linux
- 🎯 **Full Screen Mode**: Runs in full screen for dedicated POS terminals
- ☕ **Sleep Prevention**: Keeps device awake during operation

## 🚀 Quick Start

### Requirements

- **Operating System**: macOS 10.14+, Windows 10+, or Linux (Ubuntu 18.04+)
- **Python**: 3.11 or later
- **Thermal POS Printer**: HPRT, Star, Epson, or any ESC/POS compatible printer
- **Display**: Supports full screen mode for dedicated terminals

### Installation

1. **Install dependencies:**
```bash
pip3 install -r requirements.txt
```

2. **Configure your printer:**
   - Edit `config.json` with your printer details
   - Or use the Settings UI after launching

3. **Run the application:**
```bash
python3 main.py
```

## ⚙️ Configuration

All settings are stored in `config.json`:

```json
{
  "version": "1.0.0",
  "printer": {
    "type": "lan",           // usb, lan, or bluetooth
    "address": "192.168.1.80",
    "paper_width": 80,       // 58 or 80 mm
    "cups_name": "HPRT_TP808"
  },
  "app_url": "http://your-server.com/order-reception.html",
  "sounds": {
    "new_order": "neworder.mp3",
    "internet_lost": "no_internet_alert.mp3",
    "low_battery": "low_battery.mp3"
  },
  "auto_print_orders": true
}
```

## 🖨️ Supported Printers

- **HPRT**: TP808, TP805, etc.
- **Star Micronics**: TSP100, TSP650, etc.
- **Epson**: TM-T20, TM-T88, etc.
- **Any ESC/POS compatible thermal printer**

### Connection Types

1. **LAN (Network)**: Direct IP connection on port 9100
2. **USB**: Via CUPS printer system
3. **Bluetooth**: Via CUPS or direct connection

## 📱 API Endpoints

The application provides a REST API on `http://localhost:8080`:

- `POST /api/print` - Print text
- `POST /api/alarm/start` - Start alarm sound
- `POST /api/alarm/stop` - Stop alarm sound
- `GET /api/status` - Get system status

## 🔧 Settings Interface

Click the ⚙️ button in the main window to access:

- 📊 **System Information**: Version, Device ID
- 🖨️ **Printer Configuration**: Type, address, paper width, CUPS name
- 🔊 **Sound Preferences**: Customize alert sounds

## 🏗️ Building Standalone App

To create a standalone `.app` bundle:

```bash
# Install PyInstaller
pip3 install pyinstaller

# Build the app
python3 build_app.py

# The app will be created at: dist/DineSysPro.app
```

## 📂 Project Structure

```
mars_syspro_universal/
├── main.py              # Main application
├── printer_manager.py   # Printer management
├── config.json          # Configuration
├── requirements.txt     # Python dependencies
├── icon.icns           # App icon (macOS)
├── sounds/             # Alert sound files
│   ├── neworder.mp3
│   ├── no_internet_alert.mp3
│   └── low_battery.mp3
└── ui/                 # User interface
    └── settings.html   # Settings page
```

## 🐛 Troubleshooting

### Printer not printing?

1. Check printer connection (USB cable, network, Bluetooth)
2. Verify printer address in Settings
3. Test print from Settings → Test Print button
4. Check CUPS printer status: `lpstat -p`

### Swedish characters not printing correctly?

- The app uses CP850 encoding for Nordic characters
- Make sure your printer supports ESC/POS commands
- Test with the built-in test print function

### Port 8080 already in use?

```bash
# Find and kill the process
lsof -i :8080
kill -9 <PID>
```

## 📝 Version History

- **1.0.0** (2025-10-27)
  - Initial release
  - Multi-printer support (USB/LAN/Bluetooth)
  - Swedish character support
  - Settings UI
  - Sound alerts
  - WebView integration

## 🤝 Support

For issues and questions, please contact support.

## 📄 License

Proprietary - All rights reserved

---

**🍕 DineSysPro** - Professional Restaurant Management System

