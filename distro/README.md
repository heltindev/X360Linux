# X360Linux distribution

I'm building a Linux distribution for the **original Xbox 360 hardware**.

The current distribution is deliberately small: a **PowerPC64 big-endian BusyBox shell** in an `initramfs.cpio.gz` archive. It is the first part of a future full desktop OS.

## Current build

**[GitHub Actions → Build Xbox 360](https://github.com/heltindev/X360Linux/actions/workflows/build.yml)** compiles the userspace automatically and includes it in the developer ZIP.

To compile the Linux shell on Ubuntu:

```sh
sudo apt install gcc-powerpc64-linux-gnu libc6-dev-ppc64-cross \
  binutils-powerpc64-linux-gnu make bzip2 curl python3
bash distro/build-rootfs.sh
```

The output is `distro/out/initramfs.cpio.gz`.

## Booting on Xbox 360

The minimal Linux shell alone **cannot boot** the console. You also need a compatible Xbox 360 Linux ELF32 PowerPC kernel (`vmlinux`) and matching `xenon.dtb`. Both are being integrated using the manual **Build Linux image** GitHub Action.

When those files are available, put them in the same `X360Linux/` folder on a FAT32 drive. Choose the folder in X360Boot and try the boot. See [Getting started](../docs/TESTING.md).

The `Build Linux image` workflow also tries to create a USB ZIP and ISO9660 image. It is experimental and will **not** upload a full-system image unless the kernel and userspace builds succeed.

The goal is an entirely native Linux installation: CPU, memory, storage, networking, graphics, sound and a desktop running on the Xbox 360 itself, not streamed from another device.

Third-party source licenses (especially BusyBox GPL-2.0 and the Linux kernel GPL-2.0) are documented in [Credits & licenses](../docs/CREDITS.md).
