# X360Linux distribution

This is a native experimental Linux userspace for the original Xbox 360 Xenon console. The kernel has already reached a BusyBox shell prompt on real RGH hardware.

## v0.3 graphical preview

- **Architecture:** 64-bit Xenon Linux kernel + conservative static PowerPC32 big-endian BusyBox.
- **Original desktop program:** `distro/desktop/x360desk.c`, a small framebuffer media interface.
- **Photos:** JPG, PNG, BMP and PPM.
- **Videos:** silent raw RGB `.x360v` clips converted on a computer. MP4, audio and browser are future work.
- **Input:** experimental Linux `xpad` / evdev for an Xbox 360 USB controller, with analog stick cursor and A/B navigation.
- **Storage:** attempt to mount a recognized USB FAT32 partition read-only; no HDD writes.
- **Fallback:** if the framebuffer is unsupported, return to the BusyBox terminal.

**This graphical preview is not yet confirmed on physical Xbox 360 hardware.** It is not Debian and does not include a full desktop environment.

See [v0.3 beginner and technical guide](../docs/V03-GRAPHICAL-PREVIEW.md).

## Building the userspace

On Ubuntu with the cross compiler and PowerPC QEMU installed:

```sh
sudo apt update
sudo apt install -y gcc-powerpc-linux-gnu libc6-dev-powerpc-cross \
  binutils-powerpc-linux-gnu qemu-user make bzip2 curl python3
bash distro/build-rootfs.sh
```

This compiles BusyBox and X360Desk, generates original demo media, runs a QEMU PowerPC CPU smoke test, and packages `distro/out/initramfs.cpio.gz`.

The separate [Build Linux image workflow](../.github/workflows/linux-image.yml) compiles the Xenon kernel and assembles an experimental ISO and USB boot folder. The ISO is not a PC installer.

## Debian Ports integration

Debian's official `ppc64el` is **little-endian** and not the Xbox Xenon format. Debian Ports maintains unofficial `powerpc` and `ppc64` big-endian architectures. Their compatibility, performance, packages and runtime memory footprint still need validation. We are not substituting an untested Debian root filesystem for our working BusyBox yet.

Sources, exact library licenses and attribution: [Credits & licenses](../docs/CREDITS.md).

**Never flash NAND or format the Xbox internal disk with these alpha images.**
