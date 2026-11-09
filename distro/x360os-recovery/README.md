# X360OS v7.1 Recovery — Xenos Xorg compatibility bridge

**Goal:** fix the corrupt v7 native framebuffer startup shown on Xbox 360 without discarding the long-term Ubuntu-free distro project.

## Why this release

A real Xbox test of v7.0-native displayed checkerboard-like tile corruption and mixed console errors rather than a usable home screen. The image alone cannot distinguish an uninitialized framebuffer, an unsupported pixel layout, or early boot errors. The Native framebuffer C renderer must remain **disabled** on hardware until a console framebuffer probe validates pitch, memory layout and mode. Do not write directly to /dev/fb0 in this recovery image.

The original Ubuntu 10.10 PPC32 image **did boot graphically** on this user's console, using its known GDM, Xorg and `xenosfb_drv.so`. v7.1 restores that complete proven graphics path while supplying a customized X360OS GTK2 fullscreen menu. It does **not** claim to have already passed this version's real-console test.

## Exactly what's preserved

- Verified Xbox 360 kernel `vmlinux` **byte-for-byte unchanged**, XeLL/Kboot automatic boot, Casper first-stage initramfs.
- Original Xenon kernel modules, `xenosfb` Xorg driver, original Xorg configuration, GNOME compatibility desktop and GDM autologin (user `ubuntu`).
- Legacy PPC32 runtime, GTK2 and Python2.6 **temporarily**, while replacing them step-by-step with X360OS-native components.
- Kernel-backed USB, ALSA Xenon and Ethernet support — hardware output and connectivity still need tests.

## What's different from the original Ubuntu boot

- X360OS branding and version metadata, responsive dark green fullscreen X360OS launcher, keyboard input and optional experimental controller bridge.
- GDM stays on the **proven `gnome.desktop`** rather than selecting an untested custom X session.
- GNOME system autostarts the X360OS menu after login using `x360os-safe-start`. If the menu crashes, GNOME remains alive as a recovery fallback.
- No raw framebuffer UI or busy-loop restarts; no network wait or DHCP dependency before menu.
- `nopersistent` boot so the older `casper-rw` overlay cannot reinsert stale files on this first compatibility test.
- Files and logs are generated inside `~/.x360os/` during the live session. They are **not persistent** across reboot in this test build.

## What this IS and is NOT

**This v7.1 recovery build still uses Ubuntu 10.10 userspace internally**, including Xorg/GDM/GNOME, GTK2 and Python2.6. It is intentionally an **intermediate compatibility bridge** on the road to our standalone X360OS rootfs. Do not market it as fully independent, modern or secure. Its legacy Firefox must not be used for sensitive accounts. The earlier v7 native source remains intact on its separate branch.

The goal for future native builds is to replace one component at a time: first boot/graphics; then userland initialization; then controller/audio/network; then modern game/app support. Do not remove the known-working graphics driver before validating a replacement.

## Local workstation build

```bash
bash distro/x360os-recovery/build.sh /path/to/verified-v5-rootfs.squashfs /path/to/verified-v5-vmlinux /empty/output/directory
bash distro/x360os-recovery/test.sh /empty/output/directory
```

Uses WSL only to **build** the image; the Xbox runs PowerPC code. No GitHub Actions. The installer refuses to overwrite an output folder or working USB. Copy the generated release to a **separate** FAT32 pendrive; do not copy the old Ubuntu `casper-rw` with it. Start with Eject/XeLL. Do not alter NAND or the console HDD.

## DHCP failed warning

XeLL may report `DHCP failed` **before Linux starts**, especially without an Ethernet cable. The error does not itself prove that Linux crashed. This release does not modify XeLL. Linux's own network services are non-blocking for the X360OS menu. The Slim's internal Marvell Wi-Fi remains unsupported in the preserved kernel.

## Hardware acceptance checklist

1. XeLL loads `vmlinux`, Casper mounts `casper/filesystem.squashfs`, GDM starts Xorg.
2. Picture is correctly aligned with no checkerboard corruption; X360OS home appears fullscreen.
3. Keyboard works; pressing F10 exposes the recovery desktop. Controller USB support is unverified.
4. Network may be absent without stopping the menu; USB and audio require console testing.
5. User can power off safely without NAND writes; old version remains preserved.
