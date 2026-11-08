<div align="center">
  <img src="assets/x360linux-banner.svg" alt="X360Linux" width="100%" />
  <h2>Native Linux research for Xbox 360 — USB first.</h2>
  <p>Experimental PowerPC Linux boot and distro development for RGH/JTAG consoles.</p>
  <p><a href="https://github.com/heltindev/X360Linux/releases/tag/v0.3.0-alpha">v0.3 download</a> · <a href="docs/V03-LEGACY-XEX.md">XEX USB guide</a> · <a href="docs/ROADMAP.md">v0.4 roadmap</a></p>
</div>

## Corona Phison RGH - confirmed XEX black screen

**Important correction (2026-11-08):** On the maintainer's Corona Phison Xbox 360 with RGH, opening the legacy `default.xex` in Aurora **gives a black screen**. XeLL **does** open through the physical Eject button. The old 2011 XeLL/XellLaunch pair cannot be described as a verified working Corona XEX boot. A direct graphical Linux desktop remains **unverified**.

[Hardware status, Wi-Fi, progress and modular distros](docs/V04-STATUS-AND-MULTIDISTRO.md) · [Corona XEX issue](https://github.com/heltindev/X360Linux/issues/3)



## What works on the real Xbox 360?

**Corrected maintainer report — November 8, 2026:** the historical Aurora `default.xex` goes to a black screen on Corona Phison; XeLL works via Eject only. Direct Linux desktop remains unverified.

| Component | Status |
| --- | --- |
| Legacy `default.xex` via Aurora on Corona Phison | ❌ Confirmed black screen |
| NAND XeLL via physical Eject on Corona Phison | ✅ XeLL screen boots; Linux GUI not yet confirmed |
| Legacy `vmlinux` ELF and Ubuntu 10.10 SquashFS | ✅ File signatures and checksums verified |
| Automatic graphical desktop without installer | ⬜ Not yet demonstrated |
| Persistent Linux files on USB | ⬜ Not yet demonstrated |
| Keyboard, mouse, controller, audio, Ethernet | ⬜ Individual hardware tests pending |
| Separate X360Boot / Debian Ports shell experiments | ✅ Previous v0.2-era boot and shell testing; independent from the legacy XEX archive |

## v0.3.0-alpha - one XEX ZIP for everyone

**[Download X360Linux-v0.3.0-alpha-XEX-USB.zip](https://github.com/heltindev/X360Linux/releases/download/v0.3.0-alpha/X360Linux-v0.3.0-alpha-XEX-USB.zip)**

The release has a **single ZIP**, containing exactly the five files from the maintainer's Downloads/LINUX 360 directory: default.xex, xell.bin, vmlinux, casper/filesystem.squashfs, and readme.txt. The same files work as the experimental starting point for RGH/JTAG and ABadAvatar.

- **RGH/JTAG:** Extract to one FAT32 pendrive and launch default.xex from Aurora.
- **ABadAvatar:** Use TWO separate pendrives: USB 1 for ABadAvatar exploit files (unchanged), USB 2 for the same extracted Linux ZIP. Launch default.xex from USB 2 using a compatible homebrew XEX launcher.
- **Test status:** Aurora XEX fails on Corona Phison (black screen), while XeLL via Eject works. Direct Linux GUI and ABadAvatar are not confirmed.

There are **no alternative Debian/FreeMyXe assets** in the current v0.3 release. See [full instructions](docs/V03-LEGACY-XEX.md). Never flash NAND or install onto Xbox HDD partitions.

**Retired:** the old x360linux-local-cache release and tag have been deleted. The automatic cache upload and ISO packing workflow is disabled. Neither is needed for the tested XEX boot path.

## v0.4.0-alpha - preloaded XEX live USB (experimental)

[Download the v0.4.0-alpha XEX USB preview](https://github.com/heltindev/X360Linux/releases/tag/v0.4.0-alpha) - marked UNTESTED.

The existing Ubuntu 10.10 Xenon GNOME desktop comes PRELOADED in the USB SquashFS. The original XEX, XeLL and PowerPC kernel were preserved. The installer auto-start was disabled, GDM was configured for direct live-user login, and optional background services were trimmed to try improving boot speed.

The patch and ZIP passed local static verification, but actual desktop boot on Xbox, startup speed improvement, writable USB persistence and ABadAvatar are NOT yet verified. This is not modern Debian. For RGH launch default.xex from Aurora on one FAT32 USB; ABadAvatar requires a separate exploit pendrive and an XEX-capable loader for the second Linux USB.

See [v0.4 detailed guide](docs/V04-XEX-LIVE.md) and [source build script](scripts/build-v04-xex-live.sh).

## v0.4 — develop a real USB-native Linux distribution

Use the known-working Eject XeLL as the hardware baseline; the Corona Phison Aurora XEX black-screen problem must be fixed independently. The planned boot sequence is **Aurora XEX → XeLL → Xenon kernel → initramfs → USB root filesystem → lightweight Linux desktop**, without a manual installer or console commands.

Target a supported **Debian Ports PowerPC 32-bit big-endian userland**, subject to Xenon kernel ABI and driver validation, and **Openbox + LXPanel + PCManFM** (not IceWM). Add persistence, keyboard/mouse, wired networking, controller pointer and audio/video in measurable hardware-tested stages, within the Xbox 360's **512 MiB RAM** budget.

**Build v0.4 locally on Windows/WSL2.** The working folder is `Desktop/PEN DRIVE/BOOT-DIRETO/v0.4-dev`, which preserves the 2011 binaries as a reference and keeps the earlier unverified Debian image unchanged. No GitHub Actions build is required for v0.4.

See [the v0.4 roadmap](docs/ROADMAP.md).

## Project layout

```text
launcher/               Original X360Boot ELF experiments (not this legacy XEX)
kernel/                 Xenon Linux kernel work
distro/                 Debian Ports and initramfs experiments
release/                Older Debian boot ZIP generation
scripts/                Build, diagnostics and local development
docs/V03-LEGACY-XEX.md  Legacy XEX boot guide, verified hashes, limitations
docs/ROADMAP.md         v0.4 direct USB Linux milestones
```

## Safety and open-source provenance

**Never flash the NAND or rename `xell.bin` as `updxell.bin` / `updflash.bin`.** The legacy Ubuntu 10.10 image is obsolete and not suitable for sensitive browsing.

The legacy 2011 files are third-party binaries supplied to the project, not built from current X360Linux source. Their exact historical sources and redistribution/license obligations still require an audit. Repository license terms do **not** relicense XeLL, Linux or Ubuntu. See [credits and licenses](docs/CREDITS.md).
