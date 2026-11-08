# v0.3.0-alpha — legacy XeLL/XEX USB boot

**Confirmed hardware behavior (maintainer report, 2026-11-08):** `default.xex` launches from Aurora on a real RGH Xbox 360 and reaches a Linux startup/installer screen. Automatic graphical desktop, audio, controller and persistent USB Linux are **not confirmed**.

## Same XEX download for RGH/JTAG and ABadAvatar

Get **`X360Linux-v0.3.0-alpha-Legacy-XEX-USB.zip`** on the [v0.3.0-alpha release](https://github.com/heltindev/X360Linux/releases/tag/v0.3.0-alpha). **The files are identical for both methods; there is no separate ABadAvatar X360Linux ZIP.**

- **RGH/JTAG:** One FAT32 Linux pendrive. Extract the ZIP to its root and run `default.xex` from Aurora or a compatible dashboard.
- **ABadAvatar:** **TWO SEPARATE pendrives.** USB 1 keeps the ABadAvatar exploit and its required files, unchanged. USB 2 is FAT32 and contains **the same extracted Linux ZIP** as on RGH. When the exploit setup provides a compatible XEX launcher/dashboard, run `default.xex` from USB 2. ABadAvatar alone does not guarantee XEX execution.

The RGH XEX startup path was confirmed on real console hardware. The ABadAvatar two-USB handoff and automatic Linux desktop are **not yet independently hardware tested**. Older RGH/ABadAvatar Debian/IceWM ZIP assets are separate unrelated experiments; do not mix their files with this package.

## What is inside?

```text
default.xex                Original historical XeLL launch XEX
xell.bin                   Historical XeLL loader image
vmlinux                    2011 PowerPC32 big-endian Linux ELF
casper/filesystem.squashfs  Ubuntu 10.10 Linux filesystem (2011)
START-HERE.txt             Installation and safety notes
SHA256SUMS.txt             Checksums for binary files
THIRD-PARTY-NOTICE.txt     Third-party provenance warning
```

A file-format check identified a 32-bit big-endian PowerPC ELF kernel and valid SquashFS 4.0 filesystem, which reports Ubuntu 10.10. **Checksums prove copy integrity, not Xbox hardware support.**

## Run it from USB

1. Make a backup of the USB drive. Format **one FAT32 partition**, without overwriting any Xbox HDD.
2. **Extract the ZIP contents** straight into the root of the FAT32 pendrive. Do not place the ZIP itself, and do not put everything inside one outer folder.
3. Check that `default.xex`, `xell.bin`, `vmlinux` and `casper/filesystem.squashfs` are visible at the USB root.
4. On RGH/JTAG, open **Aurora** and run **`default.xex`** from the Linux USB. On ABadAvatar, leave the exploit pendrive separate and launch **`default.xex`** from **the second Linux USB** using a compatible XEX-capable launcher/dashboard.
5. A Linux startup/installer screen may appear. **Do not select disk installation or modify Xbox internal storage.** Direct-to-desktop USB Linux is planned for v0.4, not established for v0.3.

This process does **not** require Rufus or manual kernel compilation. Never rename `xell.bin` to `updxell.bin` or `updflash.bin`, never flash NAND and always retain a known-working console recovery path.

## SHA-256 for the original four files

```text
414492ce7ded99d9d8efe7e35407168cdf4f357c0b4bbff0cf6f27e473a7b2ec  default.xex
6f15f922796a5ad9187b0e6d20cda19e9d18e9e2e6584ecd2c06cd47f37ed1a8  xell.bin
b8aa8eef938275ed5f037b884592283f561ac46b283edf4cdb1200bf2d39cec8  vmlinux
73863d53ad02d8fdd74ad1ba22b7269df0df67b6e00fcc828234be81a1224de6  casper/filesystem.squashfs
```

**Historical/third-party binaries:** Supplied as a 2011 archive rather than reconstructed by this project. Precise corresponding sources and redistribution permissions need additional review. The outdated Ubuntu 10.10 software is insecure for personal accounts. Follow Free60/XeLL, Linux and Ubuntu license conditions before repackaging.

See [v0.4 direct-USB roadmap](ROADMAP.md).
