# X360Boot

**X360Boot is the native Xbox 360 launcher for X360Linux.** It is a separate PowerPC ELF application, not the Linux operating system and not XeLL.

It displays its own console menu, browses folders on FAT devices, saves `x360boot.cfg`, and can attempt to load a Linux kernel directly using LibXenon. No NAND modification is needed.

## Controller

| Button | Action |
|---|---|
| D-pad up/down | Choose folder |
| A / B | Enter folder / go back |
| LB / RB | Switch drive |
| X | Choose Linux folder and save it |
| Y | Attempt Linux boot |
| START | Toggle saved autoboot (off by default) |

## Linux files

```text
X360Linux/
├── vmlinux              # Compatible Xenon Linux ELF32 kernel (not yet shipped)
├── xenon.dtb            # Xbox 360 device tree
└── initramfs.cpio.gz    # Minimal Linux userspace
```

Settings are stored in `x360boot.cfg` on the chosen FAT device:

```ini
X360BOOT1
folder=uda0:/X360Linux/
cmdline=console=tty0 panic=30 maxcpus=6 coherent_pool=6M video=xenosfb rdinit=/init
autoboot=0
```

## Compiling

Use **Build Xbox 360** in GitHub Actions, or build locally with the Free60 LibXenon toolchain:

```sh
make -C launcher
```

Output: `launcher/x360boot.elf32`. For a compatible XeLL USB launch, make a **copy** named `xenon.elf` on a FAT32 drive. A compatible already-running first-stage ELF loader is still required; an ELF file does not boot the Xbox 360 directly from power-off.

**Current status:** ELF cross-build works. Launcher operation, folder selection and Linux handoff still need testing on a real console. Linux cannot start without a compiled, compatible Xenon kernel and device tree. Never flash an experimental ELF.

Source license: GPL-2.0-only, see [Credits & licenses](../docs/CREDITS.md).
