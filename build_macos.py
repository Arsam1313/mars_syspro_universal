#!/usr/bin/env python3
"""
Build script for macOS application
Creates a .app bundle and .dmg installer
"""

import PyInstaller.__main__
import os
import shutil
import subprocess

APP_NAME = "DineSysPro"
VERSION = "1.0.0"
MAIN_SCRIPT = "main.py"
ICON_PATH = "icon.icns"
DIST_PATH = "dist"
BUILD_PATH = "build"

# Directories and files to include
RESOURCES = [
    ("ui", "ui"),
    ("sounds", "sounds"),
    ("config.json", "."),
    ("printer_manager.py", "."),
    ("auto_updater.py", "."),
]

def clean_build():
    """Clean previous build artifacts"""
    print("🧹 Cleaning previous builds...")
    
    for path in [DIST_PATH, BUILD_PATH, f"{APP_NAME}.spec"]:
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
    
    print("✅ Clean complete")

def build_app():
    """Build macOS .app bundle"""
    print("🔨 Building macOS application...")
    
    # Detect current architecture
    import platform
    current_arch = platform.machine()
    print(f"🖥️  Building on: {current_arch}")
    
    # Prepare PyInstaller arguments
    args = [
        MAIN_SCRIPT,
        f'--name={APP_NAME}',
        '--onefile',
        '--windowed',
        f'--icon={ICON_PATH}',
        '--clean',
        f'--distpath={DIST_PATH}',
        f'--workpath={BUILD_PATH}',
        '--noconfirm',
        '--target-arch=universal2',  # Build for both Intel and Apple Silicon
    ]
    
    # Add resources
    for src, dst in RESOURCES:
        args.append(f'--add-data={src}:{dst}')
    
    # Hidden imports
    hidden_imports = [
        'pygame',
        'escpos',
        'cups',
        'flask',
        'flask_cors',
        'requests',
        'packaging',
    ]
    
    for imp in hidden_imports:
        args.append(f'--hidden-import={imp}')
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    # Remove quarantine attribute to avoid Gatekeeper issues
    app_path = os.path.join(DIST_PATH, f"{APP_NAME}.app")
    try:
        print("🔓 Removing quarantine attributes...")
        subprocess.run(['xattr', '-cr', app_path], check=False)
        print("✅ Quarantine attributes removed")
    except Exception as e:
        print(f"⚠️  Could not remove quarantine: {e}")
        print("💡 Users may need to run: xattr -cr /Applications/DineSysPro.app")
    
    print(f"✅ Application built: {DIST_PATH}/{APP_NAME}.app")

def create_dmg():
    """Create DMG installer for macOS"""
    print("📦 Creating DMG installer...")
    
    dmg_name = f"{APP_NAME}-{VERSION}-macOS.dmg"
    dmg_path = os.path.join(DIST_PATH, dmg_name)
    app_path = os.path.join(DIST_PATH, f"{APP_NAME}.app")
    
    # Remove old DMG if exists
    if os.path.exists(dmg_path):
        os.remove(dmg_path)
    
    # Create DMG
    try:
        subprocess.run([
            'hdiutil', 'create',
            '-volname', APP_NAME,
            '-srcfolder', app_path,
            '-ov',
            '-format', 'UDZO',
            dmg_path
        ], check=True)
        
        print(f"✅ DMG created: {dmg_path}")
        return dmg_path
    except subprocess.CalledProcessError as e:
        print(f"⚠️  DMG creation failed: {e}")
        print("💡 You can manually create DMG or distribute the .app directly")
        return None

def main():
    """Main build process"""
    print("="*60)
    print(f"🚀 Building {APP_NAME} v{VERSION} for macOS")
    print("="*60)
    
    # Clean previous builds
    clean_build()
    
    # Build application
    build_app()
    
    # Create DMG
    dmg_path = create_dmg()
    
    print("\n" + "="*60)
    print("✅ Build Complete!")
    print("="*60)
    print(f"\n📦 Application: {DIST_PATH}/{APP_NAME}.app")
    if dmg_path:
        print(f"📦 Installer: {dmg_path}")
    print(f"\n💡 To test: open {DIST_PATH}/{APP_NAME}.app")
    print(f"💡 To install: drag {APP_NAME}.app to /Applications")
    print("\n" + "="*60)

if __name__ == "__main__":
    main()

