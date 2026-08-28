#!/bin/bash
# GIGBOX Audio Hotplug Handler - Stable Device Naming
# SPOOKI INSTRUMENTS - GIGBOX
# Called by udev when audio devices are added/removed
# Updates ALSA configuration for stable device references

CARD="$1"
ACTION="$2"

LOG_FILE="/var/log/gigbox-audio-hotplug.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log "Audio hotplug: card=$CARD action=$ACTION"

# Wait a moment for ALSA to settle
sleep 1

# List current audio cards
log "Current audio cards:"
cat /proc/asound/cards >> "$LOG_FILE" 2>&1

# Check for PCM DAC (I2S) presence
PCM_DAC_PRESENT=false
USB_DAC_PRESENT=false

if grep -q "pcm-dac" /dev/snd/by-id/ 2>/dev/null; then
    PCM_DAC_PRESENT=true
    log "PCM DAC (I2S) detected via stable symlink"
fi

if grep -q "usb-dac" /dev/snd/by-id/ 2>/dev/null; then
    USB_DAC_PRESENT=true
    log "USB DAC detected via stable symlink"
fi

# Also check by card names in /proc/asound/cards
if cat /proc/asound/cards | grep -qi "hifiberry\|iqaudio\|rpi-dac\|bcm2835-i2s\|i2s"; then
    PCM_DAC_PRESENT=true
    log "PCM DAC detected via card name"
fi

if cat /proc/asound/cards | grep -qi "USB"; then
    USB_DAC_PRESENT=true
    log "USB DAC detected via card name"
fi

if [ "$ACTION" = "add" ]; then
    log "Audio device added: $CARD"
    
    if [ "$USB_DAC_PRESENT" = true ]; then
        log "USB audio device now available"
    fi
    
elif [ "$ACTION" = "remove" ]; then
    log "Audio device removed: $CARD"
    
    if [ "$USB_DAC_PRESENT" = false ]; then
        log "No USB audio devices remaining - using PCM DAC only"
    fi
fi

# Trigger Zynthian audio refresh via D-Bus if available
if command -v dbus-send >/dev/null 2>&1; then
    dbus-send --system --dest=org.zynthian.Audio --type=method_call /org/zynthian/Audio org.zynthian.Audio.RefreshDevices 2>/dev/null || true
fi

# Also trigger via systemd if alsa-restore is available
systemctl reload alsa-state 2>/dev/null || true

exit 0