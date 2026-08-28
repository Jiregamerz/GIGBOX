#!/usr/bin/python3
"""Live GIGBOX actions installed into the running Zynthian GUI."""

import logging
import subprocess
import types

from zyncoder.zyncore import lib_zyncore

LOGGER = logging.getLogger("GIGBOX")
TRANSPOSE_MIN = -24
TRANSPOSE_MAX = 24


def _set_global_transpose(zyngui, value):
    value = max(TRANSPOSE_MIN, min(TRANSPOSE_MAX, value))
    lib_zyncore.set_global_transpose(value)
    try:
        zyngui.show_info(f"Transpose {value:+d}", 700)
    except Exception:
        pass


def cuia_gigbox_transpose_up(zyngui, params=None):
    _set_global_transpose(zyngui, lib_zyncore.get_global_transpose() + 1)


def cuia_gigbox_transpose_down(zyngui, params=None):
    _set_global_transpose(zyngui, lib_zyncore.get_global_transpose() - 1)


def cuia_gigbox_octave_up(zyngui, params=None):
    _set_global_transpose(zyngui, lib_zyncore.get_global_transpose() + 12)


def cuia_gigbox_octave_down(zyngui, params=None):
    _set_global_transpose(zyngui, lib_zyncore.get_global_transpose() - 12)


def cuia_gigbox_sustain(zyngui, params=None):
    enabled = not getattr(zyngui, "gigbox_sustain_enabled", False)
    zyngui.gigbox_sustain_enabled = enabled
    value = 127 if enabled else 0
    for channel in range(16):
        lib_zyncore.write_zynmidi_ccontrol_change(channel, 64, value)
    try:
        zyngui.show_info(f"Sustain {'ON' if enabled else 'OFF'}", 700)
    except Exception:
        pass


def cuia_gigbox_modui(zyngui, params=None):
    try:
        subprocess.Popen(
            ["/usr/local/bin/gigbox-modui-launcher"],
            start_new_session=True,
            close_fds=True,
        )
    except Exception as err:
        LOGGER.error("Unable to launch MOD-UI: %s", err)
        try:
            zyngui.show_info("MOD-UI launch failed", 1500)
        except Exception:
            pass


def cuia_gigbox_modui_exit(zyngui, params=None):
    """Exit MOD-UI when active, otherwise preserve normal BACK behavior."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "chromium.*http://localhost:8888"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=1,
        )
        if result.returncode == 0:
            subprocess.run(["/usr/local/bin/gigbox-modui-exit"], timeout=2)
            return
    except Exception as err:
        LOGGER.debug("MOD-UI process check failed: %s", err)
    zyngui.back_screen()


def _remove_duplicate_touch_controls(screen):
    config = getattr(screen, "buttonbar_config", None)
    if not config:
        return
    duplicate_names = (
        "arrow_left", "arrow_right", "arrow_up", "arrow_down",
        "transpose_up", "transpose_down", "octave_up", "octave_down",
        "sustain", "main_menu", "screen_mixer", "screen_zs3", "alt",
    )

    def is_duplicate(item):
        text = " ".join(str(part).lower() for part in item)
        return any(name in text for name in duplicate_names)

    screen.buttonbar_config = [
        item for item in config
        if not is_duplicate(item)
    ]
    if hasattr(screen, "buttonbar_frame") and screen.buttonbar_frame:
        init_buttonbar = getattr(screen, "init_buttonbar", None)
        if callable(init_buttonbar):
            init_buttonbar()


def _install_modui_button(zyngui):
    try:
        import tkinter
        from zyngui import zynthian_gui_config

        if getattr(zyngui, "gigbox_modui_button", None):
            return
        button = tkinter.Button(
            zynthian_gui_config.top,
            text="MOD UI",
            command=lambda: cuia_gigbox_modui(zyngui),
            bg="#080808",
            fg="#ff3355",
            activebackground="#ff1744",
            activeforeground="#ffffff",
            relief=tkinter.FLAT,
            bd=0,
            highlightthickness=1,
            highlightbackground="#2a2a2a",
            font=zynthian_gui_config.font_buttonbar,
        )
        button.place(relx=1.0, rely=0.0, anchor="ne", x=-4, y=2)
        zyngui.gigbox_modui_button = button
    except Exception as err:
        LOGGER.warning("Could not create MOD-UI touch control: %s", err)


def install(zyngui):
    """Install custom actions after core screens exist and before threads start."""
    actions = {
        "cuia_gigbox_transpose_up": cuia_gigbox_transpose_up,
        "cuia_gigbox_transpose_down": cuia_gigbox_transpose_down,
        "cuia_gigbox_octave_up": cuia_gigbox_octave_up,
        "cuia_gigbox_octave_down": cuia_gigbox_octave_down,
        "cuia_gigbox_sustain": cuia_gigbox_sustain,
        "cuia_gigbox_modui": cuia_gigbox_modui,
        "cuia_gigbox_modui_exit": cuia_gigbox_modui_exit,
    }
    for name, func in actions.items():
        setattr(zyngui, name, types.MethodType(func, zyngui))

    original_long = zyngui.zynswitch_long

    def gigbox_encoder_long(self, switch):
        # Switch 3 is the encoder push input in the GIGBOX wiring profile.
        if switch == 3:
            screen = self.screens.get(self.current_screen)
            if screen and callable(getattr(screen, "switch", None)):
                if screen.switch(switch, "L"):
                    return True
            cuia_gigbox_modui_exit(self)
            return True
        return original_long(switch)

    zyngui.zynswitch_long = types.MethodType(gigbox_encoder_long, zyngui)

    screens = []
    for screen in zyngui.screens.values():
        if screen not in screens:
            screens.append(screen)
    for screen in screens:
        _remove_duplicate_touch_controls(screen)
    _install_modui_button(zyngui)
    LOGGER.info("GIGBOX runtime actions installed")
