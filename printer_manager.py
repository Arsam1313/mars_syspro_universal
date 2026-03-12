import os
import glob
import socket
import usb.core
import usb.util
from escpos import printer

SUPPORTED_CODEPAGES = {
    "default": b'\x12',   # CP858
    "epson": b'\x02',     # CP850
    "star": b'\x12',      # CP858
    "hprt": b'\x12',      # CP858 (tested OK)
    "xprinter": b'\x12',  # CP858
    "bixolon": b'\x02',   # CP850
}

COMMON_USB_PRINTERS = [
    (0x20d1, 0x7009, "HPRT TP808"),
    (0x20d1, 0x7007, "Xprinter XP-58"),
    (0x04b8, 0x0202, "Epson TM-T20"),
    (0x04b8, 0x0005, "Epson TMT20II"),
    (0x1504, 0x0006, "Sewoo LK-P21"),
    (0x0519, 0x0001, "Star TSP100"),
    (0x0519, 0x0020, "Star mC-Print2"),
    (0x0519, 0x0021, "Star mC-Print3"),
    (0x0dd4, 0x0006, "Generic Thermal Printer"),
]


class PrinterManager:
    def __init__(self, mode="auto", address=None, width=80, brand="auto"):
        self.mode = mode
        self.address = address
        self.width = width
        self.brand = brand.lower()
        self.prn = None
        self.usb_device = None
        self.usb_raw_device = None  # برای USB direct access
        self.usb_endpoint_out = None
        self.file_path = None

    def auto_connect(self, preferred_type="auto", address=None, width=80):
        """Auto-detect and connect to printer"""
        self.width = width
        self.address = address
        self.mode = preferred_type or "auto"

        print("🖨️ Auto-connecting to printer...")

        usb_printer = self._find_usb_printer()
        if usb_printer:
            vid, pid, name = usb_printer
            print(f"🔌 Found USB printer: {name} ({hex(vid)}:{hex(pid)})")
            
            # راه حل اول: استفاده مستقیم از PyUSB
            try:
                dev = usb.core.find(idVendor=vid, idProduct=pid)
                if dev is None:
                    raise ValueError("Device not found")
                
                # Detach kernel driver if needed
                try:
                    if dev.is_kernel_driver_active(0):
                        print("🔧 Detaching kernel driver...")
                        dev.detach_kernel_driver(0)
                except:
                    pass
                
                # Set configuration
                try:
                    dev.set_configuration()
                except:
                    pass
                
                # پیدا کردن bulk OUT endpoint
                cfg = dev.get_active_configuration()
                intf = cfg[(0, 0)]
                
                ep_out = None
                for ep in intf:
                    if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_OUT:
                        ep_out = ep
                        break
                
                if ep_out:
                    self.usb_raw_device = dev
                    self.usb_endpoint_out = ep_out.bEndpointAddress
                    self.usb_device = usb_printer
                    self.mode = "usb"
                    self.brand = self._detect_brand_from_name(name)
                    print(f"✅ USB printer connected via PyUSB: {name} (endpoint: {hex(self.usb_endpoint_out)})")
                    return True
                else:
                    print("⚠️ No OUT endpoint found")
            except Exception as e:
                print(f"⚠️ PyUSB direct connection failed: {e}")
            
            # راه حل دوم: استفاده از python-escpos
            print("🔄 Trying python-escpos fallback...")
            endpoint_configs = [
                (0x81, 0x02),
                (0x82, 0x02),
                (0x81, 0x03),
                (None, None),
            ]
            
            for in_ep, out_ep in endpoint_configs:
                try:
                    if in_ep and out_ep:
                        self.prn = printer.Usb(vid, pid, in_ep=in_ep, out_ep=out_ep)
                        print(f"✅ USB printer connected via escpos: {name} (in={hex(in_ep)}, out={hex(out_ep)})")
                    else:
                        self.prn = printer.Usb(vid, pid)
                        print(f"✅ USB printer connected via escpos: {name} (auto-detect)")
                    
                    self.usb_device = usb_printer
                    self.mode = "usb"
                    self.brand = self._detect_brand_from_name(name)
                    return True
                except Exception as e:
                    if in_ep and out_ep:
                        print(f"⚠️ escpos failed with in={hex(in_ep)}, out={hex(out_ep)}: {e}")
                    else:
                        print(f"⚠️ escpos failed with auto-detect: {e}")
                    continue
            
            print("❌ All USB connection methods failed")

        serial_path = self._find_serial_printer()
        if serial_path:
            try:
                self.prn = printer.File(serial_path)
                self.mode = "file"
                self.file_path = serial_path
                self.brand = self._detect_brand_from_name(serial_path)
                print(f"✅ Connected via serial port: {serial_path}")
                return True
            except Exception as e:
                print("❌ Serial printer connect failed:", e)

        if address:
            try:
                self.prn = printer.Network(address)
                self.mode = "lan"
                self.brand = self.detect_brand()
                print(f"✅ Connected to LAN printer ({address})")
                return True
            except Exception as e:
                print("❌ LAN connect failed:", e)

        print("❌ No printer found")
        return False

    def _find_usb_printer(self):
        for vid, pid, name in COMMON_USB_PRINTERS:
            dev = usb.core.find(idVendor=vid, idProduct=pid)
            if dev:
                return (vid, pid, name)
        return None

    def _find_serial_printer(self):
        serial_ports = glob.glob("/dev/tty.usb*") + glob.glob("/dev/ttyUSB*")
        return serial_ports[0] if serial_ports else None

    def _detect_brand_from_name(self, name: str):
        name = name.lower()
        for brand in ["hprt", "star", "epson", "xprinter", "bixolon"]:
            if brand in name:
                print(f"🤖 Detected brand: {brand}")
                return brand
        return "default"

    def detect_brand(self):
        if self.brand != "auto":
            return self.brand
        try:
            if self.mode == "lan" and self.address:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                sock.connect((self.address, 9100))
                sock.send(b'\x1b@')
                sock.send(b'\x1d(I\x02\x00')
                data = sock.recv(128).decode(errors='ignore').lower()
                sock.close()
                for brand in ["epson", "star", "hprt", "xprinter", "bixolon"]:
                    if brand in data:
                        self.brand = brand
                        print(f"🤖 Detected brand: {brand}")
                        return brand
        except Exception as e:
            print("⚠️ Brand auto-detect failed:", e)
        self.brand = "default"
        return self.brand

    def print_text(self, text):
        if not text:
            return "EMPTY"
        
        # چک کردن اتصال (هم PyUSB هم escpos)
        if not self.prn and not self.usb_raw_device:
            print("⚠️ Printer not connected — retrying auto-connect...")
            self.auto_connect(self.mode, self.address, self.width)
            if not self.prn and not self.usb_raw_device:
                return "ERROR: No printer connected"

        brand = self.detect_brand()
        codepage = SUPPORTED_CODEPAGES.get(brand, b'\x12')

        ESC = b'\x1b'
        GS = b'\x1d'
        init = ESC + b'@'
        charset_sweden = ESC + b'R' + b'\x06'
        select_codepage = ESC + b't' + codepage

        emoji_map = {'🚚': '', '✔️': 'OK', '🍕': '*', '🎊': '', '🧾': '', '━': '-', '¨': '~', '…': '...'}
        text_clean = text
        for e, r in emoji_map.items():
            text_clean = text_clean.replace(e, r)

        text_bytes = text_clean.encode("cp858", errors="replace")
        feed = b'\n\n\n\n'
        cut = GS + b'V' + b'\x00'
        raw_data = init + charset_sweden + select_codepage + text_bytes + feed + cut

        try:
            if self.mode == "lan" and self.address:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((self.address, 9100))
                sock.sendall(raw_data)
                sock.close()
                print(f"✅ LAN print OK ({brand})")
                return "OK"
            
            elif self.mode == "usb":
                # روش اول: PyUSB مستقیم (بهترین روش برای HPRT)
                if self.usb_raw_device and self.usb_endpoint_out:
                    try:
                        self.usb_raw_device.write(self.usb_endpoint_out, raw_data)
                        print(f"✅ USB print OK via PyUSB ({brand})")
                        return "OK"
                    except Exception as e:
                        print(f"⚠️ PyUSB write failed: {e}")
                        # ادامه به روش بعدی
                
                # روش دوم: python-escpos
                if self.prn:
                    try:
                        self.prn._raw(raw_data)
                        print(f"✅ USB print OK via escpos ({brand})")
                        return "OK"
                    except Exception as e:
                        print(f"⚠️ escpos write failed: {e}")
                        return f"ERROR: {e}"
                
                return "ERROR: No USB connection available"
            
            elif self.mode == "file" and self.file_path:
                with open(self.file_path, "wb") as f:
                    f.write(raw_data)
                print(f"✅ Serial print OK ({brand})")
                return "OK"
            
            elif self.prn:
                self.prn._raw(raw_data)
                print(f"✅ Generic print OK ({brand})")
                return "OK"
            
            else:
                return "ERROR: No printer connected"
                
        except Exception as e:
            print("❌ Print failed:", e)
            import traceback
            traceback.print_exc()
            return f"ERROR: {e}"

    def disconnect(self):
        try:
            # بستن escpos printer
            if self.prn:
                self.prn.close()
            
            # آزاد کردن USB device
            if self.usb_raw_device:
                try:
                    usb.util.dispose_resources(self.usb_raw_device)
                except:
                    pass
            
            print("🔌 Printer disconnected")
            self.prn = None
            self.usb_raw_device = None
            self.usb_endpoint_out = None
        except Exception as e:
            print(f"⚠️ Disconnect error: {e}")


# LAN discovery
def discover_lan_printers(subnet="192.168.1.", port=9100, timeout=0.3):
    found = []
    print("🌐 Scanning LAN printers...")
    for i in range(1, 255):
        ip = f"{subnet}{i}"
        try:
            s = socket.socket()
            s.settimeout(timeout)
            s.connect((ip, port))
            found.append(ip)
            s.close()
        except:
            pass
    print(f"✅ Found {len(found)} LAN printers")
    return found


# Bluetooth discovery
def discover_bluetooth_printers():
    try:
        import bluetooth
        print("🔵 Scanning Bluetooth printers...")
        nearby_devices = bluetooth.discover_devices(duration=6, lookup_names=True)
        found = [f"{addr} - {name}" for addr, name in nearby_devices]
        print(f"✅ Found {len(found)} Bluetooth devices")
        return found
    except Exception as e:
        print("⚠️ Bluetooth scan error:", e)
        return []
