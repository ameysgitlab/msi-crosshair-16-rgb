# Contributing to MSI Katana RGB Controller

Thank you for your interest in contributing! 🎉

## How to Contribute

### Reporting Bugs

1. Check if the issue already exists
2. Include your MSI laptop model and `lsusb | grep 1462` output
3. Describe steps to reproduce the bug
4. Include any error messages

### Testing on Other Devices

If you have a different MSI laptop with a 4-zone RGB keyboard:

1. Run `lsusb | grep 1462` to get your VID:PID
2. Try the app - it might just work!
3. Report your results (working or not) as an issue

### Submitting Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes with clear commit messages
4. Test your changes
5. Submit a pull request

### Code Style

- Follow PEP 8 for Python code
- Add docstrings to functions and classes
- Keep commits atomic and well-described

## Development Setup

```bash
git clone https://github.com/sarpowsky/msi-katana-rgb.git
cd msi-katana-rgb
pip install PyQt6 hidapi --break-system-packages
python3 msi-katana-rgb.py
```

## Questions?

Feel free to open an issue for any questions!
