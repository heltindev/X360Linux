<div align="center">
  <img src="assets/x360linux-banner.svg" alt="X360Linux" width="100%" />
  <h2>Native Linux research for Xbox 360 — USB first.</h2>
  <p>Experimental PowerPC Linux boot and distro development for RGH/JTAG consoles.</p>
  <p><a href="https://github.com/heltindev/X360Linux/releases/tag/v0.3.0-alpha">v0.3 download</a> · <a href="docs/V03-LEGACY-XEX.md">XEX USB guide</a> · <a href="docs/ROADMAP.md">v0.4 roadmap</a></p>
</div>

## What works on the real Xbox 360?

**Maintainer hardware report — November 8, 2026:** The legacy `default.xex` starts from an RGH Xbox 360 dashboard and reaches the Linux boot/installer experience. This verifies the XEX-to-XeLL launch path; it **does not** yet verify a complete desktop boot from USB.

| Component | Status |
| --- | --- |
| Legacy `default.xex` launched from Aurora | ✅ Confirmed by maintainer on a real RGH Xbox 360 |
| XeLL/Linux startup or installer | ✅ Reached according to maintainer's hardware test |
| Legacy `vmlinux` ELF and Ubuntu 10.10 SquashFS | ✅ File signatures and checksums verified |
| Automatic graphical desktop without installer | ⬜ Not yet demonstrated |
| Persistent Linux files on USB | ⬜ Not yet demonstrated |
| Keyboard, mouse, controller, audio, Ethernet | ⬜ Individual hardware tests pending |
| Separate X360Boot / Debian Ports shell experiments | ✅ Previous v0.2-era boot and shell testing; independent from the legacy XEX archive |

## v0.3.0-alpha — XEX is the primary boot path

**[Download release v0.3.0-alpha](https://github.com/heltindev/X360Linux/releases/tag/v0.3.0-alpha)**

- **Legacy XEX/Ubuntu Xenon:** `X360Linux-v0.3.0-alpha-Legacy-XEX-USB.zip` — historical 2011 Ubuntu 10.10 Xenon binaries. The maintainer confirmed the XEX launches the Linux startup/installer path on RGH hardware.
- **Older Debian/IceWM experiment:** The previously released RGH and FreeMyXe Debian ZIP assets are separate, historical boot methods. They are not interchangeable with the legacy XeLL/XEX files and **have not** been validated as full desktops by this test.

### Legacy XEX quick start

1. Use an RGH/JTAG Xbox 360 with a working Aurora dashboard.
2. Back up your pendrive and format it as one **FAT32** volume.
3. **Extract** the legacy ZIP onto the **USB root**, not an extra directory. Root must contain `default.xex`, `xell.bin`, `vmlinux` and `casper/filesystem.squashfs`.
4. On Xbox 360, start `default.xex` with Aurora. The compatible XeLL/Linux startup will be attempted.
5. **The Ubuntu installer/startup flow may appear. Do not install to internal Xbox storage.** Direct graphical live boot is not yet provided.

No Rufus, ISO extraction or build step is needed for that boot attempt. For precise checksums, warnings and known limitations, see **[v0.3 legacy USB instructions](docs/V03-LEGACY-XEX.md)**.

**Retired:** the old x360linux-local-cache release and tag have been deleted. The automatic cache upload and ISO packing workflow is disabled. Neither is needed for the tested XEX boot path.

## v0.4 — develop a real USB-native Linux distribution

Use the hardware-confirmed XEX launch route as the starting point. The planned boot sequence is **Aurora XEX → XeLL → Xenon kernel → initramfs → USB root filesystem → lightweight Linux desktop**, without a manual installer or console commands.

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
