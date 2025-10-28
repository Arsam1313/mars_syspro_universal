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
import sys
import subprocess
from printer_manager import (
    discover_lan_printers,
    discover_bluetooth_printers,
    PrinterManager
)
from printer_drivers.universal_manager import UniversalPrinterManager

from flask import Flask, request, jsonify
from flask_cors import CORS

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Helper function to get resource path (works with PyInstaller)
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# Get user config directory
def get_config_path():
    """Get writable config file path in user directory"""
    if platform.system() == 'Darwin':  # macOS
        app_data_dir = os.path.expanduser('~/Library/Application Support/DineSysPro')
    elif platform.system() == 'Windows':
        app_data_dir = os.path.join(os.environ.get('APPDATA', ''), 'DineSysPro')
    else:  # Linux
        app_data_dir = os.path.expanduser('~/.config/DineSysPro')
    
    os.makedirs(app_data_dir, exist_ok=True)
    return os.path.join(app_data_dir, 'config.json')

# Load configuration
def load_config():
    """Load config from user directory, or create from default"""
    user_config_path = get_config_path()
    
    # Try to load user config first
    if os.path.exists(user_config_path):
        try:
            with open(user_config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    
    # If no user config, load default from bundle
    try:
        default_config_path = resource_path('config.json')
        with open(default_config_path, 'r', encoding='utf-8') as f:
            default_config = json.load(f)
        
        # Save to user directory
        with open(user_config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2)
        
        print(f"✅ Created user config at: {user_config_path}")
        return default_config
    except:
        # Fallback to hardcoded defaults
        return {
            "printer": {"type": "lan", "address": "192.168.1.80", "paper_width": 80},
            "app_url": "http://localhost:3001/order-reception.html",
            "base_url": "http://95.217.217.200:3001",
            "auto_print_orders": True,
            "sounds": {
                "new_order": "neworder.mp3",
                "internet_lost": "no_internet_alert.mp3",
                "low_battery": "low_battery.mp3"
            },
            "version": "1.0.3"
        }

# Load config
config = load_config()
CONFIG_PATH = get_config_path()

# Extract configuration values
APP_URL = config.get("app_url", "http://localhost:3001/order-reception.html")
AUTO_PRINT_ORDERS = config.get("auto_print_orders", True)

# Extract base URL from app_url for API heartbeat
import re
base_url_match = re.match(r'(https?://[^/]+)', APP_URL)
BASE_URL = base_url_match.group(1) if base_url_match else "http://localhost:3001"
API_HEARTBEAT = f"{BASE_URL}/api/heartbeat"
APP_VERSION = config.get("version", "1.0.0")

pygame.mixer.init()

# Flask API Server for Java WebView
app = Flask(__name__)
CORS(app)
LOCAL_API_PORT = 8080

# Alarm control
alarm_playing = False

# Monitoring variables
internet_connected = True
webview_healthy = True
monitoring_active = True

# [Configuration]
@app.route('/api/print', methods=['POST'])
def api_print():
    """Function description"""
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
        
        # [Configuration]
        print("🚀 API using SAME METHOD as successful Bridge.print_text...")
        
        # [Configuration]
        api_bridge = Bridge()
        result = api_bridge.print_text(text)
        
        if "OK" in str(result):
            return jsonify({
                "success": True,
                "message": "Print job sent successfully",
                "device_id": get_device_id()
            })
        else:
            return jsonify({
                "success": False, 
                "error": f"Print failed: {result}"
            }), 500
        
    except Exception as e:
        print(f"❌ Print API error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/alarm/start', methods=['POST'])
def api_alarm_start():
    """Function description"""
    global alarm_playing
    try:
        # [Configuration]
        data = request.get_json() or {}
        loops = data.get('loops', -1)  # -1 = infinite loop
        
        if alarm_playing:
            return jsonify({"success": False, "message": "Alarm already playing"})
        
        print("🔔 Starting alarm from Java API...")
        # Use new_order sound as default alarm
        sound_file = config["sounds"].get("new_order", "neworder.mp3")
        alarm_sound_path = resource_path(f"sounds/{sound_file}")
        pygame.mixer.music.load(alarm_sound_path)
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
    """Function description"""
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
    """Function description"""
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
    """Function description"""
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
    """Function description"""
    try:
        data = request.get_json()
        sound_type = data.get("type")  # new_order, internet_lost, low_battery
        sound_file = data.get("file")  # neworder.mp3, neworder1.mp3, neworder2.mp3, etc.
        
        if sound_type not in ["new_order", "internet_lost", "low_battery"]:
            return jsonify({"success": False, "error": "Invalid sound type"}), 400
        
        # [Configuration]
        if "sounds" not in config:
            config["sounds"] = {}
        
        config["sounds"][sound_type] = sound_file
        
        # [Configuration]
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
    """Function description"""
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
    """Function description"""
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
    """Function description"""
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


@app.route('/settings')
def settings_page():
    """Serve the settings HTML page"""
    try:
        settings_html_path = resource_path("ui/settings.html")
        with open(settings_html_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"<h1>Error loading settings page</h1><p>{str(e)}</p>", 500


# ================================================================================
#                    NOTE: Socket.IO is managed by order-reception.html
#                    No Socket.IO client needed in Python app
# ================================================================================

# ================================================================================
#                    🔍 MONITORING FUNCTIONS
# ================================================================================

def check_internet_connection():
    """Function description"""
    import socket
    try:
        # [Configuration]
        socket.create_connection(("8.8.8.8", 53), 3)
        return True
    except OSError:
        return False

def check_webview_health():
    """Function description"""
    try:
        import requests
        current_url = config.get("app_url", "http://localhost:3001")
        response = requests.get(current_url, timeout=5)
        return response.status_code == 200
    except:
        return False

def internet_monitor():
    """Function description"""
    global internet_connected, alarm_playing, monitoring_active
    import time
    
    while monitoring_active:
        try:
            is_connected = check_internet_connection()
            
            if not is_connected and internet_connected:
                # [Configuration]
                internet_connected = False
                print("🚨 Internet connection lost!")
                
                # [Configuration]
                if not alarm_playing:
                    bridge = Bridge()
                    bridge.play_alert("internet_lost")
                    print("🔔 Internet alarm started")
                
            elif is_connected and not internet_connected:
                # [Configuration]
                internet_connected = True
                print("✅ Internet connection restored!")
                
                # [Configuration]
                if alarm_playing:
                    bridge = Bridge()
                    bridge.stop_alert()
                    print("🔇 Internet alarm stopped")
                
                # [Configuration]
                try:
                    if 'window' in globals():
                        window.evaluate_js("location.reload();")
                        print("🔄 WebView page refreshed")
                except:
                    print("⚠️ Could not refresh WebView")
            
            time.sleep(5)  # [SV/EN] [SV/EN] 5 [SV/EN]
            
        except Exception as e:
            print(f"❌ Internet monitor error: {e}")
            time.sleep(10)

def webview_health_monitor():
    """Function description"""
    global webview_healthy, monitoring_active
    import time
    
    while monitoring_active:
        try:
            is_healthy = check_webview_health()
            
            if not is_healthy and webview_healthy:
                # [Configuration]
                webview_healthy = False
                print("🚨 WebView health check failed!")
                
                # [Configuration]
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
                                    <div>⚠️ Ingen internetanslutning</div>
                                    <div style="font-size: 16px; margin-top: 20px;">Kan inte ansluta till servern. Kontrollera din internetanslutning och försök igen.</div>
                                `;
                                document.body.appendChild(overlay);
                            }
                        """)
                        print("🚨 System error overlay displayed")
                except:
                    print("⚠️ Could not display error overlay")
                
            elif is_healthy and not webview_healthy:
                # [Configuration]
                webview_healthy = True
                print("✅ WebView health restored!")
                
                # [Configuration]
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
            
            time.sleep(10)  # [SV/EN] [SV/EN] 10 [SV/EN]
            
        except Exception as e:
            print(f"❌ WebView health monitor error: {e}")
            time.sleep(15)

def start_flask_server():
    """Function description"""
    try:
        print(f"🌐 Starting API server on http://localhost:{LOCAL_API_PORT}")
        app.run(host='0.0.0.0', port=LOCAL_API_PORT, debug=False, threaded=True)
    except Exception as e:
        print(f"❌ Flask server error: {e}")

# [Configuration]
try:
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
except Exception:
    config = {
        "printer": {"type": "lan", "address": "192.168.1.50", "paper_width": 80},
        "app_url": "http://localhost:3001/order-reception.html",
        "sounds": {
            "new_order": "neworder.mp3",  # [SV/EN] [SV/EN]: neworder.mp3, neworder1.mp3, neworder2.mp3
            "internet_lost": "no_internet_alert.mp3",
            "low_battery": "low_battery.mp3"
        }
    }
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)

# [Configuration]
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

# [Configuration] Universal Printer Manager (Multi-brand ESC/POS)
printer = PrinterManager()
connected = printer.auto_connect(
    preferred_type=config["printer"].get("type", "auto"),
    address=config["printer"].get("address", None),
    width=config["printer"].get("paper_width", 80)
)

# پرینت خوش‌آمدگویی بعد از اتصال موفق
if connected:
    try:
        welcome_text = """
================================
   DineSysPro Connected!
================================
Printer: {mode} - {addr}
Version: {ver}
Time: {time}
================================

Ready to receive orders!

""".format(
            mode=printer.mode.upper(),
            addr=printer.address if printer.address else printer.usb_device[2] if printer.usb_device else "Auto",
            ver=APP_VERSION,
            time=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        result = printer.print_text(welcome_text)
        if result == "OK":
            print("✅ Welcome receipt printed successfully")
        else:
            print(f"⚠️ Welcome receipt failed: {result}")
    except Exception as e:
        print(f"⚠️ Welcome print error: {e}")
else:
    print("⚠️ Printer not connected - skipping welcome print")

# [Configuration]
def get_device_id():
    """
    Get or create unique device ID
    Stores in user's home directory to persist across app updates
    """
    # Use platform-specific user data directory
    if platform.system() == 'Darwin':  # macOS
        app_data_dir = os.path.expanduser('~/Library/Application Support/DineSysPro')
    elif platform.system() == 'Windows':
        app_data_dir = os.path.join(os.environ.get('APPDATA', ''), 'DineSysPro')
    else:  # Linux
        app_data_dir = os.path.expanduser('~/.config/DineSysPro')
    
    # Create directory if it doesn't exist
    os.makedirs(app_data_dir, exist_ok=True)
    
    device_info_path = os.path.join(app_data_dir, 'device_info.json')
    
    # Try to read existing device_id
    if os.path.exists(device_info_path):
        try:
            with open(device_info_path, 'r') as f:
                data = json.load(f)
                if 'device_id' in data:
                    return data['device_id']
        except:
            pass
    
    # Generate new device_id based on MAC address
    device_id = f"{uuid.getnode():012X}"
    #device_id = "8c4ca5f1ff3fa0f4"
    # Save to file
    try:
        with open(device_info_path, 'w') as f:
            json.dump({"device_id": device_id}, f)
        print(f"✅ New device ID created: {device_id}")
        print(f"📁 Saved to: {device_info_path}")
    except Exception as e:
        print(f"⚠️ Could not save device_id: {e}")
    
    return device_id

def get_device_info():
    return {
        "device_id": "8c4ca5f1ff3fa0f4",#get_device_id(),
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

# [Configuration]
threading.Thread(target=start_flask_server, daemon=True).start()

# [Configuration]
print("🔍 Starting system monitoring...")
threading.Thread(target=internet_monitor, daemon=True).start()
threading.Thread(target=webview_health_monitor, daemon=True).start()
print("✅ Internet and WebView monitoring started")


# [Configuration]
# [Configuration]
class SettingsBridge:
    def get_config(self):
        return config["printer"]
    
    def get_full_config(self):
        full_config = config.copy()
        full_config['device_id'] = get_device_id()
        return full_config

    def scan_printers(self, conn_type):
        print(f"🧩 scan_printers called with type={conn_type}")
        try:
            if conn_type == "lan":
                return discover_lan_printers() or ["No LAN printers found"]
            elif conn_type == "bluetooth":
                return discover_bluetooth_printers() or ["No Bluetooth printers found"]
            elif conn_type == "usb":
                try:
                    import usb.core
                    found_devices = []
                    common_printers = [
                        (0x20d1, 0x7009, "HPRT TP808"),
                        (0x04b8, 0x0005, "Epson TM-T20II"),
                        (0x0519, 0x0001, "Star TSP100"),
                    ]
                    for vid, pid, name in common_printers:
                        device = usb.core.find(idVendor=vid, idProduct=pid)
                        if device:
                            found_devices.append(f"{hex(vid)}:{hex(pid)} - {name}")
                    return found_devices or ["No USB printers found"]
                except Exception as e:
                    return [f"USB scan error: {str(e)}"]
            else:
                return ["Unknown printer type"]
        except Exception as e:
            print(f"❌ Scan error: {e}")
            return [f"Scan error: {str(e)}"]

    def save_config(self, new_cfg):
        try:
            # ذخیره تنظیمات در config.json
            with open(CONFIG_PATH, "r") as f:
                full_config = json.load(f)
            full_config["printer"] = new_cfg
            with open(CONFIG_PATH, "w") as f:
                json.dump(full_config, f, indent=2)
            config["printer"] = new_cfg
            
            # قطع اتصال پرینتر قبلی
            global printer
            if printer:
                printer.disconnect()
            
            # اتصال مجدد با تنظیمات جدید
            printer.auto_connect(
                preferred_type=new_cfg.get("type", "auto"),
                address=new_cfg.get("address", None),
                width=new_cfg.get("paper_width", 80)
            )
            
            print(f"💾 Printer settings updated: {new_cfg}")
            return "OK"
        except Exception as e:
            print(f"❌ Save config error: {e}")
            import traceback
            traceback.print_exc()
            return f"ERROR: {e}"

    def test_print(self):
        try:
            print("🧪 Starting test print...")
            current_config = self.get_config()
            print(f"📋 Using config: {current_config}")

            printer_type = current_config.get("type", "")
            
            # برای پرینترهای LAN که در CUPS نصب هستند، ابتدا CUPS را تست می‌کنیم
            if printer_type == "lan" and current_config.get("cups_name"):
                import subprocess, shutil
                cups_printer_name = current_config.get("cups_name")
                lp_path = shutil.which("lp") or "/usr/bin/lp"
                print(f"🔧 Testing CUPS with lp path: {lp_path}")

                direct_result = subprocess.run(
                    [lp_path, "-d", cups_printer_name, "-"],
                    input="🍕 DineSysPro\nDirect CUPS Test\n",
                    text=True, capture_output=True
                )
                if direct_result.returncode == 0:
                    print(f"✅ Direct CUPS successful: {direct_result.stdout}")
                else:
                    print(f"⚠️ Direct CUPS failed: {direct_result.stderr}")
                    # Don't return error, continue with PrinterManager

            # استفاده از PrinterManager برای همه انواع پرینتر
            print("🖨️ Testing PrinterManager connection...")
            test_printer = PrinterManager()
            connected = test_printer.auto_connect(
                preferred_type=current_config["type"],
                address=current_config["address"],
                width=current_config.get("paper_width", 80)
            )

            if not connected:
                return "ERROR: Printer connection failed"

            test_text = "🍕 DineSysPro\nTest Print Successful!\n=========================\n"
            result = test_printer.print_text(test_text)
            test_printer.disconnect()
            
            if result == "OK":
                print("✅ Test print executed successfully")
                return "OK"
            else:
                print(f"❌ Print failed: {result}")
                return f"ERROR: {result}"

        except Exception as e:
            print(f"❌ Test print failed: {e}")
            import traceback; traceback.print_exc()
            return f"ERROR: {e}"


# [Configuration]
class Bridge:
    def play_alert(self, sound_type="new_order"):
        global alarm_playing
        try:
            sound_file = config["sounds"].get(sound_type, "neworder.mp3")
            sound_path = resource_path(f"sounds/{sound_file}")
            pygame.mixer.music.load(sound_path)
            pygame.mixer.music.play(-1)
            alarm_playing = True
            print(f"🔔 Alert started: {sound_type} ({sound_file})")
            return "OK"
        except Exception as e:
            print(f"❌ Alert error: {e}")
            return f"ERROR: {e}"
    
    def playAlert(self, sound_type="new_order"):
        """Alias for play_alert - برای سازگاری با universal_bridge.js"""
        return self.play_alert(sound_type)

    def stop_alert(self):
        global alarm_playing
        try:
            pygame.mixer.music.stop()
            alarm_playing = False
            print("🔇 Alert stopped")
            return "OK"
        except Exception as e:
            print(f"❌ Stop alert error: {e}")
            return f"ERROR: {e}"
    
    def stopAlert(self):
        """Alias for stop_alert - برای سازگاری با universal_bridge.js"""
        return self.stop_alert()

    def open_settings(self):
        settings_api = SettingsBridge()
        settings_path = resource_path(os.path.join("ui", "settings.html"))
        print("⚙️ Opening settings window...")
        webview.create_window(
            "⚙️ Settings - DineSysPro",
            f"file://{settings_path}",
            js_api=settings_api,
            width=650, height=900, resizable=True
        )

    def print_text(self, text):
        try:
            print("🖨️ Print command received")
            result = printer.print_text(text)
            return "OK" if result == "OK" else f"ERROR: {result}"
        except Exception as e:
            print(f"❌ Print error: {e}")
            return f"ERROR: {e}"
    
    def print(self, text):
        """Alias for print_text - برای سازگاری با universal_bridge.js"""
        return self.print_text(text)

    def test_print(self):
        """Triggered from settings.html Test Print button"""
        try:
            url = f"http://localhost:{LOCAL_API_PORT}/api/test-print"
            print(f"🧪 Triggering API test print via {url}")
            res = requests.post(url, timeout=10)
            if res.status_code == 200:
                data = res.json()
                return "OK" if data.get("success") else f"ERROR: {data.get('error', 'Unknown error')}"
            return f"ERROR: HTTP {res.status_code}"
        except Exception as e:
            print(f"❌ WebView test_print error: {e}")
            return f"ERROR: {e}"
    
    def save_sound_config(self, sound_config):
        """Save sound configuration"""
        try:
            # Re-read config to preserve all fields
            with open(CONFIG_PATH, "r") as f:
                full_config = json.load(f)
            
            # Update only sound settings
            full_config["sounds"] = sound_config
            
            # Write back complete config
            with open(CONFIG_PATH, "w") as f:
                json.dump(full_config, f, indent=2)
            
            # Update global config
            config["sounds"] = sound_config
            
            print(f"💾 Sound settings updated: {sound_config}")
            return "OK"
        except Exception as e:
            print(f"❌ Save sound config error: {e}")
            return f"ERROR: {e}"
    
    def test_sound(self, sound_type, sound_file):
        """Function description"""
        try:
            sound_path = resource_path(f"sounds/{sound_file}")
            pygame.mixer.music.load(sound_path)
            pygame.mixer.music.play()
            print(f"🔊 Testing sound: {sound_type} = {sound_file}")
            return "OK"
        except Exception as e:
            print(f"❌ Test sound error: {e}")
            return f"ERROR: {e}"
    
    def stop_sound(self):
        """Function description"""
        try:
            pygame.mixer.music.stop()
            print("🔇 Sound stopped")
            return "OK"
        except Exception as e:
            print(f"❌ Stop sound error: {e}")
            return f"ERROR: {e}"


# [Configuration]
device_id = "8c4ca5f1ff3fa0f4"#get_device_id()
final_url = f"{APP_URL}?device_id={device_id}"

def on_loaded():
    print("✅ WebView loaded — injecting settings button")
    js = """
        (function() {
            // Function to inject settings button
            function injectSettingsButton() {
                // Check if button already exists
                if (document.getElementById('mars-settings-btn')) {
                    return;
                }
                
                const btn = document.createElement('button');
                btn.id = 'mars-settings-btn';
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
            }
            
            // Inject button immediately
            injectSettingsButton();
            
            // Re-inject button if DOM changes (e.g., page refresh)
            const observer = new MutationObserver(() => {
                if (!document.getElementById('mars-settings-btn')) {
                    console.log('Settings button missing, re-injecting...');
                    injectSettingsButton();
                }
            });
            
            // Observe body for changes
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
            
            // Also re-inject on page visibility change
            document.addEventListener('visibilitychange', () => {
                if (document.visibilityState === 'visible') {
                    setTimeout(injectSettingsButton, 100);
                }
            });
        })();
    """
    window.evaluate_js(js)

def cleanup_monitoring():
    """Cleanup on application exit"""
    global monitoring_active, alarm_playing
    print("🔄 Stopping monitoring threads...")
    monitoring_active = False
    
    # Stop alarm if playing
    if alarm_playing:
        try:
            bridge = Bridge()
            bridge.stop_alert()
            print("🔇 Alarm stopped on cleanup")
        except:
            pass
    
    # Re-enable sleep on Windows
    if sys.platform == "win32":
        try:
            import ctypes
            ES_CONTINUOUS = 0x80000000
            ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
            print("💤 Sleep re-enabled (Windows)")
        except:
            pass

import atexit
atexit.register(cleanup_monitoring)

# [Configuration]
import sys
import os
import subprocess

def prevent_sleep():
    """Prevent system from going to sleep - Cross-platform"""
    system = sys.platform
    
    try:
        if system == "darwin":  # macOS
            # Use caffeinate to prevent sleep
            print("☕ Preventing sleep on macOS...")
            subprocess.Popen(['caffeinate', '-d', '-i', '-s'])
            print("✅ Sleep prevention enabled (macOS)")
            
        elif system == "win32":  # Windows
            # Use SetThreadExecutionState to prevent sleep
            print("☕ Preventing sleep on Windows...")
            import ctypes
            ES_CONTINUOUS = 0x80000000
            ES_SYSTEM_REQUIRED = 0x00000001
            ES_DISPLAY_REQUIRED = 0x00000002
            ctypes.windll.kernel32.SetThreadExecutionState(
                ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
            )
            print("✅ Sleep prevention enabled (Windows)")
            
        elif system.startswith("linux"):  # Linux
            # Try to use systemd-inhibit or xset
            print("☕ Preventing sleep on Linux...")
            try:
                # Try systemd-inhibit first
                subprocess.Popen([
                    'systemd-inhibit',
                    '--what=idle:sleep',
                    '--who=DineSysPro',
                    '--why=Restaurant order system running',
                    '--mode=block',
                    'sleep', 'infinity'
                ])
                print("✅ Sleep prevention enabled (Linux - systemd)")
            except FileNotFoundError:
                # Fallback to xset
                try:
                    subprocess.run(['xset', 's', 'off'], check=False)
                    subprocess.run(['xset', '-dpms'], check=False)
                    print("✅ Sleep prevention enabled (Linux - xset)")
                except FileNotFoundError:
                    print("⚠️ Could not prevent sleep on Linux (install systemd or xset)")
        else:
            print(f"⚠️ Sleep prevention not implemented for {system}")
            
    except Exception as e:
        print(f"⚠️ Could not prevent sleep: {e}")

def set_background_mode():
    """Configure background mode and prevent sleep"""
    os.environ['PYTHONUNBUFFERED'] = '1'
    print("🔄 Background mode enabled")
    
    # Prevent system sleep
    prevent_sleep()

set_background_mode()

api = Bridge()
window = webview.create_window(
    "🍕 DineSysPro", 
    final_url, 
    js_api=api, 
    fullscreen=True,  # Full screen mode
    confirm_close=False  # No confirmation on close
)

# Display startup information
print("\n" + "="*50)
print("🚀 DineSysPro - Ready!")
print(f"📱 WebView: {final_url}")
print(f"🌐 API Server: http://localhost:{LOCAL_API_PORT}")
print(f"🖨️ Printer: {config['printer']['type']} - {config['printer']['address']}")
print(f"🔊 Sounds: {list(config.get('sounds', {}).keys())}")
print(f"🔍 Monitoring: Internet + WebView Health")
print("="*50 + "\n")

webview.start(func=on_loaded, debug=False)
