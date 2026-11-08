# X360Linux — Kernel, Casper and Debian support

## 1. What is `vmlinux`?

`vmlinux` is a Linux kernel image, **not an entire distribution**. The local historical X360Linux `vmlinux` is a 32-bit, big-endian PowerPC ELF kernel, version `2.6.36.2-xenon`, adapted to Xbox 360 hardware. It is loaded by XeLL and initializes CPU, memory and supported devices, then hands off to an early userspace (`initramfs`/`initrd`) and the Linux root filesystem. A normal PC `vmlinuz` or a downloaded ISO cannot be substituted for this Xbox-specific kernel without the right architecture and hardware support.

## 2. What is `casper`?

`casper` is the Ubuntu live-boot mechanism and the directory convention it searches for on live USB/CD media. The local `casper/filesystem.squashfs` is a **compressed, mostly read-only** Ubuntu 10.10 PowerPC root filesystem. Casper can use an initramfs and an overlay to provide a writable live session without installing the OS to a partition. The presence of Casper alone does not guarantee that the Xenon kernel and initramfs can find and boot it. A Casper path is not required for a native ext4 Debian install.

## 3. Other files and how booting works

| File/part | Purpose | X360Linux v0.4.1-dev status |
| --- | --- | --- |
| NAND XeLL / Eject | Loads a compatible Xbox 360 kernel and optional initramfs from USB. | XeLL starts on Corona Phison; full Linux GUI not proven. |
| `kboot.conf` | Optional XeLL Reloaded kernel menu/arguments, **if supported by the console's version**. | Experimental USB configuration. |
| `vmlinux` | Xbox 360 PowerPC kernel executable; talks to hardware. | Historical 2.6.36.2-Xenon, 32-bit big-endian. |
| `initrd.gz` / `initramfs` | Early tiny Linux that discovers storage and mounts the real root filesystem. | New experimental PowerPC initramfs. |
| `casper/filesystem.squashfs` | Old Ubuntu 10.10 compressed live root filesystem. | Retained only as fallback. |
| `distros/ubuntu-x360/rootfs.ext4` | Full preinstalled Ubuntu root filesystem **unpacked inside an ext4 image**, with writable Linux permissions. | Created and checked on PC, 3 GiB, hardware untested. |
| `ROOTFS.ID` | Prevents mounting an unrelated USB file by checking an expected identifier. | New initramfs matches `X360LINUX-UBUNTU-EXT4-V05`. |
| `default.xex` | Old method to start a launcher from Aurora. It is not the Linux kernel. | **Known black screen** on this Corona Phison; not part of the new Eject USB layout. |

Note: "uncompressed" means that the **Ubuntu files** are unpacked within `rootfs.ext4`. The FAT32 USB still sees a single ext4 image file because extracting Unix root directories directly onto FAT32 loses permissions, Unix symlinks and other Linux filesystem features.

## 4. Can X360Linux run Debian instead of Ubuntu?

**Potentially, yes. Debian has historically run on Xbox 360 in Free60 experiments, including a documented modern Debian Sid build.** Debian provides unofficial ports for 32-bit `powerpc` and 64-bit big-endian `ppc64`. However, a Debian root filesystem does **not** automatically become compatible with Xbox 360 hardware.

A candidate distro must satisfy ALL of the following:

1. **CPU / ABI:** executable packages for a Xenon-compatible PowerPC configuration. A conventional `amd64`/`x86_64` or ARM ISO cannot execute natively. Debian `ppc64el` (POWER8+ little-endian) is **not** a drop-in Xenon build. Check PowerPC/AltiVec build assumptions.
2. **Kernel:** an Xbox 360/Xenon-adapted kernel with working USB storage, graphics/framebuffer, filesystems and console support. The current 2011 kernel is 32-bit; choosing a 64-bit userland requires a compatible 64-bit kernel/boot chain.
3. **Early boot:** a suitable initramfs that knows where Debian is stored, mounts ext4, and hands control to Debian's `/sbin/init` or equivalent. Kernel and rootfs must agree on ABI/features, modules and paths.
4. **Root filesystem:** a bootstrapped Debian PowerPC rootfs on ext4, rather than copying a desktop ISO or merely renaming Ubuntu `rootfs.ext4`.
5. **Display/inputs:** a working Xbox Xenon framebuffer/X11 or other graphics stack, USB keyboard/controller input and a lightweight desktop (e.g. Openbox, LXPanel/PCManFM). None is hardware-verified on this Corona Phison for the current prototype.
6. **Resources and network:** fit the console's 512 MiB RAM; test driver/firmware for any wireless adapter. XeLL's pre-Linux DHCP error is separate from Linux networking.

### A future folder layout (EXAMPLE ONLY — Debian is NOT built in BOOT-DIRETO)

    BOOT-DIRETO/
      kboot.conf
      vmlinux                       # existing tested-path fallback kernel
      casper/filesystem.squashfs    # historical Ubuntu live fallback
      distros/
        ubuntu-x360/
          vmlinux
          initrd.gz
          ROOTFS.ID
          rootfs.ext4
        debian-x360/                 # NOT YET DEPLOYED
          vmlinux                   # compatible Xenon PowerPC kernel
          initrd.gz                 # adjusted to locate Debian files
          ROOTFS.ID                 # distinct Debian marker
          rootfs.ext4               # Debian PowerPC userland

### Current loader limitation

The existing `scripts/v041-ext4/init` is **Ubuntu-specific**: `REL=distros/ubuntu-x360`, `IDENTITY=X360LINUX-UBUNTU-EXT4-V05`, and it explicitly checks for `/usr/bin/gnome-session`. The local `kboot.conf` has only an Ubuntu entry and a legacy fallback. To boot Debian we must implement a separate Debian entry and make the boot initramfs accept a selected rootfs/marker and a desktop-agnostic check. **Do not rename the Ubuntu directory to Debian or copy placeholder entries into the active USB.**

For Debian the recommendation is to start with a **Free60-compatible Debian `powerpc` 32-bit root filesystem**, validate kernel/initrd/console startup, then attempt a lightweight graphical session. The Free60 community also documents newer `ppc64` kernels and Debian Sid; that is a more substantial kernel migration rather than a trivial rename.

**Important kernel compatibility warning:** the existing `vmlinux` is Linux **2.6.36.2 from 2011**. A modern Debian `powerpc` userspace can require newer Linux kernel interfaces (for example from its libc or init system) even though both are PowerPC 32-bit. Therefore the present vmlinux should **not** be assumed to boot current Debian. The Free60 2025 Debian Sid guide builds a Xenon-patched Linux **6.16.x** kernel and uses Debian **ppc64**; adopting that newer kernel/bootloader stack is a separate, hardware-risk-sensitive development effort, not part of the current v0.4.1 USB. Avoid XeLL/NAND flashing in an automatic workflow.

## 5. Real hardware status and safety

- Console: Xbox 360 Corona Phison RGH. Physical **Eject** enters the installed XeLL. Aurora `default.xex` from the 2011 archive results in a **black screen**.
- The 3-GiB Ubuntu ext4 image and custom initramfs passed PC checks, **not** an Xbox 360 desktop test.
- Green framebuffer progress works only after the Linux framebuffer becomes available; it cannot hide XeLL itself. Real whole-boot 0–100% is unfinished.
- Do not flash NAND or copy `updxell.bin` / `updflash.bin`. Do not modify the internal Xbox HDD. Keep the fallback and verbose diagnostics available.

## References

- Ubuntu Casper manual: https://manpages.ubuntu.com/manpages/jammy/man7/casper.7.html
- Free60 Linux kernel: https://free60.org/Linux/Linux_Kernel/
- Free60 Debian on Xbox 360 (Sid): https://free60.org/Linux/Distros/Debian/sid/
- Official Debian ports list (unofficial `powerpc` and `ppc64` listed): https://www.debian.org/ports/
- Existing project experiment: https://github.com/heltindev/X360Linux/blob/main/docs/V041-EXT4-BOOT-EXPERIMENTAL.md
