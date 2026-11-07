# Source dependencies and licenses

X360Linux's original application, scripts and documentation are hosted in this repository. Its native launcher uses **LibXenon**, and its Linux work depends on **existing, separately licensed projects**. The repository is open source, but that does **not** make third-party code original to this project.

| Component | Project/source | License boundaries |
|---|---|---|
| Initial ELF loading and Xenon device tree | [Free60 XeLL-Reloaded](https://github.com/Free60Project/xell-reloaded) | Keep upstream copyright/license notices |
| Xbox 360/Linux kernel work | [Free60 Xbox 360 Linux kernel patches](https://github.com/Free60Project/linux-kernel-xbox360) and [Linux](https://kernel.org/) | Linux kernel GPL-2.0 and relevant component licenses |
| Bare-metal ELF runtime | [Free60 LibXenon](https://github.com/Free60Project/libxenon) | Original launcher handoff integrates GPL-2.0-only code |
| Minimal userspace | [BusyBox](https://busybox.net/) | GPL-2.0; corresponding source/build instructions required |
| X360Desk photo decoding | [stb_image](https://github.com/nothings/stb) by Sean Barrett and contributors, pinned at `4e9b368bfc071e97206ea5c6adba68dd0cbf8897` | Public Domain / MIT dual license. Full header carries its license |
| X360Desk bitmap font | [font8x8](https://github.com/dhepper/font8x8) by Daniel Hepper, pinned at `8e279d2d864e79128e96188a6b9526cfa3fbfef9` | Public Domain per header |
| Future Xenos graphics | [xenos-linux-gpu](https://github.com/arelyx/xenos-linux-gpu) | Mixed licenses; see its LICENSE.md |
| Future graphics libraries | Mesa / X.Org | Follow their upstream source license notices |

Original **launcher code** in `launcher/` is GPL-2.0-only. Original repository-level scripts/documentation are Apache-2.0 unless the file states another license. Included external sources, Linux and BusyBox are **not relicensed** by the repository root LICENSE.

Pinned third-party source trees are included as Git submodules under `external/`, with their commit history and notices intact. Do not redistribute third-party binaries without checking source-availability and license obligations. No Microsoft firmware, keys, NAND images or game files belong in this project.
