#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build script for Windows application
Creates a .exe installer
Note: This should be run on a Windows machine or with Wine
"""

import sys
import io

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import PyInstaller.__main__
import os
import shutil

APP_NAME = "DineSysPro"
VERSION = "1.0.3"
MAIN_SCRIPT = "main.py"
ICON_PATH = "icon/logo_dinesyspro.ico"
DIST_PATH = "dist"
BUILD_PATH = "build"

# Directories and files to include
RESOURCES = [
    ("ui", "ui"),
    ("sounds", "sounds"),
    ("printer_drivers", "printer_drivers"),
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

def build_exe():
    """Build Windows .exe"""
    print("🔨 Building Windows application...")
    
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
    ]
    
    # Add resources
    for src, dst in RESOURCES:
        args.append(f'--add-data={src};{dst}')  # Note: Windows uses semicolon
    
    # Hidden imports
    hidden_imports = [
        'pygame',
        'escpos',
        'flask',
        'flask_cors',
        'requests',
        'packaging',
        'win32api',
        'win32con',
    ]
    
    for imp in hidden_imports:
        args.append(f'--hidden-import={imp}')
    
    # Windows specific options
    args.extend([
        '--version-file=version_info.txt',  # Optional: version info
    ])
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    print(f"✅ Application built: {DIST_PATH}/{APP_NAME}.exe")

def create_version_info():
    """Create version info file for Windows"""
    version_info = f"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({VERSION.replace('.', ', ')}, 0),
    prodvers=({VERSION.replace('.', ', ')}, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'DineSysPro'),
        StringStruct(u'FileDescription', u'DineSysPro Restaurant Management System'),
        StringStruct(u'FileVersion', u'{VERSION}'),
        StringStruct(u'InternalName', u'{APP_NAME}'),
        StringStruct(u'LegalCopyright', u'Copyright © 2024 DineSysPro'),
        StringStruct(u'OriginalFilename', u'{APP_NAME}.exe'),
        StringStruct(u'ProductName', u'DineSysPro'),
        StringStruct(u'ProductVersion', u'{VERSION}')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
    
    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_info)
    
    print("✅ Version info created")

def create_installer():
    """Create Windows installer using Inno Setup (if available)"""
    print("📦 Creating Windows installer...")
    
    # Check if Inno Setup is available
    inno_setup_path = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    
    if not os.path.exists(inno_setup_path):
        print("⚠️  Inno Setup not found. Skipping installer creation.")
        print("💡 Download from: https://jrsoftware.org/isdl.php")
        return None
    
    # Create Inno Setup script
    iss_script = f"""
[Setup]
AppName={APP_NAME}
AppVersion={VERSION}
DefaultDirName={{pf}}\\{APP_NAME}
DefaultGroupName={APP_NAME}
OutputDir={DIST_PATH}
OutputBaseFilename={APP_NAME}-{VERSION}-Windows-Setup
Compression=lzma2
SolidCompression=yes
SetupIconFile={ICON_PATH}

[Files]
Source: "{DIST_PATH}\\{APP_NAME}.exe"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "ui\\*"; DestDir: "{{app}}\\ui"; Flags: ignoreversion recursesubdirs
Source: "sounds\\*"; DestDir: "{{app}}\\sounds"; Flags: ignoreversion recursesubdirs
Source: "config.json"; DestDir: "{{app}}"; Flags: ignoreversion

[Icons]
Name: "{{group}}\\{APP_NAME}"; Filename: "{{app}}\\{APP_NAME}.exe"
Name: "{{commondesktop}}\\{APP_NAME}"; Filename: "{{app}}\\{APP_NAME}.exe"

[Run]
Filename: "{{app}}\\{APP_NAME}.exe"; Description: "Launch {APP_NAME}"; Flags: nowait postinstall skipifsilent
"""
    
    with open('installer.iss', 'w', encoding='utf-8') as f:
        f.write(iss_script)
    
    # Run Inno Setup
    try:
        import subprocess
        subprocess.run([inno_setup_path, 'installer.iss'], check=True)
        print(f"✅ Installer created: {DIST_PATH}/{APP_NAME}-{VERSION}-Windows-Setup.exe")
        return f"{DIST_PATH}/{APP_NAME}-{VERSION}-Windows-Setup.exe"
    except Exception as e:
        print(f"⚠️  Installer creation failed: {e}")
        return None

def main():
    """Main build process"""
    print("="*60)
    print(f"🚀 Building {APP_NAME} v{VERSION} for Windows")
    print("="*60)
    
    # Clean previous builds
    clean_build()
    
    # Create version info
    create_version_info()
    
    # Build application
    build_exe()
    
    # Create installer (optional)
    installer_path = create_installer()
    
    print("\n" + "="*60)
    print("✅ Build Complete!")
    print("="*60)
    print(f"\n📦 Application: {DIST_PATH}/{APP_NAME}.exe")
    if installer_path:
        print(f"📦 Installer: {installer_path}")
    print(f"\n💡 To test: {DIST_PATH}\\{APP_NAME}.exe")
    print("\n" + "="*60)

if __name__ == "__main__":
    main()

