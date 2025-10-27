#!/usr/bin/env python3
"""
Auto-updater for DineSysPro
Checks GitHub for new releases and updates the application
"""

import requests
import json
import os
import sys
import subprocess
import platform
from packaging import version as pkg_version

GITHUB_REPO = "Arsam1313/mars_syspro_universal"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
CONFIG_PATH = "config.json"

def get_current_version():
    """Get current version from config.json"""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get('version', '1.0.0')
    except:
        return '1.0.0'

def get_latest_release():
    """Get latest release info from GitHub"""
    try:
        response = requests.get(GITHUB_API_URL, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to check for updates: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error checking for updates: {e}")
        return None

def compare_versions(current, latest):
    """Compare version numbers"""
    try:
        return pkg_version.parse(latest) > pkg_version.parse(current)
    except:
        return False

def get_download_url_for_platform(release_data):
    """Get download URL for current platform"""
    system = platform.system().lower()
    assets = release_data.get('assets', [])
    
    for asset in assets:
        name = asset['name'].lower()
        
        if system == 'darwin' and name.endswith('.dmg'):
            return asset['browser_download_url']
        elif system == 'windows' and name.endswith('.exe'):
            return asset['browser_download_url']
        elif system == 'linux' and name.endswith('.appimage'):
            return asset['browser_download_url']
    
    return None

def download_update(url, filename):
    """Download update file"""
    try:
        print(f"📥 Downloading update from: {url}")
        response = requests.get(url, stream=True, timeout=60)
        total_size = int(response.headers.get('content-length', 0))
        
        with open(filename, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r📊 Progress: {percent:.1f}%", end='', flush=True)
        
        print(f"\n✅ Download complete: {filename}")
        return True
    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        return False

def install_update(filename):
    """Install the downloaded update"""
    system = platform.system().lower()
    
    try:
        if system == 'darwin':  # macOS
            print("📦 Installing macOS update...")
            print(f"Please run: open {filename}")
            print("Then drag DineSysPro.app to Applications folder")
            return True
            
        elif system == 'windows':  # Windows
            print("📦 Installing Windows update...")
            subprocess.Popen([filename])
            return True
            
        elif system == 'linux':  # Linux
            print("📦 Installing Linux update...")
            os.chmod(filename, 0o755)
            print(f"Please run: ./{filename}")
            return True
            
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        return False

def check_for_updates(silent=False):
    """Check for updates and return update info"""
    current_version = get_current_version()
    
    if not silent:
        print(f"🔍 Current version: {current_version}")
        print(f"🔍 Checking for updates...")
    
    release_data = get_latest_release()
    if not release_data:
        return None
    
    latest_version = release_data.get('tag_name', '').lstrip('v')
    
    if not silent:
        print(f"📦 Latest version: {latest_version}")
    
    if compare_versions(current_version, latest_version):
        return {
            'available': True,
            'current': current_version,
            'latest': latest_version,
            'release_notes': release_data.get('body', 'No release notes'),
            'download_url': get_download_url_for_platform(release_data),
            'release_data': release_data
        }
    else:
        if not silent:
            print("✅ You are running the latest version")
        return {
            'available': False,
            'current': current_version,
            'latest': latest_version
        }

def auto_update():
    """Automatic update process"""
    print("="*60)
    print("🔄 DineSysPro Auto-Updater")
    print("="*60)
    
    update_info = check_for_updates()
    
    if not update_info:
        print("❌ Could not check for updates")
        return False
    
    if not update_info['available']:
        print("✅ Already up to date!")
        return True
    
    print("\n" + "="*60)
    print(f"🆕 New version available: {update_info['latest']}")
    print("="*60)
    print("\n📝 Release Notes:")
    print(update_info['release_notes'])
    print("\n" + "="*60)
    
    download_url = update_info['download_url']
    if not download_url:
        print("❌ No download available for your platform")
        return False
    
    # Ask user for confirmation
    response = input("\n❓ Do you want to download and install the update? (y/n): ")
    if response.lower() != 'y':
        print("⏭️  Update skipped")
        return False
    
    # Download update
    filename = download_url.split('/')[-1]
    if download_update(download_url, filename):
        print("\n✅ Update downloaded successfully!")
        
        # Install update
        if install_update(filename):
            print("\n✅ Update installed successfully!")
            print("🔄 Please restart the application")
            return True
    
    return False

if __name__ == "__main__":
    auto_update()

