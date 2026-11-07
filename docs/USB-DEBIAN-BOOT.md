# X360Linux v0.3 USB-first Debian installation

This image is the **real, already-installed Debian Ports 32-bit big-endian PowerPC root filesystem**. It is stored in `X360Linux/system.ext4` inside the **FAT32 USB boot drive**, with an explicit `X360Linux/USB-ROOT.ID` marker.

**No Xbox 360 HDD or NAND is modified.** The XeLL/X360Boot chain continues to load `xenon.elf`, `vmlinux`, `xenon.dtb` and a tiny BusyBox initramfs. That initramfs auto-detects *only* a FAT32 partition containing the exact X360Linux USB marker, opens the ext4 system image through the Linux loop device and tries `switch_root` into Debian.

This is not a desktop installer wizard. **Extracting the ZIP onto a FAT32 pendrive is the installation step.** On first boot it attempts the Debian shell immediately; the earlier Photos/Videos/System program is **not included or started**. Changes in the ext4 system image may survive a clean shutdown, but the Xenon USB/loop/EXT4 boot path has **not yet been proven on the real console**.

## How to test on a modified Xbox 360

1. Use an already-working XeLL installation, on RGH/JTAG or with your existing FreeMyXe/ABadAvatar exploit.
2. Back up the drive, then download the correct v0.3 USB ZIP.
3. Extract it **to the FAT32 root** of a pendrive with at least 2 GB available. Keep `xenon.elf` at the root, alongside `X360Linux/`. The folder contains `system.ext4`, `USB-ROOT.ID`, the kernel, the recovery initramfs and the optional ISO.
4. Insert the pendrive and start XeLL as usual. X360Boot automatically loads the Xenon Linux kernel after a brief cancel window.
5. Linux scans USB for the marker, mounts **only the marked pendrive** for writing, then attempts to switch to the Debian root. Use a USB keyboard to run `cat /etc/os-release`.
6. If the BusyBox recovery shell appears, photograph the `X360Linux USB:` error above it. The error indicates whether Linux detected the drive, mounted FAT32, found the installation or reached the Debian runtime.

**Important**: Debian PowerPC + ext4 loop on Xbox 360 is experimental. No accelerated desktop, controller-as-mouse, native MP4 or audio is promised here. Initial priority is getting a real Debian filesystem to boot. Only after that will we add a low-memory graphical desktop.

The included ISO is **not** executed from USB. It is an optional experimental optical image. The actual Debian installation is the `system.ext4` file in the USB ZIP.
