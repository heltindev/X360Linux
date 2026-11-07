# XWT Boot — native Xbox 360 Linux boot manager

**Status: experimental; no successful hardware boot claimed.**

XWT Boot is **not XeLL and not Linux**. It is a native bare-metal PowerPC executable built with Free60 LibXenon. An existing supported loader must first load `xwtboot.elf32` (for example, XeLL from USB as `xenon.elf`). **After that initial handoff**, the LibXenon runtime provides its own screen, controller input and FAT filesystem operations.

## Features in source code

- Standalone ELF32 PowerPC application with its own startup/runtime via LibXenon.
- Text-mode native menu displayed on the console framebuffer.
- Controller navigation over folders on mounted FAT media; switch devices.
- Select Linux directory and save settings to `xwtboot.cfg` on the media.
- Optional persistent autoboot (OFF by default, B cancels during countdown).
- ELF32 PowerPC + device-tree checks before attempting a handoff.
- Linux bootargs and optional `initramfs.cpio.gz` (up to 32 MiB) passed to LibXenon's Linux ELF loader.

### Controller

| Input | Operation |
|---|---|
| D-pad up / down | Browse subfolders |
| A | Open highlighted folder |
| B | Parent folder; cancel autoboot countdown |
| LB / RB | Switch to next drive |
| X | Save current directory as Linux directory |
| Y | Attempt to boot the saved Linux entry |
| START | Toggle persistent autoboot; defaults off |

Settings live in `<selected-device>:/xwtboot.cfg`:

```ini
XWTBOOT1
folder=uda0:/X360Linux/
cmdline=console=tty0 panic=30 maxcpus=6 coherent_pool=6M video=xenosfb rdinit=/init
autoboot=0
```

Place **`vmlinux`** (ELF32 big-endian PowerPC), **`xenon.dtb`** (from Free60's XeLL repository; GPL-covered) and optionally **`initramfs.cpio.gz`** in the Linux folder. Settings changes are stored separately; this does not touch NAND.

## Compile

```bash
git clone --recurse-submodules https://github.com/heltindev/X360Linux.git
cd X360Linux
docker run --rm -v "$PWD:/app" -w /app free60/libxenon:latest \
  sh -c 'export DEVKITXENON=/usr/local/xenon; export PATH="$DEVKITXENON/bin:$DEVKITXENON/usr/bin:$PATH"; make -C xwtboot'
```

Output: `xwtboot/xwtboot.elf32`. The [XWT Boot Actions workflow](../.github/workflows/build-xwtboot.yml) also compiles it and uploads the ELF and an **ISO9660 launcher**.

## Boot mechanics and limitations

An ELF is an executable format, **not a hardware exploit or first-stage boot method**. Launch through XeLL or another compatible initial loader. Once loaded, the program does not call back into XeLL's UI: it uses the independent LibXenon ELF loader functions `kernel_build_cmdline`, `kernel_prepare_initrd`, and `elf_runWithDeviceTree` to attempt a direct handoff.

That **does not guarantee** the Linux image will start: kernel/device-tree compatibility, hardware initialization, executable memory layouts, storage and drivers are still under test.

Known limitations: no graphical theme yet (native framebuffer console), no kernel loader from NTFS/ext4 (FAT only), no mounted DVD Linux path in this build, no authenticated firmware, no verified audio/GPU/Linux boot. Use at your own risk on a modded console with a reliable recovery method.

## Licenses

Original XWT Boot source code is GPL-2.0-only because the linked LibXenon ELF/Linux handoff driver includes GPL-2.0-only components. Its license differs from the Apache-2.0 documentation in the repository root. No Microsoft firmware/keys are included.
