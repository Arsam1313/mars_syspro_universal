# 🍎 راهنمای نصب DineSysPro در macOS

اگر هنگام باز کردن DineSysPro پیام **"Du kan inte öppna appen DineSysPro eftersom den inte stöds på den här datorn"** یا پیام مشابهی دریافت کردید، این راهنما به شما کمک می‌کند.

---

## 🔒 چرا این مشکل پیش می‌آید؟

macOS به صورت پیش‌فرض فقط به برنامه‌های **امضا شده (signed)** از توسعه‌دهندگان معتبر اجازه اجرا می‌دهد. این یک ویژگی امنیتی به نام **Gatekeeper** است.

---

## ✅ راه‌حل 1: حذف Quarantine (سریع و آسان)

### مرحله 1: باز کردن Terminal

از Spotlight (⌘ + Space) تایپ کنید: **Terminal**

### مرحله 2: اجرای دستور

```bash
xattr -cr /Applications/DineSysPro.app
```

یا اگر فایل را در جای دیگری دارید:

```bash
xattr -cr ~/Downloads/DineSysPro.app
```

### مرحله 3: اجرای برنامه

حالا برنامه را دوباره باز کنید. باید بدون مشکل اجرا شود! ✅

---

## ✅ راه‌حل 2: استفاده از System Settings

### مرحله 1: سعی در باز کردن

روی `DineSysPro.app` دوبار کلیک کنید. پیام خطا ظاهر می‌شود.

### مرحله 2: System Settings

1. برید به: **System Settings** (یا System Preferences)
2. کلیک روی **Privacy & Security**
3. به پایین scroll کنید
4. پیامی مشابه این را خواهید دید:
   > "DineSysPro was blocked from use because it is not from an identified developer"
5. کلیک روی **Open Anyway**

### مرحله 3: تایید

پنجره‌ای باز می‌شود، روی **Open** کلیک کنید.

---

## ✅ راه‌حل 3: استفاده از Right-Click

1. روی `DineSysPro.app` **right-click** کنید (یا Control + Click)
2. از منو، **Open** را انتخاب کنید
3. در پنجره‌ای که باز می‌شود، روی **Open** کلیک کنید

این روش **بار اول** کار می‌کند و بعد از آن برنامه به طور عادی باز می‌شود.

---

## 🔐 برای توسعه‌دهندگان: Code Signing

اگر می‌خواهید این مشکل برای کاربران نهایی رخ ندهد، باید برنامه را **امضا (sign)** کنید:

### پیش‌نیاز:
- یک Apple Developer Account ($99/سال)
- Developer ID Application Certificate

### دستورات:

```bash
# 1. لیست certificate های موجود
security find-identity -v -p codesigning

# 2. امضای برنامه
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name (TEAM_ID)" \
  --options runtime \
  dist/DineSysPro.app

# 3. تایید امضا
codesign --verify --deep --strict --verbose=2 dist/DineSysPro.app
spctl -a -t exec -vv dist/DineSysPro.app

# 4. Notarization (اختیاری اما توصیه می‌شود)
xcrun notarytool submit dist/DineSysPro.app \
  --apple-id "your@email.com" \
  --team-id "TEAM_ID" \
  --password "app-specific-password"
```

---

## 🆘 همچنان مشکل دارید؟

### خطا: "The application is damaged and can't be opened"

این معمولاً به خاطر incomplete download یا corruption است:

```bash
# حذف و دانلود مجدد
rm -rf /Applications/DineSysPro.app
# سپس فایل را دوباره دانلود و نصب کنید
```

### خطا: "No application is set to open the document"

این به معنای نادرست build شدن برنامه است:

```bash
# بررسی ساختار app bundle
ls -la /Applications/DineSysPro.app/Contents/MacOS/
# باید یک فایل executable به نام DineSysPro وجود داشته باشد

# بررسی permissions
chmod +x /Applications/DineSysPro.app/Contents/MacOS/DineSysPro
```

---

## 📋 Checklist نصب

- [ ] فایل `.dmg` یا `.app` را دانلود کردید
- [ ] اگر `.dmg` است، آن را mount کنید
- [ ] `DineSysPro.app` را به `/Applications` کپی کنید
- [ ] Terminal را باز کنید
- [ ] دستور `xattr -cr /Applications/DineSysPro.app` را اجرا کنید
- [ ] برنامه را از Applications folder باز کنید
- [ ] ✅ لذت ببرید!

---

## 🔗 لینک‌های مفید

- [Apple Gatekeeper Documentation](https://support.apple.com/en-us/HT202491)
- [Code Signing Guide](https://developer.apple.com/documentation/security/code_signing_services)
- [Notarization Guide](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)

---

## 💡 نکته امنیتی

فقط از منابع معتبر برنامه دانلود کنید:
- ✅ GitHub Releases رسمی: https://github.com/Arsam1313/mars_syspro_universal/releases
- ❌ از سایت‌های ناشناس دانلود نکنید

---

**🎉 پس از حل مشکل، DineSysPro آماده استفاده است!**

