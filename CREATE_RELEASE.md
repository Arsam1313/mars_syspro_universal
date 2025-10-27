# 🚀 راهنمای ایجاد Release v1.0.0

## ✅ آماده‌سازی کامل شده است!

همه چیز آماده است برای ایجاد اولین release:

- ✅ کد در GitHub push شده
- ✅ Tag v1.0.0 ایجاد شده
- ✅ Application build شده: `dist/DineSysPro.app`
- ✅ فایل zip آماده: `dist/DineSysPro-1.0.0-macOS.zip` (66MB)
- ✅ Release notes نوشته شده: `RELEASE_NOTES_v1.0.0.md`

---

## 📦 فایل‌های آماده برای آپلود

```
/Users/amoreresturang/PycharmProjects/mars_syspro_universal/dist/
└── DineSysPro-1.0.0-macOS.zip  (66 MB)
```

---

## 🌐 ایجاد GitHub Release (روش 1: Web Interface)

### مرحله 1: رفتن به صفحه Releases

1. برو به: **https://github.com/Arsam1313/mars_syspro_universal/releases**
2. کلیک روی **"Draft a new release"** (یا "Create a new release")

### مرحله 2: انتخاب Tag

- **Choose a tag**: `v1.0.0` (باید در لیست باشد)
- اگر نبود، می‌توانید تایپ کنید: `v1.0.0`

### مرحله 3: عنوان و توضیحات

**Release title:**
```
🎉 DineSysPro v1.0.0 - Initial Release
```

**Description:** (کپی کنید از پایین)

```markdown
# 🎉 DineSysPro v1.0.0 - Initial Release

## 🚀 First Stable Release

این اولین نسخه رسمی DineSysPro است - یک سیستم مدیریت سفارشات رستوران با قابلیت پرینت حرفه‌ای.

---

## ✨ ویژگی‌های اصلی

### 🖨️ پشتیبانی کامل از پرینتر
- ✅ پرینترهای USB، LAN (شبکه)، و Bluetooth
- ✅ پشتیبانی از کاغذهای 58mm و 80mm
- ✅ سازگار با پرینترهای HPRT، Star، Epson و تمام پرینترهای ESC/POS
- ✅ چاپ خودکار سفارشات جدید
- ✅ پشتیبانی کامل از کاراکترهای سویدی (åäöÅÄÖ)

### 🌐 یکپارچه‌سازی WebView
- ✅ اتصال به سیستم‌های سفارش‌گیری تحت وب
- ✅ دکمه تنظیمات یکپارچه در صفحه
- ✅ مانیتورینگ سلامت WebView

### 🔊 سیستم هشدار صوتی
- ✅ آلارم برای سفارشات جدید
- ✅ هشدار قطع اینترنت
- ✅ صداهای قابل تنظیم

### 🖥️ Cross-Platform
- ✅ macOS 10.14+
- ✅ Windows 10+ (به زودی)
- ✅ Linux (Ubuntu 18.04+)

### 🎯 ویژگی‌های ویژه
- ✅ **Full Screen Mode**: برای ترمینال‌های POS اختصاصی
- ✅ **Sleep Prevention**: جلوگیری از خواب رفتن دستگاه
- ✅ **Auto-Update**: به‌روزرسانی خودکار از GitHub

---

## 📦 دانلود و نصب

### macOS

1. **دانلود:** `DineSysPro-1.0.0-macOS.zip` (از Assets پایین)
2. **نصب:** فایل zip را باز کنید و `DineSysPro.app` را به Applications بکشید
3. **اجرا:** از Applications اجرا کنید

**اگر macOS اجازه باز شدن نداد:**
```bash
xattr -cr /Applications/DineSysPro.app
```

### Linux

```bash
git clone https://github.com/Arsam1313/mars_syspro_universal.git
cd mars_syspro_universal
pip3 install -r requirements.txt
python3 main.py
```

---

## 🔄 Auto-Update

این نسخه از سیستم به‌روزرسانی خودکار پشتیبانی می‌کند:
- ✅ چک خودکار نسخه جدید
- ✅ دانلود و نصب با یک کلیک
- ✅ حفظ تنظیمات کاربر

---

## 📚 مستندات

- 📖 [README.md](https://github.com/Arsam1313/mars_syspro_universal/blob/main/README.md)
- 🔄 [UPDATE_GUIDE.md](https://github.com/Arsam1313/mars_syspro_universal/blob/main/UPDATE_GUIDE.md)
- 🔨 [BUILD_GUIDE.md](https://github.com/Arsam1313/mars_syspro_universal/blob/main/BUILD_GUIDE.md)
- 📋 [API_DOCUMENTATION.md](https://github.com/Arsam1313/mars_syspro_universal/blob/main/API_DOCUMENTATION.md)

---

## 🐛 گزارش مشکلات

[Report a Bug](https://github.com/Arsam1313/mars_syspro_universal/issues/new)

---

## 📊 آمار

- **تاریخ انتشار:** 27 اکتبر 2024
- **حجم:** 66 MB (macOS)
- **پلتفرم‌ها:** macOS, Linux

---

**🍕 DineSysPro** - Professional Restaurant Management System

Made with ❤️ for restaurants worldwide
```

### مرحله 4: آپلود فایل

در قسمت **"Attach binaries"** یا **"Assets"**:

1. کلیک روی **"Attach files by dragging & dropping, selecting or pasting them"**
2. فایل را انتخاب کنید:
   ```
   /Users/amoreresturang/PycharmProjects/mars_syspro_universal/dist/DineSysPro-1.0.0-macOS.zip
   ```
3. منتظر بمانید تا آپلود کامل شود

### مرحله 5: انتشار

- **Set as the latest release**: ✅ تیک بزنید
- **Set as a pre-release**: ❌ تیک نزنید
- کلیک روی **"Publish release"**

---

## 🔧 ایجاد GitHub Release (روش 2: GitHub CLI)

اگر GitHub CLI نصب کردید:

```bash
# نصب GitHub CLI (اگر نصب نیست)
brew install gh

# Login
gh auth login

# ایجاد Release
cd /Users/amoreresturang/PycharmProjects/mars_syspro_universal

gh release create v1.0.0 \
  --title "🎉 DineSysPro v1.0.0 - Initial Release" \
  --notes-file RELEASE_NOTES_v1.0.0.md \
  dist/DineSysPro-1.0.0-macOS.zip
```

---

## ✅ بعد از انتشار Release

### 1. تست Auto-Update

```bash
# تغییر نسخه به 0.9.0
cd /Users/amoreresturang/PycharmProjects/mars_syspro_universal
nano config.json
# "version": "0.9.0"

# تست updater
python3 auto_updater.py

# خروجی باید باشد:
# 🔍 Current version: 0.9.0
# 📦 Latest version: 1.0.0
# 🆕 New version available!
```

### 2. اشتراک‌گذاری

لینک release شما:
```
https://github.com/Arsam1313/mars_syspro_universal/releases/tag/v1.0.0
```

### 3. بررسی GitHub Actions

اگر GitHub Actions فعال باشد، می‌توانید پیشرفت build را ببینید:
```
https://github.com/Arsam1313/mars_syspro_universal/actions
```

---

## 📊 خلاصه

✅ **آماده برای انتشار:**
- Tag: `v1.0.0` ✅
- Build: `DineSysPro-1.0.0-macOS.zip` ✅
- Release Notes: `RELEASE_NOTES_v1.0.0.md` ✅
- مستندات: کامل ✅

🎯 **مرحله بعدی:**
1. برو به GitHub Releases
2. Draft a new release
3. انتخاب tag v1.0.0
4. کپی کردن release notes
5. آپلود DineSysPro-1.0.0-macOS.zip
6. Publish release

---

**🎉 موفق باشید!**

