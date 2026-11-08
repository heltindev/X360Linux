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
| Debian installed in a USB ext4 image | ✅ Mounted and reached Debian init on a real Xbox 360 |
| Boot Debian directly from USB | ✅ Debian shell and command input confirmed on a real Xbox 360 |
| USB file persistence after reboot | 🟡 Designed; **not hardware-tested** |
| IceWM desktop | 🟡 Automatic startup, pending Xbox 360 display testing |
| Audio, browser and controller inside Debian | ⬜ Future milestones |
| Xbox 360 XEX launcher | ⬜ Last milestone, after stable USB Linux |

**Current direction:** X360Linux boots the actual Debian Ports **32-bit big-endian PowerPC** filesystem from an ISO file on a FAT32 pendrive. A separate ext4 data image keeps changes. The previous Photos/Videos/System demo is not started and is not included in the new boot initramfs.

A real Xbox 360 mounted the USB ext4 image, opened the Debian shell and returned Debian GNU/Linux forky/sid from `cat /etc/os-release`. That direct ext4 build is available under [v0.2.0-alpha](https://github.com/heltindev/X360Linux/releases/tag/v0.2.0-alpha). A later hardware test confirmed the ISO reached the Debian shell. This revision starts IceWM automatically and falls back to that shell if graphics fail.

## 🚀 Quick start

1. Download the **[v0.3.0-alpha USB Debian ZIP](https://github.com/heltindev/X360Linux/releases/tag/v0.3.0-alpha)** for your RGH/JTAG or existing FreeMyXe/ABadAvatar XeLL setup.
2. Back up your FAT32 USB and extract the ZIP directly to its **root**, with `xenon.elf` next to the `X360Linux/` folder. At least **2 GB free** is recommended.
3. Check the presence of `xenon.elf`, `X360Linux/vmlinux`, `X360Linux/initramfs.cpio.gz`, `X360Linux/USB-ROOT.ID`, and `X360Linux/X360Linux.iso` and `X360Linux/USB-DATA.ext4`.
4. Boot the Xbox with the same XeLL method you already use. X360Boot automatically starts the Linux kernel.
5. Linux searches for **only the explicitly marked USB partition**, mounts the ISO and its writable data image, then starts Debian; otherwise it uses a rescue shell. Debian opens the IceWM desktop automatically. If graphics fail, the Debian shell remains available.

**No partitioning wizard, NAND flashing, Xbox HDD installation or internal disk formatting.** Extracting the ZIP onto the USB is the installation step. The ISO is read-only, and the data image stores your changes.

If XeLL stops at `Requesting DHCP`, disconnect Ethernet, restart XeLL and reconnect it after Debian starts. Debian attempts wired DHCP in the background.

See [USB Debian beginner guide](docs/USB-DEBIAN-BOOT.md) and [recovery steps](docs/TESTING.md).

## Build locally + package with GitHub Actions (recommended)

The slow Debian build is **no longer triggered automatically on each GitHub push**. The previous Action was cancelled while TAR tried to archive a mounted Linux `/proc`; this is now prevented in the build scripts.

**Windows / WSL2:** see the [one-time preparation and one-click local build guide](docs/BUILD-LOCALLY.md). After Ubuntu WSL2 is ready, double-click `scripts/BUILD-LOCAL.cmd`. The PC compiles the Xenon kernel, BusyBox and Debian Ports and uploads verified components to a GitHub build cache.

Then open [Package precompiled Linux with XeLL and ISO](https://github.com/heltindev/X360Linux/actions/workflows/package-prebuilt.yml). This **shorter workflow** compiles XeLL/X360Boot, assembles the ISO and both beginner USB ZIPs, without recompiling the Linux kernel or installing Debian again. First run with **publish_release = false** to inspect the artifacts; publishing the experimental v0.5 alpha is optional.

The older [Full Linux rebuild](https://github.com/heltindev/X360Linux/actions/workflows/build.yml) remains available **manually** for diagnostics. Fast [source checks](https://github.com/heltindev/X360Linux/actions/workflows/checks.yml) run automatically.

**Local PC status:** Ubuntu 24.04 WSL2 was installed and successfully started on Windows (2026-11-08), with no BIOS changes required. The local Xenon/Debian build and new ISO still require validation before release.

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
- [x] Confirm kernel loop, ext4 and USB mounting on real RGH hardware.
- [x] Verify Debian shell input on real RGH hardware.
- [ ] Save a file, reboot and verify persistence.
- [ ] Add a lightweight real Linux graphical desktop for 512 MB RAM.
- [ ] Add sound, compressed video, a mouse-compatible Xbox controller driver and networking.
- [ ] Add secure package updates and an appropriate PowerPC web browser.
- [ ] Only after all that, develop the optional `default.xex` launcher.

Credits and third-party licenses: [docs/CREDITS.md](docs/CREDITS.md). **Never rename files to `updflash.bin` or `updxell.bin`.**
