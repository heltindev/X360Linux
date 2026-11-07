# Historical Xbox 360 Linux Boot Pack — 2011 archive (UNVERIFIED)

> ⚠️ **Experimental preservation archive. This is NOT X360Linux 1.0, not a newly compiled Linux release and not tested on real hardware by this project.**

The maintainer supplied a legacy folder with XeLLLaunch, XeLL, a PowerPC Linux boot image and a SquashFS live filesystem. File timestamps and signatures indicate an early-2011 era boot pack, resembling the historical Ubuntu Xenon packages.

**Release ZIP:** `X360Linux-legacy-2011-UNVERIFIED.zip` (627,770,485 bytes)

**SHA-256:** `e5dccef7dc184259e46f6f99fbd90ad8444ef3098357a05358d9390528ced7e7`

## Contents

- `default.xex` — legacy XeLLLaunch application, XEX2 format
- `xell.bin` — legacy XeLL loader (do not flash)
- `vmlinux` — ELF32 PowerPC Linux boot payload
- `casper/filesystem.squashfs` — legacy Linux filesystem (SquashFS 4.0, gzip)
- `readme.txt` — original XeLLLaunch readme
- `README-FIRST.txt` — safety and provenance notice

**Not compatible with unmodified Xbox 360 consoles.** Requires a known-good compatible RGH/JTAG or other supported XeLL installation. The included XeLL image may not work on your specific console. Do not flash NAND, overwrite your existing XeLL installation or use the obsolete OS for sensitive internet activity.

## What this is NOT

- Not compiled from the current X360Linux GitHub sources
- Not Linux 6.18 + xenos-linux-gpu
- Not evidence of a working modern desktop, GPU acceleration or Wi-Fi support
- Not a claim of universal compatibility or security updates

## More information

Read the [archive provenance, verification and SHA-256 hashes](https://github.com/heltindev/X360Linux/tree/main/legacy) and the [experimental project roadmap](https://github.com/heltindev/X360Linux/blob/main/docs/ROADMAP.md).

Original third-party rights and licenses remain in effect. The legacy binaries' exact source provenance has not been independently verified.
