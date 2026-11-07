<div align="center">
  <img src="assets/x360linux-banner.svg" alt="X360Linux" width="100%" />
  <h2>Linux for Xbox 360. Native hardware. Open source.</h2>
  <p>I'm building an Xbox 360 Linux distribution that runs directly on the console's original hardware.</p>
  <p><a href="https://github.com/heltindev/X360Linux/releases/tag/v0.2.0-alpha">Download experimental v0.2.0-alpha</a> · <a href="https://github.com/heltindev/X360Linux/releases/tag/v0.1.0-alpha">Menu-only v0.1.0-alpha</a> · <a href="docs/TESTING.md">Beginner guide</a></p>
</div>

## 🧪 Project status

| Component | Status |
|---|---|
| **X360Boot launcher** (native Xbox 360 ELF) | ✅ Compiles; menu confirmed on real Xbox 360 |
| **Minimal Linux system** (PowerPC32 BusyBox) | 🟡 Rebuilding for Xenon after a real-hardware CPU instruction fault |
| **XeLL bootloader** | ✅ Reference builds compile |
| **Xbox 360 Linux kernel** | ✅ Booted on a real RGH Xbox 360; reached PID 1 |
| **Linux booting on a real Xbox 360** | 🟡 Kernel started; old PPC64 BusyBox failed with SIGILL before shell |
| **Graphics, sound, networking and storage** | ⬜ Not verified in this project |
| **Experimental Linux ISO and USB image** | 🟡 v0.2 alpha available; boot not yet verified |

**Goal:** Reach an interactive Linux shell on real Xbox 360 hardware, then improve drivers and a lightweight desktop. The Xenon kernel has already reached `/init` on an RGH console, but the old BusyBox hit an illegal instruction. The next test uses conservative 32-bit PowerPC BusyBox. This is experimental, **not a claim of full compatibility**.

## 🚀 Start here

1. **[v0.1.0-alpha — menu test](https://github.com/heltindev/X360Linux/releases/tag/v0.1.0-alpha)**: choose the RGH or ABadAvatar/FreeMyXe ZIP. The X360Boot menu is confirmed.
2. **[v0.2.0-alpha — experimental Linux test](https://github.com/heltindev/X360Linux/releases/tag/v0.2.0-alpha)**: USB packs now include the kernel, device tree and minimal shell; an untested ISO is also available.
3. Read **[Getting started and Xbox 360 testing](docs/TESTING.md)**. Only extract the ZIP for USB; the ISO is for compatible XeLL optical boot methods.
4. In the simplified X360Boot, move to **X360Linux** and press **A** to attempt boot. The progress bar covers preparation, not guaranteed boot success. A kernel panic may still show diagnostics. GitHub Actions passing does **not** prove the shell works on console.

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
- [ ] Reach an interactive Linux shell and document hardware test results.

### Phase 2 — Reliable hardware and storage

- [ ] Confirm USB storage, keyboard and controller input **inside Linux** (the X360Boot menu already supports the Xbox controller).
- [ ] Detect wired Ethernet and configure networking automatically with DHCP.
- [ ] Keep personal files and system settings after reboot (USB persistence first).
- [ ] Read and write supported Xbox 360 HDD storage safely, **without formatting existing Xbox partitions**.
- [ ] Test graphics, audio, network, storage, startup logs and recovery.

### Phase 3 — Build our own lightweight distribution

- [ ] Evaluate minimal Debian PPC64 **big-endian** packages against the current BusyBox base.
- [ ] Build a reproducible X360Linux distribution optimized for the Xbox 360's 512 MB RAM.
- [x] Make X360Boot detect a complete `X360Linux/` boot folder and start loading when A is pressed.
- [ ] Package a simple bootable USB image; investigate optional HDD installation after persistence works.
- [ ] Add a lightweight desktop, mouse and keyboard support.
- [ ] Implement lightweight picture viewing and video playback suitable for Xenon's framebuffer and 512 MB RAM.
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

**Current priority: test the Linux shell through XeLL. No XEX work yet.**

See [Roadmap](docs/ROADMAP.md). Contributions are welcome; see [Contributing](CONTRIBUTING.md). Licensing and source acknowledgements are maintained in [Credits & licenses](docs/CREDITS.md).

**X360Linux is free and open source.**
