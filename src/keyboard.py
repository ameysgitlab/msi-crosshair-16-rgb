# src/keyboard.py
# MSI Katana 15 B12V (MS-1565) Keyboard RGB Communication Layer
# Based on reverse-engineered protocol by natanalt
# https://gist.github.com/natanalt/06f1d5854230c788b9b9e7e33ab90b9f

"""
Low-level communication with MSI Katana keyboard RGB controller.
Handles HID feature reports to configure the Mystic Light controller.
"""

import struct
from typing import Optional

try:
    import hid
except ImportError:
    raise ImportError(
        "hidapi not found. Install with: pip install hidapi --break-system-packages"
    )


# MSI Katana 15 B12V keyboard identifiers
VENDOR_ID = 0x1462
PRODUCT_ID = 0x1601

# Packet structure constants
REPORT_ID_WRITE = 2
REPORT_ID_READ = 1
PACKET_SIZE = 64

# Packet IDs for different operations
PACKET_SELECT_ZONES = 1
PACKET_SET_EFFECT = 2
PACKET_LOAD_FLASH = 176  # 0xB0
PACKET_SAVE_FLASH = 160  # 0xA0

# Animation types
EFFECT_DISABLE = 0
EFFECT_STEADY = 1
EFFECT_BREATH = 2
EFFECT_COLOR_CYCLE = 3
EFFECT_COLOR_WAVE = 4

# Wave directions
WAVE_RIGHT_TO_LEFT = 0
WAVE_LEFT_TO_RIGHT = 1

# Zone bitmasks (bits 0-3 map to zones left to right)
ZONE_ALL = 0b1111
ZONE_1 = 0b0001  # leftmost
ZONE_2 = 0b0010
ZONE_3 = 0b0100
ZONE_4 = 0b1000  # rightmost


class MSIKeyboardRGB:
    """
    Handles communication with the MSI Katana keyboard RGB controller.
    
    Uses HID feature reports to send configuration packets to the
    keyboard's Mystic Light microcontroller.
    """

    def __init__(self, vendor_id: int = VENDOR_ID, product_id: int = PRODUCT_ID):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.device: Optional[hid.device] = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self):
        """Open connection to the keyboard HID device."""
        self.device = hid.device()
        try:
            self.device.open(self.vendor_id, self.product_id)
            self.device.set_nonblocking(True)
        except OSError as e:
            raise ConnectionError(
                f"Failed to open keyboard device (VID={hex(self.vendor_id)}, "
                f"PID={hex(self.product_id)}). Make sure you're running as root "
                f"or have proper udev rules installed. Error: {e}"
            )

    def close(self):
        """Close the HID device connection."""
        if self.device:
            self.device.close()
            self.device = None

    def _send_packet(self, packet_id: int, payload: bytes = b""):
        """Send a feature report packet to the keyboard."""
        # Build the packet: report_id + packet_id + payload + zero padding
        packet = bytes([REPORT_ID_WRITE, packet_id]) + payload
        packet = packet.ljust(PACKET_SIZE, b"\x00")

        # Send as feature report
        self.device.send_feature_report(packet)

        # Read response (may be necessary for some operations)
        try:
            self.device.get_feature_report(REPORT_ID_READ, PACKET_SIZE)
        except:
            pass  # Some operations don't require a read

    def select_zones(self, zone_mask: int):
        """Select which zones will be affected by the next effect configuration."""
        self._send_packet(PACKET_SELECT_ZONES, bytes([zone_mask]))

    def set_effect(
        self,
        effect_type: int,
        colors: list[tuple[int, int, int]],
        speed_seconds: float = 3.0,
        wave_direction: int = WAVE_LEFT_TO_RIGHT,
    ):
        """
        Configure the lighting effect for currently selected zones.

        Args:
            effect_type: One of EFFECT_* constants
            colors: List of (r, g, b) tuples (0-255 each)
            speed_seconds: Animation cycle duration (for animated effects)
            wave_direction: WAVE_LEFT_TO_RIGHT or WAVE_RIGHT_TO_LEFT
        """
        # Convert speed to the internal format (seconds * 100)
        speed_value = int(speed_seconds * 100)

        # Build the effect configuration payload
        payload = bytearray()

        # Animation type
        payload.append(effect_type)

        # Animation speed (u16 little endian)
        payload.extend(struct.pack("<H", speed_value))

        # Unused bytes (constant based on protocol docs)
        payload.extend([0, 0, 15, 1])

        # Wave direction
        payload.append(wave_direction)

        # Color keyframes - distribute colors evenly across the animation
        num_colors = len(colors)
        for i, (r, g, b) in enumerate(colors):
            # Calculate time value (0 to 100, evenly spaced)
            if num_colors == 1:
                time_value = 0
            else:
                time_value = int((i * 100) / (num_colors - 1)) if num_colors > 1 else 0

            # Ensure last keyframe has time=100 for proper animation looping
            if i == num_colors - 1:
                time_value = 100

            payload.extend([time_value, r, g, b])

        self._send_packet(PACKET_SET_EFFECT, bytes(payload))

    def save_to_flash(self):
        """Save current configuration to flash (persists across reboots)."""
        self._send_packet(PACKET_SAVE_FLASH)

    def load_from_flash(self):
        """Load configuration from flash."""
        self._send_packet(PACKET_LOAD_FLASH)

    # ========================================================================
    # Convenience methods for common operations
    # ========================================================================

    def set_color(self, r: int, g: int, b: int, zones: int = ZONE_ALL, save: bool = True):
        """Set a solid color on specified zones."""
        self.select_zones(zones)
        self.set_effect(EFFECT_STEADY, [(r, g, b)])
        if save:
            self.save_to_flash()

    def turn_off(self, zones: int = ZONE_ALL, save: bool = True):
        """Turn off the LEDs on specified zones."""
        self.select_zones(zones)
        self.set_effect(EFFECT_DISABLE, [(0, 0, 0)])
        if save:
            self.save_to_flash()

    def set_breath(
        self,
        colors: list[tuple[int, int, int]],
        speed: float = 3.0,
        zones: int = ZONE_ALL,
        save: bool = True,
    ):
        """Set breathing effect with one or more colors."""
        self.select_zones(zones)
        self.set_effect(EFFECT_BREATH, colors, speed)
        if save:
            self.save_to_flash()

    def set_color_cycle(
        self,
        colors: list[tuple[int, int, int]],
        speed: float = 5.0,
        zones: int = ZONE_ALL,
        save: bool = True,
    ):
        """Set color cycling effect."""
        self.select_zones(zones)
        self.set_effect(EFFECT_COLOR_CYCLE, colors, speed)
        if save:
            self.save_to_flash()

    def set_wave(
        self,
        colors: list[tuple[int, int, int]],
        speed: float = 3.0,
        direction: int = WAVE_LEFT_TO_RIGHT,
        zones: int = ZONE_ALL,
        save: bool = True,
    ):
        """Set color wave effect across the keyboard."""
        self.select_zones(zones)
        self.set_effect(EFFECT_COLOR_WAVE, colors, speed, direction)
        if save:
            self.save_to_flash()
