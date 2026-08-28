#!/bin/bash
# GIGBOX TARGET ROOTFS VALIDATION RUNNER
# Run on Linux build machine with Zynthian rootfs mounted at /mnt/zynthian-rootfs

set -e

ROOTFS="${1:-/mnt/zynthian-rootfs}"
VALIDATION_SCRIPT="/mnt/h/GIGBOX_BUILD/integration/scripts/validate-target-rootfs.py"

echo "========================================="
echo "GIGBOX TARGET ROOTFS VALIDATION"
echo "========================================="
echo "Rootfs: $ROOTFS"
echo ""

if [ ! -d "$ROOTFS" ]; then
    echo "ERROR: Rootfs not found at $ROOTFS"
    echo "Usage: $0 /path/to/zynthian/rootfs"
    exit 1
fi

if [ ! -f "$VALIDATION_SCRIPT" ]; then
    echo "ERROR: Validation script not found"
    exit 1
fi

# Copy validation script to rootfs
cp "$VALIDATION_SCRIPT" "$ROOTFS/tmp/validate-target-rootfs.py"

# Prepare chroot
mount --bind /dev "$ROOTFS/dev"
mount --bind /proc "$ROOTFS/proc"
mount --bind /sys "$ROOTFS/sys"
mount --bind /run "$ROOTFS/run" 2>/dev/null || true

# Run validation in chroot
echo "Running Python validation in chroot..."
chroot "$ROOTFS" /usr/bin/python3 /tmp/validate-target-rootfs.py
RESULT=$?

# Cleanup
umount "$ROOTFS/run" 2>/dev/null || true
umount "$ROOTFS/sys"
umount "$ROOTFS/proc"
umount "$ROOTFS/dev"

echo ""
echo "========================================="
if [ $RESULT -eq 0 ]; then
    echo "VALIDATION PASSED - Safe to build image"
else
    echo "VALIDATION FAILED - DO NOT BUILD IMAGE"
fi
echo "========================================="

exit $RESULT