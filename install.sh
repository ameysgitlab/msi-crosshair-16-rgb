#!/bin/bash
# install.sh - MSI Katana RGB Controller installer
# 
# Run with: sudo ./install.sh
#
# Author: sarpowsky (https://github.com/sarpowsky)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/opt/msi-katana-rgb"
BIN_LINK="/usr/local/bin/msi-katana-rgb"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No color

echo_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
echo_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
echo_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo_error "Please run as root: sudo ./install.sh"
    exit 1
fi

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════╗"
echo "║     MSI Katana RGB Controller Installer    ║"
echo "║         github.com/sarpowsky               ║"
echo "╚════════════════════════════════════════════╝"
echo -e "${NC}"

# Detect package manager and install dependencies
echo_info "Installing Python dependencies..."

if command -v pacman &> /dev/null; then
    # Arch-based (including CachyOS)
    echo_info "Detected Arch-based system"
    pacman -S --needed --noconfirm python python-pip python-pyqt6 python-hidapi 2>/dev/null || {
        echo_warn "Some packages may need manual installation via pip"
        pip install PyQt6 hidapi --break-system-packages 2>/dev/null || true
    }
elif command -v apt &> /dev/null; then
    # Debian/Ubuntu
    echo_info "Detected Debian-based system"
    apt update
    apt install -y python3 python3-pip python3-pyqt6 python3-hid || {
        pip install PyQt6 hidapi --break-system-packages 2>/dev/null || true
    }
elif command -v dnf &> /dev/null; then
    # Fedora
    echo_info "Detected Fedora-based system"
    dnf install -y python3 python3-pip python3-qt6 python3-hidapi || {
        pip install PyQt6 hidapi --break-system-packages 2>/dev/null || true
    }
elif command -v zypper &> /dev/null; then
    # openSUSE
    echo_info "Detected openSUSE-based system"
    zypper install -y python3 python3-pip python3-qt6 python3-hidapi || {
        pip install PyQt6 hidapi --break-system-packages 2>/dev/null || true
    }
else
    echo_warn "Unknown package manager. Installing via pip..."
    pip install PyQt6 hidapi --break-system-packages
fi

# Create installation directory
echo_info "Installing application to ${INSTALL_DIR}..."
mkdir -p "$INSTALL_DIR"
cp -r "$SCRIPT_DIR/src" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/msi-katana-rgb.py" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/msi-katana-rgb.py"

# Create symlink in PATH
echo_info "Creating executable link..."
cat > "$BIN_LINK" << 'EOF'
#!/bin/bash
python3 /opt/msi-katana-rgb/msi-katana-rgb.py "$@"
EOF
chmod +x "$BIN_LINK"

# Install udev rule
echo_info "Installing udev rule for non-root access..."
cp "$SCRIPT_DIR/99-msi-katana-rgb.rules" /etc/udev/rules.d/
udevadm control --reload-rules
udevadm trigger

# Install desktop entry
echo_info "Installing desktop entry..."
cp "$SCRIPT_DIR/msi-katana-rgb.desktop" /usr/share/applications/

echo
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         Installation complete!             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo
echo "You can now run the app in two ways:"
echo "  1. From terminal: msi-katana-rgb"
echo "  2. From your app menu: search 'MSI Katana RGB'"
echo
echo -e "${YELLOW}Note:${NC} You may need to log out and back in for the"
echo "      udev rules to take full effect (no sudo needed)."
echo
echo "To uninstall, run: sudo ./uninstall.sh"
echo
echo -e "Report issues at: ${BLUE}https://github.com/sarpowsky/msi-katana-rgb${NC}"
