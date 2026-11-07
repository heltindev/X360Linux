# Historical Xbox 360 Linux archive (2011)

> **Unverified legacy files, not X360Linux v1.0.** These files predate the current kernel/Xenos GPU work by more than a decade and **do not include original source code**.

The project maintainer provided a local directory named `LINUX 360`. Inspection on 7 November 2026 showed the following files:

| File | Bytes | Description |
|---|---:|---|
| `default.xex` | 26,624 | Xbox 360 XEX2 launcher (legacy XeLLLaunch) |
| `xell.bin` | 228,328 | Old XeLL binary |
| `vmlinux` | 11,716,364 | ELF32, big-endian PowerPC boot payload |
| `casper/filesystem.squashfs` | 615,796,736 | SquashFS 4.0 live filesystem, gzip compression, built 18 February 2011 |
| `readme.txt` | 381 | Original XeLLLaunch instructions |

Total size of these five files: **627,768,433 bytes** (approximately 598.7 MiB). SHA-256 hashes are recorded in [SHA256SUMS](SHA256SUMS).

## Release archive checksum

- File: `X360Linux-legacy-2011-UNVERIFIED.zip`
- Size: **627,770,485 bytes**
- SHA-256: `e5dccef7dc184259e46f6f99fbd90ad8444ef3098357a05358d9390528ced7e7`
- [Download the historical pre-release](https://github.com/heltindev/X360Linux/releases/tag/legacy-2011-archive)

The ZIP adds only `README-FIRST.txt` to the five original files.

## Context

The folder layout resembles historical Ubuntu Xenon live boot packs. We cannot independently establish the exact distribution release, license provenance of the launcher, original build toolchain, security updates or compatibility with each Xbox 360 revision from the binaries alone.

- [Historical Xbox 360 Linux documentation (ConsoleMods)](https://consolemods.org/wiki/Xbox_360:Linux)
- [Original Free60 source and archived images](https://sourceforge.net/projects/free60/files/)
- [XeLLLaunch documentation](https://consolemods.org/wiki/Xbox_360:XeLL)

The folder is **not** a usable base for editing Linux or GPU code: reverse engineering binary artifacts is possible but does not substitute the corresponding source trees. Active development uses the version-pinned Free60 and Xenos GPU sources in `external/`.

## Release policy

A release archive containing these files is a **historical snapshot**, not a tested build. The underlying distribution and launcher authors retain their rights and licenses. The Apache-2.0 license of X360Linux does **not** apply to these historical binaries.

- Do not assume these 2011 files work on RGH3, Corona, Trinity or any specific console.
- Do not flash `xell.bin` or any unknown image to the console's NAND.
- Do not connect an obsolete 2011 distribution to sensitive accounts or trusted networks.
- Before redistribution or modification, research the original upstream sources and required license notices.

## Hardware test status

**Not tested** by the X360Linux project. We have verified basic file signatures and hashes only. No successful boot, network, UI, controller or graphics test is claimed.
