#!/usr/bin/python3
# -*- coding: utf-8 -*-
# GIGBOX TARGET ROOTFS PYTHON VALIDATION
# Run INSIDE the Zynthian rootfs chroot:
#   sudo chroot /path/to/zynthian/rootfs /usr/bin/python3 /tmp/validate-target-rootfs.py

import sys
import subprocess
import traceback
import json
import os

def test(name, func):
    try:
        result = func()
        print(f"  [PASS] {name}")
        return True
    except Exception as e:
        print(f"  [FAIL] {name}")
        print(f"    Error: {e}")
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("GIGBOX TARGET ROOTFS PYTHON VALIDATION")
    print("=" * 60)
    print(f"Python: {sys.version}")
    print(f"Executable: {sys.executable}")
    print(f"Path: {sys.path[:3]}...")
    print()

    results = []

    # 1. Python syntax validation of GIGBOX modules
    print("1. GIGBOX MODULE SYNTAX")
    results.append(test("gigbox_wiring.py syntax", lambda: compile(open('/zynthian/zynthian-ui/zyngui/gigbox_wiring.py').read(), 'gigbox_wiring.py', 'exec')))
    results.append(test("gigbox_navigation.py syntax", lambda: compile(open('/zynthian/zynthian-ui/zyngui/gigbox_navigation.py').read(), 'gigbox_navigation.py', 'exec')))
    results.append(test("gigbox_transitions.py syntax", lambda: compile(open('/zynthian/zynthian-ui/zyngui/gigbox_transitions.py').read(), 'gigbox_transitions.py', 'exec')))
    results.append(test("zynthian_gui_config.py syntax", lambda: compile(open('/zynthian/zynthian-ui/zyngui/zynthian_gui_config.py').read(), 'zynthian_gui_config.py', 'exec')))
    results.append(test("gigbox-modui-exit-daemon.py syntax", lambda: compile(open('/usr/local/bin/gigbox-modui-exit-daemon.py').read(), 'gigbox-modui-exit-daemon.py', 'exec')))
    results.append(test("gigbox-wifi-midi.py syntax", lambda: compile(open('/usr/local/bin/gigbox-wifi-midi.py').read(), 'gigbox-wifi-midi.py', 'exec')))

    print()
    print("2. ZYNTHIAN CORE IMPORTS")
    results.append(test("zynconf", lambda: __import__('zynconf')))
    results.append(test("zyncoder.zyncore", lambda: __import__('zyncoder.zyncore', fromlist=['lib_zyncore_init'])))
    results.append(test("lib_zyncore_init", lambda: __import__('zyncoder.zyncore', fromlist=['lib_zyncore_init']).lib_zyncore_init))

    print()
    print("3. ZYNGUI IMPORTS")
    results.append(test("zyngui modules", lambda: __import__('zyngui')))
    
    zyngui_modules = [
        'zyngui.zynthian_gui',
        'zyngui.zynthian_gui_config',
        'zyngui.zynthian_soundfont',
        'zyngui.zynthian_gui_controls',
        'zyngui.zynthian_gui_list',
        'zyngui.zynthian_gui_menu',
    ]
    for mod in zyngui_modules:
        results.append(test(f"zyngui.{mod.split('.')[-1]}", lambda m=mod: __import__(m, fromlist=[''])))

    print()
    print("4. GIGBOX MODULE IMPORTS")
    results.append(test("gigbox_wiring", lambda: __import__('gigbox_wiring')))
    results.append(test("gigbox_navigation", lambda: __import__('gigbox_navigation')))
    results.append(test("gigbox_transitions", lambda: __import__('gigbox_transitions')))

    print()
    print("5. LIB_ZYNCORE INITIALIZATION ORDER")
    def test_zyncore_init():
        from zyncoder.zyncore import lib_zyncore_init
        lib = lib_zyncore_init()
        num_sw = lib.get_num_zynswitches()
        num_pots = lib.get_num_zynpots()
        print(f"    Switches: {num_sw}, Pots: {num_pots}")
        # Verify I2S-safe GPIO config (no potentiometer)
        assert num_pots == 0, f"Expected 0 pots, got {num_pots}"
        print("    Pots=0 verified (I2S-safe)")
        return True
    results.append(test("lib_zyncore_init()", test_zyncore_init))

    print()
    print("6. EXTERNAL DEPENDENCIES")
    results.append(test("rtmidi (for WiFi MIDI)", lambda: __import__('rtmidi')))
    results.append(test("PIL (for boot animation)", lambda: __import__('PIL.Image')))
    results.append(test("tkinter (for GUI)", lambda: __import__('tkinter')))

    print()
    print("7. AUDIO CONFIGURATION PARSING")
    def test_alsa_config():
        import alsaaudio
        cards = alsaaudio.cards()
        print(f"    ALSA cards: {cards}")
        return True
    results.append(test("alsaaudio", test_alsa_config))

    print()
    print("8. CONFIG FILE VALIDATION")
    def test_config_files():
        with open('/zynthian/config/gigbox_gpio_map.json') as f:
            data = json.load(f)
        # Verify I2S pins are reserved
        i2s_pins = data['gigbox_gpio_map'].get('i2s_reserved', {}).get('pins', [])
        assert len(i2s_pins) == 4, "I2S pins not properly reserved"
        print("    I2S pins reserved: verified")
        # Verify no buttons use I2S pins
        for btn in data['gigbox_gpio_map']['buttons']:
            assert btn['bcm'] not in [18, 19, 20, 21], f"Button {btn['index']} uses I2S pin {btn['bcm']}"
        print("    No buttons on I2S pins: verified")
        # Verify 18 total GPIO inputs
        encoder_count = 3
        nav_count = 5
        btn_count = len(data['gigbox_gpio_map']['buttons'])
        assert btn_count == 10, f"Expected 10 buttons, got {btn_count}"
        total = encoder_count + nav_count + btn_count
        assert total == 18, f"Expected 18 GPIO inputs, got {total}"
        print(f"    Total GPIO inputs: {total} (verified)")
        return True
    results.append(test("gigbox_gpio_map.json structure", test_config_files))

    def test_wifi_midi_port():
        with open('/usr/local/bin/gigbox-wifi-midi.py') as f:
            content = f.read()
        assert 'UDP_PORT = 4210' in content, "WiFi MIDI port not set to 4210"
        print("    UDP port 4210: verified")
        return True
    results.append(test("gigbox-wifi-midi.py port 4210", test_wifi_midi_port))

    def test_modui_exit_daemon():
        with open('/usr/local/bin/gigbox-modui-exit-daemon.py') as f:
            content = f.read()
        assert 'lib_zyncore' in content, "Exit daemon doesn't use lib_zyncore"
        assert 'gigbox_modui_exit_request' in content, "Exit daemon doesn't use trigger file"
        print("    Exit daemon uses lib_zyncore + trigger: verified")
        return True
    results.append(test("gigbox-modui-exit-daemon.py integration", test_modui_exit_daemon))

    def test_audio_config():
        with open('/etc/asound.conf') as f:
            content = f.read()
        assert 'gigbox_pcm_dac_hw' in content, "PCM DAC hw reference missing"
        assert 'gigbox_usb_dac_hw' in content, "USB DAC hw reference missing"
        assert 'by-id' in content or 'card "PCM"' in content, "Stable device naming missing"
        print("    Stable ALSA device naming: verified")
        return True
    results.append(test("asound.conf stable naming", test_audio_config))

    def test_udev_rules():
        with open('/etc/udev/rules.d/99-gigbox-audio.rules') as f:
            content = f.read()
        assert 'pcm-dac' in content, "PCM DAC udev rule missing"
        assert 'usb-dac' in content, "USB DAC udev rule missing"
        print("    Udev stable symlinks: verified")
        return True
    results.append(test("99-gigbox-audio.rules", test_udev_rules))

    # Summary
    print()
    print("=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    if passed == total:
        print("ALL TESTS PASSED")
        return 0
    else:
        print(f"FAILURES: {total - passed}")
        return 1

if __name__ == "__main__":
    sys.exit(main())