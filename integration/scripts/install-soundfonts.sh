#!/bin/bash
# GIGBOX Soundfont Installer
# SPOOKI INSTRUMENTS - GIGBOX
# Installs SF2 soundfonts into Zynthian soundfont library
# Run as root on target device or in chroot

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Source directory (where SF2 files are located on build machine)
SOURCE_DIR="${1:-/mnt/h/GIGBOX_BUILD/assets/soundfonts}"

# Target directory in Zynthian OS
TARGET_DIR="/zynthian/zynthian-data/soundfonts/GIGBOX"

# Zynthian user
ZYNTHIAN_USER="zynthian"
ZYNTHIAN_GROUP="zynthian"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  GIGBOX SOUNDFONT INSTALLER${NC}"
echo -e "${BLUE}  SPOOKI INSTRUMENTS${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root (sudo)${NC}"
    exit 1
fi

# Check source directory
if [ ! -d "$SOURCE_DIR" ]; then
    echo -e "${RED}Source directory not found: $SOURCE_DIR${NC}"
    echo "Usage: $0 [source_directory]"
    echo "Default source: /mnt/h/GIGBOX_BUILD/assets/soundfonts"
    exit 1
fi

# Count SF2 files
SF2_FILES=("$SOURCE_DIR"/*.sf2)
SF2_COUNT=${#SF2_FILES[@]}

if [ $SF2_COUNT -eq 0 ] || [ ! -f "${SF2_FILES[0]}" ]; then
    echo -e "${RED}No .sf2 files found in $SOURCE_DIR${NC}"
    exit 1
fi

echo -e "${YELLOW}Found $SF2_COUNT soundfont files${NC}"
echo ""

# Create target directory
echo -e "${YELLOW}Creating target directory: $TARGET_DIR${NC}"
mkdir -p "$TARGET_DIR"

# Copy soundfonts
echo -e "${YELLOW}Copying soundfonts...${NC}"
COPIED=0
FAILED=0

for sf2 in "${SF2_FILES[@]}"; do
    filename=$(basename "$sf2")
    target="$TARGET_DIR/$filename"
    
    if [ -f "$target" ]; then
        # Check if file is different
        if cmp -s "$sf2" "$target"; then
            echo -e "  ${GREEN}✓${NC} $filename (already up to date)"
            continue
        else
            echo -e "  ${YELLOW}↻${NC} $filename (updating)"
        fi
    else
        echo -e "  ${BLUE}+${NC} $filename"
    fi
    
    if cp "$sf2" "$target"; then
        COPIED=$((COPIED + 1))
    else
        echo -e "  ${RED}✗${NC} $filename (FAILED)"
        FAILED=$((FAILED + 1))
    fi
done

# Set permissions
echo -e "${YELLOW}Setting permissions...${NC}"
chown -R "$ZYNTHIAN_USER:$ZYNTHIAN_GROUP" "$TARGET_DIR"
chmod -R 644 "$TARGET_DIR"/*.sf2

# Verify installation
echo -e "${YELLOW}Verifying installation...${NC}"
INSTALLED=$(ls -1 "$TARGET_DIR"/*.sf2 2>/dev/null | wc -l)
TOTAL_SIZE=$(du -sh "$TARGET_DIR" | cut -f1)

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  INSTALLATION COMPLETE${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "Soundfonts installed: ${GREEN}$INSTALLED${NC}"
echo -e "Total size: ${GREEN}$TOTAL_SIZE${NC}"
echo -e "Location: ${GREEN}$TARGET_DIR${NC}"
echo ""

if [ $FAILED -gt 0 ]; then
    echo -e "${RED}$FAILED file(s) failed to copy${NC}"
    exit 1
fi

# Update FluidSynth soundfont database (if applicable)
if command -v fluidsynth >/dev/null 2>&1; then
    echo -e "${YELLOW}Updating FluidSynth soundfont cache...${NC}"
    # FluidSynth doesn't have a cache, but we can verify files are readable
    for sf2 in "$TARGET_DIR"/*.sf2; do
        if fluidsynth --dump-midi "$sf2" >/dev/null 2>&1; then
            log "Verified: $(basename "$sf2")"
        else
            log "Warning: Could not verify $(basename "$sf2")"
        fi
    done
fi

# Update Zynthian soundfont index
echo -e "${YELLOW}Updating Zynthian soundfont index...${NC}"
if [ -f /zynthian/zynthian-ui/zyngui/zynthian_soundfont.py ]; then
    python3 -c "
import sys
sys.path.insert(0, '/zynthian/zynthian-ui')
from zyngui.zynthian_soundfont import refresh_soundfont_list
refresh_soundfont_list()
print('Soundfont list refreshed')
" 2>/dev/null || echo "Soundfont list will refresh on next Zynthian start"
fi

echo ""
echo -e "${GREEN}Done! Soundfonts will appear in Zynthian under 'GIGBOX' bank.${NC}"
echo -e "${BLUE}Reboot or restart Zynthian UI to see new soundfonts.${NC}"