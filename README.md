# X360Linux

**USB-first Linux development for Xbox 360 RGH/JTAG.**

The goal is to boot a preinstalled Linux desktop from a USB drive, with no console-side installation. This is experimental: **a complete Linux desktop boot has not yet been verified on the Corona Phison Xbox 360**.

## Development checklist

- [ ] **1. Show 0–100% progress from XeLL/XEX until the Linux desktop opens.** A PowerPC framebuffer prototype displays Linux boot milestones (10/30/50/75/90); it does not cover early XeLL startup or provide verified full-boot progress.
- [x] **2. Prepare Linux already installed and unpacked.** A 3 GiB Ubuntu PowerPC root filesystem was built inside a writable ext4 image for the USB, without needing the Ubuntu installer. **Still to test:** real console boot, graphical desktop and persistence.
- [ ] **3. Enable internet without an Ethernet cable.** Identify a supported Wi-Fi adapter, driver and firmware; test Linux wireless networking. The XeLL DHCP error is a separate pre-Linux issue.
- [ ] **4. Support multiple Linux distributions.** Debian PowerPC is a candidate, but each distro needs a compatible Xenon kernel, initramfs and drivers. **Arbitrary x86/ARM ISOs cannot boot natively.**
- [ ] **5. Reduce boot time.** Measure XeLL, USB, kernel, initramfs and desktop startup on the console before claiming any speed improvement.
- [ ] **6. Replace visible boot messages with a graphical loading screen.** A green Linux framebuffer/Plymouth prototype exists, but XeLL and early kernel messages are not hidden. Keep a verbose recovery mode.
- [x] **7. Keep distributions in separate folders.** The local package uses `distros/ubuntu-x360/`; adding Debian and verifying the XeLL boot menu are still pending.

Checked boxes indicate **PC preparation or file layout only**, not successful Xbox 360 hardware testing.

## Current USB development layout

```text
BOOT-DIRETO/
├── kboot.conf
├── vmlinux                       # Legacy Xbox 360 PowerPC kernel
├── casper/
│   └── filesystem.squashfs       # Older compressed Ubuntu Live fallback
└── distros/
    └── ubuntu-x360/
        ├── vmlinux
        ├── initrd.gz
        ├── ROOTFS.ID
        └── rootfs.ext4           # Preinstalled, unpacked Ubuntu in ext4
```

**Hardware status:** On Corona Phison RGH, the console opens XeLL with **Eject**; the old `default.xex` launched from Aurora gives a **black screen**. The new XeLL menu, ext4 boot, GUI, Wi-Fi and progress display still require real-console testing. Do not flash NAND or modify the internal Xbox HDD.

## Documentation

[Development source](scripts/v041-ext4/README.md) · [Boot files and Debian compatibility](docs/BOOT-CASPER-VMLINUX-DEBIAN.md) · [Detailed technical status](docs/V041-EXT4-BOOT-EXPERIMENTAL.md) · [Latest published alpha](https://github.com/heltindev/X360Linux/releases/tag/v0.4.0-alpha) · [Credits and licenses](docs/CREDITS.md)

**The local v0.4.1-dev files are experimental and are not included in the published v0.4.0-alpha ZIP.**
