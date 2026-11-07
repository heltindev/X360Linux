<div align="center">
  <img src="assets/x360linux-banner.svg" alt="X360Linux" width="100%" />
  <h2>Native Linux for Xbox 360. USB-first. Open source.</h2>
  <p>I'm developing a lightweight Linux distribution for original Xbox 360 hardware.</p>
  <p><a href="https://github.com/heltindev/X360Linux/releases">Downloads</a> · <a href="docs/USB-DEBIAN-BOOT.md">USB Debian installation guide</a> · <a href="docs/ROADMAP.md">Roadmap</a></p>
</div>

## 🧪 Project status

| Component | Status |
|---|---|
| X360Boot / XeLL launcher | ✅ Confirmed on real Xbox 360 |
| Xenon kernel + static PowerPC32 BusyBox | ✅ Booted on real RGH Xbox 360 |
| Early X360Desk GUI (v0.3) | ✅ Showed on real Xbox 360, but **discontinued** |
| Real signed Debian Ports PowerPC base | ✅ Built and tested on QEMU PowerPC |
| Debian installed in a USB ext4 image | 🟡 Implemented; build and hardware boot need verification |
| Boot Debian directly from USB | 🟡 XeLL → Xenon kernel → USB ext4 → Debian; **not hardware-tested** |
| USB file persistence after reboot | 🟡 Designed; **not hardware-tested** |
| Desktop, audio, browser, mouse and controller inside Debian | ⬜ Future milestones |
| Xbox 360 XEX launcher | ⬜ Last milestone, after stable USB Linux |

**Current direction:** X360Linux boots the actual Debian Ports **32-bit big-endian PowerPC** filesystem from a preinstalled ext4 file on a FAT32 pendrive. The previous Photos/Videos/System demo is not started and is not included in the new boot initramfs.

The Xenon Linux kernel and early graphics have already run on actual hardware, but **the new USB ext4 Debian boot path has not yet been verified on a real Xbox 360**. The first goal is a working Debian command-line environment; a proper low-memory desktop comes later. Do not mistake compiling an image for a proven console installation.

## 🚀 Quick start

1. Download the **[v0.3.0-alpha USB Debian ZIP](https://github.com/heltindev/X360Linux/releases/tag/v0.3.0-alpha)** for your RGH/JTAG or existing FreeMyXe/ABadAvatar XeLL setup.
2. Back up your FAT32 USB and extract the ZIP directly to its **root**, with `xenon.elf` next to the `X360Linux/` folder. At least **2 GB free** is recommended.
3. Check the presence of `xenon.elf`, `X360Linux/vmlinux`, `X360Linux/initramfs.cpio.gz`, `X360Linux/USB-ROOT.ID`, and `X360Linux/system.ext4`.
4. Boot the Xbox with the same XeLL method you already use. X360Boot automatically starts the Linux kernel.
5. Linux searches for **only the explicitly marked USB partition**, mounts the ext4 system image and attempts Debian; otherwise it uses a rescue shell. A USB keyboard remains necessary for initial diagnostics.

**No partitioning wizard, NAND flashing, Xbox HDD installation or internal disk formatting.** The Debian system is preinstalled inside `system.ext4`; extracting the ZIP onto the USB is the installation step. The optional ISO is inside `X360Linux/` for experimentation.

See [USB Debian beginner guide](docs/USB-DEBIAN-BOOT.md) and [recovery steps](docs/TESTING.md).

## 📁 Project layout

```text
launcher/              Native X360Boot ELF, loads Xenon Linux via XeLL
kernel/                Free60-patched Xenon Linux kernel build
distro/rootfs/         Minimal USB discovery / recovery initramfs
distro/debian/         Debian Ports bootstrap and ext4 USB image builder
release/               Reproducible beginner FAT32 USB ZIP packs
.github/workflows/     Cross-compilation, signed Debian, USB packaging
docs/                  Beginner guide, roadmap, third-party licenses
```

## 🎯 Development priorities

- [x] Prove real Xbox 360 ELF loader, kernel and basic Linux.
- [x] Build an authenticated Debian Ports PowerPC32 base using signed packages.
- [x] Write an automatic USB-first Debian boot and fallback mechanism.
- [ ] Confirm kernel loop, ext4 and USB mounting on real RGH hardware.
- [ ] Verify Debian shell input, save a file, reboot and verify persistence.
- [ ] Add a lightweight real Linux graphical desktop for 512 MB RAM.
- [ ] Add sound, compressed video, a mouse-compatible Xbox controller driver and networking.
- [ ] Add secure package updates and an appropriate PowerPC web browser.
- [ ] Only after all that, develop the optional `default.xex` launcher.

Credits and third-party licenses: [docs/CREDITS.md](docs/CREDITS.md). **Never rename files to `updflash.bin` or `updxell.bin`.**
