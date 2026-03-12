"""
Star Micronics Printer Driver

Uses StarXpand SDK for Star printers (TSP, mC-Print, SM-L, SM-S series)
"""

from typing import Dict, Any, Optional
from .base_driver import BasePrinterDriver
import subprocess
import platform


class StarDriver(BasePrinterDriver):
    """Star Micronics printer driver using StarXpand SDK"""
    
    STAR_KEYWORDS = ['star', 'tsp', 'mcp', 'mc-print', 'mcprint', 'sm-l', 'sm-s', 'sm-t']
    
    def __init__(self, address: str, paper_width: int = 80, **kwargs):
        super().__init__(address, paper_width, **kwargs)
        self.printer = None
        self.cups_name = kwargs.get('cups_name', None)
        
    def connect(self) -> bool:
        """Connect to Star printer"""
        try:
            # Try SDK first
            try:
                from stario import StarPrinter
                
                # Detect connection type
                if ':' in self.address and len(self.address.split(':')) == 6:
                    # Bluetooth MAC address
                    conn_string = f"BT:{self.address}"
                elif self.address.count('.') == 3:
                    # LAN IP address
                    conn_string = f"TCP:{self.address}"
                else:
                    conn_string = self.address
                
                self.printer = StarPrinter(conn_string)
                self.connected = True
                print(f"✅ Star printer connected via SDK: {conn_string}")
                return True
                
            except ImportError:
                print("⚠️ StarXpand SDK not available, using CUPS fallback")
                
            # Fallback to CUPS
            if self.cups_name:
                result = subprocess.run(
                    ['/usr/bin/lpstat', '-p', self.cups_name],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    self.connected = True
                    print(f"✅ Star printer connected via CUPS: {self.cups_name}")
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ Star driver connection failed: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from Star printer"""
        try:
            if self.printer and hasattr(self.printer, 'close'):
                self.printer.close()
            self.connected = False
            return True
        except Exception as e:
            print(f"⚠️ Star disconnect error: {e}")
            return False
    
    def print_text(self, text: str) -> bool:
        """Print text to Star printer"""
        if not self.connected:
            print("❌ Printer not connected")
            return False
        
        try:
            # Try SDK first
            if self.printer and hasattr(self.printer, 'print_text'):
                self.printer.print_text(text)
                self.printer.cut()
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
                        print(f"✅ Star CUPS print successful: {result.stdout}")
                        return True
                    else:
                        print(f"❌ Star CUPS failed: {result.stderr}")
                        return False
                finally:
                    try:
                        os.unlink(tmp_path)
                    except:
                        pass
            
            return False
            
        except Exception as e:
            print(f"❌ Star print error: {e}")
            return False
    
    def print_receipt(self, receipt_data: Dict[str, Any]) -> bool:
        """Print formatted receipt"""
        # For now, convert to text and use print_text
        # TODO: Implement proper formatting with Star SDK commands
        text = receipt_data.get('text', '')
        return self.print_text(text)
    
    @staticmethod
    def detect(device_name: str, device_address: str) -> bool:
        """Detect if device is a Star printer"""
        name_lower = device_name.lower()
        return any(keyword in name_lower for keyword in StarDriver.STAR_KEYWORDS)
    
    @staticmethod
    def get_brand_name() -> str:
        return "Star Micronics"
    
    @staticmethod
    def get_priority() -> int:
        return 1  # High priority (SDK-based)

