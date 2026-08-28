# GIGBOX GPIO MAP - FINAL VALIDATED CONFIGURATION (I2S-Safe)
# SPOOKI INSTRUMENTS - GIGBOX
# Target: Raspberry Pi 5, 7-inch 800×480 MIPI DSI Display
# I2S pins (18,19,20,21) RESERVED for PCM DAC

---

## OVERVIEW

| Parameter | Value |
|-----------|-------|
| **Total GPIO Inputs** | 18 |
| **Encoder** | 3 GPIOs (A, B, Push) |
| **Navigation Module** | 5 GPIOs (UP, DOWN, LEFT, RIGHT, CLICK) |
| **Tactile Buttons** | 10 GPIOs (Button 1–10) |
| **Potentiometer** | **REMOVED** - No ADC hardware |
| **SoftPot** | **REMOVED** - No ADC hardware |
| **Numbering** | BCM (Broadcom) |
| **Logic** | Active LOW (internal pull-up, pressed = 0V) |
| **Debounce** | 5ms (buttons/switches), 1ms (encoder) |
| **Long Press** | 500ms threshold |

---

## COMPLETE GPIO ASSIGNMENT TABLE

| Physical Control | Signal | BCM GPIO | Physical Header Pin | Pull | Active Level | Debounce | Short Press | Long Press | Conflict | Notes |
|---|---|---:|---:|---|---|---:|---|---|---|---|
| **Main Encoder** | A | 5 | 29 | Up | Low | 1ms | — | — | **None** | Quadrature A - SAFE |
| **Main Encoder** | B | 6 | 31 | Up | Low | 1ms | — | — | **None** | Quadrature B - SAFE |
| **Main Encoder** | Push | 13 | 33 | Up | Low | 5ms | SELECT | BACK/CANCEL | PWM1 | Acceptable - USB DAC used |
| **Navigation** | UP | 17 | 11 | Up | Low | 5ms | UP | UP_LONG | **None** | SAFE |
| **Navigation** | DOWN | 27 | 13 | Up | Low | 5ms | DOWN | DOWN_LONG | **None** | SAFE |
| **Navigation** | LEFT | 22 | 15 | Up | Low | 5ms | LEFT | LEFT_LONG | **None** | SAFE |
| **Navigation** | RIGHT | 23 | 16 | Up | Low | 5ms | RIGHT | RIGHT_LONG | **None** | SAFE |
| **Navigation** | CLICK | 24 | 18 | Up | Low | 5ms | SELECT | BACK/CANCEL | **None** | SAFE |
| **Button 1** | Signal | 16 | 36 | Up | Low | 5ms | TRANSPOSE_UP | TRANSPOSE_UP | **None** | +1 semitone |
| **Button 2** | Signal | 7 | 26 | Up | Low | 5ms | TRANSPOSE_DOWN | TRANSPOSE_DOWN | SPI0_CE1 | -1 semitone |
| **Button 3** | Signal | 8 | 24 | Up | Low | 5ms | OCTAVE_UP | OCTAVE_UP | SPI0_CE0 | +1 octave |
| **Button 4** | Signal | 9 | 21 | Up | Low | 5ms | OCTAVE_DOWN | OCTAVE_DOWN | SPI0_MISO | -1 octave |
| **Button 5** | Signal | 25 | 22 | Up | Low | 5ms | SUSTAIN | SUSTAIN | **None** | Toggle MIDI CC 64 |
| **Button 6** | Signal | 26 | 37 | Up | Low | 5ms | PLAY_PAUSE | PLAY_PAUSE | **None** | Toggle transport |
| **Button 7** | Signal | 12 | 32 | Up | Low | 5ms | MENU | MENU | PWM0 | Main menu |
| **Button 8** | Signal | 4 | 7 | Up | Low | 5ms | MIX | MIX | I2C1_SDA alt | Mixer screen |
| **Button 9** | Signal | 10 | 19 | Up | Low | 5ms | ZS3 | ZS3 | SPI0_MOSI | ZS3 screen |
| **Button 10** | Signal | 11 | 23 | Up | Low | 5ms | ALT | ALT | SPI0_SCLK | Toggle ALT |

---

## I2S PINS - RESERVED FOR PCM DAC (DO NOT USE)

| Function | BCM GPIO | Physical Header Pin | Notes |
|---|---|---:|---|
| I2S_CLK | 18 | 12 | PCM DAC Clock |
| I2S_FS | 19 | 35 | PCM DAC Frame Sync |
| I2S_DIN | 20 | 38 | PCM DAC Data In |
| I2S_DOUT | 21 | 40 | PCM DAC Data Out |

**These pins are EXPLICITLY RESERVED and must not be used for buttons/controls.**

---

## WIRING INSTRUCTIONS

### Common Ground
All switches, buttons, and encoder connect to **common GND**.
Available GND pins on 40-pin header: **6, 9, 14, 20, 25, 30, 34, 39**

### Main Rotary Encoder
```
Encoder A (Channel A)  →  Physical Pin 29  (BCM GPIO 5)
Encoder B (Channel B)  →  Physical Pin 31  (BCM GPIO 6)
Encoder Push Switch    →  Physical Pin 33  (BCM GPIO 13)
Other encoder pin      →  GND (any ground pin)
```
- Use **twisted pair** for A/B signals
- Optional: 100nF capacitor across each switch contact for hardware debounce

### Navigation Module (5-way)
```
UP       →  Physical Pin 11  (BCM GPIO 17)
DOWN     →  Physical Pin 13  (BCM GPIO 27)
LEFT     →  Physical Pin 15  (BCM GPIO 22)
RIGHT    →  Physical Pin 16  (BCM GPIO 23)
CLICK    →  Physical Pin 18  (BCM GPIO 24)
Common   →  GND
```

### 10 Tactile Buttons
```
Button 1  →  Physical Pin 36  (BCM GPIO 16)
Button 2  →  Physical Pin 26  (BCM GPIO 7)
Button 3  →  Physical Pin 24  (BCM GPIO 8)
Button 4  →  Physical Pin 21  (BCM GPIO 9)
Button 5  →  Physical Pin 22  (BCM GPIO 25)
Button 6  →  Physical Pin 37  (BCM GPIO 26)
Button 7  →  Physical Pin 32  (BCM GPIO 12)
Button 8  →  Physical Pin 7   (BCM GPIO 4)
Button 9  →  Physical Pin 19  (BCM GPIO 10)
Button 10 →  Physical Pin 23  (BCM GPIO 11)
Other side of each button → GND
```

---

## CONFLICT RESOLUTION NOTES

### Acceptable Conflicts (Peripherals Not Used by GIGBOX)

| GPIO | Function | Conflict | Resolution |
|---|---|---|---|
| 13 | Encoder Push | PWM1 | **Acceptable** - USB DAC used, no PWM audio |
| 12 | Button 7 | PWM0 | **Acceptable** - USB DAC used, no PWM audio |
| 7 | Button 2 | SPI0_CE1 | **Acceptable** - No SPI0 devices on 40-pin header (boot SPI is separate) |
| 8 | Button 3 | SPI0_CE0 | **Acceptable** - No SPI0 devices on 40-pin header |
| 9 | Button 4 | SPI0_MISO | **Acceptable** - No SPI0 devices on 40-pin header |
| 10 | Button 9 | SPI0_MOSI | **Acceptable** - No SPI0 devices on 40-pin header |
| 11 | Button 10 | SPI0_SCLK | **Acceptable** - No SPI0 devices on 40-pin header |
| 4 | Button 8 | I2C1_SDA alt | **Acceptable** - No I2C1 devices on header |

### Critical Conflicts AVOIDED

| GPIO | Function | Conflict | Status |
|---|---|---|---|
| 18 | — | I2S_CLK | **RESERVED** for PCM DAC |
| 19 | — | I2S_FS | **RESERVED** for PCM DAC |
| 20 | — | I2S_DIN | **RESERVED** for PCM DAC |
| 21 | — | I2S_DOUT | **RESERVED** for PCM DAC |

---

## RESERVED SYSTEM PINS (DO NOT USE)

| Function | BCM | Physical | Purpose |
|----------|-----|----------|---------|
| I2C0 (HAT EEPROM) | 0, 1 | 27, 28 | HAT identification |
| I2C1 (System) | 2, 3 | 3, 5 | System peripherals |
| UART0 (Console) | 14, 15 | 8, 10 | Serial console |
| SPI0 (Boot) | — | — | Internal (not on 40-pin header) |

---

## FUNCTIONAL BEHAVIOR

### Main Encoder
- **Clockwise rotation**: Increase value / Next item
- **Counter-clockwise**: Decrease value / Previous item
- **Short press**: SELECT / OK
- **Long press (500ms)**: BACK / CANCEL (global, exits MOD-UI via daemon)

### Navigation Module
- **UP/DOWN/LEFT/RIGHT**: Directional navigation (replaces on-screen arrows)
- **CLICK**: SELECT / OK (short press)
- **CLICK long press (500ms)**: BACK / CANCEL (exits MOD-UI via daemon)

### 10 Tactile Buttons (Default Mapping)
| Button | Default Function | Long Press |
|--------|-----------------|------------|
| 1 (GPIO 16) | TRANSPOSE_UP (+1 semitone) | TRANSPOSE_UP |
| 2 (GPIO 7) | TRANSPOSE_DOWN (-1 semitone) | TRANSPOSE_DOWN |
| 3 (GPIO 8) | OCTAVE_UP (+12 semitones) | OCTAVE_UP |
| 4 (GPIO 9) | OCTAVE_DOWN (-12 semitones) | OCTAVE_DOWN |
| 5 (GPIO 25) | SUSTAIN (toggle CC 64) | SUSTAIN |
| 6 (GPIO 26) | PLAY_PAUSE | PLAY_PAUSE |
| 7 (GPIO 12) | MENU | MENU |
| 8 (GPIO 4) | MIX | MIX |
| 9 (GPIO 10) | ZS3 | ZS3 |
| 10 (GPIO 11) | ALT | ALT |

All buttons use the same action for short, bold, and long release. The actions are defined by the GIGBOX profile.

---

## REMOVED COMPONENTS

| Component | Status | Reason |
|-----------|--------|--------|
| Potentiometer | **REMOVED** | No ADC - Pi GPIO cannot read analog |
| SoftPot | **REMOVED** | No ADC - Future expansion requires external ADC |
| ADC Hardware | **NOT PRESENT** | MCP3008/ADS1115 not installed |

**Do not** configure any analog input. Use rotary encoder for master volume.

---

## VALIDATION CHECKLIST (REAL HARDWARE)

- [ ] All 18 GPIO inputs register correctly
- [ ] Encoder quadrature: CW = increment, CCW = decrement
- [ ] Encoder push: Short = SELECT, Long = BACK
- [ ] Navigation UP/DOWN/LEFT/RIGHT/CLICK all functional
- [ ] Navigation CLICK: Short = SELECT, Long = BACK
- [ ] Buttons 1–10: Short and long press detected
- [ ] No ghost events / double triggers
- [ ] Touchscreen fully functional (tap, drag, multi-touch)
- [ ] On-screen directional arrows **removed** from UI
- [ ] Remaining on-screen controls **reflowed** cleanly
- [ ] MOD-UI launches from the visible on-screen MOD UI control
- [ ] MOD-UI exits via Encoder long press OR Nav CLICK long press
- [ ] USB DAC enumerates and works
- [ ] PCM DAC (I2S) works on GPIO 18,19,20,21
- [ ] WiFi UDP MIDI receives data on port 4210
- [ ] All soundfonts load in FluidSynth
- [ ] SooperLooper, Sequencer, all plugins themed

---

## SOFTWARE INTEGRATION

The GPIO configuration is integrated into Zynthian via:
- `/zynthian/zynthian-ui/zyngui/gigbox_wiring.py` - Main wiring module
- `/zynthian/config/gigbox_gpio_map.json` - JSON configuration
- Zynthian's `lib_zyncore` handles low-level GPIO reading
- Custom switch actions mapped in `zynthian_gui_config.py`
- **MOD-UI exit daemon** (`gigbox-modui-exit-daemon.py`) monitors lib_zyncore for encoder/nav long press

To modify button mappings: Use Zynthian webconf → Hardware → Wiring Layout → GIGBOX → Custom Switches

---

## DOCUMENT VERSION

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-08-28 | GIGBOX Team | Initial |
| 2.0 | 2026-08-28 | GIGBOX Team | **I2S-Safe GPIO reassignment** - Buttons 2,3,4,9 moved off GPIO 18,19,20,21 |
| 2.1 | 2026-08-28 | GIGBOX Team | Confirmed physical button actions and live Zynthian integration |

---

**END OF GIGBOX_GPIO_MAP.md**
