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
                # Use CUPS for USB printers on macOS/Linux
                try:
                    # Try using CUPS printer name first
                    if hasattr(printer, 'CupsPrinter'):
                        # Search for HPRT TP808 printer
                        self.prn = printer.CupsPrinter("HPRT TP808")
                        print("🖨️ Connected via CUPS: HPRT TP808")
                    else:
                        raise Exception("CUPS not available")
                except:
                    try:
                        # Fallback to File printer (for macOS)
                        self.prn = printer.File("/dev/usb/lp0")
                        print("🔌 Connected via File interface")
                    except:
                        # Final fallback to direct USB
                        if ':' in str(self.address):
                            vendor_id, product_id = self.address.split(':')
                            
                            # Use appropriate backend for macOS
                            import usb.core
                            import usb.backend.libusb1
                            
                            # Set backend
                            backend = usb.backend.libusb1.get_backend()
                            
                            self.prn = printer.Usb(
                                int(vendor_id, 16), 
                                int(product_id, 16),
                                usb_args={'custom_match': lambda d: True}
                            )
                            print(f"🔌 USB Direct: {vendor_id}:{product_id}")
                        else:
                            # Auto-detect printer
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
            # Print settings for newer python-escpos versions
            try:
                # New version
                self.prn.set(align="left", font="a", bold=True)
            except TypeError:
                # Old version
                self.prn.set(align="left", font="a", text_type="B")
            
            if self.width == 58:
                max_chars = 32
            else:
                max_chars = 48
                
            lines = text.split("\n")
            for line in lines:
                if line.strip():  # Only non-empty lines
                    self.prn.text(line[:max_chars] + "\n")
                else:
                    self.prn.text("\n")  # Empty line
            
            # Add empty line at the end
            self.prn.text("\n")
            
            # Cut paper
            try:
                self.prn.cut()
            except:
                # Try partial cut if full cut doesn't work
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
    """Detect local IP range"""
    try:
        # Temporary connection to detect local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        s.connect(('10.254.254.254', 1))
        local_ip = s.getsockname()[0]
        s.close()
        # Extract first three parts of IP (e.g., 192.168.1)
        return '.'.join(local_ip.split('.')[:-1]) + '.'
    except:
        return '192.168.1.'

def scan_ip(ip, port, timeout):
    """Scan a specific IP address"""
    try:
        s = socket.socket()
        s.settimeout(timeout)
        s.connect((ip, port))
        s.close()
        return ip
    except:
        return None

def discover_lan_printers(port=9100, timeout=1.0):
    """Smart LAN scan for active printers - using Thread Pool"""
    found = []
    print("🌐 Scanning LAN printers...")
    
    # Detect local IP range
    subnet = get_local_ip_range()
    print(f"🔍 Scanning subnet: {subnet}*")
    
    # List of common IPs for faster scan
    common_ips = [1, 10, 20, 50, 100, 101, 102, 150, 200, 254]
    all_ips = common_ips + [i for i in range(1, 255) if i not in common_ips]
    
    # Use Thread Pool for efficient scanning
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = []
        for i in all_ips:
            ip = f"{subnet}{i}"
            future = executor.submit(scan_ip, ip, port, timeout)
            futures.append(future)
        
        # Collect results
        for future in futures:
            result = future.result()
            if result:
                found.append(result)
                print(f"✅ Found printer at: {result}")
    
    print(f"🖨️ Found {len(found)} LAN printers total")
    return found

def discover_bluetooth_printers():
    """List available Bluetooth devices - compatible with macOS/Windows/Linux"""
    found = []
    print("🔵 Scanning Bluetooth printers...")
    
    try:
        # Use bleak for BLE scan
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
        
        # Use pybluez for classic scan
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
