import webview
import threading
import time
import requests
import json
import uuid
import platform
import socket
import os
import urllib3
import pygame
from printer_manager import (
    PrinterManager,
    discover_lan_printers,
    discover_bluetooth_printers
)
from flask import Flask, request, jsonify
from flask_cors import CORS

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

APP_URL = "http://localhost:3001/order-reception.html"
API_HEARTBEAT = "http://95.217.217.200:3001/api/heartbeat"
CONFIG_PATH = "config.json"
APP_VERSION = "1.2.3"

pygame.mixer.init()
# ALARM_SOUND حالا dynamic هست از config

# 🌐 Flask API Server برای Java
app = Flask(__name__)
CORS(app)  # اجازه دسترسی از Java
LOCAL_API_PORT = 8080

# متغیر کنترل آلارم
alarm_playing = False

# متغیرهای مانیتورینگ
internet_connected = True
webview_healthy = True
monitoring_active = True

# 🎯 API Endpoints برای Java
@app.route('/api/print', methods=['POST'])
def api_print():
    """API برای چاپ متن از Java"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"success": False, "error": "No text provided"}), 400
        
        text = data['text']
        print("📄 Print request from Java")
        print("📋 Full API print text content:")
        print("=" * 50)
        print(text)
        print("=" * 50)
        
        # 🎯 استفاده از Direct CUPS مثل test_print موفق
        print("🚀 API using DIRECT CUPS...")
        import subprocess
        
        # 🔄 بازگشت به python-escpos (CUPS محدودیت داره)
        from escpos import printer
        print("🔄 API using python-escpos instead of CUPS...")
        
        # CUPS با chunked method + paper width formatting
        try:
            import time
            import tempfile
            import os
            
            # تنظیم عرض کاغذ بر اساس config
            current_config = config["printer"]
            paper_width = current_config.get("paper_width", 80)
            
            # محاسبه تعداد کاراکتر بر اساس عرض کاغذ
            if paper_width == 58:
                max_chars = 32  # کاغذ 58 میلی‌متری
                print("📏 API Using 58mm paper width (32 chars per line)")
            else:  # 80mm default
                max_chars = 48  # کاغذ 80 میلی‌متری  
                print("📏 API Using 80mm paper width (48 chars per line)")
            
            # فرمت کردن متن برای عرض کاغذ
            formatted_lines = []
            for line in text.split('\n'):
                if len(line) <= max_chars:
                    formatted_lines.append(line)
                else:
                    # تقسیم خطوط طولانی
                    while len(line) > max_chars:
                        formatted_lines.append(line[:max_chars])
                        line = line[max_chars:]
                    if line:  # باقی‌مانده
                        formatted_lines.append(line)
            
            # فقط خطوط غیر خالی
            lines = [line for line in formatted_lines if line.strip()]
            total_lines = len(lines)
            chunk_size = 6  # کمتر از حد buffer برای اطمینان
            
            print(f"📏 API CUPS Chunked: Printing {total_lines} lines in chunks of {chunk_size}...")
            
            chunk_results = []
            
            for chunk_start in range(0, total_lines, chunk_size):
                chunk_end = min(chunk_start + chunk_size, total_lines)
                chunk_lines = lines[chunk_start:chunk_end]
                
                print(f"🔄 API CUPS Chunk {chunk_start//chunk_size + 1}: lines {chunk_start+1}-{chunk_end}")
                
                # ساخت متن chunk
                chunk_text = '\n'.join(chunk_lines) + '\n\n'
                
                # چاپ هر chunk جداگانه
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as tmp_file:
                    tmp_file.write(chunk_text)
                    tmp_file.flush()
                    tmp_file_path = tmp_file.name
                
                try:
                    chunk_result = subprocess.run([
                        '/usr/bin/lp', '-d', 'HPRT_TP808', 
                        '-o', 'CutMode=0',  # بدون کات بین chunks
                        tmp_file_path
                    ], capture_output=True, text=True, timeout=30)
                    
                    chunk_results.append(chunk_result.returncode)
                    print(f"✅ API Chunk {chunk_start//chunk_size + 1} sent: {chunk_result.stdout.strip()}")
                    
                finally:
                    try:
                        os.unlink(tmp_file_path)
                    except:
                        pass
                
                # delay کوچک بین chunks
                if chunk_end < total_lines:
                    time.sleep(0.2)  # delay کمتر - صدای کمتر
                    print("⏱️ API CUPS Buffer delay...")
            
            # final cut در انتها
            final_cut = subprocess.run([
                '/usr/bin/lp', '-d', 'HPRT_TP808', '-'
            ], input='\n\n', text=True, capture_output=True)
            
            # نتیجه کلی
            success_chunks = sum(1 for r in chunk_results if r == 0)
            direct_result = type('MockResult', (), {
                'returncode': 0 if success_chunks == len(chunk_results) else 1,
                'stdout': f'API CUPS chunked: {success_chunks}/{len(chunk_results)} chunks successful'
            })()
            
        except Exception as e:
            print(f"❌ API python-escpos failed: {e}")
            # fallback to CUPS with better options
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as tmp_file:
                tmp_file.write(text)
                tmp_file.flush()
                tmp_file_path = tmp_file.name
            
            try:
                direct_result = subprocess.run([
                    "/usr/bin/lp", "-d", "HPRT_TP808", "-o", "CutMode=0", "-o", "FormfeedLength=20", tmp_file_path
                ], capture_output=True, text=True, timeout=30)
            finally:
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass
        
        if direct_result.returncode == 0:
            print(f"✅ API Direct CUPS successful: {direct_result.stdout}")
            return jsonify({
                "success": True, 
                "message": "Print job sent successfully",
                "device_id": get_device_id()
            })
        else:
            print(f"❌ API Direct CUPS failed: {direct_result.stderr}")
            return jsonify({"success": False, "error": f"Print failed: {direct_result.stderr}"}), 500
        
    except Exception as e:
        print(f"❌ Print API error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/alarm/start', methods=['POST'])
def api_alarm_start():
    """شروع پخش آلارم"""
    global alarm_playing
    try:
        # پارامترهای اختیاری
        data = request.get_json() or {}
        loops = data.get('loops', -1)  # -1 = infinite loop
        
        if alarm_playing:
            return jsonify({"success": False, "message": "Alarm already playing"})
        
        print("🔔 Starting alarm from Java API...")
        pygame.mixer.music.load(ALARM_SOUND)
        pygame.mixer.music.play(loops=loops)
        alarm_playing = True
        
        return jsonify({
            "success": True, 
            "message": "Alarm started",
            "loops": loops
        })
        
    except Exception as e:
        print(f"❌ Alarm start error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/alarm/stop', methods=['POST'])
def api_alarm_stop():
    """توقف آلارم"""
    global alarm_playing
    try:
        print("🔇 Stopping alarm from Java API...")
        pygame.mixer.music.stop()
        alarm_playing = False
        
        return jsonify({
            "success": True, 
            "message": "Alarm stopped"
        })
        
    except Exception as e:
        print(f"❌ Alarm stop error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/status', methods=['GET'])
def api_status():
    """وضعیت کامل سیستم"""
    return jsonify({
        "success": True,
        "device_id": get_device_id(),
        "printer_connected": printer.prn is not None,
        "printer_config": config["printer"],
        "alarm_playing": alarm_playing,
        "internet_connected": internet_connected,
        "webview_healthy": webview_healthy,
        "sounds": config.get("sounds", {}),
        "app_version": APP_VERSION
    })

@app.route('/api/test-print', methods=['POST'])
def api_test_print():
    """تست چاپ از Java"""
    try:
        settings_bridge = SettingsBridge()
        result = settings_bridge.test_print()
        
        success = "OK" in str(result)
        return jsonify({
            "success": success,
            "message": result,
            "device_id": get_device_id()
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/sound/set', methods=['POST'])
def api_set_sound():
    """تنظیم صداها"""
    try:
        data = request.get_json()
        sound_type = data.get("type")  # new_order, internet_lost, low_battery
        sound_file = data.get("file")  # neworder.mp3, neworder1.mp3, neworder2.mp3, etc.
        
        if sound_type not in ["new_order", "internet_lost", "low_battery"]:
            return jsonify({"success": False, "error": "Invalid sound type"}), 400
        
        # بروزرسانی config
        if "sounds" not in config:
            config["sounds"] = {}
        
        config["sounds"][sound_type] = sound_file
        
        # ذخیره در فایل
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2)
        
        return jsonify({
            "success": True,
            "message": f"Sound {sound_type} set to {sound_file}",
            "sounds": config["sounds"]
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/sound/test', methods=['POST'])
def api_test_sound():
    """تست پخش صدا"""
    try:
        data = request.get_json()
        sound_type = data.get("type", "new_order")
        
        bridge = Bridge()
        result = bridge.play_alert(sound_type)
        
        if result == "OK":
            return jsonify({
                "success": True,
                "message": f"Playing {sound_type} sound"
            })
        else:
            return jsonify({"success": False, "error": result}), 500
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/sound/stop', methods=['POST'])
def api_stop_sound():
    """توقف صدا"""
    try:
        bridge = Bridge()
        result = bridge.stop_alert()
        
        return jsonify({
            "success": True,
            "message": "Sound stopped"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/battery/alert', methods=['POST'])
def api_battery_alert():
    """آلارم باطری کم"""
    try:
        bridge = Bridge()
        result = bridge.play_alert("low_battery")
        
        if result == "OK":
            return jsonify({
                "success": True,
                "message": "Low battery alert started"
            })
        else:
            return jsonify({"success": False, "error": result}), 500
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def check_internet_connection():
    """چک کردن اتصال اینترنت"""
    import socket
    try:
        # تلاش برای اتصال به DNS گوگل
        socket.create_connection(("8.8.8.8", 53), 3)
        return True
    except OSError:
        return False

def check_webview_health():
    """چک کردن سلامت صفحه WebView"""
    try:
        import requests
        current_url = config.get("app_url", "http://localhost:3001")
        response = requests.get(current_url, timeout=5)
        return response.status_code == 200
    except:
        return False

def internet_monitor():
    """مانیتورینگ اتصال اینترنت در background"""
    global internet_connected, alarm_playing, monitoring_active
    import time
    
    while monitoring_active:
        try:
            is_connected = check_internet_connection()
            
            if not is_connected and internet_connected:
                # اینترنت قطع شد
                internet_connected = False
                print("🚨 Internet connection lost!")
                
                # شروع آلارم با صدای مخصوص اینترنت
                if not alarm_playing:
                    bridge = Bridge()
                    bridge.play_alert("internet_lost")
                    print("🔔 Internet alarm started")
                
            elif is_connected and not internet_connected:
                # اینترنت وصل شد
                internet_connected = True
                print("✅ Internet connection restored!")
                
                # توقف آلارم
                if alarm_playing:
                    bridge = Bridge()
                    bridge.stop_alert()
                    print("🔇 Internet alarm stopped")
                
                # رفرش صفحه WebView
                try:
                    if 'window' in globals():
                        window.evaluate_js("location.reload();")
                        print("🔄 WebView page refreshed")
                except:
                    print("⚠️ Could not refresh WebView")
            
            time.sleep(5)  # چک هر 5 ثانیه
            
        except Exception as e:
            print(f"❌ Internet monitor error: {e}")
            time.sleep(10)

def webview_health_monitor():
    """مانیتورینگ سلامت صفحه WebView در background"""
    global webview_healthy, monitoring_active
    import time
    
    while monitoring_active:
        try:
            is_healthy = check_webview_health()
            
            if not is_healthy and webview_healthy:
                # صفحه WebView مشکل دارد
                webview_healthy = False
                print("🚨 WebView health check failed!")
                
                # نمایش پیام روی صفحه
                try:
                    if 'window' in globals():
                        window.evaluate_js("""
                            if (!document.getElementById('system-error-overlay')) {
                                const overlay = document.createElement('div');
                                overlay.id = 'system-error-overlay';
                                overlay.style.cssText = `
                                    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                                    background: rgba(255,0,0,0.9); color: white; z-index: 9999;
                                    display: flex; align-items: center; justify-content: center;
                                    flex-direction: column; font-size: 24px; text-align: center;
                                `;
                                overlay.innerHTML = `
                                    <div>⚠️ سیستم قطع است</div>
                                    <div style="font-size: 16px; margin-top: 20px;">در حال تلاش برای وصل شدن...</div>
                                `;
                                document.body.appendChild(overlay);
                            }
                        """)
                        print("🚨 System error overlay displayed")
                except:
                    print("⚠️ Could not display error overlay")
                
            elif is_healthy and not webview_healthy:
                # صفحه WebView بهبود یافت
                webview_healthy = True
                print("✅ WebView health restored!")
                
                # حذف پیام خطا و رفرش
                try:
                    if 'window' in globals():
                        window.evaluate_js("""
                            const overlay = document.getElementById('system-error-overlay');
                            if (overlay) overlay.remove();
                            location.reload();
                        """)
                        print("🔄 WebView error cleared and refreshed")
                except:
                    print("⚠️ Could not clear error overlay")
            
            time.sleep(10)  # چک هر 10 ثانیه
            
        except Exception as e:
            print(f"❌ WebView health monitor error: {e}")
            time.sleep(15)

def start_flask_server():
    """اجرای Flask server در background"""
    try:
        print(f"🌐 Starting API server on http://localhost:{LOCAL_API_PORT}")
        app.run(host='0.0.0.0', port=LOCAL_API_PORT, debug=False, threaded=True)
    except Exception as e:
        print(f"❌ Flask server error: {e}")

# 📦 بارگذاری تنظیمات
try:
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
except Exception:
    config = {
        "printer": {"type": "lan", "address": "192.168.1.50", "paper_width": 80},
        "app_url": "http://localhost:3001/order-reception.html",
        "sounds": {
            "new_order": "neworder.mp3",  # یکی از: neworder.mp3, neworder1.mp3, neworder2.mp3
            "internet_lost": "no_internet_alert.mp3",
            "low_battery": "low_battery.mp3"
        }
    }
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)

# مطمئن شدن از وجود تنظیمات کامل
config_updated = False

if "app_url" not in config:
    config["app_url"] = "http://localhost:3001/order-reception.html"
    config_updated = True

if "sounds" not in config:
    config["sounds"] = {
        "new_order": "neworder.mp3",
        "internet_lost": "no_internet_alert.mp3",
        "low_battery": "low_battery.mp3"
    }
    config_updated = True

if config_updated:
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)

# 🖨️ راه‌اندازی پرینتر
printer = PrinterManager(config["printer"]["type"], config["printer"]["address"])
printer.connect()

# 🆔 شناسه دستگاه و سیستم
def get_device_id():
    path = "device_info.json"
    if os.path.exists(path):
        return json.load(open(path))["device_id"]
    did = f"{uuid.getnode():012X}"
    json.dump({"device_id": did}, open(path, "w"))
    return did

def get_device_info():
    return {
        "device_id": get_device_id(),
        "device_info": {
            "platform": platform.system(),
            "system": "python-desktop",
            "os_version": platform.release(),
            "hostname": socket.gethostname(),
            "app_version": APP_VERSION
        }
    }

# 💗 Heartbeat Thread
def heartbeat_task():
    headers = {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "x-site-origin": "dinesyspro-client"
    }
    while True:
        try:
            payload = get_device_info()
            res = requests.post(API_HEARTBEAT, json=payload, headers=headers, timeout=5)
            data = res.json()
            if data.get("success"):
                print(f"💗 Heartbeat OK ({data.get('timestamp')})")
            else:
                print("⚠️ Heartbeat failed:", data)
        except Exception as e:
            print("❌ Heartbeat error:", e)
        time.sleep(30)

threading.Thread(target=heartbeat_task, daemon=True).start()

# 🌐 راه‌اندازی Flask API Server
threading.Thread(target=start_flask_server, daemon=True).start()

# 🔍 راه‌اندازی مانیتورینگ سیستم
print("🔍 Starting system monitoring...")
threading.Thread(target=internet_monitor, daemon=True).start()
threading.Thread(target=webview_health_monitor, daemon=True).start()
print("✅ Internet and WebView monitoring started")


# ⚙️ پنل تنظیمات
class SettingsBridge:
    def get_config(self):
        return config["printer"]

    def scan_printers(self, conn_type):
        print(f"🧩 scan_printers called with type={conn_type}")
        try:
            if conn_type == "lan":
                result = discover_lan_printers()
                return result if result else ["No LAN printers found"]
            elif conn_type == "bluetooth":
                result = discover_bluetooth_printers()
                return result if result else ["No Bluetooth printers found"]
            elif conn_type == "usb":
                # بررسی پرینترهای USB با شناسایی vendor/product ID
                try:
                    import usb.core
                    found_devices = []
                    
                    # شناسه‌های معمول پرینترها
                    common_printers = [
                        (0x04b8, 0x0202, "Epson TM-T20"),
                        (0x04b8, 0x0005, "Epson TMT20II"),
                        (0x0416, 0x5011, "Winbond Thermal"),
                        (0x20d1, 0x7007, "Xprinter XP-58"),
                        (0x20d1, 0x7009, "HPRT TP808"),
                        (0x1504, 0x0006, "Sewoo LK-P21"),
                        (0x0dd4, 0x0006, "Thermal Printer"),
                        # پرینترهای Star Micronics
                        (0x0519, 0x0001, "Star TSP100"),
                        (0x0519, 0x0002, "Star TSP650"),
                        (0x0519, 0x0003, "Star TSP700"),
                        (0x0519, 0x0004, "Star TSP800"),
                        (0x0519, 0x0020, "Star mC-Print2"),
                        (0x0519, 0x0021, "Star mC-Print3"),
                        (0x0519, 0x0023, "Star mPOP"),
                        (0x0519, 0x0027, "Star SM-L200"),
                        (0x0519, 0x0028, "Star SM-L300"),
                        (0x0519, 0x002b, "Star SM-T300"),
                        (0x0519, 0x002c, "Star SM-T400i"),
                    ]
                    
                    # جستجوی پرینترهای معمول
                    for vid, pid, name in common_printers:
                        device = usb.core.find(idVendor=vid, idProduct=pid)
                        if device is not None:
                            found_devices.append(f"{hex(vid)}:{hex(pid)} - {name}")
                    
                    # جستجوی کلی پرینترها (class 7 = printer)
                    devices = usb.core.find(find_all=True, bDeviceClass=7)
                    for device in devices:
                        device_id = f"{hex(device.idVendor)}:{hex(device.idProduct)}"
                        if not any(device_id in found for found in found_devices):
                            try:
                                name = usb.util.get_string(device, device.iProduct) or "Unknown Printer"
                                found_devices.append(f"{device_id} - {name}")
                            except:
                                found_devices.append(f"{device_id} - USB Printer")
                    
                    # بررسی پورت‌های سریال نیز
                    import serial.tools.list_ports
                    ports = serial.tools.list_ports.comports()
                    for port in ports:
                        if "USB" in port.description and any(keyword in port.description.lower() for keyword in ["print", "thermal", "pos", "receipt"]):
                            found_devices.append(f"{port.device} - {port.description}")
                    
                    return found_devices if found_devices else ["No USB printers found"]
                    
                except ImportError:
                    # fallback اگر pyusb موجود نباشد
                    import serial.tools.list_ports
                    ports = serial.tools.list_ports.comports()
                    usb_devices = [f"{port.device} - {port.description}" for port in ports if "USB" in port.description]
                    return usb_devices if usb_devices else ["No USB devices found"]
                except Exception as e:
                    return [f"USB scan error: {str(e)}"]
            else:
                return ["Unknown printer type"]
        except Exception as e:
            print(f"❌ Scan error: {e}")
            return [f"Scan error: {str(e)}"]

    def save_config(self, new_cfg):
        config["printer"] = new_cfg
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2)
        global printer
        printer = PrinterManager(new_cfg["type"], new_cfg["address"])
        printer.connect()
        print("💾 Printer settings updated")
            return "OK"

    def test_print(self):
        try:
            print("🧪 Starting test print...")
            
            # بارگذاری config فعلی
            current_config = self.get_config()
            print(f"📋 Using config: {current_config}")
            
            # تست مستقیم CUPS قبل از PrinterManager
            print("🔧 Testing direct CUPS first...")
            import subprocess
            direct_result = subprocess.run([
                '/usr/bin/lp', '-d', 'HPRT_TP808', '-'
            ], input="Direct CUPS Test\nFrom Mars SysPro\n", 
            text=True, capture_output=True)
            
            if direct_result.returncode == 0:
                print(f"✅ Direct CUPS successful: {direct_result.stdout}")
            else:
                print(f"❌ Direct CUPS failed: {direct_result.stderr}")
                return f"ERROR: CUPS failed - {direct_result.stderr}"
            
            # حالا PrinterManager
            print("🖨️ Testing PrinterManager...")
            test_printer = PrinterManager(
                mode=current_config["type"], 
                address=current_config["address"],
                width=current_config.get("paper_width", 80)
            )
            
            # اتصال
            print("🔌 Connecting printer...")
            test_printer.connect()
            
            if not test_printer.prn:
                print("❌ Printer connection failed!")
                return "ERROR: Printer connection failed"
            
            # چاپ تست
            print("📄 Sending test print...")
            test_text = "🖨️ Mars SysPro Universal\nTest Print Successful!\nTime: $(date)\n" + "=" * 25 + "\n"
            test_printer.print_text(test_text)
            
            # بستن اتصال
            test_printer.close()
            
            print("✅ Test print executed successfully")
            return "OK"
            
        except Exception as e:
            error_msg = f"Test print failed: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            return f"ERROR: {error_msg}"


# 🎯 پل ارتباط HTML ↔ Python - مثل Sunmi Bridge
class Bridge:
    def play_alert(self, sound_type="new_order"):
        """پخش آلارم بر اساس نوع صدا"""
        global alarm_playing
        try:
            # انتخاب صدا از config
            sound_file = config["sounds"].get(sound_type, "neworder.mp3")
            sound_path = f"sounds/{sound_file}"
            
            pygame.mixer.music.load(sound_path)
            pygame.mixer.music.play(-1)  # infinite loop
            alarm_playing = True
            print(f"🔔 Alert sound started: {sound_type} ({sound_file})")
            return "OK"
        except Exception as e:
            print(f"❌ Alert error: {e}")
            return f"ERROR: {e}"

    def stop_alert(self):
        global alarm_playing
        try:
            pygame.mixer.music.stop()
            alarm_playing = False
            print("🔇 Alert sound stopped")
            return "OK"
        except Exception as e:
            print(f"❌ Stop alert error: {e}")
            return f"ERROR: {e}"

    def print_text(self, text):
        try:
        print("🖨️ Print command received")
            print("📄 Print text content:")
            print("=" * 50)
            print(text)
            print("=" * 50)

            # 🎯 استفاده از همون روش test_print که کار می‌کنه (Direct CUPS!)
            print("🚀 Using DIRECT CUPS like test_print...")
            import subprocess
            
            # 🔄 بازگشت به python-escpos (CUPS محدودیت داره)
            from escpos import printer
            print("🔄 Using python-escpos instead of CUPS...")
            
            # CUPS با chunked method + paper width formatting
            try:
                import time
                import tempfile
                import os
                
                # تنظیم عرض کاغذ بر اساس config
                current_config = config["printer"]
                paper_width = current_config.get("paper_width", 80)
                
                # محاسبه تعداد کاراکتر بر اساس عرض کاغذ
                if paper_width == 58:
                    max_chars = 32  # کاغذ 58 میلی‌متری
                    print("📏 Using 58mm paper width (32 chars per line)")
                else:  # 80mm default
                    max_chars = 48  # کاغذ 80 میلی‌متری  
                    print("📏 Using 80mm paper width (48 chars per line)")
                
                # فرمت کردن متن برای عرض کاغذ
                formatted_lines = []
                for line in text.split('\n'):
                    if len(line) <= max_chars:
                        formatted_lines.append(line)
                    else:
                        # تقسیم خطوط طولانی
                        while len(line) > max_chars:
                            formatted_lines.append(line[:max_chars])
                            line = line[max_chars:]
                        if line:  # باقی‌مانده
                            formatted_lines.append(line)
                
                # فقط خطوط غیر خالی
                lines = [line for line in formatted_lines if line.strip()]
                total_lines = len(lines)
                chunk_size = 6  # کمتر از حد buffer برای اطمینان
                
                print(f"📏 CUPS Chunked: Printing {total_lines} lines in chunks of {chunk_size}...")
                
                chunk_results = []
                
                for chunk_start in range(0, total_lines, chunk_size):
                    chunk_end = min(chunk_start + chunk_size, total_lines)
                    chunk_lines = lines[chunk_start:chunk_end]
                    
                    print(f"🔄 CUPS Chunk {chunk_start//chunk_size + 1}: lines {chunk_start+1}-{chunk_end}")
                    
                    # ساخت متن chunk
                    chunk_text = '\n'.join(chunk_lines) + '\n\n'
                    
                    # چاپ هر chunk جداگانه
                    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as tmp_file:
                        tmp_file.write(chunk_text)
                        tmp_file.flush()
                        tmp_file_path = tmp_file.name
                    
                    try:
                        chunk_result = subprocess.run([
                            '/usr/bin/lp', '-d', 'HPRT_TP808', 
                            '-o', 'CutMode=0',  # بدون کات بین chunks
                            tmp_file_path
                        ], capture_output=True, text=True, timeout=30)
                        
                        chunk_results.append(chunk_result.returncode)
                        print(f"✅ Chunk {chunk_start//chunk_size + 1} sent: {chunk_result.stdout.strip()}")
                        
                    finally:
                        try:
                            os.unlink(tmp_file_path)
                        except:
                            pass
                    
                    # delay کوچک بین chunks
                    if chunk_end < total_lines:
                        time.sleep(0.2)  # delay کمتر - صدای کمتر
                        print("⏱️ CUPS Buffer delay...")
                
                # final cut در انتها
                final_cut = subprocess.run([
                    '/usr/bin/lp', '-d', 'HPRT_TP808', '-'
                ], input='\n\n', text=True, capture_output=True)
                
                # نتیجه کلی
                success_chunks = sum(1 for r in chunk_results if r == 0)
                direct_result = type('MockResult', (), {
                    'returncode': 0 if success_chunks == len(chunk_results) else 1,
                    'stdout': f'CUPS chunked: {success_chunks}/{len(chunk_results)} chunks successful'
                })()
                
            except Exception as e:
                print(f"❌ python-escpos failed: {e}")
                # fallback to CUPS
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as tmp_file:
                    tmp_file.write(text)
                    tmp_file.flush()
                    tmp_file_path = tmp_file.name
                
                try:
                    direct_result = subprocess.run([
                        '/usr/bin/lp', '-d', 'HPRT_TP808', '-o', 'CutMode=0', '-o', 'FormfeedLength=20', tmp_file_path
                    ], capture_output=True, text=True, timeout=30)
                finally:
                    try:
                        os.unlink(tmp_file_path)
                    except:
                        pass
            
            if direct_result.returncode == 0:
                print(f"✅ Direct CUPS print successful: {direct_result.stdout}")
            else:
                print(f"❌ Direct CUPS failed: {direct_result.stderr}")
                # اگه direct CUPS کار نکرد، fallback به PrinterManager
                print("🔄 Falling back to PrinterManager...")
                
                current_config = config["printer"]
                print(f"📋 Using config: {current_config}")
                
                temp_printer = PrinterManager(
                    mode=current_config["type"], 
                    address=current_config["address"],
                    width=current_config.get("paper_width", 80)
                )
                
                print("🔌 Connecting printer for regular print...")
                temp_printer.connect()
                
                if not temp_printer.prn:
                    print("❌ Printer connection failed in print_text!")
                    return "ERROR: Printer connection failed"
                
                print("📄 Sending print job...")
                temp_printer.print_text(text)
                temp_printer.close()
            
            # 🔇 وقتی چاپ تمام شد، آلارم رو متوقف کن
            if alarm_playing:
                self.stop_alert()
                print("🔄 Auto-stopped alarm after print completion")
            
            print("✅ Print completed successfully")
            return "OK"
        except Exception as e:
            print(f"❌ Print error: {e}")
            import traceback
            traceback.print_exc()
            return f"ERROR: {e}"
    
    # 🎯 JavaScript Bridge Methods - مثل Sunmi
    def print(self, text):
        """مثل window.android.print روی Sunmi"""
        return self.print_text(text)
    
    def playAlert(self):
        """مثل window.android.playAlert روی Sunmi"""  
        return self.play_alert()
    
    def stopAlert(self):
        """مثل window.android.stopAlert روی Sunmi"""
        return self.stop_alert()

    def open_settings(self):
        settings_api = SettingsBridge()
        settings_path = os.path.abspath(os.path.join("ui", "printer_settings_fixed.html"))
        print("⚙️ Opening printer settings:", settings_path)
        webview.create_window(
            "🖨️ Printer Settings",
            f"file://{settings_path}",
            js_api=settings_api,
            width=420,
            height=520
        )


# 🌐 اجرای برنامه اصلی
device_id = get_device_id()
final_url = f"{APP_URL}?device_id={device_id}"

def on_loaded():
    print("✅ WebView loaded — injecting settings button")
    js = """
        const btn = document.createElement('button');
        btn.innerText = '⚙️';
        btn.title = 'Settings';
        Object.assign(btn.style, {
            position: 'fixed', bottom: '20px', right: '20px',
            width: '55px', height: '55px', borderRadius: '50%',
            background: '#2b7cff', color: 'white', fontSize: '22px',
            border: 'none', boxShadow: '0 2px 6px rgba(0,0,0,0.3)',
            cursor: 'pointer', zIndex: 999999, opacity: 0,
            transition: 'opacity 0.6s ease'
        });
        document.body.appendChild(btn);
        setTimeout(()=>btn.style.opacity='1', 500);
        btn.onclick = () => window.pywebview.api.open_settings();
    """
    window.evaluate_js(js)

def cleanup_monitoring():
    """تمیز کردن monitoring threads هنگام خروج"""
    global monitoring_active, alarm_playing
    print("🔄 Stopping monitoring threads...")
    monitoring_active = False
    
    # توقف آلارم اگر در حال پخش است
    if alarm_playing:
        try:
            bridge = Bridge()
            bridge.stop_alert()
            print("🔇 Alarm stopped on cleanup")
        except:
            pass

import atexit
atexit.register(cleanup_monitoring)

# تنظیم background operation
import sys
import os

def set_background_mode():
    """تنظیم حالت background برای اجرای بهتر"""
    if sys.platform == "darwin":  # macOS
        # اطمینان از اینکه app در background هم کار کنه
        os.environ['PYTHONUNBUFFERED'] = '1'
        print("🔄 Background mode enabled for macOS")

set_background_mode()

api = Bridge()
window = webview.create_window("Mars SysPro Universal", final_url, js_api=api, width=480, height=800)

# نمایش اطلاعات مهم قبل از شروع
print("\n" + "="*50)
print("🚀 Mars SysPro Universal - Ready!")
print(f"📱 WebView: {final_url}")
print(f"🌐 API Server: http://localhost:{LOCAL_API_PORT}")
print(f"🖨️ Printer: {config['printer']['type']} - {config['printer']['address']}")
print(f"🔊 Sounds: {list(config.get('sounds', {}).keys())}")
print(f"🔍 Monitoring: Internet + WebView Health")
print("="*50 + "\n")

webview.start(func=on_loaded, debug=False)
