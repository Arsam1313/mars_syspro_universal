#!/bin/bash

# DineSysPro Release Script
# این اسکریپت فرآیند release را خودکار می‌کند

set -e  # Exit on error

echo "======================================"
echo "🚀 DineSysPro Release Script"
echo "======================================"
echo ""

# رنگ‌ها
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# توابع کمکی
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# بررسی branch
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
    print_error "You must be on 'main' branch to release!"
    print_info "Current branch: $current_branch"
    exit 1
fi
print_success "On main branch"

# بررسی تغییرات uncommitted
if ! git diff-index --quiet HEAD --; then
    print_error "You have uncommitted changes!"
    print_info "Please commit or stash your changes first."
    exit 1
fi
print_success "No uncommitted changes"

# خواندن نسخه فعلی
current_version=$(python3 -c "import json; print(json.load(open('config.json'))['version'])")
print_info "Current version: $current_version"

# درخواست نسخه جدید
echo ""
echo "Enter new version (current: $current_version):"
read new_version

if [ -z "$new_version" ]; then
    print_error "Version cannot be empty!"
    exit 1
fi

# تایید
echo ""
print_warning "You are about to release version: $new_version"
echo "This will:"
echo "  1. Update config.json"
echo "  2. Update CHANGELOG.md"
echo "  3. Commit changes"
echo "  4. Create tag v$new_version"
echo "  5. Push to GitHub"
echo ""
echo "Continue? (y/n)"
read confirm

if [ "$confirm" != "y" ]; then
    print_info "Release cancelled"
    exit 0
fi

echo ""
print_info "Starting release process..."

# 1. به‌روزرسانی config.json
print_info "Updating config.json..."
python3 -c "
import json
with open('config.json', 'r') as f:
    config = json.load(f)
config['version'] = '$new_version'
with open('config.json', 'w') as f:
    json.dump(config, f, indent=2)
"
print_success "config.json updated"

# 2. به‌روزرسانی CHANGELOG.md
print_info "Updating CHANGELOG.md..."
today=$(date +%Y-%m-%d)
temp_file=$(mktemp)

# اضافه کردن نسخه جدید به ابتدای CHANGELOG
{
    head -n 10 CHANGELOG.md
    echo ""
    echo "## [$new_version] - $today"
    echo ""
    echo "### Added"
    echo "- New features"
    echo ""
    echo "### Fixed"
    echo "- Bug fixes"
    echo ""
    echo "### Changed"
    echo "- Improvements"
    echo ""
    tail -n +11 CHANGELOG.md
} > "$temp_file"

mv "$temp_file" CHANGELOG.md
print_success "CHANGELOG.md updated"

# 3. باز کردن CHANGELOG برای ویرایش
print_warning "Opening CHANGELOG.md for editing..."
print_info "Please update the release notes, then save and close the file."
echo "Press Enter to continue..."
read

# باز کردن با ویرایشگر پیش‌فرض
${EDITOR:-nano} CHANGELOG.md

# 4. Commit تغییرات
print_info "Committing changes..."
git add config.json CHANGELOG.md
git commit -m "Release v$new_version

- Update version to $new_version
- Update CHANGELOG.md with release notes"
print_success "Changes committed"

# 5. ایجاد tag
print_info "Creating tag v$new_version..."
git tag -a "v$new_version" -m "Release v$new_version"
print_success "Tag created"

# 6. Push به GitHub
print_info "Pushing to GitHub..."
git push origin main
git push origin "v$new_version"
print_success "Pushed to GitHub"

# 7. اطلاعات بعدی
echo ""
echo "======================================"
print_success "Release v$new_version completed!"
echo "======================================"
echo ""
print_info "Next steps:"
echo ""
echo "1️⃣  Build applications:"
echo "   macOS:   python3 build_macos.py"
echo "   Windows: python build_windows.py (on Windows)"
echo ""
echo "2️⃣  Create GitHub Release:"
echo "   https://github.com/Arsam1313/mars_syspro_universal/releases/new"
echo "   - Tag: v$new_version"
echo "   - Upload: dist/*.dmg and dist/*.exe"
echo ""
echo "3️⃣  Or use GitHub CLI:"
echo "   gh release create v$new_version \\"
echo "     --title \"DineSysPro v$new_version\" \\"
echo "     --notes-file RELEASE_NOTES.md \\"
echo "     dist/*.dmg dist/*.exe"
echo ""
echo "4️⃣  GitHub Actions will automatically build (if configured)"
echo "   Check: https://github.com/Arsam1313/mars_syspro_universal/actions"
echo ""
print_success "Done! 🎉"

