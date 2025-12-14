# MSI Katana RGB Controller

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Linux-blue?style=flat-square&logo=linux" alt="Linux">
  <img src="https://img.shields.io/badge/Python-3.10+-green?style=flat-square&logo=python" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="MIT License">
  <img src="https://img.shields.io/badge/GUI-PyQt6-orange?style=flat-square&logo=qt" alt="PyQt6">
</p>

A Linux GUI application for controlling the 4-zone RGB keyboard on MSI Katana 15 B12V laptops.

## ✨ Features

- 🎨 **Color picker** for each of the 4 keyboard zones
- 🌈 **Multiple effects**: Steady, Breathing, Color Cycle, Wave
- ⚡ **Quick presets**: All Red, Green, Blue, White, Rainbow
- 💾 **Save to flash**: Settings persist across reboots
- 🔓 **No root required** after installing udev rules
- 🖥️ **Native look**: Uses Fusion theme, integrates with your DE

## 📋 Supported Devices

| Device | Model Code | Status |
|--------|------------|--------|
| MSI Katana 15 B12V | MS-1565 | ✅ Tested |
| MSI Katana 15 B12VEK | MS-1565 | ✅ Should work |
| MSI Katana 15 B12VFK | MS-1565 | ✅ Should work |
| MSI Katana 15 B12VGK | MS-1565 | ✅ Should work |

Other MSI laptops with 4-zone RGB keyboards *may* work if they use the same Mystic Light controller (VID: 0x1462, PID: 0x1601).

## 🚀 Installation

### Quick Install (Recommended)

```bash
git clone https://github.com/sarpowsky/msi-katana-rgb.git
cd msi-katana-rgb
sudo ./install.sh
```

The installer automatically:
- Detects your package manager (pacman, apt, dnf, zypper)
- Installs Python dependencies
- Sets up udev rules for non-root access
- Adds the app to your application menu

**After installation, log out and back in** for udev rules to take effect.

### Manual Installation

1. **Install dependencies:**

```bash
# Arch/CachyOS/Manjaro
sudo pacman -S python python-pyqt6 python-hidapi

# Debian/Ubuntu
sudo apt install python3 python3-pyqt6 python3-hid

# Fedora
sudo dnf install python3 python3-qt6 python3-hidapi

# Or via pip (any distro)
pip install PyQt6 hidapi --break-system-packages
```

2. **Install udev rule (for non-root access):**

```bash
sudo cp 99-msi-katana-rgb.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```

3. **Log out and back in**, then run:

```bash
python3 msi-katana-rgb.py
```

## 🎮 Usage

### GUI Application

After installation:
- **From terminal:** `msi-katana-rgb`
- **From app menu:** Search "MSI Katana RGB"

### Controls

| Control | Description |
|---------|-------------|
| Zone buttons | Click to pick a color for each zone |
| Apply checkbox | Select which zones to modify |
| Effect dropdown | Choose lighting effect |
| Speed slider | Adjust animation speed (1-12 seconds) |
| Wave Direction | Set wave direction (for wave effect) |
| Apply (Temporary) | Apply without saving (resets on reboot) |
| Apply & Save | Apply and save to flash (persists) |
| Turn Off | Turn off all LEDs |

### Effects

- **Steady**: Solid color on each zone
- **Breathing**: Fades in and out between colors
- **Color Cycle**: Smooth interpolation between colors
- **Wave**: Creates synchronized wave effect across keyboard

## 🔧 Troubleshooting

### "Failed to connect to keyboard"

1. Verify udev rules are installed:
   ```bash
   ls -la /etc/udev/rules.d/ | grep msi
   ```

2. Check if the device exists:
   ```bash
   cat /sys/class/hidraw/hidraw*/device/uevent | grep 1462
   ```

3. As a fallback, run with sudo:
   ```bash
   sudo msi-katana-rgb
   ```

### Device not detected

Your keyboard might have a different Product ID. Check with:

```bash
lsusb | grep 1462
# or
sudo dmesg | grep -i "1462"
```

If your PID differs from `0x1601`, please [open an issue](https://github.com/sarpowsky/msi-katana-rgb/issues).

### Keyboard doesn't respond

Try power cycling:
1. Save your settings
2. Close the app
3. Suspend and resume your laptop
4. Re-apply settings

## 🗑️ Uninstallation

```bash
sudo ./uninstall.sh
```

## 📁 Project Structure

```
msi-katana-rgb/
├── src/
│   ├── __init__.py       # Package exports
│   ├── keyboard.py       # HID communication backend
│   └── gui.py            # PyQt6 GUI application
├── msi-katana-rgb.py     # Main entry point
├── install.sh            # Installation script
├── uninstall.sh          # Uninstallation script
├── 99-msi-katana-rgb.rules  # Udev rules
├── msi-katana-rgb.desktop   # Desktop entry
├── LICENSE               # MIT License
└── README.md             # This file
```

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features  
- Submit pull requests
- Test on other MSI laptop models

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

## 👏 Credits

| Contributor | Role |
|------------|------|
| [**sarpowsky**](https://github.com/sarpowsky) | Developer, maintainer |
| [**natanalt**](https://gist.github.com/natanalt/06f1d5854230c788b9b9e7e33ab90b9f) | Protocol reverse engineering |

### Acknowledgments

- Inspired by [MSIKLM](https://github.com/Gibtnix/MSIKLM), [msi-perkeyrgb](https://github.com/Askannz/msi-perkeyrgb), and [MControlCenter](https://github.com/dmitry-s93/MControlCenter)
- Thanks to the Linux MSI community for testing and feedback

---

<p align="center">
  Made with ❤️ for the Linux community
  <br>
  <a href="https://github.com/sarpowsky/msi-katana-rgb">⭐ Star on GitHub</a>
</p>
