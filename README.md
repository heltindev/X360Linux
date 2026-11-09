# X360Linux

**USB-first Linux development for Xbox 360 RGH/JTAG.**

The goal is to boot a preinstalled Linux desktop from a USB drive, with no console-side installation. This is experimental: **a complete Linux desktop boot has not yet been verified on the Corona Phison Xbox 360**.

## Development checklist

- [ ] **1. Show 0–100% progress from XeLL/XEX until the Linux desktop opens.** A PowerPC framebuffer prototype displays Linux boot milestones (10/30/50/75/90); it does not cover early XeLL startup or provide verified full-boot progress.
- [ ] **2. Boot straight into a preinstalled Linux desktop without an installer.** The 3 GiB Ubuntu PowerPC ext4 image exists on the USB, but **real console boot is not yet working**. The older `legacy_v04` entry reaches Ubuntu Live/the installer, not this preinstalled root. A PC-verified, new embedded-initramfs `x360linux.elf` is awaiting Xbox testing.
- [ ] **3. Enable internet without an Ethernet cable.** Identify a supported Wi-Fi adapter, driver and firmware; test Linux wireless networking. The XeLL DHCP error is a separate pre-Linux issue.
- [ ] **4. Support multiple Linux distributions.** The experimental initramfs can select different distro folders, but Debian still needs a compatible Xenon kernel, initramfs and drivers. **Arbitrary x86/ARM ISOs cannot boot natively.**
- [ ] **5. Reduce boot time.** Measure XeLL, USB, kernel, initramfs and desktop startup on the console before claiming any speed improvement.
- [ ] **6. Replace visible boot messages with a graphical loading screen.** A green Linux framebuffer/Plymouth prototype exists, but XeLL and early kernel messages are not hidden. Keep a verbose recovery mode.
- [x] **7. Keep distributions in separate folders.** The local package uses `distros/ubuntu-x360/`; adding Debian and verifying the XeLL boot menu are still pending.
- [ ] **8. Boot Linux from `default.xex` in Aurora, as well as via XeLL/Eject.** Develop and test a Corona Phison-compatible XEX launcher that starts the Linux boot chain without a black screen. The old 2011 `default.xex` is known to fail on this console.

Checked boxes indicate **PC preparation or file layout only**, not successful Xbox 360 hardware testing.

## Current USB development layout

```text
BOOT-DIRETO/
├── kboot.conf                   # Beginner-friendly boot choices
├── x360linux.elf                # Experimental embedded-initramfs kernel
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

**Real hardware test (November 8, 2026):** Eject boots XeLL and displays its menu. The old `legacy_v04` kernel **loads**, but displays the Ubuntu Live/installer. The earlier normal/debug entries failed. The updated `x360linux.elf` with embedded X360Linux initramfs has passed PC checks only; the preinstalled GUI has **not** been proven to boot. Aurora's old `default.xex` still black-screens on Corona Phison.

**Automatic XeLL/Eject boot (PC-configured, hardware boot UNTESTED):**
The USB kboot.conf now selects ABRIR O LINUX JA INSTALADO with timeout=0.
No manual menu selection is required. XeLL might still briefly print its
English menu, which cannot be removed from XeLL firmware using kboot.conf.
The experimental preinstalled ext4 desktop is not yet proven to boot.
The original 25-second diagnostic menu is backed up in the local work folder.
No NAND flash or internal Xbox HDD changes were made.

## Documentation

[Development source](scripts/v041-ext4/README.md) · [Boot files and Debian compatibility](docs/BOOT-CASPER-VMLINUX-DEBIAN.md) · [Detailed technical status](docs/V041-EXT4-BOOT-EXPERIMENTAL.md) · [Latest published alpha](https://github.com/heltindev/X360Linux/releases/tag/v0.4.0-alpha) · [Credits and licenses](docs/CREDITS.md)

**The local v0.4.1-dev files are experimental and are not included in the published v0.4.0-alpha ZIP.**

[Boot repair status](docs/V041-REPAIR-LOG.md) · [Inicialização automática via Eject (PT-BR)](docs/COMO-INICIAR-PTBR.md) — iniciar sem selecionar opções e recuperar o menu caso trave.
