<div align="center">
  <img src="assets/x360linux-banner.svg" alt="X360Linux" width="100%" />
  <h2>Linux for Xbox 360. Native hardware. Open source.</h2>
  <p>I'm building an Xbox 360 Linux distribution that runs directly on the console's original hardware.</p>
  <p><a href="https://github.com/heltindev/X360Linux/releases/tag/v0.3.0-alpha">v0.3.0-alpha graphical preview (experimental)</a> · <a href="https://github.com/heltindev/X360Linux/releases/tag/v0.2.0-alpha">v0.2.0-alpha known shell build</a> · <a href="https://github.com/heltindev/X360Linux/releases/tag/v0.1.0-alpha">Menu-only v0.1.0-alpha</a> · <a href="docs/TESTING.md">Beginner guide</a></p>
</div>

## 🧪 Project status

| Component | Status |
|---|---|
| **X360Boot launcher** (native Xbox 360 ELF) | ✅ Compiles; menu confirmed on real Xbox 360 |
| **Minimal Linux system** (PowerPC32 BusyBox) | ✅ Reached the BusyBox shell prompt on a real RGH Xbox 360 |
| **XeLL bootloader** | ✅ Reference builds compile |
| **Xbox 360 Linux kernel** | ✅ Booted on a real RGH Xbox 360; reached PID 1 |
| **Linux booting on a real Xbox 360** | ✅ Kernel and BusyBox shell started; interactive keyboard/TTY still under test |
| **X360Desk framebuffer interface** | ✅ Launched on an actual RGH Xbox 360; TV scaling is being improved |
| **Graphics acceleration, sound, Ethernet, HDD persistence** | ⬜ Not verified in this project |
| **Photo/video and controller navigation** | 🟡 Written for PowerPC32; real console interaction still needs testing |
| **Debian Ports big-endian powerpc base** | 🟡 Separate signed upstream bootstrap prepared; console boot not verified |
| **ISO included in beginner USB ZIPs** | 🟡 Repackaging update in progress; the ISO is NOT executed from USB |

**Milestone achieved:** X360Boot, Xenon Linux, BusyBox and **the X360Desk graphical interface all appeared on real RGH Xbox 360 hardware** (photo confirmed). The first v0.3 interface had very small text and awkward spacing; the TV-scale layout update is being compiled. USB controller input, media playback, signed Debian Ports runtime and other hardware features still require real-console testing. A fully booted Debian desktop, MP4 with audio, GPU acceleration and persistence are NOT included.

## 🚀 Start here

1. **[v0.3.0-alpha — graphical preview](https://github.com/heltindev/X360Linux/releases/tag/v0.3.0-alpha)**: the native GUI already appeared on physical Xbox 360 hardware. A readability update is under development. See the [v0.3 guide](docs/V03-GRAPHICAL-PREVIEW.md).
3. **[v0.1.0-alpha — menu test](https://github.com/heltindev/X360Linux/releases/tag/v0.1.0-alpha)**: choose the RGH or ABadAvatar/FreeMyXe ZIP. The X360Boot menu is confirmed.
2. **[v0.2.0-alpha — experimental Linux test](https://github.com/heltindev/X360Linux/releases/tag/v0.2.0-alpha)**: USB packs now include the kernel, device tree and minimal shell; an untested ISO is also available.
4. Read **[Getting started and Xbox 360 testing](docs/TESTING.md)**. The updated USB ZIP also includes the ISO as a reference. **The ISO is NOT what XeLL loads from the USB drive.**
5. **Autostart:** launch your working XeLL with the USB drive inserted. X360Boot detects the `X360Linux/` folder and starts it automatically after a 3-second window. **Press B to cancel** and keep the menu. The terminal is still minimal BusyBox, not Debian or a graphical desktop.

> **Required:** An already-working XeLL method: RGH/JTAG, or a compatible software exploit with FreeMyXe. The ABadAvatar ZIP is an add-on to existing exploit files, not an unlocker. There is no `default.xex` or NAND installer here. Never flash experimental boot files.

## 📁 Project structure

```text
X360Linux/
├── .github/workflows/    # Automatic builds
├── launcher/             # X360Boot: menu, file selection and Linux boot
├── distro/               # Our Linux userspace and image packaging
├── kernel/               # Xbox 360 Linux kernel build
├── external/             # Third-party source dependencies
└── docs/                 # Testing, roadmap and licenses
```

## 🎯 Development roadmap

**Boot and test through XeLL first.** The native `default.xex` launcher is the **last milestone**, only after Linux boots successfully on a real Xbox 360. Checkmarks indicate completed development tasks, not verified console compatibility.

### Phase 1 — First Linux shell (current focus)

- [x] Build the native X360Boot PowerPC ELF launcher.
- [x] Build a minimal BusyBox Linux userspace (now testing baseline PowerPC32 on the Xenon kernel).
- [x] Compile experimental Xbox 360 Linux kernel candidates in GitHub Actions.
- [x] Verify the Xenon kernel reaches the initramfs on the real console (old BusyBox then failed with SIGILL).
- [x] Boot the Xenon kernel through XeLL on a **real Xbox 360** (reached `/init`).
- [x] Reach a BusyBox `#` shell prompt on a real Xbox 360 (photo confirmed).
- [ ] Confirm interactive USB keyboard commands and controlling TTY (BusyBox `cttyhack` update still to be tested).

### Phase 2 — Reliable hardware and storage

- [ ] Confirm USB storage, keyboard and controller input **inside Linux** (the X360Boot menu already supports the Xbox controller).
- [ ] Detect wired Ethernet and configure networking automatically with DHCP.
- [ ] Keep personal files and system settings after reboot (USB persistence first).
- [ ] Read and write supported Xbox 360 HDD storage safely, **without formatting existing Xbox partitions**.
- [ ] Test graphics, audio, network, storage, startup logs and recovery.

### Phase 3 — Build our own lightweight distribution

- [x] Add a signed Debian Ports 32-bit big-endian bootstrap workflow, separate from the current working BusyBox boot.
- [ ] Boot and test a real Debian Ports root filesystem on an external device without touching the Xbox HDD.
- [ ] Build a reproducible X360Linux distribution optimized for the Xbox 360's 512 MB RAM.
- [x] Make X360Boot detect a complete `X360Linux/` folder and start automatically after a 3-second, B-to-cancel window.
- [ ] Package a simple bootable USB image; investigate optional HDD installation after persistence works.
- [x] Implement an original lightweight framebuffer GUI and a controller cursor (PowerPC32 build test only).
- [x] Display X360Desk framebuffer GUI on a real RGH Xbox 360 (user photo).
- [ ] Verify controller navigation, gallery playback, USB media mounting and improved TV-scale layout on real hardware.
- [x] Implement JPEG/PNG/BMP/PPM viewers and experimental silent X36V playback.
- [ ] Confirm actual graphical image/video performance on the Xbox 360, then add native compressed-video and audio support.
- [ ] Support controller navigation inside Linux and test wired and wireless controller compatibility separately.
- [ ] Improve the Xbox 360-specific kernel drivers and automatic hardware configuration.
- [ ] Add package management, practical updates and modern TLS/certificates.
- [ ] Investigate an up-to-date web browser that can actually run on PowerPC64; compatibility and speed are not guaranteed.
- [ ] Test everyday use on original hardware and publish a beginner-friendly release.

### Phase 4 — XEX launcher (final step only)

- [ ] After the XeLL-based distribution is proven, research a safe `default.xex` entry point.
- [ ] Develop and test the handoff from XEX to the native Linux boot chain.
- [ ] Enable launching from Aurora while keeping XeLL as a fallback.
- [ ] Publish XEX binaries **only after successful real-console tests**.

**Current priority: improve the native GUI, verify controller/media features on real hardware, and prepare signed Debian Ports rootfs compatibility. No XEX work yet.**

See [Roadmap](docs/ROADMAP.md). Contributions are welcome; see [Contributing](CONTRIBUTING.md). Licensing and source acknowledgements are maintained in [Credits & licenses](docs/CREDITS.md).

**X360Linux is free and open source.**
