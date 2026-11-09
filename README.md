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

## X360OS Native v8.0.0-alpha — NO Ubuntu, NO Casper

**The first truly Ubuntu-independent system tree** is now in [`distro/x360os-v8`](distro/x360os-v8/README.md), on branch `v8-native-zero-ubuntu`.

This is **not** a GNOME skin or Ubuntu remix. The USB contains the verified Free60 Xenon `vmlinux`, an independent original `initrd-x360os.gz` newc CPIO with our own `/init`, BusyBox/musl static PPC32 big-endian binaries, Free60 input modules and original X360OS C dashboard. No Ubuntu, Casper, `filesystem.squashfs`, Xorg, GTK, GDM, GNOME, APT or Python in the target image. XeLL external initrd and `rdinit=/init` replace the old `boot=casper` chain.

**Real defect found and addressed:** Xenos framebuffer memory uses 32×32 pixel tiles. Old `x360os-ui` wrote it linearly, explaining the checkerboard-like corruption in the user's Xbox photograph. v8 implements the Free60 XeLL `xenos_pset32()` tiled address mapping and pixel format. Static PowerPC compiled and QEMU-rendered tiled output matches the linear reference in both 800×480 and 1280×720.

**Still experimental:** Physical Xbox v8 XeLL-initrd handoff and framebuffer/controller behavior have NOT been verified yet. The kernel is a preserved Linux Free60 kernel, not a newly written Linux kernel. Do not overwrite working USB `E:\`, NAND or internal HDD. Keep the successful-video recovery image separate for fallback, but never copy its Ubuntu files into the native v8 build.

## X360OS v9 — CORRECTION TO THE v8 BOOT DESIGN

**Important correction:** the "original" Free60 `vmlinux` used in v8 was NOT a neutral kernel. We extracted its internal `.init.ramfs` section and proved that it contained an LZMA-compressed 15.9MB Ubuntu/Casper root environment, even though there were no Ubuntu files in the *external* initrd. Thus the earlier v8 documentation claiming the full boot was Ubuntu-free was **incorrect**. The native X360OS userspace itself was Ubuntu-free, but the kernel still had an older embedded rootfs.

[v9's new boot code](distro/x360os-v9/README.md) replaces exactly that embedded archive with our PowerPC native X360OS /init, static musl/BusyBox and our framebuffer UI. XeLL loads only the new `vmlinux` with its unchanged ELF load layout, without `initrd=`, `boot=casper` or `filesystem.squashfs`. This keeps the existing Free60 Linux kernel (not a new Linux kernel rewrite) while eliminating the old Ubuntu/Casper archive. The new full boot remains **untested on real Xbox 360 hardware** until the user tries it. We preserve the old known-picture image for recovery without putting any Ubuntu files into the new image. No NAND, HDD, USB E:, or GitHub Actions modifications.
