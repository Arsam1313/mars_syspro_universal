"""
Citizen Printer Driver

Uses ESC/POS with Citizen-specific commands for Citizen printers (CT-S, CL-S, CMP series)
"""

from typing import Dict, Any
from .base_driver import BasePrinterDriver
import subprocess


class CitizenDriver(BasePrinterDriver):
    """Citizen printer driver"""
    
    CITIZEN_KEYWORDS = ['citizen', 'ct-s', 'cl-s', 'cmp', 'cbm', 'ppu']
    
    def __init__(self, address: str, paper_width: int = 80, **kwargs):
        super().__init__(address, paper_width, **kwargs)
        self.printer = None
        self.cups_name = kwargs.get('cups_name', None)
        
    def connect(self) -> bool:
        """Connect to Citizen printer"""
        try:
            # Try ESC/POS
            try:
                from escpos import printer as escpos_printer
                
                if self.address.count('.') == 3:
                    # LAN IP address
                    self.printer = escpos_printer.Network(self.address)
                    self.connected = True
                    print(f"✅ Citizen printer connected via Network: {self.address}")
                    return True
                    
            except ImportError:
                print("⚠️ python-escpos not available")
            except Exception as e:
                print(f"⚠️ Citizen network connection failed: {e}")
            
            # Fallback to CUPS
            if self.cups_name:
                result = subprocess.run(
                    ['/usr/bin/lpstat', '-p', self.cups_name],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    self.connected = True
                    print(f"✅ Citizen printer connected via CUPS: {self.cups_name}")
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ Citizen driver connection failed: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from Citizen printer"""
        try:
            if self.printer and hasattr(self.printer, 'close'):
                self.printer.close()
            self.connected = False
            return True
        except Exception as e:
            print(f"⚠️ Citizen disconnect error: {e}")
            return False
    
    def print_text(self, text: str) -> bool:
        """Print text to Citizen printer"""
        if not self.connected:
            print("❌ Printer not connected")
            return False
        
        try:
            # Try direct printing
            if self.printer:
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
            
            # Fallback to CUPS
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
                        print(f"✅ Citizen CUPS print successful: {result.stdout}")
                        return True
                    else:
                        print(f"❌ Citizen CUPS failed: {result.stderr}")
                        return False
                finally:
                    try:
                        os.unlink(tmp_path)
                    except:
                        pass
            
            return False
            
        except Exception as e:
            print(f"❌ Citizen print error: {e}")
            return False
    
    def print_receipt(self, receipt_data: Dict[str, Any]) -> bool:
        """Print formatted receipt"""
        text = receipt_data.get('text', '')
        return self.print_text(text)
    
    @staticmethod
    def detect(device_name: str, device_address: str) -> bool:
        """Detect if device is a Citizen printer"""
        name_lower = device_name.lower()
        return any(keyword in name_lower for keyword in CitizenDriver.CITIZEN_KEYWORDS)
    
    @staticmethod
    def get_brand_name() -> str:
        return "Citizen"
    
    @staticmethod
    def get_priority() -> int:
        return 1  # High priority (SDK-based)

