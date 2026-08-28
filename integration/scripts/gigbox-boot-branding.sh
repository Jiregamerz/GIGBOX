#!/bin/bash
# GIGBOX Boot Animation & Branding Integration
# SPOOKI INSTRUMENTS - GIGBOX
# Integrates custom boot animation and branding into Zynthian OS
# Run on target device or in chroot

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

INTEGRATION_DIR="$(dirname "$(readlink -f "$0")")/.."
BOOT_DIR="/boot"
CLEAN_IMG_DIR="/zynthian/zynthian-ui/img/clean"
IMG_DIR="/zynthian/zynthian-ui/img"
ICONS_DIR="/zynthian/zynthian-ui/icons"
PLYMOUTH_DIR="/usr/share/plymouth/themes"
GRUB_DIR="/boot/grub"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  GIGBOX BOOT ANIMATION & BRANDING${NC}"
echo -e "${BLUE}  SPOOKI INSTRUMENTS${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root (sudo)${NC}"
    exit 1
fi

echo -e "${YELLOW}[1/8] Backing up original boot assets...${NC}"
mkdir -p /zynthian/gigbox-backup/boot
cp -r "$BOOT_DIR"/* /zynthian/gigbox-backup/boot/ 2>/dev/null || true
cp "$CLEAN_IMG_DIR/zynthian_logo_boot.png" /zynthian/gigbox-backup/zynthian_logo_boot.png.orig 2>/dev/null || true
cp "$IMG_DIR/zynthian_gui_loading.gif" /zynthian/gigbox-backup/zynthian_gui_loading.gif.orig 2>/dev/null || true
echo -e "${GREEN}Backups created${NC}"

echo -e "${YELLOW}[2/8] Installing GIGBOX boot logo (static)...${NC}"
if [ -f "$INTEGRATION_DIR/assets/img/gigbox_boot.png" ]; then
    cp "$INTEGRATION_DIR/assets/img/gigbox_boot.png" "$CLEAN_IMG_DIR/zynthian_logo_boot.png"
    cp "$INTEGRATION_DIR/assets/img/boot.png" "$CLEAN_IMG_DIR/boot.png" 2>/dev/null || true
    echo -e "${GREEN}Static boot logo installed${NC}"
else
    echo -e "${RED}Warning: gigbox_boot.png not found${NC}"
fi

echo -e "${YELLOW}[3/8] Installing GIGBOX boot animation (GIF)...${NC}"
if [ -f "$INTEGRATION_DIR/assets/img/gigbox_boot_anim.gif" ]; then
    cp "$INTEGRATION_DIR/assets/img/gigbox_boot_anim.gif" "$IMG_DIR/zynthian_gui_loading.gif"
    echo -e "${GREEN}Boot animation (GIF) installed${NC}"
else
    echo -e "${RED}Warning: gigbox_boot_anim.gif not found${NC}"
fi

echo -e "${YELLOW}[4/8] Installing GIGBOX splash animation...${NC}"
if [ -f "$INTEGRATION_DIR/assets/img/gigbox_splash_anim.gif" ]; then
    cp "$INTEGRATION_DIR/assets/img/gigbox_splash_anim.gif" "$CLEAN_IMG_DIR/gigbox_splash_anim.gif"
    echo -e "${GREEN}Splash animation installed${NC}"
else
    echo -e "${RED}Warning: gigbox_splash_anim.gif not found${NC}"
fi

echo -e "${YELLOW}[5/8] Installing GIGBOX branding icons...${NC}"
if [ -f "$INTEGRATION_DIR/assets/img/gigbox_brand_128.png" ]; then
    cp "$INTEGRATION_DIR/assets/img/gigbox_brand_128.png" "$ICONS_DIR/zynthian_logo.png"
    cp "$INTEGRATION_DIR/assets/img/brand.png" "$ICONS_DIR/brand.png" 2>/dev/null || true
    echo -e "${GREEN}128px brand logo installed${NC}"
fi
if [ -f "$INTEGRATION_DIR/assets/img/gigbox_brand_64.png" ]; then
    cp "$INTEGRATION_DIR/assets/img/gigbox_brand_64.png" "$ICONS_DIR/gigbox_brand_64.png"
    echo -e "${GREEN}64px brand logo installed${NC}"
fi

echo -e "${YELLOW}[6/8] Configuring Plymouth boot theme (if available)...${NC}"
if [ -d "$PLYMOUTH_DIR" ]; then
    # Create GIGBOX Plymouth theme
    GIGBOX_PLYMOUTH_DIR="$PLYMOUTH_DIR/gigbox"
    mkdir -p "$GIGBOX_PLYMOUTH_DIR"
    
    cat > "$GIGBOX_PLYMOUTH_DIR/gigbox.plymouth" << 'PLYEOF'
[Plymouth Theme]
Name=GIGBOX
Description=GIGBOX SPOOKI INSTRUMENTS Boot Theme
ModuleName=script

[script]
ImageDir=/usr/share/plymouth/themes/gigbox
ScriptFile=/usr/share/plymouth/themes/gigbox/gigbox.script
PLYEOF
    
    # Copy boot animation as Plymouth background
    if [ -f "$INTEGRATION_DIR/assets/img/gigbox_boot.png" ]; then
        cp "$INTEGRATION_DIR/assets/img/gigbox_boot.png" "$GIGBOX_PLYMOUTH_DIR/background.png"
    fi
    
    # Create simple Plymouth script
    cat > "$GIGBOX_PLYMOUTH_DIR/gigbox.script" << 'SCREOF'
# GIGBOX Plymouth Boot Script
# Minimal - shows logo with subtle pulse

background = Image("background.png");
screen_width = Window.GetWidth();
screen_height = Window.GetHeight();

# Scale background to fit
bg_sprite = Sprite(background);
bg_sprite.SetX((screen_width - background.GetWidth()) / 2);
bg_sprite.SetY((screen_height - background.GetHeight()) / 2);

# Subtle pulse animation
progress = 0;
refresh_rate = 60;

fun refresh_callback() {
    progress = (progress + 1) % refresh_rate;
    alpha = 0.7 + 0.3 * Math.Sin(progress * 2 * Math.Pi / refresh_rate);
    bg_sprite.SetOpacity(alpha);
}

# Register refresh callback
Plymouth.SetRefreshFunction(refresh_callback);
SCREOF
    
    # Update Plymouth theme
    plymouth-set-default-theme gigbox 2>/dev/null || true
    update-initramfs -u 2>/dev/null || true
    echo -e "${GREEN}Plymouth theme configured${NC}"
else
    echo -e "${YELLOW}Plymouth not available, skipping${NC}"
fi

echo -e "${YELLOW}[7/8] Configuring GRUB boot menu branding...${NC}"
if [ -f "$GRUB_DIR/grub.cfg" ]; then
    # Backup original
    cp "$GRUB_DIR/grub.cfg" "$GRUB_DIR/grub.cfg.gigbox-backup"
    
    # Update GRUB menu entry names
    sed -i 's/Zynthian/GIGBOX SPOOKI INSTRUMENTS/g' "$GRUB_DIR/grub.cfg" 2>/dev/null || true
    sed -i 's/zynthian/gigbox/g' "$GRUB_DIR/grub.cfg" 2>/dev/null || true
    echo -e "${GREEN}GRUB menu branding updated${NC}"
else
    echo -e "${YELLOW}GRUB config not found, skipping${NC}"
fi

echo -e "${YELLOW}[8/8] Setting permissions...${NC}"
chown -R zynthian:zynthian "$CLEAN_IMG_DIR" 2>/dev/null || true
chown -R zynthian:zynthian "$IMG_DIR" 2>/dev/null || true
chown -R zynthian:zynthian "$ICONS_DIR" 2>/dev/null || true
echo -e "${GREEN}Permissions set${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  BOOT ANIMATION & BRANDING COMPLETE${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Changes:${NC}"
echo "  - Static boot logo: GIGBOX/SPOOKI INSTRUMENTS"
echo "  - Boot animation: Neon pulse animation (GIF)"
echo "  - Splash animation: Custom GIGBOX splash"
echo "  - Branding icons: 128px and 64px logos"
echo "  - Plymouth theme: GIGBOX (if available)"
echo "  - GRUB menu: GIGBOX branding"
echo ""
echo -e "${BLUE}Reboot to see new boot animation${NC}"