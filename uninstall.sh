#!/bin/bash
# uninstall.sh - MSI Katana RGB Controller uninstaller
#
# Run with: sudo ./uninstall.sh
#
# Author: sarpowsky (https://github.com/sarpowsky)

set -e

INSTALL_DIR="/opt/msi-katana-rgb"
BIN_LINK="/usr/local/bin/msi-katana-rgb"
UDEV_RULE="/etc/udev/rules.d/99-msi-katana-rgb.rules"
DESKTOP_FILE="/usr/share/applications/msi-katana-rgb.desktop"

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo_info() { echo -e "${GREEN}[INFO]${NC} $1"; }

if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[ERROR]${NC} Please run as root: sudo ./uninstall.sh"
    exit 1
fi

echo -e "${BLUE}Uninstalling MSI Katana RGB Controller...${NC}"
echo

[ -d "$INSTALL_DIR" ] && rm -rf "$INSTALL_DIR" && echo_info "Removed $INSTALL_DIR"
[ -f "$BIN_LINK" ] && rm -f "$BIN_LINK" && echo_info "Removed $BIN_LINK"
[ -f "$UDEV_RULE" ] && rm -f "$UDEV_RULE" && echo_info "Removed $UDEV_RULE"
[ -f "$DESKTOP_FILE" ] && rm -f "$DESKTOP_FILE" && echo_info "Removed $DESKTOP_FILE"

udevadm control --reload-rules 2>/dev/null || true

echo
echo -e "${GREEN}Uninstall complete!${NC}"
echo
echo "Thank you for using MSI Katana RGB Controller."
echo -e "Feedback welcome at: ${BLUE}https://github.com/sarpowsky/msi-katana-rgb${NC}"
