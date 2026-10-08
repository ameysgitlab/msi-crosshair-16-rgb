#!/usr/bin/env python3
# msi-crosshair-16-rgb
# Main entry point for MSI Crosshair 16 RGB Controller

"""
MSI Crosshair 16 RGB Controller
A Linux GUI application for controlling the 4-zone RGB keyboard 
on MSI Crosshair 16 15 B12V laptops.

Author: sarpowsky (https://github.com/sarpowsky)
License: MIT
"""

import sys
import os

# Add src to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def check_dependencies():
    """Check if required dependencies are installed."""
    missing = []
    
    try:
        import hid
    except ImportError:
        missing.append("hidapi (pip install hidapi --break-system-packages)")
    
    try:
        from PyQt6.QtWidgets import QApplication
    except ImportError:
        missing.append("PyQt6 (pip install PyQt6 --break-system-packages)")
    
    if missing:
        print("Error: Missing dependencies:")
        for dep in missing:
            print(f"  - {dep}")
        print("\nOn Arch/CachyOS, you can also install via pacman:")
        print("  sudo pacman -S python-pyqt6 python-hidapi")
        sys.exit(1)


def main():
    check_dependencies()
    
    from src.gui import run_gui
    run_gui()


if __name__ == "__main__":
    main()
