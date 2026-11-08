# X360Linux v0.4.1-dev - local experimental Xenon PowerPC32 boot

This local USB boot prototype was BUILT AND VERIFIED ON THE PC. It is NOT a confirmed working graphical desktop on Xbox 360 Corona Phison RGH. The console opens XeLL by the physical Eject button; the 2011 Aurora default.xex still produces a black screen.

## BOOT-DIRETO layout

    kboot.conf
    vmlinux
    casper/filesystem.squashfs
    distros/ubuntu-x360/
        vmlinux
        initrd.gz
        ROOTFS.ID
        rootfs.ext4

The 3-GiB rootfs.ext4 contains the complete unpacked, preinstalled Ubuntu 10.10 GNOME2 PowerPC32 system. The FAT32 USB file itself has a true ext4 filesystem with Unix permissions and writable home. No Linux installer or Internet download is needed to attempt it.

The external PowerPC32 initramfs uses the Ubuntu-era static BusyBox, klibc run-init, USB-only device scanning, a matching ROOTFS.ID marker, ext4 loop mount, and emergency shell on failure. It does NOT write to internal Xbox HDD or NAND.

The default XeLL entry starts Linux with quiet/splash. A diagnostic entry keeps messages visible, and a legacy v0.4 kernel/SquashFS fallback is available. XeLL kboot.conf support and external-initrd boot on the actual Corona are not yet validated.

A statically cross-compiled PowerPC32 program draws a dark green framebuffer progress bar AFTER the Linux kernel exposes /dev/fb0, at milestones 10, 30, 50, 75 and 90. GNOME starts the Plymouth userspace theme, and a session-ready marker records the desktop starting. A true XeLL/XEX-to-GUI 0-100% bar is NOT implemented.

## Local build steps, no GitHub Actions

Using WSL2 Ubuntu with squashfs-tools, e2fsprogs, qemu-ppc-static and powerpc-linux-gnu-gcc, provide the WSL path to the parent of BOOT-DIRETO and work:

    bash extract-rootfs.sh /path/to/PEN_DRIVE
    bash prepare-rootfs.sh /path/to/PEN_DRIVE
    bash build-ext4-fast.sh /path/to/PEN_DRIVE
    bash build-fbprogress.sh
    python3 make-initramfs.py /path/to/PEN_DRIVE

Rootfs preparation requires a fresh extraction. The ext4 builder verifies filesystem health and its final SHA-256 and refuses overwrites.

## Still not working or unproven

- Aurora default.xex is known to black-screen on the Corona Phison.
- No real Xbox graphical boot, persistence or speed measurement yet.
- Wi-Fi drivers and XeLL offline DHCP optimization are unfinished.
- Arbitrary Linux ISOs are not supported: distributions need Xenon-compatible PowerPC kernels, initrds and driver userspace.
- Legacy Ubuntu 10.10 is unsupported and unsuitable for sensitive logins.

No new v0.4.1 binary release was published. Preserve old v0.3/v0.4 assets. No NAND flashing.
