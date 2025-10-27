# 🚀 Mars SysPro Universal - Java API Documentation

## 📖 راهنمای استفاده از API برای Java

برنامه Mars SysPro Universal یک **HTTP API Server** دارد که روی پورت **8080** اجرا می‌شود و Java می‌تواند از طریق آن دستورات چاپ و آلارم ارسال کند.

## 🌐 Base URL
```
http://localhost:8080
```

---

## 📄 API Endpoints

### 1. چاپ متن
**POST** `/api/print`

```json
{
  "text": "متن مورد نظر برای چاپ\nخط دوم\nخط سوم"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Print job sent successfully",
  "device_id": "ABC123456789"
}
```

### 2. شروع آلارم
**POST** `/api/alarm/start`

```json
{
  "loops": -1
}
```
- `loops`: تعداد تکرار (-1 = بی‌نهایت, 0 = یک بار, 1 = دو بار)

**Response:**
```json
{
  "success": true,
  "message": "Alarm started",
  "loops": -1
}
```

### 3. توقف آلارم
**POST** `/api/alarm/stop`

**Response:**
```json
{
  "success": true,
  "message": "Alarm stopped"
}
```

### 4. وضعیت برنامه
**GET** `/api/status`

**Response:**
```json
{
  "success": true,
  "device_id": "ABC123456789",
  "printer_connected": true,
  "printer_config": {
    "type": "usb",
    "address": "0x20d1:0x7009",
    "paper_width": 80
  },
  "alarm_playing": false,
  "app_version": "1.2.3"
}
```

### 5. تست چاپ
**POST** `/api/test-print`

**Response:**
```json
{
  "success": true,
  "message": "OK",
  "device_id": "ABC123456789"
}
```

---

## ☕ نمونه کد Java

### نصب کتابخانه HTTP (Maven)
```xml
<dependency>
    <groupId>com.squareup.okhttp3</groupId>
    <artifactId>okhttp</artifactId>
    <version>4.12.0</version>
</dependency>
```

### کلاس Java برای ارتباط با API
```java
import okhttp3.*;
import java.io.IOException;

public class MarsSysProAPI {
    private static final String BASE_URL = "http://localhost:8080";
    private final OkHttpClient client = new OkHttpClient();
    
    // چاپ متن
    public boolean printText(String text) {
        try {
            String json = "{\"text\":\"" + text.replace("\"", "\\\"") + "\"}";
            RequestBody body = RequestBody.create(
                json, MediaType.get("application/json; charset=utf-8"));
            
            Request request = new Request.Builder()
                .url(BASE_URL + "/api/print")
                .post(body)
                .build();
            
            try (Response response = client.newCall(request).execute()) {
                return response.isSuccessful();
            }
        } catch (IOException e) {
            e.printStackTrace();
            return false;
        }
    }
    
    // شروع آلارم
    public boolean startAlarm() {
        return startAlarm(-1); // infinite loop
    }
    
    public boolean startAlarm(int loops) {
        try {
            String json = "{\"loops\":" + loops + "}";
            RequestBody body = RequestBody.create(
                json, MediaType.get("application/json; charset=utf-8"));
            
            Request request = new Request.Builder()
                .url(BASE_URL + "/api/alarm/start")
                .post(body)
                .build();
            
            try (Response response = client.newCall(request).execute()) {
                return response.isSuccessful();
            }
        } catch (IOException e) {
            e.printStackTrace();
            return false;
        }
    }
    
    // توقف آلارم
    public boolean stopAlarm() {
        try {
            RequestBody body = RequestBody.create("", null);
            Request request = new Request.Builder()
                .url(BASE_URL + "/api/alarm/stop")
                .post(body)
                .build();
            
            try (Response response = client.newCall(request).execute()) {
                return response.isSuccessful();
            }
        } catch (IOException e) {
            e.printStackTrace();
            return false;
        }
    }
    
    // بررسی وضعیت
    public String getStatus() {
        try {
            Request request = new Request.Builder()
                .url(BASE_URL + "/api/status")
                .build();
            
            try (Response response = client.newCall(request).execute()) {
                if (response.isSuccessful() && response.body() != null) {
                    return response.body().string();
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        return null;
    }
    
    // تست چاپ
    public boolean testPrint() {
        try {
            RequestBody body = RequestBody.create("", null);
            Request request = new Request.Builder()
                .url(BASE_URL + "/api/test-print")
                .post(body)
                .build();
            
            try (Response response = client.newCall(request).execute()) {
                return response.isSuccessful();
            }
        } catch (IOException e) {
            e.printStackTrace();
            return false;
        }
    }
}
```

### نمونه استفاده
```java
public class Main {
    public static void main(String[] args) {
        MarsSysProAPI api = new MarsSysProAPI();
        
        // چاپ رسید
        String receipt = "==================\n" +
                        "    رستوران نمونه    \n" +
                        "==================\n" +
                        "سفارش #1234\n" +
                        "کباب کوبیده: 25000 تومان\n" +
                        "نوشابه: 5000 تومان\n" +
                        "------------------\n" +
                        "مجموع: 30000 تومان\n" +
                        "==================\n";
        
        if (api.printText(receipt)) {
            System.out.println("✅ Print successful!");
        } else {
            System.out.println("❌ Print failed!");
        }
        
        // پخش آلارم برای سفارش جدید
        if (api.startAlarm(3)) { // 3 بار تکرار
            System.out.println("🔔 Alarm started!");
            
            // بعد از 5 ثانیه آلارم را متوقف کن
            try {
                Thread.sleep(5000);
                api.stopAlarm();
                System.out.println("🔇 Alarm stopped!");
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
        
        // بررسی وضعیت
        String status = api.getStatus();
        System.out.println("📊 Status: " + status);
    }
}
```

---

## 🔄 cURL Commands (تست)

```bash
# چاپ
curl -X POST http://localhost:8080/api/print \
  -H "Content-Type: application/json" \
  -d '{"text":"تست چاپ از cURL\nخط دوم"}'

# شروع آلارم
curl -X POST http://localhost:8080/api/alarm/start \
  -H "Content-Type: application/json" \
  -d '{"loops":3}'

# توقف آلارم
curl -X POST http://localhost:8080/api/alarm/stop

# وضعیت
curl http://localhost:8080/api/status

# تست چاپ
curl -X POST http://localhost:8080/api/test-print
```

---

## ⚠️ نکات مهم

1. **اجرای برنامه**: ابتدا Mars SysPro Universal را اجرا کنید
2. **پورت**: API روی پورت 8080 در دسترس است
3. **Encoding**: از UTF-8 برای متن‌های فارسی استفاده کنید
4. **خطا handling**: همیشه response را بررسی کنید
5. **Thread safety**: API thread-safe است

## 🎯 **آماده استفاده!**

حالا Java شما می‌تواند مستقیماً با Mars SysPro Universal ارتباط برقرار کند! 🚀

