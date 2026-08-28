#!/usr/bin/python3
# -*- coding: utf-8 -*-
# GIGBOX Hardware Wiring Configuration - FINAL (I2S-Safe)
# SPOOKI INSTRUMENTS - GIGBOX
# Raspberry Pi 5 GPIO pin assignments for GIGBOX hardware
# 18 GPIO inputs: 3 encoder + 5 navigation + 10 buttons
# NO potentiometer, NO softpot, NO ADC requirement
# I2S (GPIO 18,19,20,21) kept FREE for PCM DAC

import os
import logging

# ==============================================================================
# VALIDATED GPIO PIN ASSIGNMENTS (BCM numbering) - Raspberry Pi 5
# ==============================================================================
# Verified against Pi 5 GPIO availability, Zynthian peripheral usage,
# I2C/SPI/UART reservations, audio/display requirements
# I2S pins (18,19,20,21) EXPLICITLY RESERVED for PCM DAC

# Main Rotary Encoder (3 GPIOs) - SAFE pins
ENCODER_A_PIN = 5       # BCM 5  → Physical Pin 29 - Encoder Channel A (SAFE)
ENCODER_B_PIN = 6       # BCM 6  → Physical Pin 31 - Encoder Channel B (SAFE)
ENCODER_SW_PIN = 13     # BCM 13 → Physical Pin 33 - Encoder Push Switch (PWM1 - acceptable, no PWM audio)

# Navigation Module - 5-way (5 GPIOs) - All SAFE
NAV_UP_PIN = 17         # BCM 17 → Physical Pin 11 - Navigation UP (SAFE)
NAV_DOWN_PIN = 27       # BCM 27 → Physical Pin 13 - Navigation DOWN (SAFE)
NAV_LEFT_PIN = 22       # BCM 22 → Physical Pin 15 - Navigation LEFT (SAFE)
NAV_RIGHT_PIN = 23      # BCM 23 → Physical Pin 16 - Navigation RIGHT (SAFE)
NAV_CLICK_PIN = 24      # BCM 24 → Physical Pin 18 - Navigation CLICK (SAFE)

# 10 Tactile Buttons (10 GPIOs) - Using SPI0/PWM pins (acceptable conflicts)
# SPI0 (GPIO 7,8,9,10,11) free on Pi 5 40-pin header (boot SPI is separate)
# PWM (GPIO 12,13) acceptable - USB DAC used, not PWM audio
# I2C1_SDA (GPIO 4) acceptable - no I2C1 devices on header
BUTTON_PINS = [
    16,   # Button 1 → BCM 16 → Physical Pin 36 (SAFE)
    7,    # Button 2 → BCM 7  → Physical Pin 26 (SPI0_CE1 - acceptable)
    8,    # Button 3 → BCM 8  → Physical Pin 24 (SPI0_CE0 - acceptable)
    9,    # Button 4 → BCM 9  → Physical Pin 21 (SPI0_MISO - acceptable)
    25,   # Button 5 → BCM 25 → Physical Pin 22 (SAFE)
    26,   # Button 6 → BCM 26 → Physical Pin 37 (SAFE)
    12,   # Button 7 → BCM 12 → Physical Pin 32 (PWM0 - acceptable, USB DAC used)
    4,    # Button 8 → BCM 4  → Physical Pin 7  (I2C1_SDA alt - acceptable, no I2C1 devices)
    10,   # Button 9 → BCM 10 → Physical Pin 19 (SPI0_MOSI - acceptable)
    11,   # Button 10 → BCM 11 → Physical Pin 23 (SPI0_SCLK - acceptable)
]

# ==============================================================================
# EXPLICITLY RESERVED - I2S FOR PCM DAC
# ==============================================================================
# I2S_PINS = {18, 19, 20, 21}  # DO NOT USE - Reserved for PCM DAC (L/R Main Out)
# POTENTIOMETER: REMOVED COMPLETELY - No ADC, no GPIO assignment
# SOFTPOT: REMOVED COMPLETELY - No ADC, no GPIO assignment

# ==============================================================================
# Audio Hardware
# ==============================================================================
PCM_DAC_I2S = True            # PCM DAC via I2S (GPIO 18,19,20,21 - KEPT FREE)
USB_DAC_DETECT = True         # Auto-detect USB DAC via udev/ALSA

# Display
DISPLAY_DSI = True            # 7-inch MIPI DSI display (handled by kernel/firmware)

# ==============================================================================
# Electrical Configuration
# ==============================================================================
DEBOUNCE_MS = 5               # Button/switch debounce (ms)
ENCODER_DEBOUNCE_MS = 1       # Encoder quadrature debounce (ms)
LONG_PRESS_MS = 500           # Long press threshold (ms)

ENCODER_PULL = "up"           # Internal pull-up
NAV_PULL = "up"               # Internal pull-up
BUTTON_PULL = "up"            # Internal pull-up

ENCODER_ACTIVE_LOW = True     # Active low (pressed = 0)
NAV_ACTIVE_LOW = True         # Active low
BUTTON_ACTIVE_LOW = True      # Active low

ENCODER_STEPS_PER_DETENT = 4  # Standard quadrature encoder

# ==============================================================================
# Function Mappings (Configurable via UI)
# ==============================================================================
BUTTON_FUNCTIONS = {
    0: "LAYER_UP",      # Button 1 (GPIO 16)
    1: "LAYER_DOWN",    # Button 2 (GPIO 7)
    2: "CHAIN_LEFT",    # Button 3 (GPIO 8)
    3: "CHAIN_RIGHT",   # Button 4 (GPIO 9)
    4: "SNAPSHOT_UP",   # Button 5 (GPIO 25)
    5: "SNAPSHOT_DOWN", # Button 6 (GPIO 26)
    6: "MIXER",         # Button 7 (GPIO 12)
    7: "MOD_UI",        # Button 8 (GPIO 4) - Launch MOD-UI
    8: "QUICK_EDIT",    # Button 9 (GPIO 10)
    9: "PANIC",         # Button 10 (GPIO 11) - All notes off
}

# MIDI CC mappings for buttons (future expansion via UI)
BUTTON_MIDI_CC = {
    0: {"cc": 80, "channel": 0},
    1: {"cc": 81, "channel": 0},
    2: {"cc": 82, "channel": 0},
    3: {"cc": 83, "channel": 0},
    4: {"cc": 84, "channel": 0},
    5: {"cc": 85, "channel": 0},
    6: {"cc": 86, "channel": 0},
    7: {"cc": 87, "channel": 0},
    8: {"cc": 88, "channel": 0},
    9: {"cc": 89, "channel": 0},
}

ENCODER_MIDI = {
    "cc": 16,
    "channel": 0,
    "mode": "relative",
}

NAV_MIDI = {
    "up": {"type": "note", "note": 60, "channel": 0},
    "down": {"type": "note", "note": 61, "channel": 0},
    "left": {"type": "note", "note": 62, "channel": 0},
    "right": {"type": "note", "note": 63, "channel": 0},
    "click": {"type": "note", "note": 64, "channel": 0},
}

# Zynthian wiring layout identifier
WIRING_LAYOUT = "GIGBOX"
KIT_VERSION = "GIGBOX"

# Number of controls for Zynthian core
NUM_ZYNSWITCHES = 19  # 1 encoder switch + 5 nav + 10 buttons + 3 reserved
NUM_ZYNPOTS = 0       # NO potentiometer
LAST_ZYNSWITCH_INDEX = 18

# Switch index mapping (matches Zynthian's expectation)
SWITCH_INDEX_MAP = {
    "encoder_sw": 0,
    "nav_up": 4,
    "nav_down": 5,
    "nav_left": 6,
    "nav_right": 7,
    "nav_click": 8,
    "button_1": 9,
    "button_2": 10,
    "button_3": 11,
    "button_4": 12,
    "button_5": 13,
    "button_6": 14,
    "button_7": 15,
    "button_8": 16,
    "button_9": 17,
    "button_10": 18,
}

# Custom switch actions for Zynthian UI
CUSTOM_SWITCH_ACTIONS = {
    "nav_up": {"short": "UP", "bold": "UP_BOLD", "long": "UP_LONG"},
    "nav_down": {"short": "DOWN", "bold": "DOWN_BOLD", "long": "DOWN_LONG"},
    "nav_left": {"short": "LEFT", "bold": "LEFT_BOLD", "long": "LEFT_LONG"},
    "nav_right": {"short": "RIGHT", "bold": "RIGHT_BOLD", "long": "RIGHT_LONG"},
    "nav_click": {"short": "SELECT", "bold": "SELECT_BOLD", "long": "BACK"},
    "encoder_sw": {"short": "SELECT", "bold": "SELECT_BOLD", "long": "BACK"},
    "button_1": {"short": "LAYER_UP", "long": "LAYER_MENU"},
    "button_2": {"short": "LAYER_DOWN", "long": "LAYER_MENU"},
    "button_3": {"short": "CHAIN_LEFT", "long": "CHAIN_MENU"},
    "button_4": {"short": "CHAIN_RIGHT", "long": "CHAIN_MENU"},
    "button_5": {"short": "SNAPSHOT_UP", "long": "SNAPSHOT_MENU"},
    "button_6": {"short": "SNAPSHOT_DOWN", "long": "SNAPSHOT_MENU"},
    "button_7": {"short": "MIXER", "long": "AUDIO_MENU"},
    "button_8": {"short": "MOD_UI", "long": "MOD_UI_MENU"},
    "button_9": {"short": "QUICK_EDIT", "long": "ENGINE_MENU"},
    "button_10": {"short": "PANIC", "long": "SYSTEM_MENU"},
}

def get_gpio_map():
    """Return complete GPIO mapping for documentation"""
    return {
        "encoder": {
            "a": {"bcm": ENCODER_A_PIN, "physical": 29, "function": "Encoder Channel A", "conflict": "None"},
            "b": {"bcm": ENCODER_B_PIN, "physical": 31, "function": "Encoder Channel B", "conflict": "None"},
            "switch": {"bcm": ENCODER_SW_PIN, "physical": 33, "function": "Encoder Push Switch", "conflict": "PWM1 (acceptable - USB DAC used)"},
        },
        "navigation": {
            "up": {"bcm": NAV_UP_PIN, "physical": 11, "function": "Navigation UP", "conflict": "None"},
            "down": {"bcm": NAV_DOWN_PIN, "physical": 13, "function": "Navigation DOWN", "conflict": "None"},
            "left": {"bcm": NAV_LEFT_PIN, "physical": 15, "function": "Navigation LEFT", "conflict": "None"},
            "right": {"bcm": NAV_RIGHT_PIN, "physical": 16, "function": "Navigation RIGHT", "conflict": "None"},
            "click": {"bcm": NAV_CLICK_PIN, "physical": 18, "function": "Navigation CLICK", "conflict": "None"},
        },
        "buttons": [
            {"index": i+1, "bcm": pin, "physical": _bcm_to_physical(pin), "function": BUTTON_FUNCTIONS.get(i, f"BUTTON_{i+1}"), "conflict": _get_button_conflict(pin)}
            for i, pin in enumerate(BUTTON_PINS)
        ],
        "potentiometer": {
            "status": "REMOVED",
            "reason": "No ADC hardware - Raspberry Pi GPIO cannot read analog signals",
            "note": "Use rotary encoder for master volume"
        },
        "softpot": {
            "status": "REMOVED",
            "reason": "No ADC hardware - Future expansion would require external ADC"
        },
        "i2s_reserved": {
            "note": "GPIO 18,19,20,21 (Physical 12,35,38,40) EXPLICITLY RESERVED for PCM DAC I2S",
            "pins": [
                {"bcm": 18, "physical": 12, "function": "I2S_CLK"},
                {"bcm": 19, "physical": 35, "function": "I2S_FS"},
                {"bcm": 20, "physical": 38, "function": "I2S_DIN"},
                {"bcm": 21, "physical": 40, "function": "I2S_DOUT"},
            ]
        }
    }

def _get_button_conflict(bcm):
    conflicts = {
        16: "None",
        7: "SPI0_CE1 (acceptable - no SPI0 on header)",
        8: "SPI0_CE0 (acceptable - no SPI0 on header)",
        9: "SPI0_MISO (acceptable - no SPI0 on header)",
        25: "None",
        26: "None",
        12: "PWM0 (acceptable - USB DAC used)",
        4: "I2C1_SDA alt (acceptable - no I2C1 devices)",
        10: "SPI0_MOSI (acceptable - no SPI0 on header)",
        11: "SPI0_SCLK (acceptable - no SPI0 on header)",
    }
    return conflicts.get(bcm, "Unknown")

def _bcm_to_physical(bcm):
    """Convert BCM GPIO to physical pin number - Raspberry Pi 5 40-pin header"""
    bcm_to_phys = {
        2: 3, 3: 5, 4: 7, 5: 29, 6: 31, 7: 26, 8: 24, 9: 21, 10: 19, 11: 23,
        12: 32, 13: 33, 14: 8, 15: 10, 16: 36, 17: 11, 18: 12, 19: 35, 20: 38,
        21: 40, 22: 15, 23: 16, 24: 18, 25: 22, 26: 37, 27: 13
    }
    return bcm_to_phys.get(bcm, 0)

def validate_gpio_config():
    """Validate GPIO configuration for conflicts - Pi 5 specific"""
    all_pins = []
    all_pins.extend([ENCODER_A_PIN, ENCODER_B_PIN, ENCODER_SW_PIN])
    all_pins.extend([NAV_UP_PIN, NAV_DOWN_PIN, NAV_LEFT_PIN, NAV_RIGHT_PIN, NAV_CLICK_PIN])
    all_pins.extend(BUTTON_PINS)
    
    # Check for duplicates
    seen = set()
    duplicates = []
    for pin in all_pins:
        if pin in seen:
            duplicates.append(pin)
        seen.add(pin)
    
    if duplicates:
        logging.error(f"DUPLICATE GPIO PINS: {duplicates}")
        return False
    
    # Pi 5 Reserved pins (DO NOT USE)
    critical_reserved = {
        0, 1,   # ID EEPROM (HAT) - Physical 27, 28
        2, 3,   # I2C1 (System) - Physical 3, 5
        14, 15, # UART0 (Console) - Physical 8, 10
    }
    
    # I2S - MUST KEEP FREE for PCM DAC
    i2s_reserved = {18, 19, 20, 21}
    
    conflicts_critical = [p for p in all_pins if p in critical_reserved]
    conflicts_i2s = [p for p in all_pins if p in i2s_reserved]
    
    if conflicts_critical:
        logging.error(f"CRITICAL GPIO CONFLICTS (system reserved): {conflicts_critical}")
        return False
    
    if conflicts_i2s:
        logging.error(f"I2S CONFLICTS (reserved for PCM DAC): {conflicts_i2s}")
        return False
    
    # Acceptable conflicts (peripherals not used by GIGBOX)
    acceptable_conflicts = {
        4: "I2C1_SDA alt (no I2C1 devices)",
        7: "SPI0_CE1 (no SPI0 on header)",
        8: "SPI0_CE0 (no SPI0 on header)",
        9: "SPI0_MISO (no SPI0 on header)",
        10: "SPI0_MOSI (no SPI0 on header)",
        11: "SPI0_SCLK (no SPI0 on header)",
        12: "PWM0 (USB DAC used)",
        13: "PWM1 (USB DAC used)",
    }
    
    for pin, reason in acceptable_conflicts.items():
        if pin in all_pins:
            logging.info(f"ACCEPTABLE CONFLICT: GPIO {pin} - {reason}")
    
    logging.info(f"Total GPIOs used: {len(all_pins)} (3 encoder + 5 nav + 10 buttons)")
    logging.info(f"I2S pins (18,19,20,21) reserved for PCM DAC: FREE")
    return True

def get_validated_gpio_table():
    """Return the final validated GPIO table for documentation"""
    return [
        {"control": "Main Encoder", "signal": "A", "bcm": 5, "physical": 29, "pull": "up", "active": "low", "debounce_ms": 1, "conflict": "None", "notes": "Quadrature A - SAFE"},
        {"control": "Main Encoder", "signal": "B", "bcm": 6, "physical": 31, "pull": "up", "active": "low", "debounce_ms": 1, "conflict": "None", "notes": "Quadrature B - SAFE"},
        {"control": "Main Encoder", "signal": "Push", "bcm": 13, "physical": 33, "pull": "up", "active": "low", "debounce_ms": 5, "short": "SELECT", "long": "BACK", "long_ms": 500, "conflict": "PWM1", "notes": "Acceptable - USB DAC used, no PWM audio"},
        {"control": "Navigation", "signal": "UP", "bcm": 17, "physical": 11, "pull": "up", "active": "low", "debounce_ms": 5, "short": "UP", "long": "UP_LONG", "long_ms": 500, "conflict": "None", "notes": "SAFE"},
        {"control": "Navigation", "signal": "DOWN", "bcm": 27, "physical": 13, "pull": "up", "active": "low", "debounce_ms": 5, "short": "DOWN", "long": "DOWN_LONG", "long_ms": 500, "conflict": "None", "notes": "SAFE"},
        {"control": "Navigation", "signal": "LEFT", "bcm": 22, "physical": 15, "pull": "up", "active": "low", "debounce_ms": 5, "short": "LEFT", "long": "LEFT_LONG", "long_ms": 500, "conflict": "None", "notes": "SAFE"},
        {"control": "Navigation", "signal": "RIGHT", "bcm": 23, "physical": 16, "pull": "up", "active": "low", "debounce_ms": 5, "short": "RIGHT", "long": "RIGHT_LONG", "long_ms": 500, "conflict": "None", "notes": "SAFE"},
        {"control": "Navigation", "signal": "CLICK", "bcm": 24, "physical": 18, "pull": "up", "active": "low", "debounce_ms": 5, "short": "SELECT", "long": "BACK", "long_ms": 500, "conflict": "None", "notes": "SAFE"},
        {"control": "Button", "signal": "1", "bcm": 16, "physical": 36, "pull": "up", "active": "low", "debounce_ms": 5, "short": "LAYER_UP", "long": "LAYER_MENU", "long_ms": 500, "midi_cc": 80, "conflict": "None", "notes": "SAFE"},
        {"control": "Button", "signal": "2", "bcm": 7, "physical": 26, "pull": "up", "active": "low", "debounce_ms": 5, "short": "LAYER_DOWN", "long": "LAYER_MENU", "long_ms": 500, "midi_cc": 81, "conflict": "SPI0_CE1", "notes": "Acceptable - no SPI0 on 40-pin header"},
        {"control": "Button", "signal": "3", "bcm": 8, "physical": 24, "pull": "up", "active": "low", "debounce_ms": 5, "short": "CHAIN_LEFT", "long": "CHAIN_MENU", "long_ms": 500, "midi_cc": 82, "conflict": "SPI0_CE0", "notes": "Acceptable - no SPI0 on 40-pin header"},
        {"control": "Button", "signal": "4", "bcm": 9, "physical": 21, "pull": "up", "active": "low", "debounce_ms": 5, "short": "CHAIN_RIGHT", "long": "CHAIN_MENU", "long_ms": 500, "midi_cc": 83, "conflict": "SPI0_MISO", "notes": "Acceptable - no SPI0 on 40-pin header"},
        {"control": "Button", "signal": "5", "bcm": 25, "physical": 22, "pull": "up", "active": "low", "debounce_ms": 5, "short": "SNAPSHOT_UP", "long": "SNAPSHOT_MENU", "long_ms": 500, "midi_cc": 84, "conflict": "None", "notes": "SAFE"},
        {"control": "Button", "signal": "6", "bcm": 26, "physical": 37, "pull": "up", "active": "low", "debounce_ms": 5, "short": "SNAPSHOT_DOWN", "long": "SNAPSHOT_MENU", "long_ms": 500, "midi_cc": 85, "conflict": "None", "notes": "SAFE"},
        {"control": "Button", "signal": "7", "bcm": 12, "physical": 32, "pull": "up", "active": "low", "debounce_ms": 5, "short": "MIXER", "long": "AUDIO_MENU", "long_ms": 500, "midi_cc": 86, "conflict": "PWM0", "notes": "Acceptable - USB DAC used, no PWM audio"},
        {"control": "Button", "signal": "8", "bcm": 4, "physical": 7, "pull": "up", "active": "low", "debounce_ms": 5, "short": "MOD_UI", "long": "MOD_UI_MENU", "long_ms": 500, "midi_cc": 87, "conflict": "I2C1_SDA alt", "notes": "Acceptable - no I2C1 devices on header"},
        {"control": "Button", "signal": "9", "bcm": 10, "physical": 19, "pull": "up", "active": "low", "debounce_ms": 5, "short": "QUICK_EDIT", "long": "ENGINE_MENU", "long_ms": 500, "midi_cc": 88, "conflict": "SPI0_MOSI", "notes": "Acceptable - no SPI0 on 40-pin header"},
        {"control": "Button", "signal": "10", "bcm": 11, "physical": 23, "pull": "up", "active": "low", "debounce_ms": 5, "short": "PANIC", "long": "SYSTEM_MENU", "long_ms": 500, "midi_cc": 89, "conflict": "SPI0_SCLK", "notes": "Acceptable - no SPI0 on 40-pin header"},
    ]

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("GIGBOX GPIO Configuration - FINAL (I2S-Safe, 18 inputs)")
    print("=" * 60)
    gpio_map = get_gpio_map()
    for section, data in gpio_map.items():
        print(f"\n{section.upper()}:")
        if isinstance(data, list):
            for item in data:
                print(f"  {item}")
        elif isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, dict):
                    print(f"  {k}: BCM={v.get('bcm')}, Pin={v.get('physical')}, {v.get('function')}, Conflict: {v.get('conflict', 'None')}")
                elif isinstance(v, list):
                    for item in v:
                        print(f"  {item}")
                else:
                    print(f"  {k}: {v}")
    
    print("\nValidation:", "PASS" if validate_gpio_config() else "FAIL")
    
    print("\n\nFINAL VALIDATED GPIO TABLE (I2S-Safe):")
    print("-" * 80)
    table = get_validated_gpio_table()
    for row in table:
        conflict = row.get("conflict", "None")
        notes = row.get("notes", "")
        print(f"{row['control']:15} {row['signal']:5} BCM={row['bcm']:2} Pin={row['physical']:2} Pull={row['pull']:4} Active={row['active']:4} Debounce={row['debounce_ms']:2}ms Conflict={conflict:<25} {notes}")