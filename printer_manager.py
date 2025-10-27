# printer_manager.py
from escpos import printer

class PrinterManager:
    def __init__(self, mode="lan", address=None, width=80):
        self.mode = mode
        self.address = address
        self.width = width
        self.prn = None

    def connect(self):
        try:
            if self.mode == "lan":
                self.prn = printer.Network(self.address)
            elif self.mode == "usb":
                # استفاده از CUPS برای پرینترهای USB در macOS/Linux
                try:
                    # ابتدا تلاش برای استفاده از نام پرینتر CUPS
                    if hasattr(printer, 'CupsPrinter'):
                        # جستجو برای پرینتر HPRT TP808
                        self.prn = printer.CupsPrinter("HPRT TP808")
                        print("🖨️ Connected via CUPS: HPRT TP808")
                    else:
                        raise Exception("CUPS not available")
                except:
                    try:
                        # fallback به File printer (برای macOS)
                        self.prn = printer.File("/dev/usb/lp0")
                        print("🔌 Connected via File interface")
                    except:
                        # fallback نهایی به USB مستقیم
                        if ':' in str(self.address):
                            vendor_id, product_id = self.address.split(':')
                            
                            # استفاده از backend مناسب برای macOS
                            import usb.core
                            import usb.backend.libusb1
                            
                            # تنظیم backend
                            backend = usb.backend.libusb1.get_backend()
                            
                            self.prn = printer.Usb(
                                int(vendor_id, 16), 
                                int(product_id, 16),
                                usb_args={'custom_match': lambda d: True}
                            )
                            print(f"🔌 USB Direct: {vendor_id}:{product_id}")
                        else:
                            # پیدا کردن خودکار
                            import usb.core
                            device = usb.core.find(idVendor=0x20d1, idProduct=0x7009)
                            if device:
                                self.prn = printer.Usb(0x20d1, 0x7009)
                                print("🔌 Auto-detected HPRT TP808")
                            else:
                                raise Exception("USB printer not found")
            elif self.mode == "bluetooth":
                self.prn = printer.Bluetooth(self.address)
            else:
                print("⚠️ Unknown printer mode. Using network fallback.")
                self.prn = printer.Network("192.168.1.50")
            print("✅ Printer connected successfully.")
        except Exception as e:
            print("❌ Printer connection failed:", e)

    def print_text(self, text):
        if not self.prn:
            print("⚠️ Printer not connected.")
            return
        try:
            # تنظیمات چاپ برای نسخه جدید python-escpos
            try:
                # نسخه جدید
                self.prn.set(align="left", font="a", bold=True)
            except TypeError:
                # نسخه قدیم
                self.prn.set(align="left", font="a", text_type="B")
            
            if self.width == 58:
                max_chars = 32
            else:
                max_chars = 48
                
            lines = text.split("\n")
            for line in lines:
                if line.strip():  # فقط خطوط غیر خالی
                    self.prn.text(line[:max_chars] + "\n")
                else:
                    self.prn.text("\n")  # خط خالی
            
            # اضافه کردن خط خالی در انتها
            self.prn.text("\n")
            
            # برش کاغذ
            try:
                self.prn.cut()
            except:
                # اگر cut کار نکرد، partial cut امتحان کن
                try:
                    self.prn.cut(mode='PART')
                except:
                    print("⚠️ Paper cut not supported")
                    
            print("🖨️ Print successful.")
        except Exception as e:
            print("❌ Print error:", e)

    def close(self):
        try:
            if self.prn:
                self.prn.close()
        except:
            pass
import socket
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

def get_local_ip_range():
    """تشخیص محدوده IP محلی"""
    try:
        # اتصال موقت برای تشخیص IP محلی
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        s.connect(('10.254.254.254', 1))
        local_ip = s.getsockname()[0]
        s.close()
        # استخراج سه بخش اول IP (مثل 192.168.1)
        return '.'.join(local_ip.split('.')[:-1]) + '.'
    except:
        return '192.168.1.'

def scan_ip(ip, port, timeout):
    """اسکن یک IP مشخص"""
    try:
        s = socket.socket()
        s.settimeout(timeout)
        s.connect((ip, port))
        s.close()
        return ip
    except:
        return None

def discover_lan_printers(port=9100, timeout=1.0):
    """اسکن هوشمند LAN برای پرینترهای فعال - با استفاده از Thread Pool"""
    found = []
    print("🌐 Scanning LAN printers...")
    
    # تشخیص محدوده IP محلی
    subnet = get_local_ip_range()
    print(f"🔍 Scanning subnet: {subnet}*")
    
    # لیست IP های مشترک برای اسکن سریع
    common_ips = [1, 10, 20, 50, 100, 101, 102, 150, 200, 254]
    all_ips = common_ips + [i for i in range(1, 255) if i not in common_ips]
    
    # استفاده از Thread Pool برای اسکن موثر
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = []
        for i in all_ips:
            ip = f"{subnet}{i}"
            future = executor.submit(scan_ip, ip, port, timeout)
            futures.append(future)
        
        # جمع‌آوری نتایج
        for future in futures:
            result = future.result()
            if result:
                found.append(result)
                print(f"✅ Found printer at: {result}")
    
    print(f"🖨️ Found {len(found)} LAN printers total")
    return found

def discover_bluetooth_printers():
    """لیست دستگاه‌های بلوتوث موجود - سازگار با macOS/Windows/Linux"""
    found = []
    print("🔵 Scanning Bluetooth printers...")
    
    try:
        # استفاده از bleak برای اسکن BLE
        try:
            from bleak import BleakScanner
            devices = asyncio.run(BleakScanner.discover(timeout=10))
            for d in devices:
                if d.name and ('print' in d.name.lower() or 'epson' in d.name.lower() or 'canon' in d.name.lower() or 'hp' in d.name.lower()):
                    found.append(f"{d.address} - {d.name}")
            print(f"📱 Found {len(found)} BLE devices")
        except ImportError:
            print("⚠️ Bleak not available for BLE scan")
        except Exception as e:
            print(f"⚠️ BLE scan error: {e}")
        
        # استفاده از pybluez برای اسکن کلاسیک
        try:
            import bluetooth
            nearby_devices = bluetooth.discover_devices(duration=10, lookup_names=True)
            for addr, name in nearby_devices:
                if name and ('print' in name.lower() or 'epson' in name.lower() or 'canon' in name.lower() or 'hp' in name.lower()):
                    found.append(f"{addr} - {name}")
            print(f"📶 Found {len(nearby_devices)} classic Bluetooth devices")
        except ImportError:
            print("⚠️ PyBluez not available for classic Bluetooth scan")
        except Exception as e:
            print(f"⚠️ Classic Bluetooth scan error: {e}")
        
    except Exception as e:
        print(f"❌ Bluetooth scan failed: {e}")
    
    print(f"🔵 Found {len(found)} Bluetooth printers total")
    return found if found else ["No Bluetooth printers found"]
