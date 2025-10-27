"""
Epson Printer Driver

Uses ePOS SDK for Epson printers (TM-T, TM-m, TM-P series)
"""

from typing import Dict, Any
from .base_driver import BasePrinterDriver
import subprocess


class EpsonDriver(BasePrinterDriver):
    """Epson printer driver using ePOS SDK"""
    
    EPSON_KEYWORDS = ['epson', 'tm-t', 'tm-m', 'tm-p', 'tm-u', 'tm-l', 'tm-h', 'tm', 'et-', 'wf-', 'xp-', 'ecotank']
    
    def __init__(self, address: str, paper_width: int = 80, **kwargs):
        super().__init__(address, paper_width, **kwargs)
        self.printer = None
        self.cups_name = kwargs.get('cups_name', None)
        
    def is_pos_printer(self, device_name: str = "") -> bool:
        """Check if this is a POS thermal printer (TM series) vs office printer (ET/WF/XP series)"""
        pos_keywords = ['tm-t', 'tm-m', 'tm-p', 'tm-u', 'tm-l', 'tm-h']
        name_lower = device_name.lower()
        return any(keyword in name_lower for keyword in pos_keywords)
    
    def connect(self) -> bool:
        """Connect to Epson printer"""
        try:
            device_name = self.kwargs.get('device_name', '')
            
            # Check if this is a POS printer (thermal receipt printer)
            if self.is_pos_printer(device_name):
                # Try ESC/POS SDK for POS printers
                try:
                    from escpos import printer as escpos_printer
                    
                    # Detect connection type
                    if self.address.count('.') == 3:
                        # LAN IP address
                        self.printer = escpos_printer.Network(self.address)
                        self.connected = True
                        print(f"✅ Epson POS printer connected via Network: {self.address}")
                        return True
                        
                except ImportError:
                    print("⚠️ python-escpos not available")
                except Exception as e:
                    print(f"⚠️ Epson POS network connection failed: {e}")
            else:
                # Office printer (ET, WF, XP series) - use CUPS only
                print(f"ℹ️ Detected Epson office printer: {device_name}")
            
            # Fallback to CUPS
            if self.cups_name:
                result = subprocess.run(
                    ['/usr/bin/lpstat', '-p', self.cups_name],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    self.connected = True
                    print(f"✅ Epson printer connected via CUPS: {self.cups_name}")
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ Epson driver connection failed: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from Epson printer"""
        try:
            if self.printer and hasattr(self.printer, 'close'):
                self.printer.close()
            self.connected = False
            return True
        except Exception as e:
            print(f"⚠️ Epson disconnect error: {e}")
            return False
    
    def print_text(self, text: str) -> bool:
        """Print text to Epson printer"""
        if not self.connected:
            print("❌ Printer not connected")
            return False
        
        try:
            device_name = self.kwargs.get('device_name', '')
            is_pos = self.is_pos_printer(device_name)
            
            # Try direct ESC/POS printing only for POS printers
            if self.printer and is_pos:
                max_chars = 32 if self.paper_width == 58 else 48
                lines = text.split("\n")
                
                for line in lines:
                    if line.strip():
                        self.printer.text(line[:max_chars] + "\n")
                    else:
                        self.printer.text("\n")
                
                self.printer.text("\n")
                
                try:
                    self.printer.cut()
                except:
                    try:
                        self.printer.cut(mode='PART')
                    except:
                        pass
                
                return True
            
            # Use CUPS for office printers
            if self.cups_name:
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as tmp:
                    tmp.write(text)
                    tmp.flush()
                    tmp_path = tmp.name
                
                try:
                    result = subprocess.run(
                        ['/usr/bin/lp', '-d', self.cups_name, tmp_path],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        print(f"✅ Epson CUPS print successful: {result.stdout}")
                        return True
                    else:
                        print(f"❌ Epson CUPS failed: {result.stderr}")
                        return False
                finally:
                    try:
                        os.unlink(tmp_path)
                    except:
                        pass
            
            # Last resort: Try IPP printing for office printers
            if not is_pos and self.address.count('.') == 3:
                print(f"ℹ️ Attempting IPP print to {self.address}")
                try:
                    # Try IPP (Internet Printing Protocol) - standard for office printers
                    result = subprocess.run(
                        ['/usr/bin/lp', '-h', self.address, '-'],
                        input=text,
                        text=True,
                        capture_output=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        print(f"✅ Epson IPP print successful")
                        return True
                    else:
                        print(f"❌ Epson IPP failed: {result.stderr}")
                except Exception as e:
                    print(f"❌ IPP print error: {e}")
            
            return False
            
        except Exception as e:
            print(f"❌ Epson print error: {e}")
            return False
    
    def print_receipt(self, receipt_data: Dict[str, Any]) -> bool:
        """Print formatted receipt"""
        text = receipt_data.get('text', '')
        return self.print_text(text)
    
    @staticmethod
    def detect(device_name: str, device_address: str) -> bool:
        """Detect if device is an Epson printer"""
        name_lower = device_name.lower()
        return any(keyword in name_lower for keyword in EpsonDriver.EPSON_KEYWORDS)
    
    @staticmethod
    def get_brand_name() -> str:
        return "Epson"
    
    @staticmethod
    def get_priority() -> int:
        return 1  # High priority (SDK-based)

