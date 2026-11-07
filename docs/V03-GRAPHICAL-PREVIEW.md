# X360Linux v0.3 — experimental graphical preview

**Status:** The Xenon Linux kernel and BusyBox shell reached the `#` prompt on a real RGH Xbox 360 with v0.2. The X360Desk graphical program, media viewers and Linux controller input in v0.3 are **not yet verified on real hardware**.

## Why not install stock Debian?

The console has a big-endian PowerPC Xenon CPU and 512 MB RAM. Debian's official `ppc64el` architecture is **little-endian** and incompatible. Debian Ports has unofficial `powerpc` (32-bit) and `ppc64` (big-endian) ports, but even their packages need hardware, CPU-instruction and RAM testing on Xenon.

This build keeps the known-booting **Linux 64-bit Xenon kernel + static 32-bit big-endian BusyBox** and adds an original C framebuffer interface. This is not Debian, not X.Org and not a full desktop distribution yet.

Sources: [Debian ports](https://www.debian.org/ports/) · [Debian PPC64](https://wiki.debian.org/PPC64) · [Linux xpad driver](https://github.com/torvalds/linux/blob/master/drivers/input/joystick/xpad.c)

## What the alpha prototype implements

- Framebuffer user interface using `/dev/fb0`, without X11 or GPU acceleration
- JPEG, PNG, BMP and PPM image viewing with memory limits
- Experimental silent `.x360v` video playback (raw RGB frames; **no MP4 or audio playback**)
- Xbox 360 wired USB controller input using Linux `xpad` + `/dev/input/event*` when devices are detected
- Left analog stick controls an on-screen cursor; A selects, B returns, D-pad selects items
- Keyboard fallback: arrow keys, Enter, Escape and Q
- Built-in photo/video test media in the initramfs so a USB media mount is not required to check the screen
- FAT32 pendrive media mounted **read-only** from `/dev/sda1`, `sdb1` or `sdc1` when recognized
- BusyBox terminal fallback if `/dev/fb0` is unavailable or the user quits X360Desk

**Not verified:** Xbox 360 framebuffer mapping, image/video speed, controller device registration, USB storage mount, audio, wireless controllers, Ethernet, native browser, persistent storage.

## First-time USB test

1. Download the **RGH/JTAG ZIP** from the v0.3 pre-release if your console uses RGH/JTAG. For ABadAvatar/FreeMyXe, use the different ZIP and keep your existing exploit files.
2. Extract it to a **FAT32** pendrive, merging directories. Do not format your HDD.
3. Boot your existing working XeLL. X360Boot should discover `X360Linux/` and start automatically after the three-second cancel window.
4. After the Linux kernel and BusyBox start, X360Desk will attempt to draw its interface.
5. If graphical output fails, it should print an error and return to the BusyBox terminal instead. Photograph any panic or red error screen.

To add photos and experimental videos, create these folders **on the same USB drive**:

```text
USB:/
  xenon.elf
  X360Linux/
    vmlinux
    xenon.dtb
    initramfs.cpio.gz
  X360MEDIA/
    PHOTOS/
      photo.jpg
      picture.png
    VIDEOS/
      clip.x360v
```

The demo photos/video are already included in the system image.

## Convert an existing video on your PC

Install **Python 3** and **FFmpeg** on your PC. From the cloned repository:

```sh
python distro/tools/convert-video.py "my-video.mp4" "clip.x360v"
```

Copy `clip.x360v` into `X360MEDIA/VIDEOS/`. The converter defaults to **320×180, 12 FPS, maximum 20 seconds, no sound**. This is a temporary experimental playback format, not native MP4 support.

## Technical notes

- Video input format: 16-byte little-endian header `X36V`, width `u16`, height `u16`, FPS `u32`, frame count `u32`, followed by raw RGB888 frames.
- Images are decoded through public-domain/MIT **stb_image**; text is drawn with public-domain **font8x8**. Attribution is in `docs/CREDITS.md`.
- Framebuffer pixel format is read through Linux `FBIOGET_VSCREENINFO` / `FBIOGET_FSCREENINFO`; unsupported pixel depths fall back to the shell.
- The image workflow builds for generic big-endian PPC32 without requiring AltiVec/VSX in userspace.
- **No Xbox NAND flashing, no internal HDD formatting, no XEX.** XEX remains a later milestone.

## Next work after hardware verification

Confirm `/dev/fb0` exists; input devices emit button/axis events; safe USB mount works; photo/video demo playback speed is usable. Then assess Debian Ports package compatibility, a real video decoder with sound and a native desktop. A successful GitHub build is **not** proof of console functionality.
