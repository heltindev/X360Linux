# X360OS Native v7.0.0-alpha — Xbox 360 custom Linux distribution

**New userspace built from source, not an Ubuntu rebrand.**

## Architecture

- **Kernel:** known-booting Free60 Xenon kernel `2.6.36.2-xenon`, preserved byte-for-byte.
- **C library:** musl 1.2.5, cross-compiled as static PowerPC 32-bit big-endian.
- **Core system:** BusyBox 1.36.1, static PowerPC.
- **Boot PID 1:** original X360OS `init` shell script; mounts proc/sys/dev, detects console, loads matching Free60 input modules, mounts only USB mass-storage devices read-only, starts wired DHCP and framebuffer UI.
- **Interface:** custom native C dashboard on `/dev/fb0` with controller/USB-keyboard input and photo/video preview. No X11, Wayland or compositing.
- **Graphics:** CPU software rendering over Xenos framebuffer; no 3D GPU acceleration.
- **Tools:** local WSL cross-compilation with QEMU user-mode smoke checks. No GitHub Actions.

## Completely removed from NEW rootfs

Ubuntu 10.10, GNOME, GDM, Openbox, GTK2, Xorg, APT/dpkg, Python, Firefox, LibreOffice, systemd, PulseAudio and other distribution-specific services. No userland files are copied from the previous Ubuntu rootfs. Only matching Free60 **kernel .ko drivers** are extracted from the previous rootfs.

## Transitional first-stage boot — important

The old verified v5 `vmlinux` has an **embedded Ubuntu-derived Casper bootstrap**. Its use still makes the *first boot stage* dependent on Casper while it mounts the new, Ubuntu-free `casper/filesystem.squashfs`. The rootfs itself is native and independent, but the overall boot chain is **not yet fully free of Casper**.

The next kernel/boot project must replace Casper with an independent initramfs, ideally after this rootfs is proven on the Xbox. We are deliberately preserving the old `vmlinux` to avoid a new black screen.

This candidate is **NON-PERSISTENT**. DO NOT copy old `casper-rw` alongside it: the old overlay contains Ubuntu files and could break the clean system. Existing v5/v6 files and USB drives are left unchanged.

## Features included in first native alpha

| Feature | Status |
| --- | --- |
| Free60 Xenon CPU, SMP, USB, framebuffer | Supported in preserved kernel; this new boot still needs real-console testing |
| Xbox software dashboard | Built and rendered under PPC32 QEMU |
| Photo viewer | JPEG, PNG, BMP, PPM with in-repo stb_image |
| Local video | Silent preconverted X36V clips only (no MP4 decoder) |
| USB joystick / evdev controller | Userspace input included; internal RF controller may not enumerate |
| USB keyboard | Userspace input included |
| Wired Ethernet | Native driver already built into kernel, BusyBox udhcpc included; connection untested |
| Wi-Fi internal | **NOT SUPPORTED**: kernel built without CONFIG_WIRELESS/WLAN |
| ALSA Xenon | CONFIG_SND_XENON in kernel, but no audio application yet |
| DOOM | Not in first native alpha; will require a new framebuffer-native port |
| Native persistence | Future step after reliable boot; old Ubuntu persistence intentionally excluded |

## Build (Windows + WSL Ubuntu *only as build workstation*)

The **PC's WSL environment is a build tool only**; the resulting Xbox rootfs contains no Ubuntu.

1. Run `bootstrap-toolchain.sh` to build PPC musl (compiler: `powerpc-linux-gnu-gcc`, `-mlong-double-64`).
2. Run `bootstrap-busybox.sh` to build PPC BusyBox; the setup excludes the obsolete `tc`/CBQ kernel API not needed on Xbox.
3. Generate new UI source with `python3 generate-ui.py`, then `build-ui.sh` to compile and render-check native framebuffer program.
4. Run `build-native-rootfs.sh <original-v5-vmlinux> <v5-squashfs> <empty-output-directory>` to construct a new system without modifying working boot files.
5. After host checks, copy output files to a **separate** FAT32 USB for first Xbox testing.

No NAND or internal Xbox HDD modifications, no automatic overwrite of `BOOT-DIRETO` or `E:\`.

## Tests and limits

QEMU verifies static PPC ELF and headless framebuffer rendering, **not** real XeLL boot, actual controller mapping, Ethernet/DHCP or display. Kernel 2.6.36.2 predates some musl POSIX functionality (musl recommends Linux >=2.6.39 for full conformance); real-console checks are mandatory before declaring stability.

Upstream kernel research: https://github.com/Free60Project/linux-kernel-xbox360
