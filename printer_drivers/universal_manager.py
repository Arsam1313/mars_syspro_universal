"""
Universal Printer Manager

Auto-detects printer brand and uses appropriate driver
"""

from typing import Optional, List, Tuple, Dict, Any
from .base_driver import BasePrinterDriver
from .star_driver import StarDriver
from .epson_driver import EpsonDriver
from .citizen_driver import CitizenDriver
from .generic_driver import GenericESCPOSDriver
from .cups_manager import CUPSManager


class UniversalPrinterManager:
    """
    Universal printer manager that auto-detects printer brand
    and uses the appropriate driver
    """
    
    # Available drivers sorted by priority
    AVAILABLE_DRIVERS = [
        StarDriver,
        EpsonDriver,
        CitizenDriver,
        GenericESCPOSDriver,  # Always last as fallback
    ]
    
    def __init__(self):
        self.current_driver: Optional[BasePrinterDriver] = None
        self.current_config: Dict[str, Any] = {}
        
    @classmethod
    def detect_driver(cls, device_name: str, device_address: str) -> type:
        """
        Auto-detect which driver to use based on device name
        
        Args:
            device_name: Name of the printer device
            device_address: Address of the printer
            
        Returns:
            Driver class to use
        """
        # Find all matching drivers
        matching_drivers = []
        
        for driver_class in cls.AVAILABLE_DRIVERS:
            if driver_class.detect(device_name, device_address):
                priority = driver_class.get_priority()
                matching_drivers.append((priority, driver_class))
        
        # Sort by priority (lower number = higher priority)
        matching_drivers.sort(key=lambda x: x[0])
        
        if matching_drivers:
            selected_driver = matching_drivers[0][1]
            print(f"🎯 Auto-detected printer: {selected_driver.get_brand_name()}")
            return selected_driver
        
        # Fallback to generic (should never happen as Generic always returns True)
        print(f"🎯 Using fallback: Generic ESC/POS")
        return GenericESCPOSDriver
    
    def connect(self, printer_type: str, address: str, paper_width: int = 80, 
                device_name: str = "", cups_name: str = None) -> bool:
        """
        Connect to printer with auto-detection and automatic CUPS registration
        
        Args:
            printer_type: Type hint (lan, bluetooth, usb) - not used for brand detection
            address: Printer address
            paper_width: Paper width in mm
            device_name: Device name for brand detection
            cups_name: CUPS printer name (optional)
            
        Returns:
            bool: True if connection successful
        """
        try:
            # Auto-detect driver
            driver_class = self.detect_driver(device_name, address)
            
            # Auto-register Bluetooth printers in CUPS if needed
            if printer_type == 'bluetooth' and cups_name and device_name:
                print("🔧 Checking CUPS registration for Bluetooth printer...")
                
                # Check if CUPS is available
                if CUPSManager.is_cups_available():
                    # Check if printer is already registered
                    if not CUPSManager.is_printer_registered(cups_name):
                        print(f"📝 Printer not registered in CUPS, auto-registering...")
                        
                        # Extract MAC address from address
                        mac_address = self._extract_mac_address(address)
                        
                        if mac_address:
                            # Try to auto-register
                            success = CUPSManager.register_bluetooth_printer(
                                device_name=cups_name,
                                mac_address=mac_address
                            )
                            
                            if success:
                                print(f"✅ Bluetooth printer auto-registered in CUPS: {cups_name}")
                            else:
                                print(f"⚠️ Could not auto-register, will try direct connection")
                    else:
                        print(f"✅ Printer already registered in CUPS: {cups_name}")
                else:
                    print("⚠️ CUPS not available on this system")
            
            # Create driver instance
            self.current_driver = driver_class(
                address=address,
                paper_width=paper_width,
                cups_name=cups_name
            )
            
            # Store config
            self.current_config = {
                'type': printer_type,
                'address': address,
                'paper_width': paper_width,
                'device_name': device_name,
                'cups_name': cups_name,
                'brand': driver_class.get_brand_name()
            }
            
            # Connect
            success = self.current_driver.connect()
            
            if success:
                print(f"✅ Universal Printer Manager: Connected to {driver_class.get_brand_name()}")
            else:
                print(f"❌ Universal Printer Manager: Failed to connect")
                
            return success
            
        except Exception as e:
            print(f"❌ Universal Printer Manager connection error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _extract_mac_address(self, address: str) -> Optional[str]:
        """
        Extract MAC address from various address formats
        
        Args:
            address: Address string (e.g., "macOS-BT: 00:11:62:4B:18:FF", "00:11:62:4B:18:FF")
            
        Returns:
            MAC address or None
        """
        import re
        
        # MAC address pattern: XX:XX:XX:XX:XX:XX
        mac_pattern = r'([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})'
        
        match = re.search(mac_pattern, address)
        if match:
            return match.group(1)
        
        return None
    
    def disconnect(self) -> bool:
        """Disconnect from current printer"""
        if self.current_driver:
            return self.current_driver.disconnect()
        return True
    
    def print_text(self, text: str) -> bool:
        """Print text using current driver"""
        if not self.current_driver:
            print("❌ No printer connected")
            return False
        
        return self.current_driver.print_text(text)
    
    def print_receipt(self, receipt_data: Dict[str, Any]) -> bool:
        """Print receipt using current driver"""
        if not self.current_driver:
            print("❌ No printer connected")
            return False
        
        return self.current_driver.print_receipt(receipt_data)
    
    def get_current_brand(self) -> str:
        """Get current printer brand"""
        if self.current_driver:
            return self.current_driver.get_brand_name()
        return "None"
    
    def get_config(self) -> Dict[str, Any]:
        """Get current printer configuration"""
        return self.current_config.copy()
    
    def is_connected(self) -> bool:
        """Check if printer is connected"""
        return self.current_driver is not None and self.current_driver.connected

