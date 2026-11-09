# X360Linux v0.4.1-dev - repair status (Corona Phison)

Experimental local USB boot code revision. Preparation and integrity checks passed on the PC. A complete graphical boot has NOT been validated on the real Xbox 360.

## Changes to local BOOT-DIRETO

- Rebuilt and validated the PowerPC32 initrd.gz as a gzip/newc archive containing 35 entries, including Ubuntu-era BusyBox, klibc run-init and a no-libc framebuffer progress helper.
- Updated early Linux init to use the selected distro folder (x360distro parameter) and expected ROOTFS.ID marker (x360id parameter). Strict folder name validation and USB-only storage discovery protect against mounting an unexpected internal device.
- Added /proc/uptime readings to boot milestone logs for later speed benchmarking; no actual Xbox boot-time measurement has been made.
- Updated kboot.conf with explicit Ubuntu folder and marker arguments, plus normal, verbose debugging and historical v0.4 fallback entries.
- Corrected Plymouth green splash callback argument order: show_progress(progress, time), as documented by Ubuntu 10.10. Rebuilt the local preinstalled 3-GiB ext4 Ubuntu image with this fix; checked using e2fsck. The original ext4 image remains backed up in the authorized PC WSL environment.
- Improved local initramfs build script: portable root detection, temporary output plus atomic replace after gzip integrity and shell syntax checks.
- Retained the Ubuntu 10.10 Casper/SquashFS and historical Xenon vmlinux fallback. No unverified XEX, XeLL flash image or other NAND update file was added.

## Eight feature goals: verified status

1. Full XeLL/XEX-to-desktop 0-100% progress: NOT achieved. The Linux framebuffer renders milestones only when /dev/fb0 works; Plymouth progress is userspace-only and estimated.
2. Preinstalled Linux without installer: 3-GiB ext4 Ubuntu GNOME2 rootfs created on PC; actual on-console GUI and persistence still NOT verified.
3. DHCP and internet over Wi-Fi: NOT achieved; real supported adapter/driver/firmware required. XeLL DHCP happens before Linux. Upstream Free60 offers a compile-time NO_NETWORKING option in source/lv2/config.h, not an Ubuntu Wi-Fi configuration.
4. Any Linux distro: NOT possible generically. The initrd now supports a selected folder and root marker for compatible Xenon PowerPC distros, but Debian is NOT currently built.
5. Faster boot: NOT measured. Boot-time stage logging added; no timing claim.
6. Hide early XeLL/kernel logs: NOT achieved. Splash begins only after Linux framebuffer/Plymouth. Debug entry keeps diagnostics visible.
7. Separate distro folders: structure available in distros/ubuntu-x360. Other distro rootfs/driver/kernel compatibility still pending.
8. Launch via default.xex/Aurora: NOT achieved. The known 2011 XellLaunch still gives a black screen on Corona Phison RGH. A new compatible XEX handoff cannot be verified merely by copying a renamed XeLL binary.

The XeLL already installed on the console opens by physical Eject. For hardware testing, use that route with a clean FAT32 USB and select the verbose/debug entry first. Keep original boot backups. Do not flash NAND or write to the internal Xbox HDD.

Public v0.4.0-alpha release ZIP is unchanged. This document reports development code, not a new verified working release.

Upstream references:
- https://github.com/Free60Project/xell-reloaded/blob/master/kboot.conf
- https://github.com/Free60Project/xell-reloaded/blob/master/source/lv2/config.h
- https://github.com/Free60Project/xell-reloaded/blob/master/CHANGELOG
- https://github.com/heltindev/X360Linux/issues/3
