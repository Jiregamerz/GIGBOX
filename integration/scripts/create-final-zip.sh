#!/bin/bash
# GIGBOX Final ZIP Packager
# SPOOKI INSTRUMENTS - GIGBOX
# Creates the final deliverable ZIP package

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

FINAL_DIR="/mnt/h/GIGBOX_BUILD/FINAL"
ZIP_FILE="/mnt/h/GIGBOX_BUILD/GIGBOX_FINAL_PACKAGE.zip"
INTEGRATION_DIR="/mnt/h/GIGBOX_BUILD/integration"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  GIGBOX FINAL ZIP PACKAGER${NC}"
echo -e "${BLUE}  SPOOKI INSTRUMENTS${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

if [ ! -f "$FINAL_DIR/gigbox-final.img.xz" ]; then
    echo -e "${RED}Final image not found: $FINAL_DIR/gigbox-final.img.xz${NC}"
    echo "Run build-final-image.sh first"
    exit 1
fi

cd "$FINAL_DIR"

echo -e "${YELLOW}Verifying deliverables...${NC}"

# Required files
REQUIRED=(
    "gigbox-final.img.xz"
    "GIGBOX_GPIO_MAP.md"
    "GIGBOX_BUILD_REPORT.md"
    "README.md"
    "checksums.txt"
)

for file in "${REQUIRED[@]}"; do
    if [ -f "$file" ]; then
        size=$(du -h "$file" | cut -f1)
        echo -e "  ${GREEN}✓${NC} $file ($size)"
    else
        echo -e "  ${RED}✗${NC} $file - MISSING!"
        exit 1
    fi
done

# Optional files
OPTIONAL=(
    "docs/"
    "scripts/"
    "diagnostics/"
)

for item in "${OPTIONAL[@]}"; do
    if [ -e "$item" ]; then
        echo -e "  ${BLUE}✓${NC} $item (included)"
    fi
done

echo -e "${YELLOW}Creating ZIP package...${NC}"
# Create ZIP with only required files (no temp/build files)
zip -r "$ZIP_FILE" \
    gigbox-final.img.xz \
    GIGBOX_GPIO_MAP.md \
    GIGBOX_BUILD_REPORT.md \
    README.md \
    checksums.txt \
    -x "*/.*" -x "*__pycache__*" -x "*.pyc" -x "*.tmp" -x "*.bak" -x "*.orig" -x "*.backup"

echo -e "${GREEN}ZIP created: $ZIP_FILE${NC}"
ls -lh "$ZIP_FILE"

echo -e "${YELLOW}Verifying ZIP contents...${NC}"
unzip -l "$ZIP_FILE"

echo -e "${YELLOW}Generating final checksums...${NC}"
sha256sum "$ZIP_FILE" > "$FINAL_DIR/GIGBOX_FINAL_PACKAGE.zip.sha256"
cat "$FINAL_DIR/GIGBOX_FINAL_PACKAGE.zip.sha256"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  FINAL ZIP PACKAGE COMPLETE${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Package: $ZIP_FILE${NC}"
echo -e "${BLUE}Size: $(du -h "$ZIP_FILE" | cut -f1)${NC}"
echo -e "${BLUE}SHA256: $(cat "$FINAL_DIR/GIGBOX_FINAL_PACKAGE.zip.sha256" | cut -d' ' -f1)${NC}"
echo ""
echo -e "${YELLOW}Contents:${NC}"
echo "  - gigbox-final.img.xz (compressed bootable image)"
echo "  - GIGBOX_GPIO_MAP.md (complete wiring diagram)"
echo "  - GIGBOX_BUILD_REPORT.md (build documentation)"
echo "  - README.md (user guide)"
echo "  - checksums.txt (file integrity)"
echo ""
echo -e "${GREEN}Ready for distribution!${NC}"