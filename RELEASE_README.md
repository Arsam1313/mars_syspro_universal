# 📦 DineSysPro - راهنمای نصب

به DineSysPro خوش آمدید! این برنامه یک سیستم مدیریت سفارشات رستوران با قابلیت پرینت حرفه‌ای است.

---

## 🍎 نصب در macOS

### مرحله 1: دانلود
فایل `DineSysPro-X.X.X-macOS.dmg` را دانلود کنید.

### مرحله 2: نصب
1. فایل `.dmg` را دوبار کلیک کنید
2. `DineSysPro.app` را به پوشه `Applications` بکشید

### مرحله 3: اجرای اولین بار

**⚠️ مهم:** ممکن است macOS به دلیل Gatekeeper اجازه باز شدن برنامه را ندهد.

**راه‌حل سریع:**
```bash
# در Terminal اجرا کنید:
xattr -cr /Applications/DineSysPro.app
```

**یا:**
- روی برنامه **Right-Click** کنید
- **Open** را انتخاب کنید
- در پنجره باز شده، روی **Open** کلیک کنید

📖 **راهنمای کامل:** [MACOS_INSTALL_GUIDE.md](https://github.com/Arsam1313/mars_syspro_universal/blob/main/MACOS_INSTALL_GUIDE.md)

---

## 🪟 نصب در Windows

### مرحله 1: دانلود
فایل `DineSysPro-X.X.X-Windows-Setup.exe` یا `DineSysPro.exe` را دانلود کنید.

### مرحله 2: نصب

**اگر Setup.exe دارید:**
1. فایل را دوبار کلیک کنید
2. مراحل نصب را دنبال کنید
3. برنامه را از Start Menu اجرا کنید

**اگر فقط DineSysPro.exe دارید:**
- این یک فایل portable است
- کافیست دوبار کلیک کنید!

### ⚠️ هشدار Windows Defender

ممکن است Windows Defender یک هشدار نمایش دهد (چون برنامه unsigned است):

1. روی **More info** کلیک کنید
2. روی **Run anyway** کلیک کنید

---

## 🐧 نصب در Linux

### Ubuntu/Debian:
```bash
# اجازه اجرا بدهید
chmod +x DineSysPro-X.X.X-Linux.AppImage

# اجرا کنید
./DineSysPro-X.X.X-Linux.AppImage
```

---

## ⚙️ پیکربندی اولیه

پس از اجرای برنامه:

1. روی دکمه **⚙️** (پایین سمت راست) کلیک کنید
2. تنظیمات پرینتر را انجام دهید:
   - نوع پرینتر: USB / LAN / Bluetooth
   - اندازه کاغذ: 58mm یا 80mm
3. تنظیمات را ذخیره کنید

---

## 🖨️ راه‌اندازی پرینتر

### macOS:
1. پرینتر را در **System Preferences > Printers & Scanners** اضافه کنید
2. نام پرینتر را در تنظیمات DineSysPro وارد کنید

### Windows:
1. پرینتر را در **Settings > Devices > Printers** نصب کنید
2. نام پرینتر را در تنظیمات DineSysPro وارد کنید

---

## 🔄 به‌روزرسانی خودکار

DineSysPro به صورت خودکار نسخه‌های جدید را چک می‌کند و اطلاع می‌دهد.

برای به‌روزرسانی دستی:
- macOS: فایل جدید را دانلود و جایگزین کنید
- Windows: نسخه جدید را نصب کنید

---

## 🆘 پشتیبانی

### مشکلات رایج:

**برنامه باز نمیشه (macOS):**
```bash
xattr -cr /Applications/DineSysPro.app
```

**پرینتر کار نمی‌کنه:**
- چک کنید پرینتر روشن و متصل است
- نام پرینتر را در تنظیمات بررسی کنید
- تست پرینت از سیستم عامل انجام دهید

**صدا پخش نمیشه:**
- چک کنید volume سیستم روشن است
- فایل‌های صوتی در پوشه `sounds/` موجودند

### لینک‌های مفید:

- 📖 **مستندات کامل:** [README.md](https://github.com/Arsam1313/mars_syspro_universal)
- 🐛 **گزارش مشکل:** [GitHub Issues](https://github.com/Arsam1313/mars_syspro_universal/issues)
- 🚀 **راهنمای Build:** [BUILD_GUIDE.md](https://github.com/Arsam1313/mars_syspro_universal/blob/main/BUILD_GUIDE.md)

---

## ✨ ویژگی‌ها

- 🖨️ پشتیبانی از پرینترهای USB, LAN, Bluetooth
- 📄 پشتیبانی از کاغذ 58mm و 80mm
- 🇸🇪 پشتیبانی کامل از حروف سوئدی (åäöÅÄÖ)
- 🔊 هشدارهای صوتی برای سفارش جدید
- 🌐 اتصال به سیستم سفارش‌گیری وب
- 🔄 به‌روزرسانی خودکار
- 🎯 حالت تمام صفحه برای ترمینال‌های POS
- ☕ جلوگیری از خواب رفتن دستگاه

---

## 📋 سیستم مورد نیاز

- **macOS:** 10.14 یا بالاتر
- **Windows:** 10 یا بالاتر
- **Linux:** Ubuntu 18.04+ یا معادل
- **پرینتر:** هر پرینتر حرارتی سازگار با ESC/POS

---

## 📞 تماس با ما

- 🌐 **وبسایت:** https://github.com/Arsam1313/mars_syspro_universal
- 📧 **ایمیل:** support@dinesyspro.com
- 🐛 **گزارش باگ:** [GitHub Issues](https://github.com/Arsam1313/mars_syspro_universal/issues)

---

**🎉 از استفاده از DineSysPro لذت ببرید!**

---

## 📝 یادداشت‌های نسخه

برای مشاهده تغییرات هر نسخه، به [CHANGELOG.md](https://github.com/Arsam1313/mars_syspro_universal/blob/main/CHANGELOG.md) مراجعه کنید.

## 📜 مجوز

این نرم‌افزار تحت مجوز MIT منتشر شده است.

