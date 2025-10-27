# 🍕 DineSysPro - Restaurant Order Management System

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/Arsam1313/mars_syspro_universal/releases)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey.svg)](https://github.com/Arsam1313/mars_syspro_universal)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://github.com/Arsam1313/mars_syspro_universal/workflows/Build%20and%20Release/badge.svg)](https://github.com/Arsam1313/mars_syspro_universal/actions)

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
- 🔄 **Auto-Update**: Automatic updates from GitHub releases

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

## 📦 Downloads

### Latest Release

Download the latest version for your platform:

- 🍎 **macOS**: [DineSysPro-1.0.0-macOS.dmg](https://github.com/Arsam1313/mars_syspro_universal/releases/latest)
- 🪟 **Windows**: [DineSysPro-1.0.0-Windows-Setup.exe](https://github.com/Arsam1313/mars_syspro_universal/releases/latest)
- 🐧 **Linux**: Run from source (see Installation above)

### Installation

**macOS:**
1. Download the `.dmg` file
2. Open it and drag `DineSysPro.app` to Applications
3. Launch from Applications folder

**Windows:**
1. Download the `.exe` installer
2. Run the installer
3. Launch from Start Menu or Desktop shortcut

## 🔄 Auto-Update

DineSysPro includes an automatic update system:

- ✅ Checks for updates on startup
- ✅ Notifies you when new versions are available
- ✅ One-click download and installation
- ✅ Your settings are preserved during updates

### Manual Update Check

```bash
python3 auto_updater.py
```

Or use the Settings UI → Check for Updates

## 🛠️ Development

### Building from Source

**macOS:**
```bash
python3 build_macos.py
```

**Windows:**
```bash
python build_windows.py
```

See [BUILD_GUIDE.md](BUILD_GUIDE.md) for detailed instructions.

### Creating a Release

```bash
./release.sh
```

See [UPDATE_GUIDE.md](UPDATE_GUIDE.md) for complete release workflow.

## 📚 Documentation

- 📖 [Build Guide](BUILD_GUIDE.md) - How to build applications
- 🔄 [Update Guide](UPDATE_GUIDE.md) - Release and update process
- 🎨 [Icon Guide](ICON_GUIDE.md) - Creating custom icons
- 📋 [API Documentation](API_DOCUMENTATION.md) - API endpoints
- ✨ [Features](FEATURES.md) - Complete feature list
- 📝 [Changelog](CHANGELOG.md) - Version history

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🐛 Bug Reports

Found a bug? Please open an issue on GitHub:

[Report a Bug](https://github.com/Arsam1313/mars_syspro_universal/issues/new?template=bug_report.md)

## 💡 Feature Requests

Have an idea? We'd love to hear it:

[Request a Feature](https://github.com/Arsam1313/mars_syspro_universal/issues/new?template=feature_request.md)

## 🤝 Support

For issues and questions:

- 🐛 [GitHub Issues](https://github.com/Arsam1313/mars_syspro_universal/issues)
- 📧 Email: support@dinesyspro.com
- 📚 [Wiki](https://github.com/Arsam1313/mars_syspro_universal/wiki)

## 📊 Project Stats

- ⭐ Stars: ![GitHub stars](https://img.shields.io/github/stars/Arsam1313/mars_syspro_universal?style=social)
- 🍴 Forks: ![GitHub forks](https://img.shields.io/github/forks/Arsam1313/mars_syspro_universal?style=social)
- 📥 Downloads: ![GitHub downloads](https://img.shields.io/github/downloads/Arsam1313/mars_syspro_universal/total)
- 📝 Commits: ![GitHub commits](https://img.shields.io/github/commit-activity/m/Arsam1313/mars_syspro_universal)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- Built with [PyWebView](https://pywebview.flowrl.com/)
- Printer support via [python-escpos](https://python-escpos.readthedocs.io/)
- Sound playback with [pygame](https://www.pygame.org/)

---

**🍕 DineSysPro** - Professional Restaurant Management System

Made with ❤️ for restaurants worldwide

