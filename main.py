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
    PrinterManager,
    discover_lan_printers,
    discover_bluetooth_printers
)
from flask import Flask, request, jsonify
from flask_cors import CORS

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load configuration from config.json
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# Extract configuration values
APP_URL = config.get("app_url", "http://localhost:3001/order-reception.html")
AUTO_PRINT_ORDERS = config.get("auto_print_orders", True)

# Extract base URL from app_url for API heartbeat
import re
base_url_match = re.match(r'(https?://[^/]+)', APP_URL)
BASE_URL = base_url_match.group(1) if base_url_match else "http://localhost:3001"
API_HEARTBEAT = f"{BASE_URL}/api/heartbeat"

CONFIG_PATH = "config.json"
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

# [Configuration]
printer = PrinterManager(config["printer"]["type"], config["printer"]["address"])
printer.connect()

# [Configuration]
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

# [Configuration]
threading.Thread(target=start_flask_server, daemon=True).start()

# [Configuration]
print("🔍 Starting system monitoring...")
threading.Thread(target=internet_monitor, daemon=True).start()
threading.Thread(target=webview_health_monitor, daemon=True).start()
print("✅ Internet and WebView monitoring started")


# [Configuration]
class SettingsBridge:
    def get_config(self):
        """Function description"""
        return config["printer"]
    
    def get_full_config(self):
        """Get full configuration including device_id"""
        full_config = config.copy()
        full_config['device_id'] = get_device_id()
        return full_config

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
                # [Configuration]
                try:
                    import usb.core
                    found_devices = []
                    
                    # [Configuration]
                    common_printers = [
                        (0x04b8, 0x0202, "Epson TM-T20"),
                        (0x04b8, 0x0005, "Epson TMT20II"),
                        (0x0416, 0x5011, "Winbond Thermal"),
                        (0x20d1, 0x7007, "Xprinter XP-58"),
                        (0x20d1, 0x7009, "HPRT TP808"),
                        (0x1504, 0x0006, "Sewoo LK-P21"),
                        (0x0dd4, 0x0006, "Thermal Printer"),
                        # [Configuration]
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
                    
                    # [Configuration]
                    for vid, pid, name in common_printers:
                        device = usb.core.find(idVendor=vid, idProduct=pid)
                        if device is not None:
                            found_devices.append(f"{hex(vid)}:{hex(pid)} - {name}")
                    
                    # [Configuration]
                    devices = usb.core.find(find_all=True, bDeviceClass=7)
                    for device in devices:
                        device_id = f"{hex(device.idVendor)}:{hex(device.idProduct)}"
                        if not any(device_id in found for found in found_devices):
                            try:
                                name = usb.util.get_string(device, device.iProduct) or "Unknown Printer"
                                found_devices.append(f"{device_id} - {name}")
                            except:
                                found_devices.append(f"{device_id} - USB Printer")
                    
                    # [Configuration]
                    import serial.tools.list_ports
                    ports = serial.tools.list_ports.comports()
                    for port in ports:
                        if "USB" in port.description and any(keyword in port.description.lower() for keyword in ["print", "thermal", "pos", "receipt"]):
                            found_devices.append(f"{port.device} - {port.description}")
                    
                    return found_devices if found_devices else ["No USB printers found"]
                    
                except ImportError:
                    # [Configuration]
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
        # Re-read config to preserve all fields
        with open(CONFIG_PATH, "r") as f:
            full_config = json.load(f)
        
        # Update only printer settings
        full_config["printer"] = new_cfg
        
        # Write back complete config
        with open(CONFIG_PATH, "w") as f:
            json.dump(full_config, f, indent=2)
        
        # Update global config
        config["printer"] = new_cfg
        
        global printer
        printer = PrinterManager(new_cfg["type"], new_cfg["address"])
        printer.connect()
        print("💾 Printer settings updated")
        return "OK"

    def test_print(self):
        try:
            print("🧪 Starting test print...")
            
            # [Configuration]
            current_config = self.get_config()
            print(f"📋 Using config: {current_config}")
            
            # [Configuration]
            print("🔧 Testing direct CUPS first...")
            import subprocess
            
            # [Configuration]
            cups_printer_name = current_config.get("cups_name", "HPRT_TP808")
            print(f"🖨️ CUPS Printer: {cups_printer_name}")
            
            direct_result = subprocess.run([
                '/usr/bin/lp', '-d', cups_printer_name, '-'
            ], input="Direct CUPS Test\nFrom DineSysPro\n", 
            text=True, capture_output=True)
            
            if direct_result.returncode == 0:
                print(f"✅ Direct CUPS successful: {direct_result.stdout}")
            else:
                print(f"❌ Direct CUPS failed: {direct_result.stderr}")
                return f"ERROR: CUPS failed - {direct_result.stderr}"
            
            # [Configuration]
            print("🖨️ Testing PrinterManager...")
            test_printer = PrinterManager(
                mode=current_config["type"], 
                address=current_config["address"],
                width=current_config.get("paper_width", 80)
            )
            
            # [Configuration]
            print("🔌 Connecting printer...")
            test_printer.connect()
            
            if not test_printer.prn:
                print("❌ Printer connection failed!")
                return "ERROR: Printer connection failed"
            
            # [Configuration]
            print("📄 Sending test print...")
            test_text = "🍕 DineSysPro\nTest Print Successful!\nTime: $(date)\n" + "=" * 25 + "\n"
            test_printer.print_text(test_text)
            
            # [Configuration]
            test_printer.close()
            
            print("✅ Test print executed successfully")
            return "OK"
            
        except Exception as e:
            error_msg = f"Test print failed: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            return f"ERROR: {error_msg}"
    
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
            sound_path = f"sounds/{sound_file}"
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
class Bridge:
    def play_alert(self, sound_type="new_order"):
        """Function description"""
        global alarm_playing
        try:
            # [Configuration]
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
        """Function description"""
        try:
            print("🖨️ Print command received")
            print("📄 Print text content:")
            print("=" * 50)
            print(text)
            print("=" * 50)

            # [Configuration]
            print("🚀 Using SAME METHOD as successful test_print...")
            
            # [Configuration]
            current_config = config["printer"]
            paper_width = current_config.get("paper_width", 80)
            
            # [Configuration]
            if paper_width == 58:
                max_chars = 32  # Paper 58 [SV/EN]‌[SV/EN]
                print("📏 Using 58mm paper width (32 chars per line)")
            else:  # 80mm default
                max_chars = 48  # Paper 80 [SV/EN]‌[SV/EN]  
                print("📏 Using 80mm paper width (48 chars per line)")
            
            # [Configuration]
            formatted_lines = []
            for line in text.split('\n'):
                if len(line) <= max_chars:
                    formatted_lines.append(line)
                else:
                    # [Configuration]
                    while len(line) > max_chars:
                        formatted_lines.append(line[:max_chars])
                        line = line[max_chars:]
                    if line:  # [SV/EN]‌[SV/EN]
                        formatted_lines.append(line)
            
            formatted_text = '\n'.join(formatted_lines)
            
            # [Configuration]
            print("🔧 Using direct CUPS method like test_print...")
            import subprocess
            import tempfile
            import os
            
            # [Configuration]
            # [Configuration]
            if current_config["type"] == "lan":
                print("🚀 Using RAW printing directly to LAN printer...")
                try:
                    import socket
                    
                    # [Configuration]
                    printer_ip = current_config["address"]
                    print(f"📡 Connecting to printer at {printer_ip}:9100")
                    
                    # [Configuration]
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(10)
                    sock.connect((printer_ip, 9100))
                    
                    # [Configuration]
                    ESC = b'\x1b'  # Escape character
                    GS = b'\x1d'   # Group separator
                    
                    # [Configuration]
                    init_cmd = ESC + b'@'  # Reset printer
                    
                    # [Configuration]
                    # ESC R n - Select international character set
                    # n = 7: Nordic (Sweden, Finland)
                    select_nordic_charset = ESC + b'R' + b'\x07'
                    
                    # [Configuration]
                    # ESC t n - Select character code table
                    # n = 5: PC850 (Multilingual)
                    select_codepage_850 = ESC + b't' + b'\x05'
                    
                    print("🔧 Setting ESC/POS Character Set for Swedish (åäö)...")
                    
                    # [Configuration]
                    emoji_map = {
                        '🚚': '', '✔️': 'OK', '🧾': '', 
                        '🎯': '*', '🎊': '',
                        '━': '-', '¨': '~',
                    }
                    
                    text_clean = formatted_text
                    for emoji, replacement in emoji_map.items():
                        text_clean = text_clean.replace(emoji, replacement)
                    
                    # [Configuration]
                    try:
                        text_bytes = text_clean.encode('cp850', errors='replace')
                        print(f"📝 Using CP850 encoding: {len(text_bytes)} bytes (Nordic characters supported)")
                    except:
                        # [Configuration]
                        try:
                            text_bytes = text_clean.encode('iso-8859-1', errors='replace')
                            print(f"📝 Fallback to ISO-8859-1: {len(text_bytes)} bytes")
                        except:
                            text_bytes = text_clean.encode('ascii', errors='replace')
                            print(f"📝 Fallback to ASCII: {len(text_bytes)} bytes")
                    
                    # [Configuration]
                    feed_lines = b'\n\n\n\n\n\n'  # 6 [SV/EN] [SV/EN] [SV/EN] [SV/EN]
                    cut_cmd = GS + b'V' + b'\x00'  # Full cut command
                    
                    # [Configuration]
                    raw_data = init_cmd + select_nordic_charset + select_codepage_850 + text_bytes + feed_lines + cut_cmd
                    
                    print(f"📄 Sending {len(raw_data)} bytes to printer with ESC/POS commands")
                    sock.send(raw_data)
                    sock.close()
                    
                    print("✅ RAW print data sent directly to printer!")
                    
                    # [Configuration]
                    self.stop_alert()
                    print("✅ Print completed successfully")
                    return "OK"
                    
                except Exception as raw_error:
                    print(f"❌ RAW printing failed: {raw_error}")
                    # [Configuration]
            
            # [Configuration]
            print("🔄 Using CUPS printing...")
            
            # [Configuration]
            cups_printer_name = current_config.get("cups_name", "HPRT_TP808")
            print(f"🖨️ CUPS Printer: {cups_printer_name}")
            
            # [Configuration]
            if current_config["type"] == "usb":
                print("📦 Using CHUNKED printing for USB (buffer limitation fix)...")
                import time
                
                # [Configuration]
                lines = formatted_text.split('\n')
                total_lines = len(lines)
                chunk_size = 6  # [SV/EN] [SV/EN] 6 [SV/EN]
                
                print(f"📏 Total lines: {total_lines}, chunk size: {chunk_size}")
                
                success_count = 0
                for chunk_start in range(0, total_lines, chunk_size):
                    chunk_end = min(chunk_start + chunk_size, total_lines)
                    chunk_lines = lines[chunk_start:chunk_end]
                    chunk_text = '\n'.join(chunk_lines) + '\n'
                    
                    print(f"🔄 Chunk {chunk_start//chunk_size + 1}: lines {chunk_start+1}-{chunk_end}")
                    
                    # [Configuration]
                    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as tmp_file:
                        tmp_file.write(chunk_text)
                        tmp_file.flush()
                        tmp_file_path = tmp_file.name
                    
                    try:
                        chunk_result = subprocess.run([
                            '/usr/bin/lp', '-d', cups_printer_name, tmp_file_path
                        ], capture_output=True, text=True, timeout=30)
                        
                        if chunk_result.returncode == 0:
                            success_count += 1
                            print(f"✅ Chunk {chunk_start//chunk_size + 1} sent")
                        else:
                            print(f"❌ Chunk {chunk_start//chunk_size + 1} failed: {chunk_result.stderr}")
                    finally:
                        try:
                            os.unlink(tmp_file_path)
                        except:
                            pass
                    
                    # [Configuration]
                    if chunk_end < total_lines:
                        time.sleep(0.2)
                
                # [Configuration]
                final_cut = '\n\n\n\n\n\n'
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as tmp_file:
                    tmp_file.write(final_cut)
                    tmp_file.flush()
                    tmp_file_path = tmp_file.name
                
                try:
                    subprocess.run([
                        '/usr/bin/lp', '-d', cups_printer_name, tmp_file_path
                    ], capture_output=True, text=True, timeout=30)
                finally:
                    try:
                        os.unlink(tmp_file_path)
                    except:
                        pass
                
                if success_count > 0:
                    print(f"✅ CUPS chunked print successful: {success_count} chunks")
                    self.stop_alert()
                    print("✅ Print completed successfully")
                    return "OK"
                else:
                    print(f"❌ All chunks failed")
                    return "ERROR: Print failed"
            
            else:
                # [Configuration]
                print("📄 Using DIRECT printing for LAN/Bluetooth...")
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as tmp_file:
                    tmp_file.write(formatted_text + '\n\n')
                    tmp_file.flush()
                    tmp_file_path = tmp_file.name
                
                try:
                    direct_result = subprocess.run([
                        '/usr/bin/lp', '-d', cups_printer_name, tmp_file_path
                    ], capture_output=True, text=True, timeout=30)
                    
                    if direct_result.returncode == 0:
                        print(f"✅ CUPS print successful: {direct_result.stdout}")
                        self.stop_alert()
                        print("✅ Print completed successfully")
                        return "OK"
                    else:
                        print(f"❌ CUPS failed: {direct_result.stderr}")
                        
                finally:
                    try:
                        os.unlink(tmp_file_path)
                    except:
                        pass
            
            return "ERROR: Print failed after all attempts"
            
        except Exception as e:
            print(f"❌ Print error: {e}")
            import traceback
            traceback.print_exc()
            return f"ERROR: {e}"
    
    # [Configuration]
    def print(self, text):
        """Function description"""
        return self.print_text(text)
    
    def playAlert(self):
        """Function description"""
        return self.play_alert()
    
    def stopAlert(self):
        """Function description"""
        return self.stop_alert()

    def open_settings(self):
        """Function description"""
        settings_api = SettingsBridge()
        settings_path = os.path.abspath(os.path.join("ui", "settings.html"))
        print("⚙️ Opening settings:", settings_path)
        webview.create_window(
            "⚙️ Settings - DineSysPro",
            f"file://{settings_path}",
            js_api=settings_api,
            width=650,
            height=900,
            fullscreen=False,
            resizable=True
        )
    
    def check_for_updates(self):
        """Check for updates from GitHub"""
        try:
            from auto_updater import check_for_updates
            update_info = check_for_updates(silent=True)
            return update_info
        except Exception as e:
            print(f"❌ Update check failed: {e}")
            return {
                'available': False,
                'error': str(e)
            }
    
    def download_update(self):
        """Download and install update"""
        try:
            from auto_updater import auto_update
            # Run in background thread
            import threading
            update_thread = threading.Thread(target=auto_update)
            update_thread.daemon = True
            update_thread.start()
            return "Update process started"
        except Exception as e:
            print(f"❌ Update download failed: {e}")
            return f"ERROR: {e}"


# [Configuration]
device_id = get_device_id()
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
