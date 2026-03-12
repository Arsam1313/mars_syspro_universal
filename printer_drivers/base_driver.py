"""
Base Printer Driver Abstract Class

All printer drivers must inherit from this class.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class BasePrinterDriver(ABC):
    """Abstract base class for all printer drivers"""
    
    def __init__(self, address: str, paper_width: int = 80, **kwargs):
        """
        Initialize printer driver
        
        Args:
            address: Printer address (MAC, IP, etc.)
            paper_width: Paper width in mm (58 or 80)
            **kwargs: Additional driver-specific options
        """
        self.address = address
        self.paper_width = paper_width
        self.options = kwargs
        self.connected = False
        
    @abstractmethod
    def connect(self) -> bool:
        """
        Connect to the printer
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """
        Disconnect from the printer
        
        Returns:
            bool: True if disconnection successful, False otherwise
        """
        pass
    
    @abstractmethod
    def print_text(self, text: str) -> bool:
        """
        Print text content
        
        Args:
            text: Text to print
            
        Returns:
            bool: True if print successful, False otherwise
        """
        pass
    
    @abstractmethod
    def print_receipt(self, receipt_data: Dict[str, Any]) -> bool:
        """
        Print a formatted receipt
        
        Args:
            receipt_data: Receipt data dictionary
            
        Returns:
            bool: True if print successful, False otherwise
        """
        pass
    
    def cut_paper(self) -> bool:
        """
        Cut paper (optional, may not be supported by all printers)
        
        Returns:
            bool: True if successful, False otherwise
        """
        return True
    
    def open_cash_drawer(self) -> bool:
        """
        Open cash drawer (optional)
        
        Returns:
            bool: True if successful, False otherwise
        """
        return True
    
    @staticmethod
    @abstractmethod
    def detect(device_name: str, device_address: str) -> bool:
        """
        Check if this driver supports the detected device
        
        Args:
            device_name: Device name from scan
            device_address: Device address
            
        Returns:
            bool: True if this driver supports the device
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_brand_name() -> str:
        """
        Get the brand name this driver supports
        
        Returns:
            str: Brand name (e.g., "Star", "Epson", "Citizen")
        """
        pass
    
    @staticmethod
    def get_priority() -> int:
        """
        Get driver priority (lower = higher priority)
        SDK-based drivers should return 1
        Generic drivers should return 10
        
        Returns:
            int: Priority value
        """
        return 5

