# X360OS Shell v7.2.0-dev — Xbox 360 dedicated session

This build is the next step after the user confirmed the v7.1 recovery image **shows picture** on an Xbox 360, but still enters the Ubuntu desktop and does not use the gamepad as a mouse.

## New behavior

- The original known-video `2.6.36.2-xenon` kernel, XeLL bootstrap, GDM/Xorg, `xenosfb_drv.so` and GNOME **fallback** are preserved.
- GDM's default graphical session is `x360os`, with a standalone fullscreen GTK2 **X360OS** menu, not a GNOME panel/background.
- If the menu cannot start or exits, session script falls back to the existing GNOME desktop so the video path can still be diagnosed.
- Controller helper starts in the **same X11 session**, with unbuffered logs under `~/.x360os/controller.log`. The left stick defaults to mouse movement and A/B act as mouse clicks, while X switches mouse/menu control.
- A root read-only hardware probe records `/var/log/x360os-input-hardware.txt` so we can distinguish `no detected /dev/input/js0` from XTest mapping errors.
- Boot remains independent of Ethernet/DHCP. `DHCP failed` in XeLL happens **before** Linux and is not a reason for menu startup to fail.

## The crucial compatibility distinction

**This is an X360OS-branded independent user session, not yet a completely Ubuntu-free rootfs.** The Ubuntu 10.10 PPC32 libraries remain **inside** solely for the proven Xenon Xorg driver and GTK2 compatibility while we replace the OS in phases. We cannot remove the Ubuntu userspace and promise that video stays working until a fully native graphical stack is validated on real hardware.

## Controller reality

- The Linux `xpad` USB driver is built into the kernel, with `joydev` and `evdev` modules available.
- The kernel must enumerate a compatible USB gamepad or wireless **USB receiver** for the controller bridge to see any events.
- A directly paired console RF wireless controller may not be exposed to the Linux input subsystem. A userspace cursor mapper alone **cannot** fix missing RF hardware support.
- Use a **wired USB 360 controller** or a compatible USB 360 wireless receiver for the first test; note that a charge-and-play cable does not transform the original wireless pad into a wired USB controller.
- The new mouse mode is implemented but remains **unverified on physical Xbox hardware** until the next test.

## Build locally (Windows WSL)

```sh
bash distro/x360os-shell/build.sh PATH_TO_v7.1_SQUASHFS PATH_TO_ORIGINAL_VMLINUX NEW_EMPTY_OUTPUT_DIR
bash distro/x360os-shell/test.sh PATH_TO_v7.1_SQUASHFS NEW_OUTPUT_DIR
```

The scripts refuse an existing output target. Keep the v7.1 functioning video image and the original USB `E:\` untouched. Create a **separate FAT32 test USB** (no old `casper-rw` overlay) for this version. No NAND, Xbox internal HDD or Github Actions are modified.

## On-console validation

1. Does XeLL boot local USB and produce stable video?
2. Does the screen show the **green X360OS menu**, not the classic Ubuntu desktop? Press F10 to enter GNOME recovery.
3. Does an actual **wired** USB Xbox 360 controller show mouse movement with the left stick and click with A/B? Press X to toggle menu mode.
4. If the pointer does not move, check `~/.x360os/controller.log` for `INPUT` vs `NO INPUT DEVICE` and `/var/log/x360os-input-hardware.txt`. Send a photo of any error if logs cannot be saved due to nonpersistent boot.
5. Confirm keyboard fallback and power-off work. Networking and sound are still unverified.

Do not call this a stable native distro yet. The `v7-native-development` implementation remains separate for eventual full replacement of Ubuntu components.
