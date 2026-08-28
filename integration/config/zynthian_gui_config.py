#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ******************************************************************************
# GIGBOX OS - Zynthian GUI Configuration
# SPOOKI INSTRUMENTS
# Dark futuristic electronic instrument aesthetic
# Near black background, neon red primary accent
# PCB trace design language
# ******************************************************************************

import os
import sys
import logging

# Zynthian specific modules
import zynconf

def get_env_int(env_var, default_val=0):
    try:
        return int(os.environ.get(env_var, str(default_val)))
    except:
        logging.warning(f"Failed to retrieve environmental variable {env_var}")
        return default_val

# ------------------------------------------------------------------------------
# Log level and debugging
# ------------------------------------------------------------------------------
debug_thread = get_env_int('ZYNTHIAN_DEBUG_THREAD', 0)
log_level = get_env_int('ZYNTHIAN_LOG_LEVEL', logging.WARNING)
logging.basicConfig(format='%(levelname)s:%(module)s.%(funcName)s: %(message)s', stream=sys.stderr, level=log_level)
logging.getLogger().setLevel(level=log_level)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.info("GIGBOX UI CONFIG ...")

# ------------------------------------------------------------------------------
# Kit name and Wiring layout - GIGBOX CUSTOM
# ------------------------------------------------------------------------------
kit_version = "GIGBOX"
wiring_layout = "GIGBOX"
logging.info(f"Kit Version: {kit_version}")
logging.info(f"Wiring Layout: {wiring_layout}")
select_ctrl = 3

def check_kit_version(kits):
    for kit in kits:
        if kit_version.startswith(kit):
            return True
    return False

def check_wiring_layout(wls):
    for wl in wls:
        if wiring_layout.startswith(wl):
            return True
    return False

# ------------------------------------------------------------------------------
# GUI layout - GIGBOX 7-inch 800x480 optimized
# ------------------------------------------------------------------------------
gui_layout = "GIGBOX"
layout = {
    'name': 'GIGBOX',
    'columns': 3,
    'rows': 2,
    'ctrl_pos': [
        (0, 0),
        (1, 0),
        (0, 2),
        (1, 2)
    ],
    'list_pos': (0, 1),
    'ctrl_orientation': 'vertical',
    'ctrl_order': (0, 2, 1, 3),
    'ctrl_width': 0.23
}

# ------------------------------------------------------------------------------
# Custom Switches Action Configuration
# ------------------------------------------------------------------------------
custom_switch_ui_actions = []
custom_switch_midi_events = []
GIGBOX_BUTTON_ACTIONS = [
    "GIGBOX_TRANSPOSE_UP",
    "GIGBOX_TRANSPOSE_DOWN",
    "GIGBOX_OCTAVE_UP",
    "GIGBOX_OCTAVE_DOWN",
    "GIGBOX_SUSTAIN",
    "TOGGLE_PLAY",
    "MAIN_MENU",
    "SCREEN_MIXER",
    "SCREEN_ZS3",
    "TOGGLE_ALT_MODE",
]
GIGBOX_SWITCH_ACTIONS = [
    "UP", "DOWN", "LEFT", "RIGHT", "SELECT",
] + GIGBOX_BUTTON_ACTIONS
zynswitch_bold_us = 1000 * 300
zynswitch_long_us = 1000 * 2000
zynswitch_bold_seconds = zynswitch_bold_us / 1000000
zynswitch_long_seconds = zynswitch_long_us / 1000000

def config_zynswitch_timing():
    global zynswitch_bold_us, zynswitch_long_us, zynswitch_bold_seconds, zynswitch_long_seconds
    try:
        zynswitch_bold_us = 1000 * get_env_int('ZYNTHIAN_UI_SWITCH_BOLD_MS', 300)
        zynswitch_long_us = 1000 * get_env_int('ZYNTHIAN_UI_SWITCH_LONG_MS', 2000)
        zynswitch_bold_seconds = zynswitch_bold_us / 1000000
        zynswitch_long_seconds = zynswitch_long_us / 1000000
    except Exception as err:
        logging.error("ERROR configuring zynswitch timing: {}".format(err))

def get_env_switch_action(varname):
    action = os.environ.get(varname, "").strip()
    if not action or action == "NONE":
        action = None
    return action

def config_custom_switches():
    global custom_switch_ui_actions, custom_switch_midi_events, num_zynswitches
    custom_switch_ui_actions = []
    custom_switch_midi_events = []
    for i in range(num_zynswitches - 4):
        cuias = None
        midi_event = None
        root_varname = "ZYNTHIAN_WIRING_CUSTOM_SWITCH_{:02d}".format(i+1)
        custom_type = os.environ.get(root_varname, "")
        if custom_type == "UI_ACTION_PUSH":
            cuias = {
                'P': get_env_switch_action(root_varname + "__UI_PUSH"),
                'S': "", 'B': "", 'L': "",
                'AP': get_env_switch_action(root_varname + "__UI_ALT_PUSH"),
                'AS': "", 'AB': "", 'AL': ""
            }
        elif custom_type == "UI_ACTION" or custom_type == "UI_ACTION_RELEASE":
            cuias = {
                'P': "",
                'S': get_env_switch_action(root_varname + "__UI_SHORT"),
                'B': get_env_switch_action(root_varname + "__UI_BOLD"),
                'L': get_env_switch_action(root_varname + "__UI_LONG"),
                'AP': "",
                'AS': get_env_switch_action(root_varname + "__UI_ALT_SHORT"),
                'AB': get_env_switch_action(root_varname + "__UI_ALT_BOLD"),
                'AL': get_env_switch_action(root_varname + "__UI_ALT_LONG")
            }
        elif custom_type != "":
            if custom_type == "MIDI_CC": evtype = 0xB
            elif custom_type == "MIDI_NOTE": evtype = 0x9
            elif custom_type == "MIDI_PROG_CHANGE": evtype = 0xC
            elif custom_type == "MIDI_CLOCK": evtype = 0xF8
            elif custom_type == "MIDI_TRANSPORT_START": evtype = 0xFA
            elif custom_type == "MIDI_TRANSPORT_CONTINUE": evtype = 0xFB
            elif custom_type == "MIDI_TRANSPORT_STOP": evtype = 0xFC
            elif custom_type == "CVGATE_IN": evtype = -4
            elif custom_type == "CVGATE_OUT": evtype = -5
            elif custom_type == "GATE_OUT": evtype = -6
            elif custom_type == "MIDI_CC_SWITCH": evtype = -7
            else: evtype = None
            if evtype:
                chan = os.environ.get(root_varname + "__MIDI_CHAN")
                try:
                    chan = int(chan) - 1
                    if chan < 0 or chan > 15: chan = None
                except: chan = None
                if evtype in (-4, -5):
                    num = os.environ.get(root_varname + "__CV_CHAN")
                else:
                    num = os.environ.get(root_varname + "__MIDI_NUM")
                try:
                    val = get_env_int(root_varname + "__MIDI_VAL")
                    val = max(min(127, val), 0)
                except: val = 0
                try:
                    num = int(num)
                    if 0 <= num <= 127:
                        midi_event = {'type': evtype, 'chan': chan, 'num': num, 'val': val}
                except: pass
        custom_switch_ui_actions.append(cuias)
        custom_switch_midi_events.append(midi_event)

    # The physical GIGBOX controls must not inherit a previous Webconf profile.
    if wiring_layout == "GIGBOX":
        while len(custom_switch_ui_actions) < len(GIGBOX_SWITCH_ACTIONS):
            custom_switch_ui_actions.append(None)
            custom_switch_midi_events.append(None)
        for i, action in enumerate(GIGBOX_SWITCH_ACTIONS):
            custom_switch_ui_actions[i] = {
                'P': '', 'S': action, 'B': action, 'L': action,
                'AP': '', 'AS': '', 'AB': '', 'AL': ''
            }
        custom_switch_ui_actions[4]['B'] = 'GIGBOX_MODUI_EXIT'
        custom_switch_ui_actions[4]['L'] = 'GIGBOX_MODUI_EXIT'


def configure_gigbox_wiring():
    """Expose GIGBOX GPIOs to lib_zyncore before it is initialized."""
    if wiring_layout != "GIGBOX":
        return

    pins = [-1] * 36
    pin_by_switch = {
        3: 13,
        4: 17, 5: 27, 6: 22, 7: 23, 8: 24,
        9: 16, 10: 7, 11: 8, 12: 9, 13: 25,
        14: 26, 15: 12, 16: 4, 17: 10, 18: 11,
    }
    for switch, pin in pin_by_switch.items():
        pins[switch] = pin
    os.environ['ZYNTHIAN_WIRING_LAYOUT'] = 'GIGBOX'
    os.environ['ZYNTHIAN_WIRING_SWITCHES'] = ','.join(str(pin) for pin in pins)

def config_zynpot2switch():
    global zynpot2switch, num_zynpots
    zynpot2switch = []
    if num_zynpots > 0:
        for i, cuias in enumerate(custom_switch_ui_actions):
            try:
                if cuias and cuias['S'].startswith("V5_ZYNPOT_SWITCH"):
                    zynpot2switch.append(4 + i)
            except: pass
        if len(zynpot2switch) < num_zynpots:
            zynpot2switch = [0, 1, 2, 3]
        logging.info(f"zynpot2switch => {zynpot2switch}")

# ------------------------------------------------------------------------------
# MIDI Configuration
# ------------------------------------------------------------------------------
def set_midi_config():
    global active_midi_channel, midi_prog_change_zs3, midi_bank_change, midi_fine_tuning
    global midi_usb_by_port, transport_clock_source, transport_analog_clock_divisor
    global midi_filter_rules, midi_network_enabled, midi_rtpmidi_enabled, midi_netump_enabled
    global midi_touchosc_enabled, bluetooth_enabled, ble_controller, midi_aubionotes_enabled
    midi_fine_tuning = float(os.environ.get('ZYNTHIAN_MIDI_FINE_TUNING', "440.0"))
    active_midi_channel = get_env_int('ZYNTHIAN_MIDI_ACTIVE_CHANNEL', 0)
    midi_prog_change_zs3 = get_env_int('ZYNTHIAN_MIDI_PROG_CHANGE_ZS3', 1)
    midi_bank_change = get_env_int('ZYNTHIAN_MIDI_BANK_CHANGE', 0)
    midi_usb_by_port = get_env_int("ZYNTHIAN_MIDI_USB_BY_PORT", 0)
    midi_network_enabled = get_env_int('ZYNTHIAN_MIDI_NETWORK_ENABLED', 1)
    midi_netump_enabled = get_env_int('ZYNTHIAN_MIDI_NETUMP_ENABLED', 1)
    midi_rtpmidi_enabled = get_env_int('ZYNTHIAN_MIDI_RTPMIDI_ENABLED', 1)
    midi_touchosc_enabled = get_env_int('ZYNTHIAN_MIDI_TOUCHOSC_ENABLED', 0)
    bluetooth_enabled = get_env_int('ZYNTHIAN_MIDI_BLE_ENABLED', 0)
    ble_controller = os.environ.get('ZYNTHIAN_MIDI_BLE_CONTROLLER', "")
    midi_aubionotes_enabled = get_env_int('ZYNTHIAN_MIDI_AUBIONOTES_ENABLED', 0)
    transport_clock_source = get_env_int('ZYNTHIAN_MIDI_TRANSPORT_CLOCK_SOURCE', 0)
    transport_analog_clock_divisor = get_env_int('ZYNTHIAN_MIDI_TRANSPORT_ANALOG_CLOCK_DIVISOR', 1)
    midi_filter_rules = os.environ.get('ZYNTHIAN_MIDI_FILTER_RULES', "").replace("\\n", "\n")

def set_mmc_config():
    global master_midi_channel, master_midi_change_type, master_midi_note_cuia
    global master_midi_program_change_up, master_midi_program_change_down
    global master_midi_program_base, master_midi_bank_change_ccnum
    global master_midi_bank_change_up, master_midi_bank_change_down
    global master_midi_bank_change_down_ccnum, master_midi_bank_base
    master_midi_channel = int(os.environ.get("ZYNTHIAN_MIDI_MASTER_CHANNEL", 0)) - 1
    if master_midi_channel > 15: master_midi_channel = 15
    master_midi_change_type = os.environ.get("ZYNTHIAN_MIDI_MASTER_CHANGE_TYPE", "Roland")
    master_midi_bank_change_ccnum = get_env_int("ZYNTHIAN_MIDI_MASTER_BANK_CHANGE_CCNUM", 0x20)
    mmpcu = os.environ.get('ZYNTHIAN_MIDI_MASTER_PROGRAM_CHANGE_UP', "")
    if master_midi_channel >= 0 and len(mmpcu) == 4:
        try:
            ev = int("{:<06}".format(mmpcu.replace("#", hex(master_midi_channel)[2])), 16)
            master_midi_program_change_up = ev.to_bytes(3, 'big')
        except: pass
    mmpcd = os.environ.get('ZYNTHIAN_MIDI_MASTER_PROGRAM_CHANGE_DOWN', "")
    if master_midi_channel >= 0 and len(mmpcd) == 4:
        try:
            ev = int("{:<06}".format(mmpcd.replace("#", hex(master_midi_channel)[2])), 16)
            master_midi_program_change_down = ev.to_bytes(3, 'big')
        except: pass
    mmbcu = os.environ.get('ZYNTHIAN_MIDI_MASTER_BANK_CHANGE_UP', "")
    if master_midi_channel >= 0 and len(mmbcu) == 6:
        try:
            ev = int("{:<06}".format(mmbcu.replace("#", hex(master_midi_channel)[2])), 16)
            master_midi_bank_change_up = ev.to_bytes(3, 'big')
        except: pass
    mmbcd = os.environ.get('ZYNTHIAN_MIDI_MASTER_BANK_CHANGE_DOWN', "")
    if master_midi_channel >= 0 and len(mmbcd) == 6:
        try:
            ev = int("{:<06}".format(mmbcd.replace("#", hex(master_midi_channel)[2])), 16)
            master_midi_bank_change_down = ev.to_bytes(3, 'big')
        except: pass
    mmncuia_envar = os.environ.get('ZYNTHIAN_MIDI_MASTER_NOTE_CUIA', None)
    if mmncuia_envar is None:
        master_midi_note_cuia = zynconf.NoteCuiaDefault
    else:
        master_midi_note_cuia = {}
        for cuianote in mmncuia_envar.split('\\n'):
            cuianote = cuianote.strip()
            if cuianote:
                try:
                    parts = cuianote.split(':')
                    note = parts[0].strip()
                    cuia = parts[1].strip()
                    if note and cuia:
                        master_midi_note_cuia[note] = cuia
                except Exception as err:
                    logging.warning("Bad MIDI Master Note CUIA config {} => {}".format(cuianote, err))

# ------------------------------------------------------------------------------
# UI Color Parameters - GIGBOX DARK NEON RED THEME
# Near black backgrounds, neon red accents, PCB trace design
# ------------------------------------------------------------------------------

# Core palette
color_bg = "#030303"                    # Near black background
color_tx = "#ffffff"                    # Primary text - white
color_tx_off = "#8a8a8a"                # Dim text - medium grey
color_on = "#ff1744"                    # Neon red - PRIMARY ACCENT
color_off = "#1a1a1a"                   # Off state - dark grey
color_hl = "#ff3355"                    # Highlight - bright neon red
color_ml = "#ffcc00"                    # MIDI yellow (selective use only)
color_low_on = "#aa0011"                # Low intensity red
color_panel_bg = "#080808"              # Panel background - slightly lighter than bg
color_panel_hl = "#0d0d0d"              # Panel highlight
color_info = "#ff1744"                  # Info - neon red
color_midi = "#ff3355"                  # MIDI indicator - bright neon red
color_alt = "#ff1744"                   # Alt accent - neon red (not purple)
color_alt2 = "#ffaa00"                  # Alt2 - amber (selective use)
color_error = "#ff1744"                 # Error - neon red

# Derived color scheme
color_panel_bd = "#1a1a1a"              # Panel border - subtle grey line
color_panel_tx = "#ffffff"
color_header_bg = "#050505"
color_header_tx = "#ffffff"
color_ctrl_bg_off = "#1a1a1a"
color_ctrl_bg_on = "#ff1744"
color_ctrl_tx = "#ffffff"
color_ctrl_tx_off = "#8a8a8a"
color_status_midi = "#ff3355"
color_status_play = "#ff1744"
color_status_record = "#aa0011"
color_status_play_midi = "#ffaa00"
color_status_play_seq = "#ff1744"
color_status_error = "#ff1744"

# PCB trace colors
color_pcb_trace = "#2a0808"             # Subtle red trace lines
color_pcb_trace_bright = "#3a1010"      # Brighter trace for hover
color_pcb_via = "#ff1744"               # Via points - neon red

# Pad colors - all red family, no rainbow
PAD_COLOUR_DISABLED = '#1a1a1a'
PAD_COLOUR_DISABLED_LIGHT = '#2a2a2a'
PAD_COLOUR_STARTING = '#ffaa00'
PAD_COLOUR_PLAYING = '#ff1744'
PAD_COLOUR_STOPPING = '#aa0011'
PAD_COLOUR_GROUP = [
    '#ff1744', '#ff3355', '#ff4466', '#ff5577',  # Red variations
    '#cc0022', '#aa0011', '#ee2244', '#dd3355',
    '#ff1744', '#ff3355', '#ff4466', '#ff5577',
    '#cc0022', '#aa0011', '#ee2244', '#dd3355',
    '#ff1744', '#ff3355',
]

def color_variant(hex_color, brightness_offset=1):
    if len(hex_color) != 7:
        raise Exception("Passed %s into color_variant(), needs #87c95f format." % hex_color)
    rgb_hex = [hex_color[x:x+2] for x in [1, 3, 5]]
    new_rgb_int = [int(h, 16) + brightness_offset for h in rgb_hex]
    new_rgb_int = [min(255, max(0, i)) for i in new_rgb_int]
    return "#" + "".join([hex(i)[2:].zfill(2) for i in new_rgb_int])

PAD_COLOUR_GROUP_LIGHT = [color_variant(c, 40) for c in PAD_COLOUR_GROUP]

# ------------------------------------------------------------------------------
# Font Family - Audiowide for futuristic look
# ------------------------------------------------------------------------------
font_family = "Audiowide"

# ------------------------------------------------------------------------------
# Touch Options - GIGBOX has hardware controls, minimal touch
# ------------------------------------------------------------------------------
touch_navigation = os.environ.get('ZYNTHIAN_UI_TOUCH_NAVIGATION2', '_UNDEF_')
if touch_navigation == "_UNDEF_":
    touch_navigation = os.environ.get('ZYNTHIAN_UI_TOUCH_NAVIGATION', '')
    if touch_navigation == "1":
        touch_navigation = "touch_widgets"
    elif touch_navigation == "0":
        touch_keypad = os.environ.get('ZYNTHIAN_TOUCH_KEYPAD', '')
        if touch_keypad == "V5":
            touch_navigation = "v5_keypad_left"
        else:
            touch_navigation = None

match touch_navigation:
    case "touch_widgets":
        enable_touch_navigation = True
        touch_keypad_option = ""
        touch_keypad_side_left = True
        enable_touch_controller_switches = 1
        main_screen_column = 0
    case "v5_keypad_left":
        enable_touch_navigation = False
        touch_keypad_option = "V5"
        touch_keypad_side_left = True
        enable_touch_controller_switches = 1
        main_screen_column = 1
    case "v5_keypad_right":
        enable_touch_navigation = False
        touch_keypad_option = "V5"
        touch_keypad_side_left = False
        enable_touch_controller_switches = 1
        main_screen_column = 0
    case _:
        enable_touch_navigation = False
        touch_keypad_option = ""
        touch_keypad_side_left = True
        enable_touch_controller_switches = 0
        main_screen_column = 0

try:
    force_enable_cursor = get_env_int('ZYNTHIAN_UI_ENABLE_CURSOR', 0)
except:
    force_enable_cursor = 0

if touch_keypad_option == "V5" and wiring_layout == "TOUCH_ONLY":
    if os.environ.get("ZYNTHIAN_WIRING_LAYOUT_CUSTOM_PROFILE", "") != "v5":
        config_dir = os.environ.get("ZYNTHIAN_CONFIG_DIR", "/zynthian/config")
        zynconf.load_plain_envars(f"{config_dir}/wiring-profiles/v5", True)
        os.environ["ZYNTHIAN_WIRING_SWITCHES"] = ",".join(36 * ["-1"])

# ------------------------------------------------------------------------------
# UI Options
# ------------------------------------------------------------------------------
restore_last_state = get_env_int('ZYNTHIAN_UI_RESTORE_LAST_STATE', 1)
snapshot_mixer_settings = get_env_int('ZYNTHIAN_UI_SNAPSHOT_MIXER_SETTINGS', 1)
show_cpu_status = get_env_int('ZYNTHIAN_UI_SHOW_CPU_STATUS', 1)
visible_mixer_strips = get_env_int('ZYNTHIAN_UI_VISIBLE_MIXER_STRIPS', 0)
ctrl_graph = get_env_int('ZYNTHIAN_UI_CTRL_GRAPH', 1)
control_test_enabled = get_env_int('ZYNTHIAN_UI_CONTROL_TEST_ENABLED', 0)
power_save_secs = 60 * get_env_int('ZYNTHIAN_UI_POWER_SAVE_MINUTES', 0)
preset_preload = get_env_int('ZYNTHIAN_UI_PRESET_PRELOAD', 1)

# ------------------------------------------------------------------------------
# Audio Options
# ------------------------------------------------------------------------------
rbpi_headphones = get_env_int('ZYNTHIAN_RBPI_HEADPHONES', 1)
enable_dpm = get_env_int('ZYNTHIAN_DPM', 1)
hotplug_audio_enabled = get_env_int('ZYNTHIAN_HOTPLUG_AUDIO', 1)
disabled_audio_in = os.environ.get('ZYNTHIAN_HOTPLUG_AUDIO_DISABLED_IN', "").split(',')
disabled_audio_out = os.environ.get('ZYNTHIAN_HOTPLUG_AUDIO_DISABLED_OUT', '').split(',')

# ------------------------------------------------------------------------------
# Networking Options
# ------------------------------------------------------------------------------
vncserver_enabled = get_env_int('ZYNTHIAN_VNCSERVER_ENABLED', 0)

# ------------------------------------------------------------------------------
# Player configuration
# ------------------------------------------------------------------------------
midi_play_loop = get_env_int('ZYNTHIAN_MIDI_PLAY_LOOP', 0)
audio_play_loop = get_env_int('ZYNTHIAN_AUDIO_PLAY_LOOP', 0)

# ------------------------------------------------------------------------------
# Experimental features
# ------------------------------------------------------------------------------
experimental_features = os.environ.get('ZYNTHIAN_EXPERIMENTAL_FEATURES', "").split(',')

# ------------------------------------------------------------------------------
# GIGBOX Specific: Animation & Transition Settings
# ------------------------------------------------------------------------------
gigbox_fade_duration = get_env_int('GIGBOX_FADE_DURATION', 150)  # ms
gigbox_transition_easing = "ease-out-cubic"
gigbox_pcb_trace_animation = get_env_int('GIGBOX_PCB_TRACE_ANIM', 1)
gigbox_boot_animation = get_env_int('GIGBOX_BOOT_ANIMATION', 1)

# ------------------------------------------------------------------------------
# X11 Related Stuff
# ------------------------------------------------------------------------------
if "zynthian_main.py" in sys.argv[0]:
    configure_gigbox_wiring()
    import tkinter
    from PIL import Image, ImageTk

    try:
        top = tkinter.Tk()

        if os.environ.get('DISPLAY_WIDTH'):
            display_width = get_env_int('DISPLAY_WIDTH')
        else:
            try:
                display_width = top.winfo_screenwidth()
            except:
                logging.warning("Can't get screen width. Using default 800!")
                display_width = 800

        if os.environ.get('DISPLAY_HEIGHT'):
            display_height = get_env_int('DISPLAY_HEIGHT')
        else:
            try:
                display_height = top.winfo_screenheight()
            except:
                logging.warning("Can't get screen height. Using default 480!")
                display_height = 480

        font_size = get_env_int('ZYNTHIAN_UI_FONT_SIZE', None)
        if not font_size:
            font_size = int(display_width / 40)

        touch_keypad = None
        if touch_keypad_option == 'V5':
            touch_keypad_side_width = display_height // 3
            touch_keypad_bottom_height = display_height // 6
            screen_width = display_width - touch_keypad_side_width
            screen_height = display_height - touch_keypad_bottom_height
            try:
                from zyngui.zynthian_gui_touchkeypad_v5 import zynthian_gui_touchkeypad_v5
                touch_keypad = zynthian_gui_touchkeypad_v5(top, side_width=touch_keypad_side_width, left_side=touch_keypad_side_left)
                touch_keypad.show()
            except Exception as e:
                logging.error(f"Can't start touch keypad {touch_keypad_option} => {e}")

        if not touch_keypad:
            touch_keypad_side_width = 0
            touch_keypad_bottom_height = 0
            screen_width = display_width
            screen_height = display_height

        button_width = screen_width // 4
        if screen_width >= 800:
            topbar_height = screen_height // 12
            topbar_fs = int(1.5 * font_size)
        else:
            topbar_height = screen_height // 10
            topbar_fs = int(1.1 * font_size)

        top.geometry(f'{display_width}x{display_height}')
        top.maxsize(display_width, display_height)
        top.minsize(display_width, display_height)

        if force_enable_cursor or wiring_layout in ("EMULATOR", "TOUCH_ONLY", "GIGBOX"):
            top.config(cursor="arrow")
        else:
            top.config(cursor="none")

        font_listbox = (font_family, int(1.0 * font_size))
        font_topbar = (font_family, topbar_fs)
        font_buttonbar = (font_family, int(0.8 * font_size))

        # GIGBOX Loading Animation - uses custom boot animation
        loading_imgs = []
        try:
            pil_frame = Image.open("./img/zynthian_gui_loading.gif")
            fw, fh = pil_frame.size
            fw2 = screen_width // 4 - 8
            fh2 = int(fh * fw2 / fw)
            nframes = 0
            while pil_frame:
                pil_frame2 = pil_frame.resize((fw2, fh2), Image.LANCZOS)
                loading_imgs.append(ImageTk.PhotoImage(pil_frame2))
                nframes += 1
                try:
                    pil_frame.seek(nframes)
                except EOFError:
                    break
            logging.info(f"GIGBOX loading animation: {nframes} frames loaded")
        except Exception as e:
            logging.warning(f"Could not load GIGBOX boot animation: {e}")
            # Fallback to simple text
            loading_imgs = []

    except Exception as e:
        logging.error("ERROR initializing Tkinter graphic framework => {}".format(e))

    # ------------------------------------------------------------------------------
    # Initialize ZynCore low-level library
    # ------------------------------------------------------------------------------
    from zyncoder.zyncore import lib_zyncore_init

    # ------------------------------------------------------------------------------
    # Initialize and config control I/O subsystem
    # ------------------------------------------------------------------------------
    try:
        lib_zyncore = lib_zyncore_init()
    except Exception as e:
        logging.error(f"lib_zyncore: {e.args[0]} ({e.args[1]})")
        exit(200 + e.args[1])

    try:
        num_zynswitches = lib_zyncore.get_num_zynswitches()
        last_zynswitch_index = lib_zyncore.get_last_zynswitch_index()
        num_zynpots = lib_zyncore.get_num_zynpots()
    except Exception as e:
        logging.warning(f"Can't init control I/O subsytem: {e}")
        num_zynswitches = 0
        last_zynswitch_index = -1
        num_zynpots = 0

    config_zynswitch_timing()
    config_custom_switches()
    config_zynpot2switch()
    config_zynaptik()
    config_zyntof()

    # ------------------------------------------------------------------------------
    # Load MIDI config
    # ------------------------------------------------------------------------------
    try:
        set_midi_config()
        set_mmc_config()
    except Exception as e:
        logging.error("ERROR configuring MIDI: {}".format(e))

# ------------------------------------------------------------------------------
# Zynthian GUI object
# ------------------------------------------------------------------------------
zyngui = None

# ------------------------------------------------------------------------------
# GIGBOX Branding Constants
# ------------------------------------------------------------------------------
GIGBOX_BRAND_NAME = "SPOOKI INSTRUMENTS"
GIGBOX_MODEL_NAME = "GIGBOX"
GIGBOX_VERSION = "1.0.0"
