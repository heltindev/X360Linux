# X360Linux Linux distribution

The default boot environment is now an **actual Debian Ports PowerPC32 big-endian USB filesystem**, NOT the old X360Desk Photos/Videos/System preview.

The FAT32 USB boot partition contains:
- `xenon.elf` for the existing working XeLL → X360Boot startup
- `X360Linux/vmlinux`, `xenon.dtb`, `initramfs.cpio.gz`
- `X360Linux/USB-ROOT.ID`, an exact marker limiting writable media discovery
- `X360Linux/system.ext4`, a **preinstalled Debian Ports root filesystem** with POSIX permissions and optional persistent files

The initramfs uses the static big-endian PowerPC32 BusyBox solely as a safe USB detection and recovery stage. It attempts to mount the marked FAT32 partition, mounts `system.ext4` via the built-in Linux loop and ext4 drivers, and switches into a Debian `/sbin/init` shell. It no longer runs `/bin/x360desk`, and it contains no photos/videos or custom launcher cards.

This is **not a proven Xbox 360 Debian boot yet**; build and QEMU tests are not hardware verification. No normal Debian graphical desktop is bundled until USB boot and persistence are tested. No internal HDD writes or NAND flashing.

Build/test instructions: [USB Debian guide](../docs/USB-DEBIAN-BOOT.md), [signed Debian builder](debian/README.md), [third-party license credits](../docs/CREDITS.md).
