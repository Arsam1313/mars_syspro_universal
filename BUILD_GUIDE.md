# 🚀 DineSysPro Build & Release Guide

این راهنما نحوه ساخت و انتشار نسخه‌های جدید DineSysPro را توضیح می‌دهد.

---

## 📋 فهرست مطالب

1. [پیش‌نیازها](#پیش‌نیازها)
2. [ساخت برای macOS](#ساخت-برای-macos)
3. [ساخت برای Windows](#ساخت-برای-windows)
4. [انتشار در GitHub](#انتشار-در-github)
5. [سیستم Auto-Update](#سیستم-auto-update)

---

## 🔧 پیش‌نیازها

### همه پلتفرم‌ها:
```bash
pip3 install -r requirements.txt
```

### macOS:
- Python 3.8+
- PyInstaller
- Xcode Command Line Tools (برای hdiutil)

### Windows:
- Python 3.8+
- PyInstaller
- Inno Setup (اختیاری، برای installer)

---

## 🍎 ساخت برای macOS

### 1️⃣ ساخت Application Bundle (.app)

```bash
python3 build_macos.py
```

این دستور:
- ✅ یک فایل `.app` در `dist/DineSysPro.app` می‌سازد
- ✅ یک فایل `.dmg` در `dist/DineSysPro-1.0.0-macOS.dmg` می‌سازد

### 2️⃣ تست Application

```bash
open dist/DineSysPro.app
```

### 3️⃣ نصب در Applications

```bash
cp -r dist/DineSysPro.app /Applications/
```

### 📦 خروجی:
- `dist/DineSysPro.app` - Application Bundle
- `dist/DineSysPro-1.0.0-macOS.dmg` - DMG Installer

---

## 🪟 ساخت برای Windows

### ⚠️ توجه:
این اسکریپت باید روی یک سیستم Windows اجرا شود.

### 1️⃣ ساخت Executable (.exe)

```cmd
python build_windows.py
```

این دستور:
- ✅ یک فایل `.exe` در `dist/DineSysPro.exe` می‌سازد
- ✅ یک installer در `dist/DineSysPro-1.0.0-Windows-Setup.exe` می‌سازد (اگر Inno Setup نصب باشد)

### 2️⃣ تست Application

```cmd
dist\DineSysPro.exe
```

### 📦 خروجی:
- `dist/DineSysPro.exe` - Standalone Executable
- `dist/DineSysPro-1.0.0-Windows-Setup.exe` - Installer (اختیاری)

---

## 🐙 انتشار در GitHub

### 1️⃣ آماده‌سازی Release

```bash
# 1. به‌روزرسانی نسخه در config.json
nano config.json
# "version": "1.0.1"

# 2. Commit تغییرات
git add .
git commit -m "Release v1.0.1"
git push origin main
```

### 2️⃣ ایجاد GitHub Release

#### روش 1: از طریق GitHub Web Interface

1. برو به: `https://github.com/Arsam1313/mars_syspro_universal/releases`
2. کلیک روی **"Draft a new release"**
3. **Tag version**: `v1.0.1`
4. **Release title**: `DineSysPro v1.0.1`
5. **Description**: توضیحات تغییرات
6. **Attach files**:
   - `dist/DineSysPro-1.0.0-macOS.dmg`
   - `dist/DineSysPro-1.0.0-Windows-Setup.exe` (یا `.exe`)
7. کلیک **"Publish release"**

#### روش 2: از طریق GitHub CLI

```bash
# نصب GitHub CLI (اگر نصب نیست)
brew install gh  # macOS
# یا
winget install GitHub.cli  # Windows

# Login
gh auth login

# ایجاد Release
gh release create v1.0.1 \
  --title "DineSysPro v1.0.1" \
  --notes "Release notes here" \
  dist/DineSysPro-1.0.0-macOS.dmg \
  dist/DineSysPro-1.0.0-Windows-Setup.exe
```

### 3️⃣ فرمت Release Notes

```markdown
## 🎉 DineSysPro v1.0.1

### ✨ New Features
- Feature 1
- Feature 2

### 🐛 Bug Fixes
- Fix 1
- Fix 2

### 🔧 Improvements
- Improvement 1
- Improvement 2

### 📦 Downloads
- **macOS**: DineSysPro-1.0.1-macOS.dmg
- **Windows**: DineSysPro-1.0.1-Windows-Setup.exe

### 📋 Installation
**macOS**: Open DMG and drag to Applications
**Windows**: Run the installer

### 🔄 Auto-Update
این نسخه از Auto-Update پشتیبانی می‌کند. اپلیکیشن به صورت خودکار به‌روزرسانی‌ها را چک می‌کند.
```

---

## 🔄 سیستم Auto-Update

### چگونه کار می‌کند؟

1. **هنگام شروع برنامه**:
   - اپلیکیشن نسخه فعلی را از `config.json` می‌خواند
   - به GitHub API متصل می‌شود
   - آخرین release را چک می‌کند

2. **اگر نسخه جدید موجود باشد**:
   - به کاربر اطلاع می‌دهد
   - لینک دانلود را نمایش می‌دهد
   - کاربر می‌تواند به‌روزرسانی را دانلود و نصب کند

### استفاده از Auto-Updater

#### از طریق Python:

```python
from auto_updater import check_for_updates, auto_update

# چک کردن به‌روزرسانی
update_info = check_for_updates()

if update_info['available']:
    print(f"New version: {update_info['latest']}")
    print(f"Current version: {update_info['current']}")
    
    # دانلود و نصب
    auto_update()
```

#### از طریق Terminal:

```bash
python3 auto_updater.py
```

### تست Auto-Update

```bash
# 1. تغییر نسخه به یک نسخه قدیمی‌تر
nano config.json
# "version": "0.9.0"

# 2. اجرای updater
python3 auto_updater.py

# خروجی:
# 🔍 Current version: 0.9.0
# 📦 Latest version: 1.0.0
# 🆕 New version available!
# ❓ Do you want to download and install? (y/n):
```

---

## 📊 Workflow کامل Release

```bash
# 1. Development
git checkout -b feature/new-feature
# ... توسعه ...
git commit -m "Add new feature"
git push origin feature/new-feature

# 2. Merge to main
git checkout main
git merge feature/new-feature
git push origin main

# 3. به‌روزرسانی نسخه
nano config.json
# "version": "1.0.1"
git add config.json
git commit -m "Bump version to 1.0.1"
git push origin main

# 4. Build برای هر پلتفرم
python3 build_macos.py      # روی macOS
python build_windows.py     # روی Windows

# 5. ایجاد GitHub Release
gh release create v1.0.1 \
  --title "DineSysPro v1.0.1" \
  --notes-file RELEASE_NOTES.md \
  dist/DineSysPro-1.0.1-macOS.dmg \
  dist/DineSysPro-1.0.1-Windows-Setup.exe

# 6. اطلاع‌رسانی به کاربران
# کاربران به صورت خودکار از به‌روزرسانی مطلع می‌شوند
```

---

## 🔐 امضای کد (Code Signing)

### macOS:

```bash
# امضای application
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name" \
  dist/DineSysPro.app

# تایید امضا
codesign --verify --deep --strict --verbose=2 dist/DineSysPro.app
spctl -a -t exec -vv dist/DineSysPro.app
```

### Windows:

```cmd
# امضای executable با signtool
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com dist\DineSysPro.exe
```

---

## 🧪 تست قبل از Release

### Checklist:

- [ ] تست عملکرد پرینتر (USB/LAN/Bluetooth)
- [ ] تست صداهای آلارم
- [ ] تست اتصال به WebView
- [ ] تست مانیتورینگ اینترنت
- [ ] تست تنظیمات
- [ ] تست Full Screen Mode
- [ ] تست Sleep Prevention
- [ ] تست Auto-Update
- [ ] تست روی سیستم‌های مختلف
- [ ] بررسی لاگ‌ها برای خطا

---

## 📝 نکات مهم

### 1. نام‌گذاری فایل‌ها:

```
DineSysPro-{VERSION}-{PLATFORM}.{EXT}

مثال:
- DineSysPro-1.0.0-macOS.dmg
- DineSysPro-1.0.0-Windows-Setup.exe
- DineSysPro-1.0.0-Linux.AppImage
```

### 2. Versioning:

از [Semantic Versioning](https://semver.org/) استفاده کنید:
- `MAJOR.MINOR.PATCH`
- مثال: `1.0.0`, `1.0.1`, `1.1.0`, `2.0.0`

### 3. GitHub Release Tags:

همیشه با `v` شروع کنید:
- `v1.0.0`, `v1.0.1`, `v2.0.0`

### 4. Changelog:

یک فایل `CHANGELOG.md` نگه‌داری کنید:

```markdown
# Changelog

## [1.0.1] - 2024-01-15
### Added
- New feature

### Fixed
- Bug fix

## [1.0.0] - 2024-01-01
### Added
- Initial release
```

---

## 🆘 عیب‌یابی

### مشکل: PyInstaller خطا می‌دهد

```bash
# پاک کردن cache
rm -rf build/ dist/ *.spec
pip3 install --upgrade pyinstaller
```

### مشکل: Application در macOS باز نمی‌شود

```bash
# حذف quarantine
xattr -cr dist/DineSysPro.app
```

### مشکل: Windows Defender برنامه را block می‌کند

- امضای کد (Code Signing) انجام دهید
- یا فایل را به Windows Defender اضافه کنید

---

## 📞 پشتیبانی

برای سوالات و مشکلات:
- 🐛 GitHub Issues: https://github.com/Arsam1313/mars_syspro_universal/issues
- 📧 Email: support@dinesyspro.com

---

## ✅ خلاصه

```bash
# Build macOS
python3 build_macos.py

# Build Windows (روی Windows)
python build_windows.py

# Release
gh release create v1.0.1 \
  --title "DineSysPro v1.0.1" \
  --notes "Release notes" \
  dist/*.dmg dist/*.exe

# تست Auto-Update
python3 auto_updater.py
```

---

**🎉 حالا آماده‌اید که DineSysPro را build و release کنید!**

