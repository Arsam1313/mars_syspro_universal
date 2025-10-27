"""
CUPS Auto-Registration Manager

Automatically registers printers in CUPS without manual setup
"""

import subprocess
import platform
import os
from typing import Optional, Dict, Any


class CUPSManager:
    """Manages automatic printer registration in CUPS"""
    
    @staticmethod
    def is_cups_available() -> bool:
        """Check if CUPS is available on the system"""
        try:
            result = subprocess.run(['lpstat', '-r'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            return result.returncode == 0
        except:
            return False
    
    @staticmethod
    def is_printer_registered(printer_name: str) -> bool:
        """Check if a printer is already registered in CUPS"""
        try:
            result = subprocess.run(['lpstat', '-p', printer_name], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            return result.returncode == 0
        except:
            return False
    
    @staticmethod
    def get_available_drivers() -> list:
        """Get list of available CUPS drivers"""
        try:
            result = subprocess.run(['lpinfo', '-m'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')
            return []
        except:
            return []
    
    @staticmethod
    def find_best_driver(device_name: str) -> Optional[str]:
        """
        Find the best CUPS driver for a printer
        
        Args:
            device_name: Name of the printer (e.g., "mcprint3", "ET-2870")
            
        Returns:
            Driver name or None if not found
        """
        device_lower = device_name.lower()
        
        # Driver mapping for common printers
        driver_keywords = {
            # Star Micronics
            'star': ['star', 'starmicronics'],
            'tsp': ['star', 'tsp'],
            'mcprint': ['star', 'mcprint'],
            'mcp': ['star', 'mcprint'],
            'sm-l': ['star'],
            'sm-s': ['star'],
            'sm-t': ['star'],
            
            # Epson
            'epson': ['epson', 'escpos'],
            'tm-t': ['epson', 'tm'],
            'tm-m': ['epson', 'tm'],
            'tm-p': ['epson', 'tm'],
            'et-': ['epson'],
            'wf-': ['epson'],
            'xp-': ['epson'],
            
            # Citizen
            'citizen': ['citizen'],
            'ct-s': ['citizen'],
            
            # Generic ESC/POS
            'hprt': ['escpos', 'generic'],
            'rongta': ['escpos', 'generic'],
            'xprinter': ['escpos', 'generic'],
        }
        
        # Try to get available drivers
        available_drivers = CUPSManager.get_available_drivers()
        
        if not available_drivers:
            # Fallback to generic driver
            return 'drv:///sample.drv/generic.ppd'
        
        # Find matching driver
        for keyword, search_terms in driver_keywords.items():
            if keyword in device_lower:
                for driver in available_drivers:
                    driver_lower = driver.lower()
                    if any(term in driver_lower for term in search_terms):
                        # Extract driver name (format: "drivername description")
                        driver_name = driver.split()[0]
                        print(f"📦 Found driver: {driver_name}")
                        return driver_name
        
        # Generic ESC/POS fallback
        for driver in available_drivers:
            driver_lower = driver.lower()
            if 'generic' in driver_lower or 'escpos' in driver_lower or 'raw' in driver_lower:
                driver_name = driver.split()[0]
                print(f"📦 Using generic driver: {driver_name}")
                return driver_name
        
        # Last resort: sample generic driver
        print("📦 Using sample generic driver")
        return 'drv:///sample.drv/generic.ppd'
    
    @staticmethod
    def register_bluetooth_printer(device_name: str, mac_address: str) -> bool:
        """
        Automatically register a Bluetooth printer in CUPS
        
        Args:
            device_name: Printer name (e.g., "mcprint3")
            mac_address: Bluetooth MAC address
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"🔧 Auto-registering Bluetooth printer: {device_name}")
            
            # Check if already registered
            if CUPSManager.is_printer_registered(device_name):
                print(f"✅ Printer already registered: {device_name}")
                return True
            
            # Find best driver
            driver = CUPSManager.find_best_driver(device_name)
            if not driver:
                print("❌ No suitable driver found")
                return False
            
            # macOS Bluetooth URI format
            # For macOS, we use the Bonjour/AirPrint discovery or serial port
            # First, try to find the printer's serial port
            bt_uri = CUPSManager._find_bluetooth_uri(device_name, mac_address)
            
            if not bt_uri:
                print("⚠️ Could not determine Bluetooth URI")
                # Try generic Bluetooth URI
                bt_uri = f"bluetooth://{mac_address.replace(':', '')}"
            
            print(f"🔗 Using URI: {bt_uri}")
            print(f"🔗 Using driver: {driver}")
            
            # Try lpadmin command (may require sudo)
            cmd = [
                'lpadmin',
                '-p', device_name,
                '-v', bt_uri,
                '-m', driver,
                '-E',  # Enable printer
                '-o', 'printer-is-shared=false'
            ]
            
            print(f"🔧 Running: {' '.join(cmd)}")
            
            # Try without sudo first
            result = subprocess.run(cmd, 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=30)
            
            if result.returncode == 0:
                print(f"✅ Printer registered successfully: {device_name}")
                return True
            
            # If failed, try with sudo (will prompt for password)
            print("⚠️ Registration requires admin privileges")
            print("💡 You may be prompted for your password...")
            
            result = subprocess.run(['sudo'] + cmd, 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=60)
            
            if result.returncode == 0:
                print(f"✅ Printer registered successfully with sudo: {device_name}")
                return True
            else:
                print(f"❌ Failed to register printer: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Registration timed out")
            return False
        except Exception as e:
            print(f"❌ Error registering printer: {e}")
            return False
    
    @staticmethod
    def _find_bluetooth_uri(device_name: str, mac_address: str) -> Optional[str]:
        """
        Find the Bluetooth URI for a printer on macOS
        
        Args:
            device_name: Printer name
            mac_address: MAC address
            
        Returns:
            Bluetooth URI or None
        """
        if platform.system() != 'Darwin':
            return None
        
        try:
            # Try to find via lpinfo
            result = subprocess.run(['lpinfo', '-v'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    # Look for Bluetooth device
                    if mac_address.lower() in line.lower() or device_name.lower() in line.lower():
                        # Extract URI (format: "network uri")
                        parts = line.split()
                        if len(parts) >= 2:
                            uri = parts[1]
                            print(f"🔍 Found URI via lpinfo: {uri}")
                            return uri
            
            # Fallback: Check for serial port
            serial_ports = [
                f"/dev/cu.{device_name}",
                f"/dev/cu.{device_name}-SerialPort",
                f"/dev/tty.{device_name}",
                f"/dev/tty.{device_name}-SerialPort"
            ]
            
            for port in serial_ports:
                if os.path.exists(port):
                    print(f"🔍 Found serial port: {port}")
                    return f"serial://{port}?baud=115200"
            
        except Exception as e:
            print(f"⚠️ Error finding Bluetooth URI: {e}")
        
        return None
    
    @staticmethod
    def unregister_printer(printer_name: str) -> bool:
        """
        Remove a printer from CUPS
        
        Args:
            printer_name: Name of printer to remove
            
        Returns:
            True if successful
        """
        try:
            result = subprocess.run(['lpadmin', '-x', printer_name], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
            return result.returncode == 0
        except:
            return False

