#!/usr/bin/env python3
"""
Build script for DineSysPro macOS application
Creates a standalone .app bundle with custom icon
"""

import os
import sys
import shutil
import subprocess

APP_NAME = "DineSysPro"
MAIN_SCRIPT = "main.py"
ICON_NAME = "icon.icns"  # You need to provide this file

def create_icon_from_emoji():
    """Create a simple icon file (placeholder)"""
    print("📝 Note: For a custom icon, place an 'icon.icns' file in the project root")
    print("   You can create one at: https://cloudconvert.com/png-to-icns")
    print("   Or use: https://www.img2icnsconverter.com/")

def build_with_pyinstaller():
    """Build app using PyInstaller"""
    print(f"🔨 Building {APP_NAME}.app with PyInstaller...")
    
    cmd = [
        "pyinstaller",
        "--name", APP_NAME,
        "--windowed",  # No console window
        "--onefile",   # Single executable
        "--clean",     # Clean cache
    ]
    
    # Add icon if exists
    if os.path.exists(ICON_NAME):
        cmd.extend(["--icon", ICON_NAME])
        print(f"✅ Using icon: {ICON_NAME}")
    else:
        print(f"⚠️  No icon file found: {ICON_NAME}")
        create_icon_from_emoji()
    
    # Add data files
    cmd.extend([
        "--add-data", "config.json:.",
        "--add-data", "sounds:sounds",
        "--add-data", "ui:ui",
        "--add-data", "printer_manager.py:.",
    ])
    
    # Add hidden imports
    cmd.extend([
        "--hidden-import", "pygame",
        "--hidden-import", "escpos",
        "--hidden-import", "flask",
        "--hidden-import", "flask_cors",
        "--hidden-import", "pycups",
    ])
    
    cmd.append(MAIN_SCRIPT)
    
    try:
        subprocess.run(cmd, check=True)
        print(f"\n✅ Build complete!")
        print(f"📦 App location: dist/{APP_NAME}.app")
        print(f"\n🚀 To run: open dist/{APP_NAME}.app")
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        sys.exit(1)

def install_pyinstaller():
    """Install PyInstaller if not available"""
    try:
        import PyInstaller
        print("✅ PyInstaller is installed")
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

if __name__ == "__main__":
    print("="*60)
    print(f"🍕 Building {APP_NAME} macOS Application")
    print("="*60)
    
    # Check if PyInstaller is installed
    install_pyinstaller()
    
    # Build the app
    build_with_pyinstaller()
    
    print("\n" + "="*60)
    print("📝 Next steps:")
    print("1. Create a custom icon (icon.icns) for better branding")
    print("2. Test the app: open dist/DineSysPro.app")
    print("3. Distribute: Copy DineSysPro.app to Applications folder")
    print("="*60)

