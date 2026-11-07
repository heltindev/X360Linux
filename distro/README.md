# X360Linux minimal PowerPC64 Linux userspace

**Experimental root filesystem, not a finished or independently bootable OS image.**

This project contains an original `/init` script, an initramfs packer and an optional build workflow producing **static BusyBox for PowerPC64 big-endian**. The root filesystem is **a real Linux shell**, not an Android or Windows executable and not a graphical desktop.

To reproduce the build on Ubuntu:

```bash
sudo apt install gcc-powerpc64-linux-gnu libc6-dev-ppc64-cross \
  binutils-powerpc64-linux-gnu make bzip2 curl python3
bash distro/build-rootfs.sh
```

Output: `distro/out/initramfs.cpio.gz` (compressed `newc` cpio archive).

## Launch via XWT Boot

Place these files in a FAT32 folder (for example, `X360Linux/` on USB):

```text
X360Linux/
├── vmlinux                 # Your compatible Xenon Linux ELF32 kernel
├── xenon.dtb               # Free60 XeLL source device tree
└── initramfs.cpio.gz       # Our static BusyBox PowerPC64 root filesystem
```

Choose that folder in XWT Boot. `xwtboot.cfg` stores the location and Linux kernel parameters. An independently built/tested Free60 kernel is **required**. The ISO9660 image in the XWT Actions workflow contains only the launcher, **not the kernel or Linux OS**.

## Why not just an ISO?

The original XeLL project supports booting ELF files from FAT USB, TFTP and ISO9660 CD/DVD. A conventional PC ISO with GRUB cannot boot an Xbox 360. A matching ELF kernel + device tree + initramfs is the actual Linux boot set. We can bundle that into an ISO only **after** the kernel and loader are verified.

## Optional full-system Linux ISO from GitHub Actions

The [manual "Build EXPERIMENTAL Xenon Linux system image" workflow](../.github/workflows/build-linux-system.yml) has separate kernel and userspace builds. If **both** cross-build successfully and the Xenon kernel has a valid ELF32 PowerPC header, the workflow packages an experimental Linux boot folder and ISO9660 CD image.

This pipeline is **manually triggered** because downloading, patching and compiling the kernel takes substantial runner resources. Its output is an **untested boot candidate**, not a ready-to-install desktop distro. The builder deliberately rejects unexpected kernel formats rather than silently shipping a broken ISO.

From a Linux host with the verified kernel, DTB and initramfs already present:

```bash
python3 distro/make_system_image.py \
  --kernel /path/to/bootable-vmlinux \
  --dtb external/xell-reloaded/source/lv2/linux/xenon.dtb \
  --initramfs distro/out/initramfs.cpio.gz \
  --output-dir distro/out/system --iso
```

## Licensing

- Original packaging code and shell scripts follow the root Apache-2.0 license.
- **BusyBox is GPL-2.0** and downloaded from its official project. Binary distribution must retain source/build information and GPL notices. A generated initramfs is **not** Apache-2.0 only.
- Linux kernel and XeLL files retain their own upstream licenses. Never distribute the original 2011 blobs as part of the modern build.
