# X360Linux v0.4.0-alpha - preloaded XEX live USB

WARNING: This build was generated and statically verified on a Windows PC using Ubuntu WSL2. It has NOT been tested as a working graphical desktop on a real Xbox 360. It is a trial, not a confirmed fix.

Download: https://github.com/heltindev/X360Linux/releases/tag/v0.4.0-alpha

## Boot method

For RGH/JTAG: Extract the ZIP contents directly to a FAT32 USB root, then launch default.xex in Aurora. No Rufus, Linux download, installer or console shell commands should be necessary for this attempt.

For ABadAvatar: Keep the original ABadAvatar exploit files on USB 1 unchanged. Extract the EXACT SAME v0.4 ZIP to a DIFFERENT FAT32 pendrive (USB 2). When your exploit environment provides an XEX-capable launcher, run default.xex from USB 2. This ABadAvatar path is not independently verified.

The XEX, XeLL image and original PowerPC32 Xenon kernel are unchanged from the v0.3 baseline (verified using SHA-256). The old Ubuntu 10.10 Xenon OS is already packaged inside casper/filesystem.squashfs. This is a READ-ONLY live root; persistent installation and saved user changes are not implemented.

## Changes from v0.3

1. Extracted the full Ubuntu live SquashFS into WSL2 (no network downloads).
2. Disabled the Ubiquity installer automatic Upstart start event.
3. Added /etc/gdm/custom.conf requesting autologin as the casper-created ubuntu live user to the included GNOME 2 desktop.
4. Disabled a few optional XDG autostart tasks: update notification, Bluetooth applet, print applet and GNOME screensaver.
5. Disabled optional SysV startup symlinks for services irrelevant to Xbox hardware: Bluetooth, time sync, scanning, speech dispatcher, rsync, kerneloops, PowerBook daemon and binfmt.
6. Preserved original xenosfb X.Org framebuffer driver, Xorg config, network services, dbus, fancontrol and sound components.
7. Repacked a compatible gzip SquashFS v4 with 131072-byte blocks; checked the resulting installer and GDM settings by extracting the new image again.

## Validation status

| Component | Result |
| --- | --- |
| Original XEX, XeLL and Xenon kernel unchanged | Verified on PC |
| Preloaded Ubuntu GNOME 2 and xenosfb inside SquashFS | Verified on PC |
| Ubiquity auto-start disabled | Verified on PC |
| GDM ubuntu autologin configured | Verified on PC |
| USB ZIP CRC and SHA-256 checked | Verified on PC |
| Real Xbox GUI appears, no installer | Not tested |
| Actual boot performance improvement | Not measured |
| Settings stored persistently on USB | Not implemented |
| ABadAvatar two-pendrive method | Not tested |

The package is NOT a new Debian distribution or proof of a persistent install. See scripts/build-v04-xex-live.sh for the build source, and docs/ROADMAP.md for future milestones.

Never flash the NAND, rename xell.bin as a flash payload, or install to the Xbox internal HDD. Ubuntu 10.10 (2011) is obsolete and unsuitable for sensitive browsing. Source provenance and third-party license obligations are not fully audited.

If a black screen remains, capture the console boot output to determine if the issue is kernel, Casper, GDM, Xorg or xenosfb. Do not claim success until physical hardware confirms a desktop.

## Planned (not yet included in alpha ZIP): offline DHCP and green boot bar

The maintainer reported a XeLL DHCP error without Ethernet and requested a graphical progress bar from 0 to 100%. The root cause of the early DHCP text appears inside XeLL, before Ubuntu. Plymouth can show estimated progress only once the Linux framebuffer and userspace are active.

See [ongoing engineering investigation](V04-DHCP-SPLASH.md). A source-only splash prototype exists in distro/plymouth/x360linux; no ZIP changes have been published.
