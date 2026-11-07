# Upstream credit and license boundaries

This project integrates **existing work**. Original repository scripts and documentation retain the existing **Apache License 2.0**; third-party source code is not relicensed.

| Project | GitHub | License / notes |
|---|---|---|
| XeLL-Reloaded | https://github.com/Free60Project/xell-reloaded | Upstream source and license govern |
| XeLL historical | https://github.com/FuckinRandy/git-github.com-Free60Project-xell | Historical Xenon Linux Loader; README specifies GPL-2.0-only |
| Free60 kernel patches | https://github.com/Free60Project/linux-kernel-xbox360 | Kernel-related patches; preserve Linux upstream GPL obligations |
| Xenos Linux GPU | https://github.com/arelyx/xenos-linux-gpu | Mixed; see detailed upstream `LICENSE.md` |
| Free60 libxenon | https://github.com/Free60Project/libxenon | SDK/toolchain; check notices in distribution |
| Mesa freedreno | https://mesa3d.org/ | Mesa licensing and relevant MIT/BSD license files |
| X.Org | https://www.x.org/ | Xorg source and relevant MIT/X11 notices |

The xenos-linux-gpu upstream specifies: `kernel/`, `userspace/`, most scripts and tools under GPL-2.0-only; `mesa/patches/` under MIT; `xorg/` under MIT/X11; conformance big-endian patch under Apache-2.0; `docs/` under CC BY 4.0.

**We only link their source as a Git submodule**, preserving original authors, commits and license statements. The upstream screenshot linked in the README is also attributed to arelyx and shown from their repository.

## Important upstream caveat

The Xenos GPU project explicitly identifies its code as an AI-driven exploratory bring-up that has not undergone extensive human review. Do not misrepresent it as production-ready, formally verified or endorsed by upstream maintainers. Do not forward patches upstream as though they were our work.

## Release policy

Before any binary distribution, audit complete corresponding source, copyleft notices, attribution, microcode provenance and build instructions. Do not distribute Microsoft firmware, NAND dumps, machine-specific keys or copyrighted commercial game content.
