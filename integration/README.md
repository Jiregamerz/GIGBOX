# GIGBOX OS - SPOOKI INSTRUMENTS
**Based on Zynthian OS** | **Version 1.0.0** | **Raspberry Pi 5**

---

## OVERVIEW

GIGBOX is a **complete modification of the Zynthian OS** - not a skin, not a theme package, but the actual Zynthian OS filesystem modified to become a dedicated GIGBOX / SPOOKI INSTRUMENTS instrument.

### What This Is
- ✅ Modified Zynthian OS root filesystem
- ✅ Integrated GIGBOX dark neon red theme (near black, PCB trace design)
- ✅ Custom hardware GPIO configuration (18 inputs)
- ✅ MOD-UI integration (manual launch, hardware exit)
- ✅ WiFi UDP MIDI receiver (auto-start)
- ✅ USB DAC / PCM DAC audio configuration
- ✅ 42 GIGBOX soundfonts pre-installed
- ✅ Custom boot animation & branding
- ✅ Screen transition animations (fade in/out)
- ✅ SooperLooper & all plugins themed
- ✅ On-screen directional arrows REMOVED (physical nav is primary)

### What This Is NOT
- ❌ A theme/skin package
- ❌ An overlay or external application
- ❌ A web-based UI
- ❌ A replacement for Zynthian's backend

---

## HARDWARE REQUIREMENTS

| Component | Specification |
|-----------|---------------|
| **SBC** | Raspberry Pi 5 (4GB or 8GB recommended) |
| **Display** | 7-inch 800×480 MIPI DSI touchscreen |
| **Main Encoder** | Rotary encoder: A, B, Push (3 GPIOs) |
| **Navigation** | 5-way module: UP, DOWN, LEFT, RIGHT, CLICK (5 GPIOs) |
| **Buttons** | 10× tactile buttons (10 GPIOs) |
| **Audio Out** | PCM DAC via I2S (L/R) OR USB DAC |
| **Headphones** | USB DAC (headphone + mic) |
| **Storage** | MicroSD 32GB+ (A2 class recommended) |
| **Power** | 5V 3A+ USB-C PD |

**Total GPIO: 18 inputs** (no potentiometer, no softpot, no ADC)

---

## GPIO WIRING

See **GIGBOX_GPIO_MAP.md** for complete wiring diagram with:
- BCM GPIO numbers
- Physical header pin numbers
- Pull-up/down configuration
- Active levels
- Debounce times
- Short/long press actions
- MIDI CC mappings
- Conflict warnings (I2S vs Buttons 2,3,4,9)

### Quick Reference
| Function | BCM | Physical Pin |
|----------|-----|--------------|
| Encoder A | 5 | 29 |
| Encoder B | 6 | 31 |
| Encoder Push | 13 | 33 |
| Nav UP | 17 | 11 |
| Nav DOWN | 27 | 13 |
| Nav LEFT | 22 | 15 |
| Nav RIGHT | 23 | 16 |
| Nav CLICK | 24 | 18 |
| Button 1 | 16 | 36 |
| Button 2 | 19 | 35 |
| Button 3 | 20 | 38 |
| Button 4 | 21 | 40 |
| Button 5 | 25 | 22 |
| Button 6 | 26 | 37 |
| Button 7 | 12 | 32 |
| Button 8 | 4 | 7 |
| Button 9 | 18 | 12 |
| Button 10 | 7 | 26 |

**All inputs: Active LOW, internal pull-up, software debounce**

---

## FLASHING THE IMAGE

### Linux / macOS
```bash
# Identify SD card (BE CAREFUL!)
lsblk
# or
diskutil list

# Flash (replace /dev/sdX with your SD card)
sudo dd if=gigbox-final.img of=/dev/sdX bs=4M status=progress conv=fsync
sync
```

### Windows
- Use **Rufus** or **BalenaEtcher**
- Select `gigbox-final.img`
- Target your SD card
- Flash

### From Compressed Image
```bash
# Decompress and flash in one command
xzcat gigbox-final.img.xz | sudo dd of=/dev/sdX bs=4M status=progress conv=fsync
sync
```

---

## FIRST BOOT

1. **Insert SD card** into Raspberry Pi 5
2. **Connect hardware** per GPIO map
3. **Connect display** via MIPI DSI
4. **Connect USB DAC** (headphones/mic)
5. **Power on** (5V 3A+ USB-C)

### Boot Sequence
1. Raspberry Pi firmware → Rainbow screen
2. **GIGBOX Plymouth theme** → SPOOKI INSTRUMENTS logo with neon pulse
3. Linux kernel → Boot messages (quiet)
4. **GIGBOX Zynthian UI** → Dark neon red interface
5. Auto-starts: Audio, MIDI, WiFi MIDI, Zynthian services

---

## CONTROLS & OPERATION

### Main Encoder
| Action | Function |
|--------|----------|
| Rotate CW | Increase / Next |
| Rotate CCW | Decrease / Previous |
| Short Press | SELECT / OK |
| Long Press (500ms) | BACK / CANCEL (global, exits MOD-UI) |

### Navigation Module (5-way)
| Action | Function |
|--------|----------|
| UP | Navigate Up |
| DOWN | Navigate Down |
| LEFT | Navigate Left |
| RIGHT | Navigate Right |
| CLICK (short) | SELECT / OK |
| CLICK (long) | BACK / CANCEL |

### 10 Tactile Buttons (Default Mapping)
| Button | Short Press | Long Press | MIDI CC |
|--------|-------------|------------|---------|
| 1 | LAYER_UP | LAYER_MENU | 80 |
| 2 | LAYER_DOWN | LAYER_MENU | 81 |
| 3 | CHAIN_LEFT | CHAIN_MENU | 82 |
| 4 | CHAIN_RIGHT | CHAIN_MENU | 83 |
| 5 | SNAPSHOT_UP | SNAPSHOT_MENU | 84 |
| 6 | SNAPSHOT_DOWN | SNAPSHOT_MENU | 85 |
| 7 | MIXER | AUDIO_MENU | 86 |
| 8 | **MOD_UI** | MOD_UI_MENU | 87 |
| 9 | QUICK_EDIT | ENGINE_MENU | 88 |
| 10 | PANIC | SYSTEM_MENU | 89 |

**All buttons user-configurable via Zynthian Webconf → Hardware → Wiring**

### Touchscreen
- Fully functional for all interactions
- Select parameters, patches, effects
- Navigate MOD-UI pedalboard
- **No on-screen directional arrows** (removed - use physical nav)

---

## MOD-UI OPERATION

### Launching MOD-UI
1. Press **Button 8** (or select from System menu)
2. Chromium launches in kiosk mode at `http://localhost:8888`
3. On-screen **EXIT button** appears top-right (red ✕)
4. Use touchscreen for pedalboard editing

### Exiting MOD-UI
**Any of these:**
- Tap on-screen **EXIT button** (top-right)
- **Encoder long press** (500ms)
- **Navigation CLICK long press** (500ms)
- Returns to GIGBOX/Zynthian UI

### Important
- MOD-UI does **NOT** auto-start at boot
- Runs locally on device (no external PC needed)
- mod-host runs in background always

---

## AUDIO CONFIGURATION

### PCM DAC (Main L/R Output)
- I2S interface (GPIO 18,19,20,21)
- **CONFLICT**: Buttons 2,3,4,9 use same GPIOs
- **Solution**: Use USB DAC as primary, or reassign buttons

### USB DAC (Headphones + Mic)
- Auto-detected via udev
- Becomes ALSA card 1
- Headphone output + Mic input
- **Recommended as primary** to avoid GPIO conflicts

### ALSA Devices
| Name | Device | Description |
|------|--------|-------------|
| `gigbox_main` | PCM DAC | Main L/R out |
| `gigbox_headphones` | USB DAC | Headphone out |
| `gigbox_mic` | USB DAC | Microphone in |
| `default` | PCM DAC | Zynthian default |

---

## WIFI UDP MIDI

- **Port**: 5004 (UDP)
- **Auto-starts** on boot (systemd service)
- **Formats**: Raw MIDI, RTP-MIDI, AppleMIDI
- **Injection**: Direct to Zynthian MIDI system
- **No external PC required**

### Testing
```bash
# From another device on same network
# Send MIDI note on channel 1
echo -ne '\x90\x3c\x7f' | nc -u -w1 <gigbox-ip> 5004
```

---

## SOUNDFONTS

**42 SF2 files** pre-installed in `/zynthian/zynthian-data/soundfonts/GIGBOX/`

| Category | Soundfonts |
|----------|------------|
| Pianos | VS_Upright_Piano_lite, PianoFB, PocketSongsGM |
| Guitars | SpanishClassical, EGuitarFSBS (5 variants), Power_Guitar |
| Bass | FingerBass, PickedBass, Microgame_Bass |
| Synths | Module series (89,90,91,Master), Prismsynth, DX_Pad, Syn_Voices |
| Orchestral | Indian Ensemble, Tabla, Marimba, Timpani, TubularBells |
| Voices | Voice_Oohs, Voice_Sing, Synth_Calliope, Synth_Bamboo_Flute |
| Drums/LoFi | Lo-Fi_Bells, Lo-Fi_Sample_Module, Gold_Gong |
| Experimental | Vini_s_Sample_Library, Waves, Sine, etc. |

Available in FluidSynth engines under **GIGBOX** bank.

---

## THEME & VISUALS

### Color Palette
| Role | Hex | Description |
|------|-----|-------------|
| Background | `#030303` | Near black |
| Panel BG | `#080808` | Slightly lighter |
| Primary Accent | `#ff1744` | Neon red |
| Highlight | `#ff3355` | Bright neon red |
| Dim | `#1a1a1a` | Dark grey |
| Text | `#ffffff` | White |
| Text Dim | `#8a8a8a` | Medium grey |
| PCB Trace | `#2a0808` | Subtle red lines |

### Design Language
- **Dark futuristic electronic instrument**
- **PCB trace patterns** on panels/containers
- **Neon red glow** on focus/active states
- **Via point animations** (pulsing)
- **No rainbow colors** - red family only
- **Functional hierarchy** preserved

### Animated Elements
- Boot logo: Subtle pulse
- Beat markers: Glow on beat
- Via points: Slow pulse
- Screen transitions: 150ms fade
- Recording indicator: Red pulse

---

## ZYNTHIAN FUNCTIONALITY PRESERVED

All core Zynthian features work unchanged:
- ✅ Patch/Chain/Layer management
- ✅ Synth engines (FluidSynth, Dexed, Surge, etc.)
- ✅ Effects & FX chains
- ✅ Mixer & audio routing
- ✅ MIDI routing & mapping
- ✅ Snapshots & ZS3
- ✅ Sequencer & Recorder
- ✅ SooperLooper (themed)
- ✅ Webconf (network config)
- ✅ Bluetooth MIDI
- ✅ USB MIDI host
- ✅ All existing engines

---

## KNOWN LIMITATIONS

| Limitation | Impact | Workaround |
|------------|--------|------------|
| Buttons 2,3,4,9 conflict with I2S | PCM DAC may not work | Use USB DAC as primary |
| Button 8 (GPIO 4) = I2C1_SDA | I2C devices may conflict | Reassign Button 8 if using I2C |
| Button 10 (GPIO 7) = SPI0_CE1 | SPI CE1 unavailable | Acceptable if not using SPI CE1 |
| No ADC | No potentiometer/SoftPot | Use encoder for volume |
| QEMU testing limited | No Pi 5 emulation | Test on real hardware |
| Encoder Push = PWM1 | PWM audio conflict | Use USB DAC |

---

## RECOVERY

### Restore Original Zynthian
If you need to revert (from running GIGBOX):
```bash
sudo /zynthian/gigbox-backup/restore.sh
# Or manually:
sudo cp /zynthian/gigbox-backup/zynthian_gui_config.py.orig /zynthian/zynthian-ui/zyngui/zynthian_gui_config.py
sudo cp -r /zynthian/gigbox-backup/icons.orig/* /zynthian/zynthian-ui/icons/
sudo cp -r /zynthian/gigbox-backup/img.orig/* /zynthian/zynthian-ui/img/
sudo cp -r /zynthian/gigbox-backup/clean.orig/* /zynthian/zynthian-ui/img/clean/
sudo reboot
```

### Re-flash Image
Simply re-flash `gigbox-final.img` to SD card.

---

## DEVELOPMENT / CUSTOMIZATION

### Modify Theme
Edit `/zynthian/zynthian-ui/zyngui/zynthian_gui_config.py` (colors) and `/usr/share/themes/GIGBOX/gtk-3.0/gtk.css` (GTK3).

### Modify Button Mappings
Zynthian Webconf → Hardware → Wiring Layout → GIGBOX → Custom Switches

### Add Soundfonts
Copy `.sf2` files to `/zynthian/zynthian-data/soundfonts/GIGBOX/`

### Modify GPIO
Edit `/zynthian/zynthian-ui/zyngui/gigbox_wiring.py` and `/zynthian/config/gigbox_gpio_map.json`

---

## CREDITS

- **Zynthian OS** by Fernando Moyano & community (https://zynthian.org)
- **GIGBOX Integration** by SPOOKI INSTRUMENTS
- **Icons** generated for GIGBOX visual language
- **Fonts**: Audiowide (Google Fonts)

---

## LICENSE

GIGBOX modifications: Personal project only
Zynthian OS: GPL v2+
See Zynthian licensing for base OS terms.

---

## SUPPORT

This is a **personal project build**. For issues:
1. Check `GIGBOX_BUILD_REPORT.md` for build details
2. Verify hardware wiring per `GIGBOX_GPIO_MAP.md`
3. Test on real Raspberry Pi 5 hardware
4. Consult Zynthian documentation for base OS features

**Not for commercial distribution.**
