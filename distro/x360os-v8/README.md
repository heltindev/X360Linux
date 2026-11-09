# X360OS Native v8.0 — Xbox 360 Linux distribution, NO Ubuntu

**This is a genuinely separate PowerPC Linux distribution, not an Ubuntu theme, custom GDM session, or remastered Ubuntu ISO.**

## The actual boot chain

```text
Xbox 360 (RGH/JTAG) — Eject
    XeLL-Reloaded (existing console bootloader)
      └── uda:/vmlinux (preserved 2.6.36.2 Xenon Free60 PPC kernel)
          + uda:/initrd-x360os.gz (NEW X360OS original gzip/newc CPIO)
            └── /init (X360OS PID 1, no Casper)
                ├── BusyBox 1.36.1 (static PPC big-endian)
                ├── musl 1.2.5 (statically linked)
                ├── Free60 Xenon input drivers
                └── /usr/bin/x360os-ui (native C, Xenos tiled framebuffer)
```

XeLL supports external initrd through `initrd=uda:/...` in `kboot.conf`. The original verified kernel config contains `CONFIG_BLK_DEV_INITRD=y` and `CONFIG_RD_GZIP=y`, so the kernel can unpack this gzip/newc archive. `rdinit=/init` starts **our** PID 1 directly. No Ubuntu `filesystem.squashfs`, live Caspar scripts, installer or Ubuntu root filesystem.

### What is not in this distribution

**Zero Ubuntu userland files.** There is NO GNOME, GDM, Xorg, Openbox, Ubuntu, APT, dpkg, GTK, Python, systemd, Firefox, `casper-rw` or `boot=casper` in this image. The only carry-over from the old Ubuntu image consists of TWO original **Free60 Xenon kernel object modules** `joydev.ko` and `evdev.ko` for the preserved kernel; these are kernel drivers, not Ubuntu packages or userspace. The original `vmlinux` file is unchanged and GPL-licensed Linux; writing a Linux distribution does not mean rewriting the Linux kernel.

WSL Ubuntu is used on the Windows developer PC **only as a cross-compilation workstation**; the Xbox runs an entirely separate PowerPC userspace built from source.

## Screen corruption and fix

The user's real Xbox 360 showed severe checkerboard/tile corruption in the previous v7 native build. Free60 documentation states the Xenos framebuffer is **not linearly laid out**: it contains 32x32-pixel tiles, with pixel groups scattered inside each tile. Our v7 app incorrectly treated `/dev/fb0` as a linear pixel array.

v8 implements the original open-source **Free60 XeLL `xenos_pset32` tile address mapping** and native 32-bpp B:G:R:00 pixel format. Direct framebuffer rendering is independent of any Ubuntu/Xorg libraries.

- Source reference: https://github.com/Free60Project/xell/blob/master/xenos.c
- Architecture reference: https://free60.org/Hardware/Console/Xenos_%28GPU%29/
- Our `generate-tiled-ui.py` constructs the standalone C native renderer; `build-ui.sh` compiles it with musl.
- Tests render the same dashboard at 800x480 and 1280x720 in **linear** and **Xenos tile** memory, then convert tiled output back to pixel coordinates; both outputs match byte-for-byte under QEMU PPC32. **The physical Xbox display is not yet validated for v8.**

## Why no more Ubuntu recovery

Earlier `v7.1` and `v7.2` delivered GTK2 menus *on top of Ubuntu 10.10*, which did not meet the user's repeated request for a distro from zero. The v8 build **does not include any old Ubuntu rootfs**. Its only userland is built for X360OS. Prior recovery images remain unchanged, in separate directories, to preserve a known-picture reference in case this experimental new boot fails.

## Current hardware functionality

| Component | Native v8 status |
| --- | --- |
| CPU and kernel | Original XeLL-booting Free60 Xenon PowerPC kernel reused |
| Root/init | NEW, original X360OS initramfs with `/init`, no Casper |
| Display | Xenos 32x32-tiled C renderer, host simulation passed, console test pending |
| UI | X360OS dashboard: photos, videos in limited silent X36V format, system screen |
| Input | USB xpad built into kernel, joydev/evdev modules included; USB controller hardware test pending |
| Xbox wireless controller | NOT supported unless kernel enumerates receiver (internal RF may require new driver) |
| Network | Intentionally DISABLED in initial boot; XeLL DHCP is separate |
| Wi-Fi | Not implemented in preserved kernel |
| Audio | Xenon ALSA compiled in kernel; no standalone audio app yet |
| Persistent storage | No; read-only/nonpersistent root initramfs, memory files disappear on reboot |
| Browser and games | Not yet ported for native system |

## Local build, NO GitHub Actions

The developer PC needs WSL Ubuntu with `powerpc-linux-gnu-gcc`, `qemu-ppc-static`, `unsquashfs`, `python3`, and the already-built PPC musl + BusyBox cross-toolchain from `distro/x360os-native`.

```bash
python3 distro/x360os-v8/generate-tiled-ui.py
bash distro/x360os-v8/build-ui.sh
bash distro/x360os-v8/build.sh <verified-v5-vmlinux> <verified-v5-kernel-module-source-squashfs> <new-output-dir>
python3 distro/x360os-v8/verify-initramfs.py <new-output-dir>
```

The **kernel module source squashfs** is read only to extract two matching Linux .ko drivers: nothing else is copied. New output directory must not already exist.

The output is `vmlinux`, `initrd-x360os.gz`, `kboot.conf`, SHA checksums and instructions. Copy it to the ROOT of a **SEPARATE FAT32 TEST USB**, then launch XeLL with Eject. Do not include any previous `casper` or `casper-rw`. No manual terminal commands or installation expected if XeLL can load the external initrd.

### Independent tests

`verify-initramfs.py` decompresses and parses the generated CPIO from its header bytes, checks that `/init` exists and is executable, that `/bin/sh` points at static BusyBox, that device nodes and Free60 drivers are correct, that no Ubuntu artifacts exist, and then executes PPC32 BusyBox and the Xenos tile renderer under `qemu-ppc-static`.

**Not tested**: actual XeLL external initramfs load, early kernel -> `/init` handoff, real Xenos framebuffer pitch/address and physical controller support. Do not describe this as a stable console-tested release. Preserve existing working images and never flash NAND or touch the Xbox internal HDD.

## Licensing and origins

- Linux Xenon kernel: Linux GPL-2.0 + Free60 patches.
- Freely licensed static musl and BusyBox and their upstream conditions.
- Free60 XeLL xenos tiling formula (GPL-2.0 source reference in generated C).
- Existing in-repo X360OS C renderer (GPL-2.0); stb_image and bitmap font retain their original notices.

The build uses NO downloaded commercial Xbox SDK or proprietary Microsoft binaries.
