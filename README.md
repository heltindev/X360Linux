<div align="center">
  <img src="assets/x360linux-banner.svg" alt="X360Linux" width="100%" />
  <h2>Linux for Xbox 360. Native hardware. Open source.</h2>
  <p>I'm building an Xbox 360 Linux distribution that runs directly on the console's original hardware.</p>
  <p><a href="https://github.com/heltindev/X360Linux/releases/tag/v0.1.0-alpha">Download v0.1.0-alpha</a> · <a href="https://github.com/heltindev/X360Linux/actions">GitHub Actions</a> · <a href="docs/TESTING.md">Getting started</a></p>
</div>

## 🧪 Project status

| Component | Status |
|---|---|
| **X360Boot launcher** (native Xbox 360 ELF) | ✅ Compiles in GitHub Actions |
| **Minimal Linux system** (PowerPC64 BusyBox) | ✅ Compiles in GitHub Actions |
| **XeLL bootloader** | ✅ Reference builds compile |
| **Xbox 360 Linux kernel** | 🟡 Build/integration in progress |
| **Linux booting on a real Xbox 360** | ⬜ Not verified |
| **Graphics, sound, networking and storage** | ⬜ Not verified in this project |
| **Complete ready-to-use Linux image** | ⬜ Not available yet |

**Goal:** Boot a minimal Linux shell on a real Xbox 360 first, then improve hardware support and build a full desktop distribution. This is an early alpha, **not a claim of 100% compatibility**.

## 🚀 Start here

1. **[Download v0.1.0-alpha](https://github.com/heltindev/X360Linux/releases/tag/v0.1.0-alpha)** for the experimental launcher and Linux userspace.
2. Read **[Getting started and Xbox 360 testing](docs/TESTING.md)** before placing files on a USB drive.
3. Want to compile the project? Open **[GitHub Actions](https://github.com/heltindev/X360Linux/actions)** and run **Build Xbox 360**.
4. A full Linux image will require a compatible Xenon kernel. The **Build Linux image** workflow is experimental.

> **Required:** An Xbox 360 already modified for homebrew (RGH/JTAG), with a known-working initial ELF loader such as XeLL. There is no stock-console boot method, XEX or NAND installer here. Never flash experimental boot files.

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

## 🎯 Roadmap

**First:** Linux shell on Xbox 360. **Next:** Better Xbox 360 hardware support. **Later:** Our own native desktop distribution and an optional XEX launcher.

See [Roadmap](docs/ROADMAP.md). Contributions are welcome; see [Contributing](CONTRIBUTING.md). Licensing and source acknowledgements are maintained in [Credits & licenses](docs/CREDITS.md).

**X360Linux is free and open source.**
