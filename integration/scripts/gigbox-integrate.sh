#!/bin/bash
# GIGBOX OS INTEGRATION SCRIPT
# Run this ON THE TARGET DEVICE (Raspberry Pi) or in a chroot of the Zynthian rootfs
# This script modifies the actual Zynthian OS filesystem to become GIGBOX OS

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

INTEGRATION_DIR="$(dirname "$(readlink -f "$0")")/.."
ZYNTHIAN_UI_DIR="/zynthian/zynthian-ui"
ZYNGUI_DIR="$ZYNTHIAN_UI_DIR/zyngui"
ICONS_DIR="$ZYNTHIAN_UI_DIR/icons"
IMG_DIR="$ZYNTHIAN_UI_DIR/img"
CLEAN_IMG_DIR="$ZYNTHIAN_UI_DIR/img/clean"
CONFIG_DIR="/zynthian/config"
SOUNDFONTS_DIR="/zynthian/zynthian-data/soundfonts"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  GIGBOX OS INTEGRATION${NC}"
echo -e "${BLUE}  SPOOKI INSTRUMENTS${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root (sudo)${NC}"
    exit 1
fi

# Verify we're on a Zynthian system
if [ ! -d "$ZYNGUI_DIR" ] || [ ! -f "$ZYNGUI_DIR/zynthian_gui_config.py" ]; then
    echo -e "${RED}Zynthian UI not found at $ZYNGUI_DIR${NC}"
    echo "This script must run on a Zynthian OS system or in its chroot."
    exit 1
fi

echo -e "${YELLOW}[1/12] Backing up original files...${NC}"
mkdir -p /zynthian/gigbox-backup
cp "$ZYNGUI_DIR/zynthian_gui_config.py" /zynthian/gigbox-backup/zynthian_gui_config.py.orig
cp "$ZYNGUI_DIR/zynthian_gui.py" /zynthian/gigbox-backup/zynthian_gui.py.orig
cp -r "$ICONS_DIR" /zynthian/gigbox-backup/icons.orig 2>/dev/null || true
cp -r "$IMG_DIR" /zynthian/gigbox-backup/img.orig 2>/dev/null || true
cp -r "$CLEAN_IMG_DIR" /zynthian/gigbox-backup/clean.orig 2>/dev/null || true
echo -e "${GREEN}Backups created in /zynthian/gigbox-backup/${NC}"

echo -e "${YELLOW}[2/12] Installing GIGBOX theme configuration...${NC}"
cp "$INTEGRATION_DIR/config/zynthian_gui_config.py" "$ZYNGUI_DIR/zynthian_gui_config.py"
cp "$INTEGRATION_DIR/config/gtk.css" /usr/share/themes/GIGBOX/gtk-3.0/gtk.css 2>/dev/null || {
    mkdir -p /usr/share/themes/GIGBOX/gtk-3.0
    cp "$INTEGRATION_DIR/config/gtk.css" /usr/share/themes/GIGBOX/gtk-3.0/gtk.css
}
echo -e "${GREEN}Theme config installed${NC}"

echo -e "${YELLOW}[3/12] Installing GIGBOX icons (264 PNG files)...${NC}"
cp "$INTEGRATION_DIR/assets/icons"/*.png "$ICONS_DIR/"
echo -e "${GREEN}$(ls "$INTEGRATION_DIR/assets/icons"/*.png 2>/dev/null | wc -l) icons installed${NC}"

echo -e "${YELLOW}[4/12] Installing boot/branding assets...${NC}"
cp "$INTEGRATION_DIR/assets/img/gigbox_boot.png" "$CLEAN_IMG_DIR/zynthian_logo_boot.png"
cp "$INTEGRATION_DIR/assets/img/gigbox_boot_anim.gif" "$IMG_DIR/zynthian_gui_loading.gif"
cp "$INTEGRATION_DIR/assets/img/gigbox_splash_anim.gif" "$CLEAN_IMG_DIR/gigbox_splash_anim.gif"
cp "$INTEGRATION_DIR/assets/img/gigbox_brand_128.png" "$ICONS_DIR/zynthian_logo.png"
cp "$INTEGRATION_DIR/assets/img/gigbox_brand_64.png" "$ICONS_DIR/gigbox_brand_64.png"
cp "$INTEGRATION_DIR/assets/img/boot.png" "$CLEAN_IMG_DIR/boot.png" 2>/dev/null || true
cp "$INTEGRATION_DIR/assets/img/brand.png" "$ICONS_DIR/brand.png" 2>/dev/null || true
echo -e "${GREEN}Boot/branding assets installed${NC}"

echo -e "${YELLOW}[5/12] Installing soundfonts...${NC}"
mkdir -p "$SOUNDFONTS_DIR/GIGBOX"
cp "$INTEGRATION_DIR/assets/soundfonts"/*.sf2 "$SOUNDFONTS_DIR/GIGBOX/" 2>/dev/null || true
sf2_count=$(ls "$SOUNDFONTS_DIR/GIGBOX"/*.sf2 2>/dev/null | wc -l)
echo -e "${GREEN}$sf2_count soundfonts installed to $SOUNDFONTS_DIR/GIGBOX/${NC}"

echo -e "${YELLOW}[6/12] Installing hardware configuration (GPIO, encoder, buttons)...${NC}"
cp "$INTEGRATION_DIR/config/gigbox_wiring.py" "$ZYNGUI_DIR/gigbox_wiring.py"
cp "$INTEGRATION_DIR/config/gigbox_gpio_map.json" "$CONFIG_DIR/gigbox_gpio_map.json"
cp "$INTEGRATION_DIR/config/gigbox_runtime.py" "$ZYNGUI_DIR/gigbox_runtime.py"
echo -e "${GREEN}Hardware config installed${NC}"

echo -e "${YELLOW}Installing live Zynthian action hook...${NC}"
python3 - "$ZYNGUI_DIR/zynthian_gui_config.py" "$ZYNGUI_DIR/zynthian_gui.py" <<'PY'
import sys
from pathlib import Path

config_path, gui_path = map(Path, sys.argv[1:])
config = config_path.read_text()
if "configure_gigbox_wiring()" not in config:
    raise SystemExit("GIGBOX config hook is missing")

gui = gui_path.read_text()
import_marker = "from zyngui import zynthian_gui_keybinding"
if "import gigbox_runtime" not in gui:
    if import_marker not in gui:
        raise SystemExit("Zynthian GUI import marker not found")
    gui = gui.replace(import_marker, import_marker + "\nimport gigbox_runtime", 1)

hook_marker = "        # Initialize OSC\n"
hook = "        # Install GIGBOX actions before UI threads start.\n        gigbox_runtime.install(self)\n\n"
if "gigbox_runtime.install(self)" not in gui:
    if hook_marker not in gui:
        raise SystemExit("Zynthian GUI screen-init marker not found")
    gui = gui.replace(hook_marker, hook + hook_marker, 1)
gui_path.write_text(gui)
PY
echo -e "${GREEN}Live Zynthian action hook installed${NC}"

echo -e "${YELLOW}[7/12] Installing MOD-UI launcher (manual launch, with exit button)...${NC}"
cp "$INTEGRATION_DIR/scripts/gigbox-modui-launcher" /usr/local/bin/gigbox-modui-launcher
chmod +x /usr/local/bin/gigbox-modui-launcher
cp "$INTEGRATION_DIR/scripts/gigbox-modui-exit" /usr/local/bin/gigbox-modui-exit
chmod +x /usr/local/bin/gigbox-modui-exit
cp "$INTEGRATION_DIR/scripts/gigbox-modui-exit-daemon.py" /usr/local/bin/gigbox-modui-exit-daemon.py
chmod +x /usr/local/bin/gigbox-modui-exit-daemon.py
mkdir -p /usr/share/applications
cp "$INTEGRATION_DIR/config/gigbox-modui.desktop" /usr/share/applications/gigbox-modui.desktop
echo -e "${GREEN}MOD-UI launcher installed (manual launch only)${NC}"

echo -e "${YELLOW}[8/12] Installing MOD-UI exit daemon (encoder/nav long-press)...${NC}"
cp "$INTEGRATION_DIR/systemd/gigbox-modui-exit.service" /etc/systemd/system/gigbox-modui-exit.service
systemctl daemon-reload
systemctl enable gigbox-modui-exit.service
echo -e "${GREEN}MOD-UI exit daemon installed and enabled${NC}"

echo -e "${YELLOW}[9/12] Installing WiFi UDP MIDI receiver service (UDP 4210)...${NC}"
cp "$INTEGRATION_DIR/systemd/gigbox-wifi-midi.service" /etc/systemd/system/gigbox-wifi-midi.service
cp "$INTEGRATION_DIR/scripts/gigbox-wifi-midi.py" /usr/local/bin/gigbox-wifi-midi.py
chmod +x /usr/local/bin/gigbox-wifi-midi.py
systemctl daemon-reload
systemctl enable gigbox-wifi-midi.service
echo -e "${GREEN}WiFi UDP MIDI service installed and enabled (port 4210)${NC}"

echo -e "${YELLOW}[10/12] Installing USB DAC / ALSA audio configuration (stable device IDs)...${NC}"
cp "$INTEGRATION_DIR/config/asound.conf" /etc/asound.conf
mkdir -p /etc/gigbox
cp "$INTEGRATION_DIR/config/asound-auto.conf" /etc/gigbox/asound-auto.conf
cp "$INTEGRATION_DIR/udev/99-gigbox-audio.rules" /etc/udev/rules.d/99-gigbox-audio.rules
cp "$INTEGRATION_DIR/config/gigbox-audio.conf" /etc/modprobe.d/gigbox-audio.conf
cp "$INTEGRATION_DIR/scripts/gigbox-audio-hotplug.sh" /usr/local/bin/gigbox-audio-hotplug.sh
chmod +x /usr/local/bin/gigbox-audio-hotplug.sh
cp "$INTEGRATION_DIR/systemd/gigbox-audio-init.service" /etc/systemd/system/gigbox-audio-init.service
mkdir -p /etc/systemd/system/zynthian.service.d
cp "$INTEGRATION_DIR/systemd/zynthian-audio-order.conf" /etc/systemd/system/zynthian.service.d/10-gigbox-audio.conf
systemctl daemon-reload
systemctl enable gigbox-audio-init.service
udevadm control --reload-rules
udevadm trigger
echo -e "${GREEN}USB DAC/ALSA config installed (stable device identification)${NC}"

echo -e "${YELLOW}[11/12] Installing screen transition animations...${NC}"
cp "$INTEGRATION_DIR/scripts/gigbox-transitions.py" "$ZYNGUI_DIR/gigbox_transitions.py"
echo -e "${GREEN}Screen transitions installed${NC}"

echo -e "${YELLOW}[12/12] Installing SooperLooper theme (red beat highlights)...${NC}"
cp "$INTEGRATION_DIR/config/sooperlooper_gigbox.css" /usr/share/sooperlooper/gigbox.css 2>/dev/null || {
    mkdir -p /usr/share/sooperlooper
    cp "$INTEGRATION_DIR/config/sooperlooper_gigbox.css" /usr/share/sooperlooper/gigbox.css
}
echo -e "${GREEN}SooperLooper theme installed${NC}"

echo -e "${YELLOW}[13/13] Installing on-screen navigation controls (no arrow buttons)...${NC}"
cp "$INTEGRATION_DIR/config/gigbox_navigation.py" "$ZYNGUI_DIR/gigbox_navigation.py"
echo -e "${GREEN}On-screen navigation configured${NC}"

echo -e "${YELLOW}[14/14] Installing boot animation & branding...${NC}"
if [ -f "$INTEGRATION_DIR/scripts/gigbox-boot-branding.sh" ]; then
    cp "$INTEGRATION_DIR/scripts/gigbox-boot-branding.sh" /usr/local/bin/gigbox-boot-branding.sh
    chmod +x /usr/local/bin/gigbox-boot-branding.sh
    /usr/local/bin/gigbox-boot-branding.sh
fi
echo -e "${GREEN}Boot animation & branding installed${NC}"

echo -e "${YELLOW}Setting permissions...${NC}"
chown -R zynthian:zynthian "$ZYNGUI_DIR" 2>/dev/null || true
chown -R zynthian:zynthian "$ICONS_DIR" 2>/dev/null || true
chown -R zynthian:zynthian "$IMG_DIR" 2>/dev/null || true
chown -R zynthian:zynthian "$SOUNDFONTS_DIR/GIGBOX" 2>/dev/null || true
chown zynthian:zynthian "$ZYNGUI_DIR/gigbox_runtime.py" 2>/dev/null || true

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  GIGBOX OS INTEGRATION COMPLETE!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Reboot the system"
echo "  2. GIGBOX branding will appear at boot"
echo "  3. MOD-UI launches only when selected from menu"
echo "  4. Long-press BACK/CANCEL to exit MOD-UI"
echo "  5. WiFi UDP MIDI runs automatically"
echo ""
echo -e "${BLUE}To revert: Run /zynthian/gigbox-backup/restore.sh${NC}"
