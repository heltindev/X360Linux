# X360Linux

**USB-first Linux development for Xbox 360 RGH/JTAG.**

The hardware-tested path boots an Ubuntu 10.10 desktop directly from a FAT32 USB drive on an Xbox 360 Corona Phison. It uses the verified legacy Xenon kernel, a modified Casper SquashFS without the Ubiquity installer launcher, and a 3 GiB persistent `casper-rw` filesystem.

## Kernel

The working Ubuntu kernel is **Linux 2.6.36.2-xenon**, a 32-bit big-endian PowerPC kernel built for the Xbox 360 Xenon platform.

## Confirmed hardware result

Confirmed on November 8, 2026:

- XeLL/Eject automatically starts Linux with `timeout=0`;
- the verified legacy `vmlinux` opens the Ubuntu desktop;
- the Ubiquity **Install** desktop launcher is removed;
- no command or boot-menu selection is required;
- no NAND flash or Xbox internal HDD modification is required;
- experimental custom-initramfs entries 0 and 1 black-screened and are not used by the default boot.

The messages `stderr error 0` and `can't open /dev/sr0: No medium found` may appear. They do not prevent the desktop from opening.

## Active USB layout

```text
USB root/
|-- kboot.conf
|-- vmlinux
|-- x360linux.elf
|-- casper-rw
|-- casper/
|   `-- filesystem.squashfs
`-- distros/ubuntu-x360/
    |-- vmlinux
    |-- initrd.gz
    |-- ROOTFS.ID
    `-- rootfs.ext4
```

The active `kboot.conf` contains one automatic English entry and uses the verified legacy kernel with `boot=casper persistent`.

## Important limitation

The words **XeLL Main Menu** may flash briefly because XeLL renders them before Linux starts. Removing that firmware screen would require changing the installed XeLL/NAND, which this project intentionally does not do.

The persistent overlay is prepared and host-verified. Retention after a second physical Xbox reboot still needs confirmation.

## X360OS v6 — work in progress

The new [X360OS v6 prototype](distro/x360os-v6/README.md) is a controller-first, SteamOS-style lightweight GTK2 desktop built on the existing Xenon/Ubuntu PowerPC system. The prototype includes a home screen, experimental gamepad mouse mapping, an on-screen browser URL keyboard, NetworkManager and existing Ubuntu applications. **It has not yet been boot-tested on Xbox hardware.** The v5 download below remains the verified baseline.

## Release

Download [**X360Linux v5.0.0 — Persistent USB Direct Boot**](https://github.com/heltindev/X360Linux/releases/tag/v5.0.0).

The release assets contain the complete USB payload split into packages that can be extracted to the same FAT32 USB root.

## Documentation

- [X360OS roadmap and checklist](docs/X360OS-ROADMAP.md)
- [Persistent USB design](docs/PERSISTENT-USB-LEGACY-KERNEL.md)
- [Hardware test log](docs/V041-CORONA-TEST-2026-11-08.md)
- [Credits and licenses](docs/CREDITS.md)

## X360OS Native — Xbox 360-only system (v7.0.0-alpha)

The new [X360OS Native](distro/x360os-native/README.md) is a **fully custom, Ubuntu-free root filesystem** for Xbox 360 RGH/JTAG hardware, built locally for PowerPC 32-bit big-endian using **musl + BusyBox + a C framebuffer interface**. No GNOME, Xorg, APT, Python or browser is included in the new userspace.

The verified Free60 Xenon kernel remains unchanged. **The kernel's pre-existing Casper first-stage loader is still used temporarily**, so the complete boot chain is not yet entirely independent of Ubuntu. A new custom initramfs and real Xbox console testing are required for full independence.

The native-alpha image is built separately from the working v5/v6 distributions, does **not** reuse Ubuntu `casper-rw`, does not modify the Xbox NAND/HDD, and is not a stable release. Its USB-ready testing files are produced only by the local workstation build scripts under `distro/x360os-native`. This development does not use GitHub Actions.

## X360OS 7.1 Recovery (after native framebuffer crash on Xbox 360)

The real Xbox 360 test of the v7.0 native alpha produced a corrupt/checkerboard console display and boot errors. Do not use that image as a known-working replacement. The [7.1 recovery bridge](distro/x360os-recovery/README.md) preserves the **original v5 Xenon kernel, Xorg/xenosfb video driver and GDM/GNOME autologin**, then starts a custom X360OS fullscreen dashboard through GNOME autostart. If the menu fails, the original desktop remains available.

**Transparency:** v7.1 is an Ubuntu 10.10 PPC32 **compatibility build**, not yet an Ubuntu-free system; we need that proven graphics/boot stage until a native replacement passes physical Xbox tests. The independently built Ubuntu-free native rootfs code remains on branch `v7-native-development` for continued engineering. The test image uses `nopersistent` and must be tested on a separate FAT32 USB without old Ubuntu `casper-rw` overlays. Neither XeLL/NAND nor internal HDD is modified. DHCP messages from XeLL may occur before Linux boots and are unrelated to Linux DHCP.

## X360OS 7.2 — custom Xbox shell and controller mouse

The user's Xbox 360 **successfully displayed video** with the v7.1 recovery image, but still displayed Ubuntu and did not move the pointer with a controller. The new [v7.2 custom shell](distro/x360os-shell/README.md) runs an **X360OS-specific fullscreen GDM graphical session** instead of the GNOME panel. It adds a USB joystick/evdev → X11/XTest pointer mapping with mouse mode ON by default (left stick moves cursor, A left-click, B right-click, X toggles menu/mouse), plus read-only hardware/input diagnostics and a fallback to the proven desktop if the menu crashes.

The **known-working original Xenon kernel, framebuffer driver and Xorg configuration are preserved** and verified byte-for-byte. This still contains legacy Ubuntu 10.10 PowerPC compatibility libraries and GDM/Xorg underneath: it is NOT yet a fully Ubuntu-independent rootfs. The independent native rootfs remains under `distro/x360os-native`, but its raw framebuffer display was unstable in the real Xbox test. Physical controller enumeration remains unverified; console-internal wireless RF cannot be fixed solely through joystick-to-mouse mapping.

The v7.2 test output is a separate FAT32 USB folder. Do not overwrite a working USB or reuse old Ubuntu `casper-rw`. No NAND/Xbox HDD writes, no GitHub Actions.
