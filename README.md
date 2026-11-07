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
| **Minimal Linux system** (PowerPC64 BusyBox) | ✅ Compiles in GitHub Actions |
| **XeLL bootloader** | ✅ Reference builds compile |
| **Xbox 360 Linux kernel** | ✅ Compiles in Actions; console boot not yet verified |
| **Linux booting on a real Xbox 360** | ⬜ Not verified |
| **Graphics, sound, networking and storage** | ⬜ Not verified in this project |
| **Experimental Linux ISO and USB image** | 🟡 v0.2 alpha available; boot not yet verified |

**Goal:** Boot a minimal Linux shell on a real Xbox 360 first, then improve hardware support and build a full desktop distribution. This is an early alpha, **not a claim of 100% compatibility**.

## 🚀 Start here

1. **[v0.1.0-alpha — menu test](https://github.com/heltindev/X360Linux/releases/tag/v0.1.0-alpha)**: choose the RGH or ABadAvatar/FreeMyXe ZIP. The X360Boot menu is confirmed.
2. **[v0.2.0-alpha — experimental Linux test](https://github.com/heltindev/X360Linux/releases/tag/v0.2.0-alpha)**: USB packs now include the kernel, device tree and minimal shell; an untested ISO is also available.
3. Read **[Getting started and Xbox 360 testing](docs/TESTING.md)**. Only extract the ZIP for USB; the ISO is for compatible XeLL optical boot methods.
4. Want to compile? Use **[GitHub Actions](https://github.com/heltindev/X360Linux/actions)**. A green build does **not** prove Linux boots on console.

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
- [x] Build a minimal PowerPC64 BusyBox Linux userspace.
- [x] Compile experimental Xbox 360 Linux kernel candidates in GitHub Actions.
- [ ] Verify the kernel, Xenon device tree and initramfs work together.
- [ ] Boot the full system through XeLL on a **real Xbox 360**.
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
- [ ] Make X360Boot detect a complete `X360Linux/` boot folder automatically.
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
