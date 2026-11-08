# X360Linux v0.3.0-alpha — Debian PowerPC USB with IceWM

**Download the ready-to-copy ZIP for your boot method. You do not need to compile Linux, extract an ISO, install Debian manually, or type a command on the console.**

- **RGH/JTAG:** `X360Linux-v0.3.0-alpha-RGH-USB.zip`
- **Existing ABadAvatar/FreeMyXe:** `X360Linux-v0.3.0-alpha-ABadAvatar-FreeMyXe-USB.zip` (preserve the exploit files you already use).

## Installation

1. Back up the USB contents and especially `X360Linux/USB-DATA.ext4` if it already exists (this file stores Linux changes).
2. Extract the contents of the chosen ZIP **straight onto the root of a FAT32 pendrive**, with at least 2 GB free. Do not create an extra outer folder.
3. The extracted USB root must contain `xenon.elf` and an `X360Linux/` folder holding the complete `X360Linux.iso`, kernel, initramfs and writable `USB-DATA.ext4`.
4. Plug the pendrive into the Xbox 360 and boot using your **already working XeLL method**. X360Boot finds the system and Debian attempts to open the IceWM desktop automatically.

Everything runs from the USB drive. This ZIP does not install to the Xbox HDD, flash NAND, or include an Xbox 360 XEX. The ISO is already in the pack; **do not extract the ISO**.

**Experimental hardware support:** The Debian PowerPC desktop packages are built and smoke-tested in QEMU, and USB/ISO/persistence packaging has been tested on the CI runner. The IceWM graphics path has **not yet been confirmed on a real Xbox 360**. If the framebuffer or Xorg fails, the system falls back to a console rather than pretending graphics are working.

`SHA256SUMS` is provided for download verification. Before removing the USB, shut Linux down cleanly. This is an alpha release for an already XeLL-bootable console.
