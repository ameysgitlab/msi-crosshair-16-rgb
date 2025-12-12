# src/gui.py
# MSI Katana RGB Controller - GUI Module

"""
PyQt6-based graphical user interface for the MSI Katana RGB controller.
Provides an intuitive way to configure keyboard lighting.
"""

import sys
from typing import Callable

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QComboBox, QSlider, QGroupBox,
    QColorDialog, QMessageBox, QCheckBox, QFrame, QDialog, QTextBrowser
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QAction

from .keyboard import (
    MSIKeyboardRGB,
    EFFECT_DISABLE, EFFECT_STEADY, EFFECT_BREATH, EFFECT_COLOR_CYCLE, EFFECT_COLOR_WAVE,
    WAVE_LEFT_TO_RIGHT, WAVE_RIGHT_TO_LEFT,
    ZONE_ALL, ZONE_1, ZONE_2, ZONE_3, ZONE_4
)


__version__ = "1.0.0"


class ColorButton(QPushButton):
    """A button that displays and allows selecting a color."""

    def __init__(self, initial_color: QColor = QColor(255, 0, 0)):
        super().__init__()
        self._color = initial_color
        self.setFixedSize(60, 40)
        self.clicked.connect(self._pick_color)
        self._update_style()

    def _update_style(self):
        """Update button appearance to show current color."""
        # Calculate contrasting text color for readability
        luminance = (
            0.299 * self._color.red() + 
            0.587 * self._color.green() + 
            0.114 * self._color.blue()
        ) / 255
        text_color = "#000000" if luminance > 0.5 else "#ffffff"
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._color.name()};
                color: {text_color};
                border: 2px solid #555;
                border-radius: 5px;
                font-weight: bold;
                font-size: 10px;
            }}
            QPushButton:hover {{
                border: 2px solid #888;
            }}
        """)
        self.setText(self._color.name().upper())

    def _pick_color(self):
        """Open color picker dialog."""
        color = QColorDialog.getColor(self._color, self, "Select Zone Color")
        if color.isValid():
            self._color = color
            self._update_style()

    def color(self) -> QColor:
        return self._color

    def set_color(self, color: QColor):
        self._color = color
        self._update_style()

    def rgb(self) -> tuple[int, int, int]:
        return (self._color.red(), self._color.green(), self._color.blue())


class ZoneWidget(QFrame):
    """Widget representing a single keyboard zone."""

    def __init__(self, zone_name: str, zone_number: int):
        super().__init__()
        self.zone_number = zone_number
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(1)

        layout = QVBoxLayout(self)
        layout.setSpacing(5)

        # Zone label
        label = QLabel(zone_name)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label)

        # Color button
        self.color_btn = ColorButton()
        layout.addWidget(self.color_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Enable checkbox
        self.enabled_cb = QCheckBox("Apply")
        self.enabled_cb.setChecked(True)
        layout.addWidget(self.enabled_cb, alignment=Qt.AlignmentFlag.AlignCenter)

    def is_enabled(self) -> bool:
        return self.enabled_cb.isChecked()

    def rgb(self) -> tuple[int, int, int]:
        return self.color_btn.rgb()

    def set_color(self, r: int, g: int, b: int):
        self.color_btn.set_color(QColor(r, g, b))


class AboutDialog(QDialog):
    """About dialog showing credits and information."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About MSI Katana RGB")
        self.setFixedSize(420, 320)

        layout = QVBoxLayout(self)

        # App info
        info_text = """
        <h2 style="text-align: center;">MSI Katana RGB Controller</h2>
        <p style="text-align: center;">Version 1.0.0</p>
        <hr>
        <p>A Linux GUI application for controlling the 4-zone RGB keyboard 
        on MSI Katana 15 B12V laptops.</p>
        
        <h3>Credits</h3>
        <ul>
            <li><b>Developer:</b> <a href="https://github.com/sarpowsky">sarpowsky</a></li>
            <li><b>Protocol RE:</b> <a href="https://gist.github.com/natanalt/06f1d5854230c788b9b9e7e33ab90b9f">natanalt</a></li>
        </ul>
        
        <h3>License</h3>
        <p>MIT License - Free and Open Source</p>
        
        <p style="text-align: center; margin-top: 15px;">
            <a href="https://github.com/sarpowsky/msi-katana-rgb">GitHub Repository</a>
        </p>
        """
        
        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)
        text_browser.setHtml(info_text)
        layout.addWidget(text_browser)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MSI Katana RGB Controller")
        self.setMinimumSize(520, 450)

        self._setup_menubar()
        self._setup_ui()

    def _setup_menubar(self):
        """Set up the menu bar."""
        menubar = self.menuBar()

        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_ui(self):
        """Set up the main user interface."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Keyboard zones section
        zones_group = QGroupBox("Keyboard Zones (Left → Right)")
        zones_layout = QHBoxLayout(zones_group)

        self.zones = []
        zone_names = ["Zone 1", "Zone 2", "Zone 3", "Zone 4"]
        default_colors = [
            (255, 0, 0),    # red
            (0, 255, 0),    # green
            (0, 0, 255),    # blue
            (255, 255, 0),  # yellow
        ]

        for i, (name, color) in enumerate(zip(zone_names, default_colors)):
            zone = ZoneWidget(name, i + 1)
            zone.set_color(*color)
            self.zones.append(zone)
            zones_layout.addWidget(zone)

        main_layout.addWidget(zones_group)

        # Quick actions row
        quick_group = QGroupBox("Quick Presets")
        quick_layout = QHBoxLayout(quick_group)

        presets = [
            ("All Red", (255, 0, 0)),
            ("All Green", (0, 255, 0)),
            ("All Blue", (0, 0, 255)),
            ("All White", (255, 255, 255)),
            ("Rainbow", None),  # special case
        ]

        for name, color in presets:
            btn = QPushButton(name)
            if color:
                btn.clicked.connect(lambda checked, c=color: self._set_all_zones(c))
            else:
                btn.clicked.connect(self._set_rainbow)
            quick_layout.addWidget(btn)

        main_layout.addWidget(quick_group)

        # Effect settings
        effect_group = QGroupBox("Effect Settings")
        effect_layout = QGridLayout(effect_group)

        # Effect type
        effect_layout.addWidget(QLabel("Effect:"), 0, 0)
        self.effect_combo = QComboBox()
        self.effect_combo.addItems(["Steady", "Breathing", "Color Cycle", "Wave", "Off"])
        self.effect_combo.currentIndexChanged.connect(self._on_effect_changed)
        effect_layout.addWidget(self.effect_combo, 0, 1)

        # Speed slider
        effect_layout.addWidget(QLabel("Speed:"), 1, 0)
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(10, 120)  # 1.0s to 12.0s (in tenths)
        self.speed_slider.setValue(30)  # 3.0s default
        self.speed_slider.valueChanged.connect(self._update_speed_label)
        effect_layout.addWidget(self.speed_slider, 1, 1)

        self.speed_label = QLabel("3.0s")
        self.speed_label.setFixedWidth(40)
        effect_layout.addWidget(self.speed_label, 1, 2)

        # Wave direction
        effect_layout.addWidget(QLabel("Wave Direction:"), 2, 0)
        self.wave_combo = QComboBox()
        self.wave_combo.addItems(["Left → Right", "Right → Left"])
        effect_layout.addWidget(self.wave_combo, 2, 1)

        main_layout.addWidget(effect_group)

        # Apply buttons
        buttons_layout = QHBoxLayout()

        self.apply_btn = QPushButton("Apply (Temporary)")
        self.apply_btn.setToolTip("Apply without saving - will reset on reboot")
        self.apply_btn.clicked.connect(lambda: self._apply_settings(save=False))
        buttons_layout.addWidget(self.apply_btn)

        self.save_btn = QPushButton("Apply && Save")
        self.save_btn.setToolTip("Apply and save to flash - persists after reboot")
        self.save_btn.setStyleSheet("font-weight: bold;")
        self.save_btn.clicked.connect(lambda: self._apply_settings(save=True))
        buttons_layout.addWidget(self.save_btn)

        self.off_btn = QPushButton("Turn Off")
        self.off_btn.clicked.connect(self._turn_off)
        buttons_layout.addWidget(self.off_btn)

        main_layout.addLayout(buttons_layout)

        # Status bar
        self.statusBar().showMessage("Ready - Remember to run as root (sudo) or install udev rules")

        # Initial UI state
        self._on_effect_changed()

    def _update_speed_label(self, value: int):
        """Update speed label when slider changes."""
        self.speed_label.setText(f"{value / 10:.1f}s")

    def _on_effect_changed(self):
        """Enable/disable controls based on selected effect."""
        effect = self.effect_combo.currentIndex()
        # Speed is relevant for animated effects (breath, cycle, wave)
        animated = effect in [1, 2, 3]
        self.speed_slider.setEnabled(animated)
        self.speed_label.setEnabled(animated)
        # Wave direction only for wave effect
        self.wave_combo.setEnabled(effect == 3)

    def _set_all_zones(self, color: tuple[int, int, int]):
        """Set all zones to the same color."""
        for zone in self.zones:
            zone.set_color(*color)

    def _set_rainbow(self):
        """Set zones to rainbow colors."""
        colors = [
            (255, 0, 0),
            (255, 165, 0),
            (0, 255, 0),
            (0, 0, 255),
        ]
        for zone, color in zip(self.zones, colors):
            zone.set_color(*color)

    def _get_enabled_zones_mask(self) -> int:
        """Get bitmask of enabled zones."""
        mask = 0
        for i, zone in enumerate(self.zones):
            if zone.is_enabled():
                mask |= (1 << i)
        return mask

    def _get_colors(self) -> list[tuple[int, int, int]]:
        """Get colors from enabled zones."""
        colors = []
        for zone in self.zones:
            if zone.is_enabled():
                colors.append(zone.rgb())
        return colors if colors else [(0, 0, 0)]

    def _apply_settings(self, save: bool = True):
        """Apply current settings to keyboard."""
        try:
            with MSIKeyboardRGB() as kb:
                zone_mask = self._get_enabled_zones_mask()
                if zone_mask == 0:
                    self.statusBar().showMessage("No zones selected!")
                    return

                effect_map = {
                    0: EFFECT_STEADY,
                    1: EFFECT_BREATH,
                    2: EFFECT_COLOR_CYCLE,
                    3: EFFECT_COLOR_WAVE,
                    4: EFFECT_DISABLE,
                }
                effect = effect_map[self.effect_combo.currentIndex()]
                speed = self.speed_slider.value() / 10.0
                direction = (
                    WAVE_RIGHT_TO_LEFT 
                    if self.wave_combo.currentIndex() == 1 
                    else WAVE_LEFT_TO_RIGHT
                )

                colors = self._get_colors()

                # For steady effect, apply each zone individually with its color
                if effect == EFFECT_STEADY:
                    for i, zone in enumerate(self.zones):
                        if zone.is_enabled():
                            kb.select_zones(1 << i)
                            kb.set_effect(EFFECT_STEADY, [zone.rgb()])
                else:
                    # For animated effects, select all enabled zones and apply
                    kb.select_zones(zone_mask)
                    kb.set_effect(effect, colors, speed, direction)

                if save:
                    kb.save_to_flash()
                    self.statusBar().showMessage("Settings applied and saved to flash!")
                else:
                    self.statusBar().showMessage(
                        "Settings applied (not saved - will reset on reboot)"
                    )

        except ConnectionError as e:
            QMessageBox.critical(
                self,
                "Connection Error",
                f"Failed to connect to keyboard:\n\n{e}\n\n"
                "Make sure you're running as root (sudo) or have udev rules installed."
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred:\n\n{e}")

    def _turn_off(self):
        """Turn off all keyboard LEDs."""
        try:
            with MSIKeyboardRGB() as kb:
                kb.select_zones(ZONE_ALL)
                kb.set_effect(EFFECT_DISABLE, [(0, 0, 0)])
                kb.save_to_flash()
                self.statusBar().showMessage("Keyboard LEDs turned off")
        except ConnectionError as e:
            QMessageBox.critical(
                self,
                "Connection Error",
                f"Failed to connect to keyboard:\n\n{e}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred:\n\n{e}")

    def _show_about(self):
        """Show the about dialog."""
        dialog = AboutDialog(self)
        dialog.exec()


def run_gui():
    """Entry point for the GUI application."""
    import os
    if os.geteuid() != 0:
        print("Warning: Not running as root. You may encounter permission errors.")
        print("Consider running with: sudo msi-katana-rgb")
        print("Or install the udev rules for non-root access.")

    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Consistent look across different DEs
    app.setApplicationName("MSI Katana RGB")
    app.setApplicationVersion(__version__)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
