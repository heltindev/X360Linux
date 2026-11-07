# Debian Ports base for Xbox 360 — experimental

Free60 documents [Debian Sid on Xbox 360](https://free60.org/Linux/Distros/Debian/sid/). We bootstrap the real signed **Debian Ports 32-bit big-endian `powerpc`** packages with debootstrap, and verify Debian Bash under generic PowerPC QEMU without AltiVec.

The output `debian-ports-powerpc-rootfs.tar.gz` preserves Unix file permissions and symbolic links. **It is not the active live boot root:** X360Linux keeps its already-booted Xenon kernel + static BusyBox + X360Desk. The Debian base requires a later, carefully tested external ext4 root mount and CPU/RAM validation.

**Never extract the tarball onto FAT32 or format the Xbox 360 HDD.** The signed package repository is https://deb.debian.org/debian-ports/. The CI build refuses any incomplete second stage or unsigned archive.

Run on Ubuntu Linux with binfmt/QEMU: `sudo bash distro/debian/build-debian-rootfs.sh` after installing debootstrap, qemu-user-static, qemu-user, binfmt-support, and debian-ports-archive-keyring.