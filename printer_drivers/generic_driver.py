"""
Generic ESC/POS Printer Driver

Fallback driver for all ESC/POS compatible printers
(HPRT, Rongta, Xprinter, Bixolon, Zebra, and other brands)
"""

from typing import Dict, Any
from .base_driver import BasePrinterDriver
import subprocess


class GenericESCPOSDriver(BasePrinterDriver):
    """Generic ESC/POS printer driver (fallback for all printers)"""
    
    def __init__(self, address: str, paper_width: int = 80, **kwargs):
        super().__init__(address, paper_width, **kwargs)
        self.printer = None
        self.cups_name = kwargs.get('cups_name', None)
        
    def connect(self) -> bool:
        """Connect to generic ESC/POS printer"""
        try:
            # Try python-escpos
            try:
                from escpos import printer as escpos_printer
                
                # Detect connection type
                if self.address.count('.') == 3:
                    # LAN IP address
                    self.printer = escpos_printer.Network(self.address)
                    self.connected = True
                    print(f"✅ Generic printer connected via Network: {self.address}")
                    return True
                elif ':' in self.address and len(self.address.split(':')) == 6:
                    # Bluetooth MAC address - not directly supported, use CUPS
                    pass
                    
            except ImportError:
                print("⚠️ python-escpos not available")
            except Exception as e:
                print(f"⚠️ Generic network connection failed: {e}")
            
            # Fallback to CUPS
            if self.cups_name:
                result = subprocess.run(
                    ['/usr/bin/lpstat', '-p', self.cups_name],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    self.connected = True
                    print(f"✅ Generic printer connected via CUPS: {self.cups_name}")
                    return True
            
            # If we have any address, consider it "connected" and try CUPS
            if self.address:
                self.connected = True
                print(f"✅ Generic printer marked as connected: {self.address}")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Generic driver connection failed: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from generic printer"""
        try:
            if self.printer and hasattr(self.printer, 'close'):
                self.printer.close()
            self.connected = False
            return True
        except Exception as e:
            print(f"⚠️ Generic disconnect error: {e}")
            return False
    
    def print_text(self, text: str) -> bool:
        """Print text to generic ESC/POS printer"""
        if not self.connected:
            print("❌ Printer not connected")
            return False
        
        try:
            # Try direct printing first
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
                        print(f"✅ Generic CUPS print successful: {result.stdout}")
                        return True
                    else:
                        print(f"❌ Generic CUPS failed: {result.stderr}")
                        return False
                finally:
                    try:
                        os.unlink(tmp_path)
                    except:
                        pass
            
            # Try RAW socket printing for LAN
            if self.address.count('.') == 3:
                import socket
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    sock.connect((self.address, 9100))
                    sock.send(text.encode('utf-8'))
                    sock.close()
                    print(f"✅ Generic RAW print successful")
                    return True
                except Exception as e:
                    print(f"⚠️ Generic RAW print failed: {e}")
            
            return False
            
        except Exception as e:
            print(f"❌ Generic print error: {e}")
            return False
    
    def print_receipt(self, receipt_data: Dict[str, Any]) -> bool:
        """Print formatted receipt"""
        text = receipt_data.get('text', '')
        return self.print_text(text)
    
    @staticmethod
    def detect(device_name: str, device_address: str) -> bool:
        """Generic driver matches everything as fallback"""
        return True  # Always return True as fallback
    
    @staticmethod
    def get_brand_name() -> str:
        return "Generic ESC/POS"
    
    @staticmethod
    def get_priority() -> int:
        return 10  # Low priority (fallback driver)

