# Changelog

All notable changes to DineSysPro will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Linux AppImage support
- Multi-language support (Swedish, English, Persian)
- Advanced analytics dashboard
- Cloud backup for settings

---

## [1.0.3] - 2024-10-27

### Fixed
- ✅ **Critical:** App crash on startup - added resource_path helper function
- ✅ Fixed all file path references to work with PyInstaller bundled app
- ✅ Fixed undefined ALARM_SOUND variable in API
- ✅ config.json, sounds/, and ui/ files now properly located in bundled app

### Changed
- ✅ Added resource_path() helper function for cross-platform file location
- ✅ All file operations now use resource_path() for PyInstaller compatibility

### Technical Notes
- This version fixes the startup crash caused by files not being found
- Uses sys._MEIPASS to locate resources in bundled applications
- Maintains compatibility with development mode (non-bundled)

---

## [1.0.2] - 2024-10-27

### Fixed
- ✅ macOS architecture compatibility - separate builds for Intel and Apple Silicon
- ✅ GitHub Actions permissions for creating releases
- ✅ Windows console encoding for emoji support
- ✅ PyInstaller incompatibility with universal2 binaries

### Added
- ✅ Swedish installation guide (INSTALLATIONSGUIDE.md)
- ✅ Separate macOS builds: ARM64 (Apple Silicon) and Intel (x86_64)
- ✅ Automatic architecture detection in build script

### Changed
- ✅ Changed from onefile to onedir mode (PyInstaller recommendation)
- ✅ GitHub Actions now builds for both Intel (macos-13) and ARM (macos-14)
- ✅ Removed all Persian documentation (project is Swedish/English only)

### Technical Notes
- Users should download the appropriate version for their Mac:
  - **ARM64**: For M1/M2/M3 Macs (2020+)
  - **Intel**: For Intel-based Macs (pre-2020)

---

## [1.0.1] - 2024-10-27

### Fixed
- ✅ Settings modal fullscreen issue
- ✅ Windows Unicode errors in build script

---

## [1.0.0] - 2024-10-27

### Added
- ✅ Initial release of DineSysPro
- ✅ Multi-printer support (USB, LAN, Bluetooth)
- ✅ Cross-platform support (macOS, Windows, Linux)
- ✅ Full screen mode for POS terminals
- ✅ Sleep prevention for 24/7 operation
- ✅ Swedish character support (åäöÅÄÖ)
- ✅ Sound alerts for new orders and system events
- ✅ Settings UI with version and device ID display
- ✅ WebView integration for order management
- ✅ Internet connectivity monitoring
- ✅ WebView health checks
- ✅ Auto-print orders feature
- ✅ Support for 58mm and 80mm thermal paper
- ✅ ESC/POS command support for thermal printers
- ✅ Configurable sound alerts
- ✅ Device ID generation and tracking
- ✅ Flask API for external integrations
- ✅ GitHub auto-update system
- ✅ Build scripts for macOS and Windows
- ✅ GitHub Actions CI/CD workflow

### Printer Support
- ✅ Star printers
- ✅ Epson printers
- ✅ HPRT printers
- ✅ Generic ESC/POS printers

### Supported Platforms
- ✅ macOS 10.14+
- ✅ Windows 10+
- ✅ Linux (Ubuntu, Debian, Fedora)

### Configuration
- ✅ JSON-based configuration
- ✅ Persistent settings storage
- ✅ Easy printer switching
- ✅ Sound customization

### API Endpoints
- ✅ `/api/print` - Print text
- ✅ `/api/test-print` - Test printer
- ✅ `/api/play-alert` - Play sound alert
- ✅ `/api/stop-alert` - Stop sound alert
- ✅ `/api/scan-printers` - Discover printers
- ✅ `/api/get-printer-config` - Get printer settings
- ✅ `/api/save-printer-config` - Save printer settings

### Documentation
- ✅ Complete README with installation guide
- ✅ API documentation
- ✅ Features list
- ✅ Icon creation guide
- ✅ Build and release guide

---

## Release Notes Format

Each release will include:

### ✨ New Features
New functionality added to the application.

### 🐛 Bug Fixes
Issues that have been resolved.

### 🔧 Improvements
Enhancements to existing features.

### 🔒 Security
Security-related updates.

### 📚 Documentation
Documentation updates and improvements.

### ⚠️ Breaking Changes
Changes that may require user action.

### 🗑️ Deprecated
Features that are being phased out.

---

## Version History

| Version | Release Date | Highlights |
|---------|-------------|------------|
| 1.0.0   | 2024-10-27  | Initial release with full POS functionality |

---

## Upgrade Guide

### From 0.x to 1.0.0
This is the initial stable release. No upgrade path needed.

---

## Known Issues

### v1.0.0
- None reported

---

## Future Roadmap

### v1.1.0 (Planned)
- [ ] Cloud sync for settings
- [ ] Multi-restaurant support
- [ ] Advanced printer queue management
- [ ] Email notifications

### v1.2.0 (Planned)
- [ ] Mobile app for remote monitoring
- [ ] Advanced analytics
- [ ] Custom receipt templates
- [ ] Barcode/QR code printing

### v2.0.0 (Planned)
- [ ] Complete UI redesign
- [ ] Plugin system
- [ ] Multi-language support
- [ ] Advanced reporting

---

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

---

## Support

For issues and questions:
- 🐛 [GitHub Issues](https://github.com/Arsam1313/mars_syspro_universal/issues)
- 📧 Email: support@dinesyspro.com
- 📚 [Documentation](https://github.com/Arsam1313/mars_syspro_universal/wiki)

---

**Legend:**
- ✨ New Feature
- 🐛 Bug Fix
- 🔧 Improvement
- 🔒 Security
- 📚 Documentation
- ⚠️ Breaking Change
- 🗑️ Deprecated

