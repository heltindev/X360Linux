# X360Linux v0.4.1-dev - USB ext4 and graphical progress experiment

**PC preparation COMPLETE; actual Xbox 360 Corona Phison boot UNTESTED.** The 2011 Aurora default.xex is still broken on this console. Physical Eject opens the already installed XeLL.

The local BOOT-DIRETO now includes kboot.conf and the distros/ubuntu-x360 folder holding vmlinux, an external initrd.gz, a 3-GiB unpacked Ubuntu GNOME2 ext4 image and a ROOTFS.ID marker. Original v0.4 kernel and Casper SquashFS are retained for recovery.

The ext4 image was prepared with mke2fs in WSL2 and verified with e2fsck/debugfs, using features compatible with the old Linux 2.6.36 kernel. Linux is installed into the image; there is no console-side installer. The initrd contains an older PowerPC BusyBox and run-init and can mount ext4 from FAT32 via loop if kernel support works on hardware.

The 0-100% request is only PARTIALLY addressed: an early Linux framebuffer renderer shows actual stage milestones 10/30/50/75/90 if /dev/fb0 becomes available. A Plymouth theme handles estimated userspace progress. It cannot hide the initial XeLL messages; a full measured progress indicator from XeLL to GNOME requires bootloader changes and real-console testing.

Wi-Fi adapter drivers, XeLL DHCP wait, any-ISO compatibility, true faster boot and a usable final desktop are not verified or solved. The modular directory now supports one old PowerPC distro only.

Source and WSL2 build steps: https://github.com/heltindev/X360Linux/tree/main/scripts/v041-ext4

The public v0.4.0-alpha ZIP and v0.3 ZIP have NOT been replaced. This is development source, not a hardware-proven release. Do not modify Xbox NAND or internal HDD.

## Understanding Casper, vmlinux and Debian

The historical vmlinux is the Xenon-specific PowerPC kernel; casper/filesystem.squashfs is the older compressed Ubuntu Live rootfs, while the new distros/ubuntu-x360/rootfs.ext4 contains a preinstalled, unpacked ext4 Ubuntu root filesystem. Debian PowerPC is a realistic future port, NOT a working second boot entry yet. The current initramfs hardcodes the Ubuntu directory and checks for GNOME. A Debian build needs its own PowerPC-compatible rootfs, boot arguments, initramfs adaptations and verified Xenon-compatible kernel/drivers.

Read the [Casper, vmlinux and Debian compatibility guide](https://github.com/heltindev/X360Linux/blob/main/docs/BOOT-CASPER-VMLINUX-DEBIAN.md).
