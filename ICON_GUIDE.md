# 🍕 DineSysPro Icon Guide

## How to Create a Custom App Icon

### Option 1: Online Converter (Easiest)

1. **Create or find a PNG image** (1024x1024 pixels recommended)
   - Use a pizza emoji 🍕
   - Or create a custom logo with your restaurant branding

2. **Convert to .icns format:**
   - Visit: https://cloudconvert.com/png-to-icns
   - Or: https://www.img2icnsconverter.com/
   - Upload your PNG image
   - Download the generated `icon.icns` file

3. **Add to project:**
   - Save the `icon.icns` file in this directory
   - Run: `python3 build_app.py`

### Option 2: Using macOS Command Line

```bash
# 1. Create a 1024x1024 PNG image named "icon.png"

# 2. Create iconset directory
mkdir icon.iconset

# 3. Generate different sizes
sips -z 16 16     icon.png --out icon.iconset/icon_16x16.png
sips -z 32 32     icon.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32     icon.png --out icon.iconset/icon_32x32.png
sips -z 64 64     icon.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128   icon.png --out icon.iconset/icon_128x128.png
sips -z 256 256   icon.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256   icon.png --out icon.iconset/icon_256x256.png
sips -z 512 512   icon.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512   icon.png --out icon.iconset/icon_512x512.png
sips -z 1024 1024 icon.png --out icon.iconset/icon_512x512@2x.png

# 4. Convert to .icns
iconutil -c icns icon.iconset

# 5. Clean up
rm -rf icon.iconset
```

### Option 3: Quick Emoji Icon

For a quick solution, you can use an emoji as the icon:

```bash
# Install ImageMagick (if not installed)
brew install imagemagick

# Create icon from emoji
convert -background none -fill "#FF6B35" -font "Apple Color Emoji" \
        -pointsize 512 label:"🍕" -resize 1024x1024 icon.png

# Then convert to .icns using Option 2
```

## Building the App

Once you have `icon.icns`:

```bash
# Install PyInstaller
pip3 install pyinstaller

# Build the app
python3 build_app.py

# The app will be created at: dist/DineSysPro.app
```

## Installing the App

```bash
# Copy to Applications folder
cp -r dist/DineSysPro.app /Applications/

# Or just double-click DineSysPro.app to run
```

## Current Status

✅ App title: 🍕 DineSysPro  
⚠️ App icon: Default (needs icon.icns file)  

To add a custom icon, follow the steps above and rebuild the app.

