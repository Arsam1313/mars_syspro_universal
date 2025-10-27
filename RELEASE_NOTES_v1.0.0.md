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
- ✅ رفرش خودکار در صورت قطعی

### 🔊 سیستم هشدار صوتی
- ✅ آلارم برای سفارشات جدید
- ✅ هشدار قطع اینترنت
- ✅ هشدار باتری کم
- ✅ صداهای قابل تنظیم توسط کاربر

### ⚙️ تنظیمات آسان
- ✅ رابط کاربری ساده و کاربرپسند
- ✅ تنظیمات پرینتر بدون نیاز به کد
- ✅ انتخاب آسان صداهای آلارم
- ✅ نمایش نسخه و Device ID

### 🖥️ Cross-Platform
- ✅ macOS 10.14+
- ✅ Windows 10+
- ✅ Linux (Ubuntu 18.04+)

### 🎯 ویژگی‌های ویژه
- ✅ **Full Screen Mode**: برای ترمینال‌های POS اختصاصی
- ✅ **Sleep Prevention**: جلوگیری از خواب رفتن دستگاه
- ✅ **Auto-Update**: به‌روزرسانی خودکار از GitHub
- ✅ **Internet Monitoring**: مانیتورینگ مداوم اتصال اینترنت
- ✅ **Device ID Tracking**: شناسایی یکتای هر دستگاه

---

## 📦 دانلود و نصب

### macOS

1. **دانلود فایل:**
   - [DineSysPro-1.0.0-macOS.zip](https://github.com/Arsam1313/mars_syspro_universal/releases/download/v1.0.0/DineSysPro-1.0.0-macOS.zip)

2. **نصب:**
   - فایل zip را باز کنید
   - `DineSysPro.app` را به پوشه Applications بکشید
   - از Applications اجرا کنید

3. **اگر macOS اجازه باز شدن نداد:**
   ```bash
   xattr -cr /Applications/DineSysPro.app
   ```

### Windows

**توجه:** Build Windows در نسخه‌های بعدی ارائه خواهد شد.

### Linux

برای لینوکس، از source اجرا کنید:
```bash
git clone https://github.com/Arsam1313/mars_syspro_universal.git
cd mars_syspro_universal
pip3 install -r requirements.txt
python3 main.py
```

---

## ⚙️ پیکربندی اولیه

### 1. تنظیم پرینتر

هنگام اولین اجرا:
1. روی دکمه ⚙️ (Settings) کلیک کنید
2. نوع پرینتر را انتخاب کنید (USB/LAN/Bluetooth)
3. آدرس پرینتر را وارد کنید
4. عرض کاغذ را انتخاب کنید (58mm یا 80mm)
5. تست پرینت انجام دهید

### 2. تنظیم URL اپلیکیشن

در فایل `config.json`:
```json
{
  "app_url": "http://your-domain.com/order-reception.html"
}
```

### 3. انتخاب صداهای آلارم

از Settings می‌توانید صداهای مختلف را انتخاب کنید.

---

## 🔄 Auto-Update

این نسخه از سیستم به‌روزرسانی خودکار پشتیبانی می‌کند:

- ✅ چک خودکار نسخه جدید هنگام شروع
- ✅ اطلاع‌رسانی به کاربر
- ✅ دانلود و نصب با یک کلیک
- ✅ حفظ تنظیمات کاربر

برای چک دستی:
```bash
python3 auto_updater.py
```

---

## 📋 API Endpoints

برای یکپارچه‌سازی با سیستم‌های خارجی:

```
POST /api/print          - چاپ متن
POST /api/test-print     - تست پرینتر
POST /api/play-alert     - پخش آلارم
POST /api/stop-alert     - توقف آلارم
GET  /api/scan-printers  - جستجوی پرینترها
```

مستندات کامل: [API_DOCUMENTATION.md](https://github.com/Arsam1313/mars_syspro_universal/blob/main/API_DOCUMENTATION.md)

---

## 🐛 مشکلات شناخته شده

### v1.0.0
- هیچ مشکل شناخته شده‌ای گزارش نشده

اگر مشکلی پیدا کردید، لطفاً در [GitHub Issues](https://github.com/Arsam1313/mars_syspro_universal/issues) گزارش دهید.

---

## 📚 مستندات

- 📖 [README.md](https://github.com/Arsam1313/mars_syspro_universal/blob/main/README.md) - راهنمای اصلی
- 🔄 [UPDATE_GUIDE.md](https://github.com/Arsam1313/mars_syspro_universal/blob/main/UPDATE_GUIDE.md) - راهنمای به‌روزرسانی
- 🔨 [BUILD_GUIDE.md](https://github.com/Arsam1313/mars_syspro_universal/blob/main/BUILD_GUIDE.md) - راهنمای build
- ✨ [FEATURES.md](https://github.com/Arsam1313/mars_syspro_universal/blob/main/FEATURES.md) - لیست کامل ویژگی‌ها
- 📋 [API_DOCUMENTATION.md](https://github.com/Arsam1313/mars_syspro_universal/blob/main/API_DOCUMENTATION.md) - مستندات API

---

## 🔜 نسخه‌های آینده

### v1.1.0 (برنامه‌ریزی شده)
- [ ] Build Windows
- [ ] پشتیبانی از چند زبان
- [ ] تمپلیت‌های سفارشی رسید
- [ ] گزارش‌گیری پیشرفته

### v1.2.0 (برنامه‌ریزی شده)
- [ ] پشتیبانی از چند رستوران
- [ ] Cloud sync تنظیمات
- [ ] Mobile app برای مانیتورینگ
- [ ] چاپ بارکد/QR code

---

## 🤝 مشارکت

ما از مشارکت شما استقبال می‌کنیم! برای مشارکت:

1. Fork کنید
2. Feature branch بسازید
3. تغییرات را commit کنید
4. Pull Request بفرستید

---

## 📞 پشتیبانی

برای سوالات و مشکلات:

- 🐛 [GitHub Issues](https://github.com/Arsam1313/mars_syspro_universal/issues)
- 📧 Email: support@dinesyspro.com
- 📚 [Wiki](https://github.com/Arsam1313/mars_syspro_universal/wiki)

---

## 📊 آمار نسخه

- **تاریخ انتشار:** 27 اکتبر 2024
- **حجم فایل:** 66 MB (macOS)
- **نسخه Python:** 3.11+
- **پلتفرم‌ها:** macOS, Windows (به زودی), Linux

---

## 📄 مجوز

MIT License - برای جزئیات به [LICENSE](https://github.com/Arsam1313/mars_syspro_universal/blob/main/LICENSE) مراجعه کنید.

---

## 🙏 تشکر

- Built with [PyWebView](https://pywebview.flowrl.com/)
- Printer support via [python-escpos](https://python-escpos.readthedocs.io/)
- Sound playback with [pygame](https://www.pygame.org/)

---

**🍕 DineSysPro v1.0.0** - Professional Restaurant Management System

Made with ❤️ for restaurants worldwide

---

## 💬 بازخورد

نظرات و پیشنهادات شما برای ما ارزشمند است! لطفاً بازخورد خود را در [Discussions](https://github.com/Arsam1313/mars_syspro_universal/discussions) به اشتراک بگذارید.

---

**🎉 از استفاده از DineSysPro متشکریم!**

