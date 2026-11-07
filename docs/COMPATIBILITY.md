# Hardware compatibility matrix

This is an evidence-based matrix, not a marketing checklist.

| Hardware / configuration | Upstream evidence | X360Linux verified? |
|---|---|---|
| Xbox 360 Trinity Slim + Peer Pressure compatible XeLL | Linux 6.18.58, GPU, IceWM: [arelyx](https://github.com/arelyx/xenos-linux-gpu) | **No** |
| Xbox 360 RGH or JTAG using XeLL-Reloaded | Bootloader source supports relevant boot entry points | **No** |
| Xbox 360 Xenon / Zephyr / Falcon / Jasper | Individual model behavior not established here | **No** |
| Xbox 360 Corona / Winchester | GPU and Linux compatibility not established here | **No** |
| Linux 6.18.58 + Free60 Xenon patch | Used by upstream GPU research | **Not built here** |
| GLES 2.0 / OpenGL 2.0 acceleration | Upstream demo on Trinity | **Not reproduced here** |
| Xorg / IceWM | Upstream demo on Trinity | **Not reproduced here** |
| Audio output on TV | Upstream module reports playback, not confirmed by listening | **No** |
| HDMI modes beyond 720p | Unverified | **No** |

Do not infer Xbox 360 model compatibility only from a shared CPU or GPU family.

## Required hardware report

For each positive claim, provide:

- Board revision and mod/boot method (no CPU/DVD keys).
- XeLL version and exact `kboot.conf` boot entry with credentials removed.
- Kernel tarball version, Free60 patch commit and GPU submodule commit.
- Kernel config, cross-compiler version, module versions.
- Real-TV video or reproducible boot logs, graphical mode and connected peripherals.
- Negative results, hangs, memory measurements and safe recovery procedure.

A tested build must clearly distinguish: **PC compilation**, **XeLL image loading**, **Linux shell**, **GPU initialization** and **desktop usability**.
