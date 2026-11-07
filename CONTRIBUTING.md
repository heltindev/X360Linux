# Contributing to X360Linux

Thank you for helping bring open-source operating systems to the Xbox 360.

## First principles

- Write issues, code comments, documentation and pull requests in **English**.
- State exactly which Xbox 360 revision, RGH/JTAG or softmod, XeLL version, kernel version and toolchain you used.
- Attach redacted build/boot logs, reproduction steps and clear before/after results.
- Keep experimental claims separate from measured results. A successful PC build is **not** a successful console boot.
- Do not distribute console-specific keys, NAND images, proprietary firmware or copyrighted game content.
- Do not flash NAND to test the research build. Keep the installed XeLL recovery method working.
- Send upstream Xenos GPU patches to arelyx's project only after appropriate review; do not imply our repo authors wrote that source.

## Suggested workflow

1. Read [roadmap](docs/ROADMAP.md) and [boot safety](docs/BOOT-SAFETY.md).
2. Run `bash scripts/doctor.sh` and `python3 scripts/validate.py`.
3. Fork, create a topic branch and make the smallest reproducible change.
4. Document measured behavior and note what you did **not** test.
5. Open a pull request, linking an issue or a relevant upstream discussion.

## License boundaries

Original X360Linux text and scripts are Apache-2.0. Submodules and their component licenses remain unchanged; see [license notes](docs/UPSTREAM-AND-LICENSES.md). Do not copy upstream GPL-licensed code into Apache headers.
