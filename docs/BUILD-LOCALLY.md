# Build X360Linux on the Windows PC

Linux kernel and Debian compilation can happen on the computer; GitHub Actions only needs to compile XeLL/X360Boot and package the resulting ISO and USB ZIP files.

## First-time setup

The connected Windows PC has an Intel Xeon E5-2667 v4 (8 cores, 16 threads) and approximately 16 GB RAM. Ubuntu 24.04 LTS has now been installed and booted successfully as WSL2 on the connected Windows computer (2026-11-08). The Windows firmware virtualization flag was misleading: the WSL2 Linux kernel did start. The build launcher selects `Ubuntu-24.04` and runs within this dedicated WSL environment; it does not change the PC BIOS.

Ubuntu **WSL2** is required because the Debian PowerPC build needs Linux mount namespaces, chroot, QEMU and Unix filesystem permissions. Git Bash alone is insufficient. If the PC's firmware virtualization is disabled, enable Intel VT-x in BIOS/UEFI. On a PC running inside a VM, nested virtualization may be necessary.

Install Ubuntu WSL2 once, from an administrator PowerShell (Windows command: wsl --install -d Ubuntu), restart when prompted, and complete Ubuntu's first-run account setup. The script will not change PC firmware or reboot your computer automatically.

## One-click local build

Double-click **scripts/BUILD-LOCAL.cmd**. It will:

1. Clone the GitHub source into the Ubuntu WSL2 filesystem (not the Windows NTFS drive).
2. Install Ubuntu PowerPC cross-compilers and QEMU, and set up Docker Engine with Free60's existing Xenon toolchain image.
3. Compile the Linux kernel and PowerPC recovery environment on the PC.
4. Construct the Debian Ports root filesystem from cryptographically signed packages; exclude all mounted proc/dev pseudo-filesystems.
5. Build a reproducible archive in Windows Downloads and stage it to a separate **x360linux-local-cache** GitHub prerelease using your existing Windows Git login.

The local build output includes kernel/vmlinux, xenon.dtb, xenon.elf, recovery initramfs and static BusyBox, Debian rootfs, the exact source commit SHA and a SHA256 manifest.

## Fast GitHub packaging

Open [Package precompiled Linux with XeLL and ISO](https://github.com/heltindev/X360Linux/actions/workflows/package-prebuilt.yml), click **Run workflow** and keep **publish_release = false** the first time. It downloads the already-built Linux files, compiles XeLL and X360Boot, builds the Debian ISO plus the RGH/FreeMyXe ZIPs, validates their contents and makes the downloadable packages available as workflow artifacts.

Only after testing those packages on real Xbox 360 hardware should you use **publish_release = true**, which publishes them to a separate **v0.5.0-alpha**, leaving previous tested releases unchanged.

A source SHA check prevents the Action from combining a newly changed source tree with older precompiled components. The slow full-GitHub build remains available only by manual launch; normal pushes run fast source checks instead.

**No NAND flashing, formatting the Xbox 360 internal HDD or modifying game saves.** The new Debian/XeLL ISO is still an experimental build until verified on a physical console.
