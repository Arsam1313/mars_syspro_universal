# 🔄 راهنمای به‌روزرسانی DineSysPro

این راهنما نحوه استفاده از سیستم Auto-Update و انتشار نسخه‌های جدید را توضیح می‌دهد.

---

## 📋 فهرست

1. [نحوه کار Auto-Update](#نحوه-کار-auto-update)
2. [برای کاربران](#برای-کاربران)
3. [برای توسعه‌دهندگان](#برای-توسعه‌دهندگان)
4. [انتشار نسخه جدید](#انتشار-نسخه-جدید)

---

## 🔍 نحوه کار Auto-Update

### معماری سیستم:

```
┌─────────────────────────────────────────────────────────────┐
│  DineSysPro Application                                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  1. خواندن نسخه فعلی از config.json                   │ │
│  │     version: "1.0.0"                                   │ │
│  └────────────────────────────────────────────────────────┘ │
│                          ↓                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  2. درخواست به GitHub API                             │ │
│  │     GET /repos/Arsam1313/mars_syspro_universal/        │ │
│  │         releases/latest                                │ │
│  └────────────────────────────────────────────────────────┘ │
│                          ↓                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  3. مقایسه نسخه‌ها                                    │ │
│  │     Current: 1.0.0                                     │ │
│  │     Latest:  1.0.1                                     │ │
│  │     → Update Available!                                │ │
│  └────────────────────────────────────────────────────────┘ │
│                          ↓                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  4. نمایش اطلاعیه به کاربر                            │ │
│  │     "New version 1.0.1 available!"                     │ │
│  │     [Download] [Skip]                                  │ │
│  └────────────────────────────────────────────────────────┘ │
│                          ↓                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  5. دانلود فایل مناسب برای پلتفرم                     │ │
│  │     macOS:   DineSysPro-1.0.1-macOS.dmg                │ │
│  │     Windows: DineSysPro-1.0.1-Windows-Setup.exe        │ │
│  └────────────────────────────────────────────────────────┘ │
│                          ↓                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  6. راهنمای نصب                                        │ │
│  │     macOS:   "Open DMG and drag to Applications"      │ │
│  │     Windows: "Run the installer"                       │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 👥 برای کاربران

### چک کردن به‌روزرسانی

#### روش 1: خودکار (هنگام شروع برنامه)
برنامه به صورت خودکار هنگام شروع، به‌روزرسانی‌ها را چک می‌کند.

#### روش 2: دستی (از طریق تنظیمات)
1. باز کردن DineSysPro
2. کلیک روی دکمه ⚙️ (Settings)
3. کلیک روی "Check for Updates"

#### روش 3: از طریق Terminal

```bash
cd /Applications/DineSysPro.app/Contents/MacOS
python3 auto_updater.py
```

### نصب به‌روزرسانی

#### macOS:
1. دانلود فایل `.dmg`
2. باز کردن فایل DMG
3. کشیدن `DineSysPro.app` به پوشه Applications
4. جایگزینی نسخه قبلی

#### Windows:
1. دانلود فایل `.exe`
2. اجرای installer
3. نصب خودکار

### تنظیمات شما حفظ می‌شود!
✅ تمام تنظیمات پرینتر
✅ تنظیمات صدا
✅ URL اپلیکیشن
✅ Device ID

---

## 👨‍💻 برای توسعه‌دهندگان

### استفاده از Auto-Updater در کد

```python
from auto_updater import check_for_updates, auto_update

# چک کردن به‌روزرسانی
update_info = check_for_updates(silent=False)

if update_info and update_info['available']:
    print(f"🆕 New version: {update_info['latest']}")
    print(f"📝 Release notes: {update_info['release_notes']}")
    print(f"📥 Download URL: {update_info['download_url']}")
    
    # دانلود و نصب
    auto_update()
else:
    print("✅ Already up to date!")
```

### ساختار Response

```python
{
    'available': True,          # آیا به‌روزرسانی موجود است؟
    'current': '1.0.0',         # نسخه فعلی
    'latest': '1.0.1',          # آخرین نسخه
    'release_notes': '...',     # یادداشت‌های انتشار
    'download_url': 'https://...',  # لینک دانلود
    'release_data': {...}       # داده‌های کامل release
}
```

### تست Auto-Update

```bash
# 1. تغییر نسخه به یک نسخه قدیمی‌تر
nano config.json
# "version": "0.9.0"

# 2. اجرای updater
python3 auto_updater.py

# 3. بررسی خروجی
# 🔍 Current version: 0.9.0
# 📦 Latest version: 1.0.0
# 🆕 New version available!
```

---

## 🚀 انتشار نسخه جدید

### گام به گام:

#### 1️⃣ آماده‌سازی کد

```bash
# به‌روزرسانی کد
git checkout -b release/v1.0.1
# ... انجام تغییرات ...
git commit -m "Prepare v1.0.1 release"
git push origin release/v1.0.1
```

#### 2️⃣ به‌روزرسانی نسخه

```bash
# ویرایش config.json
nano config.json
```

```json
{
  "version": "1.0.1",
  ...
}
```

```bash
# ویرایش CHANGELOG.md
nano CHANGELOG.md
```

```markdown
## [1.0.1] - 2024-10-28

### Added
- New feature X

### Fixed
- Bug Y
```

```bash
# Commit تغییرات
git add config.json CHANGELOG.md
git commit -m "Bump version to 1.0.1"
git push origin release/v1.0.1
```

#### 3️⃣ Merge به main

```bash
git checkout main
git merge release/v1.0.1
git push origin main
```

#### 4️⃣ ایجاد Tag

```bash
git tag -a v1.0.1 -m "Release v1.0.1"
git push origin v1.0.1
```

#### 5️⃣ Build برای هر پلتفرم

**macOS:**
```bash
python3 build_macos.py
# خروجی: dist/DineSysPro-1.0.1-macOS.dmg
```

**Windows (روی Windows):**
```cmd
python build_windows.py
# خروجی: dist/DineSysPro-1.0.1-Windows-Setup.exe
```

#### 6️⃣ ایجاد GitHub Release

**روش 1: GitHub Web Interface**

1. برو به: https://github.com/Arsam1313/mars_syspro_universal/releases
2. کلیک "Draft a new release"
3. انتخاب tag: `v1.0.1`
4. عنوان: `DineSysPro v1.0.1`
5. توضیحات:

```markdown
## 🎉 DineSysPro v1.0.1

### ✨ New Features
- Feature 1
- Feature 2

### 🐛 Bug Fixes
- Fix 1
- Fix 2

### 📦 Downloads
- **macOS**: DineSysPro-1.0.1-macOS.dmg
- **Windows**: DineSysPro-1.0.1-Windows-Setup.exe

### 📋 Installation
- **macOS**: Open DMG and drag to Applications
- **Windows**: Run the installer

### 🔄 Auto-Update
This version supports automatic updates.
```

6. آپلود فایل‌ها:
   - `dist/DineSysPro-1.0.1-macOS.dmg`
   - `dist/DineSysPro-1.0.1-Windows-Setup.exe`

7. کلیک "Publish release"

**روش 2: GitHub CLI**

```bash
gh release create v1.0.1 \
  --title "DineSysPro v1.0.1" \
  --notes-file RELEASE_NOTES.md \
  dist/DineSysPro-1.0.1-macOS.dmg \
  dist/DineSysPro-1.0.1-Windows-Setup.exe
```

#### 7️⃣ تست Auto-Update

```bash
# روی یک سیستم با نسخه قدیمی‌تر
python3 auto_updater.py

# باید نسخه جدید را تشخیص دهد و پیشنهاد دانلود کند
```

---

## 🤖 استفاده از GitHub Actions (خودکار)

GitHub Actions به صورت خودکار build می‌سازد:

### فعال‌سازی:

1. Push کردن یک tag:
```bash
git tag v1.0.1
git push origin v1.0.1
```

2. GitHub Actions به صورت خودکار:
   - ✅ Build macOS را می‌سازد
   - ✅ Build Windows را می‌سازد
   - ✅ Release را ایجاد می‌کند
   - ✅ فایل‌ها را آپلود می‌کند

3. بررسی پیشرفت:
   - برو به: https://github.com/Arsam1313/mars_syspro_universal/actions

---

## 📊 Workflow کامل

```
Development → Testing → Version Bump → Tag → Build → Release → Auto-Update
     ↓           ↓            ↓          ↓       ↓        ↓          ↓
  Feature    Unit Tests   config.json  v1.0.1  .dmg    GitHub   Users Get
   Branch                              git tag  .exe    Release  Notified
```

---

## 🔐 امنیت

### Checksum Verification (آینده)

```python
import hashlib

def verify_download(file_path, expected_sha256):
    """Verify downloaded file integrity"""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest() == expected_sha256
```

### Code Signing (توصیه شده)

**macOS:**
```bash
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name" \
  dist/DineSysPro.app
```

**Windows:**
```cmd
signtool sign /f certificate.pfx /p password dist\DineSysPro.exe
```

---

## 📝 Checklist قبل از Release

- [ ] تمام تست‌ها pass شده‌اند
- [ ] نسخه در `config.json` به‌روز شده
- [ ] `CHANGELOG.md` به‌روز شده
- [ ] Release notes نوشته شده
- [ ] Build برای macOS موفق
- [ ] Build برای Windows موفق
- [ ] فایل‌ها تست شده‌اند
- [ ] Tag ایجاد شده
- [ ] Release در GitHub منتشر شده
- [ ] Auto-update تست شده

---

## 🆘 عیب‌یابی

### مشکل: Auto-update نسخه جدید را نمی‌بیند

```bash
# چک کردن دستی
curl https://api.github.com/repos/Arsam1313/mars_syspro_universal/releases/latest

# بررسی tag
git tag -l

# بررسی release در GitHub
open https://github.com/Arsam1313/mars_syspro_universal/releases
```

### مشکل: دانلود فایل fail می‌شود

- بررسی اتصال اینترنت
- بررسی فضای دیسک
- بررسی دسترسی‌های فایروال

### مشکل: نصب به‌روزرسانی fail می‌شود

**macOS:**
```bash
# حذف quarantine
xattr -cr /path/to/DineSysPro.app
```

**Windows:**
```cmd
# اجرا به عنوان Administrator
```

---

## 📞 پشتیبانی

برای سوالات و مشکلات:
- 🐛 GitHub Issues: https://github.com/Arsam1313/mars_syspro_universal/issues
- 📧 Email: support@dinesyspro.com
- 📚 Documentation: https://github.com/Arsam1313/mars_syspro_universal/wiki

---

## ✅ خلاصه

```bash
# 1. به‌روزرسانی نسخه
nano config.json  # version: "1.0.1"
nano CHANGELOG.md

# 2. Commit و Tag
git add .
git commit -m "Release v1.0.1"
git tag v1.0.1
git push origin main --tags

# 3. Build (یا منتظر GitHub Actions بمانید)
python3 build_macos.py
python build_windows.py  # روی Windows

# 4. Release در GitHub
gh release create v1.0.1 \
  --title "DineSysPro v1.0.1" \
  --notes "Release notes" \
  dist/*.dmg dist/*.exe

# 5. تست
python3 auto_updater.py
```

---

**🎉 سیستم Auto-Update شما آماده است!**

