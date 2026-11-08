# X360Linux local development - XEX first (November 2026)

## Main experimental boot

The maintainer confirmed that the historical default.xex launches the XeLL/Linux startup path through Aurora on an RGH Xbox 360. Full USB desktop boot and persistent storage are NOT yet proven.

For v0.3, download X360Linux-v0.3.0-alpha-Legacy-XEX-USB.zip from:
https://github.com/heltindev/X360Linux/releases/tag/v0.3.0-alpha

Extract the ZIP to the root of a FAT32 USB drive, connect it to the Xbox 360 and launch default.xex through Aurora. Read docs/V03-LEGACY-XEX.md for the complete safety guidance.

The old x360linux-local-cache release and tag have been removed. Its uploader and GitHub Actions ISO packaging path are disabled. They are NOT required to boot the console via XEX.

## v0.4 local development

Develop on the Windows PC in Desktop/PEN DRIVE/BOOT-DIRETO/v0.4-dev/ using Ubuntu WSL2 where appropriate. The historical binary baseline is preserved in legacy-v0.3-base. The experimental-no-installer directory has a modified 2011 Ubuntu 10.10 filesystem with installer autostart disabled; XEX, XeLL and kernel are unchanged.

The v0.4 experiment is NOT hardware tested as a complete desktop. Goal: Aurora XEX -> XeLL -> Xenon Linux kernel -> root filesystem on USB -> automatic graphical desktop, without an installer or console commands.

Later steps: maintainable Debian Ports PowerPC32 (only if Xenon kernel-compatible), USB persistence, Openbox desktop, USB mouse and keyboard, gamepad pointer, wired network, sound and video.

The old BUILD-LOCAL.cmd is legacy research. It may compile old ELF/ISO inputs locally, but it no longer uploads cache archives or dispatches GitHub Actions.

Never flash NAND or overwrite Xbox HDD partitions. Ubuntu 10.10 is obsolete and unsuitable for sensitive accounts.
