# src/__init__.py
# MSI Katana RGB Controller

from .keyboard import (
    MSIKeyboardRGB,
    EFFECT_DISABLE,
    EFFECT_STEADY,
    EFFECT_BREATH,
    EFFECT_COLOR_CYCLE,
    EFFECT_COLOR_WAVE,
    WAVE_LEFT_TO_RIGHT,
    WAVE_RIGHT_TO_LEFT,
    ZONE_ALL,
    ZONE_1,
    ZONE_2,
    ZONE_3,
    ZONE_4,
)

__version__ = "1.0.0"
__author__ = "sarpowsky"
__github__ = "https://github.com/sarpowsky"
__repo__ = "https://github.com/sarpowsky/msi-katana-rgb"
