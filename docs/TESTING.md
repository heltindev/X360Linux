# Getting started — Xbox 360

## What do I need?

- An **Xbox 360 with RGH/JTAG** that already has a **working XeLL/ELF boot method**.
- A **FAT32 USB drive**, a controller and a way to recover from a frozen console.
- An Xbox 360-compatible Xenon Linux kernel (`vmlinux`, ELF32 PowerPC) and device tree (`xenon.dtb`) to actually start Linux. **These are not in v0.1.0-alpha yet.**

## Try the X360Boot launcher (experimental)

1. Download **`xenon.elf`** from [v0.1.0-alpha](https://github.com/heltindev/X360Linux/releases/tag/v0.1.0-alpha), or extract it from **`X360Linux-development-kit.zip`**.
2. Format a spare USB drive as FAT32.
3. Copy **`xenon.elf`** directly to the **root** of the USB drive. Do **not** rename files to `updxell.bin` or `updflash.bin`.
4. Start the console using its already-working XeLL method, with this USB inserted. XeLL should load `xenon.elf` if its version and configuration support USB ELF loading.
5. If the X360Boot menu appears, record the console model and a picture or short log. This is a **launcher test, not a Linux boot test**.

## Linux directory (once a compatible kernel is available)

Place these files together on the same FAT32 drive:

```text
USB:/
├── xenon.elf
└── X360Linux/
    ├── vmlinux
    ├── xenon.dtb
    └── initramfs.cpio.gz
```

In X360Boot, use D-pad to navigate, **A** to open a folder, **B** to return, **X** to save the Linux folder, **Y** to attempt the Linux boot. **START** toggles autoboot (disabled by default).

**Important:** The alpha initramfs is only a Linux userspace shell. It cannot boot without the matching kernel/device tree. The X360Boot launcher ISO is **not** a full Linux ISO. The `Build Linux image` Action tries to create a complete image, but its kernel is not yet validated.

## Compile without configuring a toolchain

1. Open [GitHub Actions](https://github.com/heltindev/X360Linux/actions).
2. Select **Build Xbox 360**, then choose **Run workflow** on `main`.
3. Open the successful run and download **X360Linux-development-kit** under **Artifacts**.
4. Extract it to your computer. It contains the X360Boot ELF, launcher ISO and minimal initramfs; the kernel is still separate until that build is validated.

To attempt a kernel/system ISO build, run **Build Linux image** manually. If that Action fails, no complete Linux image is available. A green check in Actions **does not** prove the console has booted.

## First successful Linux boot: collect evidence

If Linux reaches a shell, record the video output and run:

```sh
uname -a
cat /proc/cpuinfo
cat /proc/meminfo
dmesg
```

Share logs with any private machine identifiers removed. Never share Xbox keys, NAND dumps or personal information. Do not overwrite internal firmware or flash NAND for this project.
