# X360Linux v0.4 — Verified Status and Multi-Distro Design

**Hardware report: Xbox 360 Corona Phison RGH; November 8, 2026.** Aurora `default.xex` produces a **black screen**. The XeLL installed on NAND opens via the physical **Eject** button. Neither successful direct-to-desktop boot nor a graphical loading bar has been verified on this hardware. These facts override older README and release descriptions.

## Verified files in local BOOT-DIRETO

- `vmlinux`: 11,716,364 bytes, ELF32 big-endian PowerPC, sha256 `b8aa8eef938275ed5f037b884592283f561ac46b283edf4cdb1200bf2d39cec8`.
- `casper/filesystem.squashfs`: 619,175,936 bytes, SquashFS v4 gzip, sha256 `676bf810043f0ae256baef3483a3cb6b2a109bc750312d214e6c5d8d4e583406`.
- The SquashFS contains a **PRELOADED Ubuntu 10.10 Maverick PowerPC32 GNOME 2 live filesystem** (108,184 inodes). It is **compressed and read-only**, **not** an unpacked persistent ext4 installation, and **not** an ISO that must be installed to boot.
- Ubiquity auto-start is disabled inside the rebuilt rootfs; GDM is configured for `ubuntu` live autologin. This is statically verified on the Windows developer PC, but not confirmed to reach the desktop on hardware.
- There is **no separate initrd or kboot.conf in the current BOOT-DIRETO**. Whether the kernel contains sufficient early-boot support or requires an external matching initramfs is not established.

## Requested features — factual status

| Goal | Present now? | What must happen |
| --- | --- | --- |
| Full 0–100% graphical progress from XeLL/XEX to desktop | **No** | Current Plymouth example is source-only; userspace progress estimate starts after kernel and framebuffer. True whole-boot status needs loader/kernel/userland event instrumentation. |
| Hide XeLL/kernel boot messages | **No** | Need Corona-compatible bootloader, validated kernel arguments and framebuffer splash; preserve a verbose diagnostics mode. |
| Linux ready without installer | **Partially** | SquashFS includes the whole OS; Ubiquity is disabled, but actual kernel → initramfs → SquashFS → GDM handoff remains untested. |
| Uncompressed installed OS on the pendrive | **No** | Needs an ext4 root partition or ext4 loop image and matching early-boot initramfs. Unpacking a Linux filesystem directly onto FAT32 breaks Unix permissions and symlinks. |
| Wi-Fi Internet without Ethernet cable | **No** | Ubuntu has NetworkManager, wpa_supplicant and wireless user tools, but a working adapter driver and firmware have not been verified. XeLL's earlier wired DHCP attempt is independent of Linux Wi-Fi. |
| Any Linux distribution | **No** | Must match Xenon CPU/PowerPC ABI, working kernel/drivers and 512 MiB RAM. x86-64/ARM ISOs cannot simply be used. |
| Faster startup | **Not measured** | A few optional services are disabled. Profile XeLL DHCP, USB, kernel, Casper and desktop separately on hardware. |
| Keep different distributions in different folders | **Design possible, untested** | Compatible XeLL Reloaded versions support kboot.conf kernel paths and initramfs. Check the actual NAND XeLL version and match each distro's boot components. |

## Planned modular USB layout (NOT DEPLOYED)

    kboot.conf                          optional when XeLL supports it
    vmlinux                            optional tested rescue boot
    distros/
      ubuntu-x360/
        vmlinux
        initrd.gz                       not yet prepared
        casper/filesystem.squashfs
      debian-ppc-x360/
        vmlinux
        initrd.gz                       not yet prepared
        system.ext4                     requires a matching initramfs/loop mount

`kboot.conf` can offer a distro menu or default timeout when supported. The old 2011 XeLL and the NAND XeLL on Corona Phison have not been proven compatible with this layout. **Do not move the live system or copy placeholder config into BOOT-DIRETO yet.**

A normal ISO file alone is not recognized as a bootable XeLL kernel. Each distro needs a compatible ELF Linux kernel plus matching initramfs, kernel arguments, root filesystem and hardware drivers.

## Execution order

1. Verify kernel loading through **Eject** with the present FAT32 USB; collect last XeLL / kernel screen, not just a black-screen symptom.
2. Confirm initramfs/Casper root detection and working Xorg framebuffer GUI. Repair the Aurora XEX handoff separately.
3. Measure boot duration. Improve offline XeLL DHCP behavior and load services only when necessary.
4. Validate persistence with ext4 (no internal Xbox disk and no NAND modification).
5. Add tested kboot.conf distro selection and modular folders with matching boot files.
6. Identify/enable Wi-Fi adapter driver and firmware in Linux, then test Wi-Fi DHCP.
7. Integrate Plymouth userspace graphical progress, maintain a verbose fallback, and investigate optional early XeLL splash.
8. Trial maintainable PowerPC userlands with light Openbox/LXPanel/PCManFM desktop.

## References

- [XeLL Reloaded kboot.conf syntax](https://github.com/Free60Project/xell-reloaded/blob/master/kboot.conf)
- [XeLL support and bootloader README](https://github.com/Free60Project/xell-reloaded/blob/master/README.md)
- [Corona history in XeLL changelog](https://github.com/Free60Project/xell-reloaded/blob/master/CHANGELOG)
- [Current Corona Phison blocker](https://github.com/heltindev/X360Linux/issues/3)
- [DHCP issue](https://github.com/heltindev/X360Linux/issues/1)
- [Plymouth progress issue](https://github.com/heltindev/X360Linux/issues/2)

Public v0.3 and v0.4 **binaries were not changed** as part of this audit.

## New local v0.4.1-dev prototype

The two-file live USB snapshot above describes v0.4. The new LOCAL v0.4.1-dev boot folder additionally has kboot.conf and distros/ubuntu-x360 with a full 3-GiB preinstalled ext4 Ubuntu image, new PowerPC initramfs and Linux milestone renderer. This is NOT part of the existing v0.4 public ZIP and NOT confirmed bootable on real Corona hardware. [New notes](V041-EXT4-BOOT-EXPERIMENTAL.md).

## Understanding Casper, vmlinux and Debian

The historical vmlinux is the Xenon-specific PowerPC kernel; casper/filesystem.squashfs is the older compressed Ubuntu Live rootfs, while the new distros/ubuntu-x360/rootfs.ext4 contains a preinstalled, unpacked ext4 Ubuntu root filesystem. Debian PowerPC is a realistic future port, NOT a working second boot entry yet. The current initramfs hardcodes the Ubuntu directory and checks for GNOME. A Debian build needs its own PowerPC-compatible rootfs, boot arguments, initramfs adaptations and verified Xenon-compatible kernel/drivers.

Read the [Casper, vmlinux and Debian compatibility guide](https://github.com/heltindev/X360Linux/blob/main/docs/BOOT-CASPER-VMLINUX-DEBIAN.md).
