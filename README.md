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
