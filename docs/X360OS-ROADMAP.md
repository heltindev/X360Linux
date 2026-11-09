# X360OS roadmap — console-style Linux for Xbox 360

## Base decision

### Phase 1: proven Ubuntu/Xenon base

Use the hardware-tested Ubuntu 10.10 PowerPC Casper system and the
2.6.36.2 Xenon kernel for the first usable X360OS prototype.

Why:

- it already reaches the desktop on the Corona Phison console;
- USB, framebuffer, audio foundations and the `xpad` controller driver are
  present;
- persistent USB storage is already prepared;
- it gives the project a stable recovery path while the new interface is built.

This base is old and must not be presented as a secure modern desktop.
Its browser is useful for compatibility experiments, not sensitive accounts.

### Phase 2: modern Debian PowerPC research

Debian still has an unofficial 32-bit PowerPC port, but it is not an official
release architecture. A modern Debian userland and browser must not be assumed
to work with the current 2.6.36 Xenon kernel.

Move to Debian only after a newer Xenon kernel can boot with USB, framebuffer,
audio, input, ext4 and networking verified on the Xbox.

## Product goal

A controller-first, television-friendly Linux shell inspired by SteamOS:

- boots directly from USB;
- opens a full-screen home interface;
- launches a browser and selected applications;
- uses the Xbox controller for navigation;
- provides controller-driven mouse input;
- provides an on-screen keyboard;
- keeps settings and files across reboots;
- always retains a recovery boot path;
- never requires NAND or internal-HDD modification.

## Checklist

### 0. Preserve the working baseline

- [x] Legacy Xenon kernel reaches the Ubuntu desktop.
- [x] Automatic `timeout=0` boot works.
- [x] Ubiquity Install launcher is removed.
- [x] 3 GiB `casper-rw` persistence image is prepared.
- [ ] Confirm a desktop file survives a physical reboot.
- [ ] Archive a complete checksum manifest of the working USB.
- [ ] Keep the original SquashFS and recovery menu offline.

### 1. Controller discovery

- [x] Confirm kernel configuration includes built-in `JOYSTICK_XPAD`.
- [x] Confirm `joydev` and `evdev` are available as modules.
- [ ] Test a wired Xbox 360 controller on the console.
- [ ] Record `/dev/input/js*` and `/dev/input/event*` mappings.
- [ ] Record button, trigger and analog-stick values.
- [ ] Test reconnect after unplugging the controller.
- [ ] Decide whether wireless controllers need a USB receiver.

### 2. Controller-first input service

- [ ] Build a small PowerPC-native daemon; avoid Electron and heavy runtimes.
- [ ] Read the controller through evdev or the joystick API.
- [ ] Map left stick to pointer movement through X11/XTest.
- [ ] Map A to left click and B to right click/back.
- [ ] Map D-pad to menu focus navigation.
- [ ] Map shoulder buttons to page/tab switching.
- [ ] Map triggers to vertical scrolling.
- [ ] Add dead zones, acceleration and configurable sensitivity.
- [ ] Add a safe button combination to exit/restart the shell.
- [ ] Enable the service automatically only after X is ready.

The current kernel does not expose `CONFIG_INPUT_UINPUT` in its configuration.
The first version should use X11/XTest. A future kernel can enable uinput for
system-wide virtual mouse and keyboard devices.

### 3. On-screen keyboard

- [ ] Evaluate the existing Ubuntu on-screen keyboard packages.
- [ ] If too heavy, build a small GTK2 keyboard suitable for 720p.
- [ ] Open the keyboard with the Guide button or a configurable shortcut.
- [ ] Support letters, numbers, URL symbols and navigation keys.
- [ ] Provide PT-BR and English layouts.
- [ ] Allow analog-stick selection and D-pad selection.
- [ ] Add predictive URL/history buttons only after the basic keyboard works.
- [ ] Confirm text entry in the browser address bar and web forms.

### 4. SteamOS-style home interface

- [ ] Choose a project name and visual identity.
- [ ] Design a 10-foot UI for 720p televisions.
- [ ] Implement Home, Browser, Applications, Files, Settings and Power.
- [ ] Use GTK2/C or another lightweight PowerPC-compatible toolkit.
- [ ] Start full-screen automatically after login.
- [ ] Keep a hidden recovery shortcut to the normal desktop.
- [ ] Show network, storage, time and controller status.
- [ ] Add readable focus states and controller navigation.
- [ ] Measure idle RAM and keep enough memory for the browser.

### 5. Browser

- [ ] Inventory the Firefox/WebKit versions that run on the current image.
- [ ] Test HTTPS/TLS, certificate store and DNS.
- [ ] Test simple sites before heavy JavaScript sites.
- [ ] Measure RAM usage with one, two and three tabs.
- [ ] Test YouTube only after basic browsing; expect codec/performance limits.
- [ ] Add controller shortcuts for back, forward, tabs, zoom and address bar.
- [ ] Clearly label the legacy browser as unsafe for passwords or sensitive use.
- [ ] Research a newer PowerPC browser only after the modern-kernel track boots.

Mozilla classifies Linux PowerPC as Tier 3: community maintained and not
routinely tested by Mozilla. A current browser is therefore a porting project,
not a package we can assume exists.

### 6. Persistence and storage

- [ ] Confirm the overlay survives ten reboot/write cycles.
- [ ] Detect and report a damaged `casper-rw` filesystem.
- [ ] Add a clean shutdown action to reduce corruption risk.
- [ ] Add a free-space indicator.
- [ ] Decide which user folders should live outside the overlay.
- [ ] Add an offline backup/restore tool for settings.
- [ ] Investigate why the FAT32 root appeared empty after previous console tests.

### 7. Network

- [ ] Confirm Ethernet in Linux independently of XeLL DHCP messages.
- [ ] Inventory USB Wi-Fi adapters with PowerPC-era Linux drivers.
- [ ] Select one chipset with firmware that can be redistributed.
- [ ] Build a controller-friendly network setup screen.
- [ ] Test DHCP, DNS, HTTPS and reconnect after suspend/reboot.
- [ ] Never store Wi-Fi passwords in the public repository.

### 8. Audio and media

- [ ] Confirm desktop audio output over the active video cable.
- [ ] Add volume control to the shell.
- [ ] Test lightweight music playback.
- [ ] Test hardware/software video decode limits.
- [ ] Define realistic supported resolutions and codecs.

### 9. Boot experience

- [ ] Keep the verified legacy kernel as the default.
- [ ] Suppress the harmless `/dev/sr0: No medium found` probe if possible.
- [ ] Investigate the displayed `stderr error 0` without hiding real failures.
- [ ] Add an X360OS splash only after boot reliability is stable.
- [ ] Do not claim control over the early XeLL screen from `kboot.conf`.
- [ ] Keep a verbose recovery configuration offline.

### 10. Modern-kernel/Debian research track

- [ ] Locate the complete Xenon kernel patch history and build toolchain.
- [ ] Reproduce the known 2.6.36 kernel build first.
- [ ] Port Xenon platform, framebuffer, USB, audio and input patches forward.
- [ ] Enable devtmpfs, ext4, loop, evdev, joydev, xpad and uinput.
- [ ] Boot a minimal initramfs on hardware.
- [ ] Boot a minimal Debian PowerPC rootfs.
- [ ] Validate libc/kernel compatibility before adding a desktop.
- [ ] Measure whether a modern browser is feasible within Xbox 360 memory.
- [ ] Keep this track separate from the working Ubuntu release.

### 11. Release engineering

- [ ] Create reproducible build scripts for every modified artifact.
- [ ] Store source and checksums in Git; do not commit multi-gigabyte images.
- [ ] Publish hardware results separately from PC-only validation.
- [ ] Version the UI, input daemon and USB layout independently.
- [ ] Document licenses for Ubuntu, Debian, kernel patches and bundled software.
- [ ] Provide upgrade and rollback instructions.
- [ ] Never ship NAND-flashing files in the active USB tree.

## First milestone

**X360OS Milestone 1: Controller Browser Prototype**

Definition of done:

1. the Xbox boots automatically to the full-screen X360OS home screen;
2. a wired controller moves focus and opens the Browser tile;
3. the left stick can move the mouse pointer;
4. A/B provide click/back behavior;
5. the on-screen keyboard can enter a URL;
6. a simple HTTPS page opens;
7. settings and one desktop test file survive a reboot;
8. normal desktop recovery remains available.
