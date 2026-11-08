# X360Linux v0.3.0-alpha - XEX USB

## Corona Phison hardware correction

**The maintainer's Corona Phison RGH black-screens when running the legacy Aurora default.xex.** Eject boots the existing NAND XeLL. Therefore the old XEX route must NOT be described as confirmed on this model. The direct Linux desktop is still unverified. See [v0.4 hardware audit](V04-STATUS-AND-MULTIDISTRO.md).

**The same ZIP and XEX files are used for RGH/JTAG and ABadAvatar.**

[Download the single XEX USB ZIP](https://github.com/heltindev/X360Linux/releases/download/v0.3.0-alpha/X360Linux-v0.3.0-alpha-XEX-USB.zip)

## Exact ZIP contents

The ZIP was packed, without changing any file, from the maintainer's Downloads/LINUX 360 folder:

- default.xex
- xell.bin
- vmlinux
- casper/filesystem.squashfs
- readme.txt

Extract the files directly to the root of a FAT32 USB pendrive. No extra LINUX 360 parent folder should be created.

## Xbox 360 RGH/JTAG

Use **one USB drive** containing the extracted Linux files. In Aurora or another homebrew XEX-capable dashboard, run **default.xex** from the USB.

## Xbox 360 ABadAvatar

Use **two separate USB drives**. USB 1 holds the ABadAvatar exploit and must be kept unchanged. USB 2 holds **the same extracted Linux ZIP** as RGH users. When your setup provides a compatible XEX-capable launcher, execute **default.xex** from USB 2. ABadAvatar by itself may not supply an XEX launcher.

## Status

CORRECTED: On Corona Phison RGH, Aurora default.xex gives a black screen; Eject starts the NAND XeLL. Linux GUI remains unverified. **Automatic USB desktop boot and the ABadAvatar two-USB setup remain unverified**; this is an experimental 2011 Ubuntu 10.10 Xenon PowerPC32 environment.

The original Linux binary SHA-256 values are:

- default.xex: 414492ce7ded99d9d8efe7e35407168cdf4f357c0b4bbff0cf6f27e473a7b2ec
- xell.bin: 6f15f922796a5ad9187b0e6d20cda19e9d18e9e2e6584ecd2c06cd47f37ed1a8
- vmlinux: b8aa8eef938275ed5f037b884592283f561ac46b283edf4cdb1200bf2d39cec8
- casper/filesystem.squashfs: 73863d53ad02d8fdd74ad1ba22b7269df0df67b6e00fcc828234be81a1224de6

ZIP SHA-256: 54fd2025762082762a27e816be2c7713ad008f1402e7eb4e7394fa91f2b04fc5

**Never flash NAND, modify the console's HDD partitions, or rename xell.bin as a NAND flashing payload.** Ubuntu 10.10 is obsolete. Third-party source and redistribution licensing requirements remain subject to audit.

See the [v0.4 roadmap](ROADMAP.md) for the direct USB Linux desktop goal.
