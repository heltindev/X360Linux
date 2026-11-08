#!/usr/bin/env python3
"""Assemble an experimental Xbox 360 Linux boot folder + ISO9660 image.

Requires a *separately compiled* Linux ELF32 Xenon kernel + Xenon DTB and
PowerPC32 BE initramfs. This is NOT a PC/UEFI installer or verified console OS.
"""
import argparse
import hashlib
from pathlib import Path
import shutil
import subprocess
import tempfile
import tarfile
import zipfile

README = """X360LINUX DEBIAN POWERPC USB IMAGE
---------------------------------
Extract the complete RGH or FreeMyXe ZIP to a FAT32 USB drive.
XeLL starts xenon.elf and the Xenon Linux kernel from the USB drive.
Linux mounts X360Linux.iso from the USB drive and runs the Debian
system stored in the ISO. X360Linux/USB-DATA.ext4 stores changes.
The USB boot does not require an optical drive or a network connection.
Wait for the Debian version and the prompt. A USB keyboard is optional.
Never flash NAND or format the Xbox HDD.
"""

def check_elf(path):
    with path.open("rb") as f:
        h = f.read(64)
    if (len(h) < 52 or h[:6] != b"\x7fELF\x01\x02" or h[18:20] != b"\x00\x14"):
        raise ValueError(f"Kernel is not ELF32 big-endian PowerPC: {path}")
def check_dtb(path):
    with path.open("rb") as f:
        h = f.read(8)
    if h[:4] != b"\xd0\x0d\xfe\xed":
        raise ValueError(f"Invalid FDT device tree: {path}")
def check_initramfs(path):
    with path.open("rb") as f:
        h = f.read(4)
    if h[:2] != b"\x1f\x8b":
        raise ValueError(f"Expected gzip initramfs: {path}")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kernel", required=True, type=Path)
    parser.add_argument("--dtb", required=True, type=Path)
    parser.add_argument("--initramfs", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--iso", action="store_true")
    parser.add_argument("--usb-root", type=Path,
                        help="Preinstalled ext4 Debian USB system image (no HDD installation)")
    parser.add_argument("--debian-rootfs", type=Path,
                        help="Optional signed Debian Ports powerpc base tar.gz; NOT auto-booted")
    args = parser.parse_args()
    for name in ("kernel","dtb","initramfs"):
        path = getattr(args,name)
        if not path.is_file() or path.stat().st_size < 32:
            parser.error(f"{name} input missing or empty")
    check_elf(args.kernel)
    check_dtb(args.dtb)
    check_initramfs(args.initramfs)
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="x360linux-") as tmp:
        root = Path(tmp)
        linux_dir = root / "X360Linux"
        linux_dir.mkdir()
        for src, name in ((args.kernel,"vmlinux"),(args.dtb,"xenon.dtb"),
                          (args.initramfs,"initramfs.cpio.gz")):
            shutil.copyfile(src, linux_dir / name)
        if args.usb_root:
            if not args.usb_root.is_file() or args.usb_root.stat().st_size < 50 * 1024 * 1024:
                parser.error("Preinstalled Debian ext4 USB image is missing or too small")
            with args.usb_root.open("rb") as file:
                file.seek(1080)
                if file.read(2) != b"\x53\xef":
                    parser.error("Invalid ext4 superblock: expected 0xEF53")
            shutil.copyfile(args.usb_root, linux_dir / "system.ext4")
            (linux_dir / "USB-ROOT.ID").write_text("X360LINUX-USB-ROOT-V1\n", encoding="ascii")
        # XeLL searches ISO9660 root for vmlinux and its kboot.conf menu.
        shutil.copyfile(args.kernel, root / "vmlinux")
        shutil.copyfile(args.initramfs, root / "initramfs.cpio.gz")
        (root / "kboot.conf").write_text(
            '#KBOOTCONFIG\ntimeout=20\ndefault=x360linux\n'
            'x360linux="vmlinux console=tty0 quiet loglevel=1 panic=30 maxcpus=6 '
            'coherent_pool=6M video=xenosfb rdinit=/init '
            'initrd=initramfs.cpio.gz"\n', encoding="ascii")
        (root / "README.TXT").write_text(README, encoding="ascii")
        if args.debian_rootfs:
            if not args.debian_rootfs.is_file() or args.debian_rootfs.stat().st_size > 512 * 1024 * 1024:
                parser.error("Debian Ports tarball missing or exceeds safety size limit")
            with tarfile.open(args.debian_rootfs, "r:gz") as tf:
                if not any(x.endswith("/usr/bin/bash") or x == "./usr/bin/bash"
                           for x in tf.getnames()):
                    parser.error("Debian Ports tarball missing a real bash runtime")
            debian_dir = root / "DEBIAN-PORTS"
            debian_dir.mkdir()
            shutil.copyfile(args.debian_rootfs, debian_dir / "debian-ports-powerpc-rootfs.tar.gz")
            (debian_dir / "README.TXT").write_text(
                "Real Debian Ports powerpc rootfs (experimental). NOT auto-booted.\n"
                "The console runs the tested BusyBox/X360Desk initramfs by default.\n"
                "Do not extract this tar archive on FAT32 or format the Xbox HDD.\n",
                encoding="ascii")
        zipout = out / "X360Linux-boot-files-UNVERIFIED.zip"
        with zipfile.ZipFile(zipout, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
            for path in sorted(root.rglob("*")):
                if path.is_file():
                    zf.write(path, path.relative_to(root).as_posix())
        print("Boot-files ZIP: " + str(zipout))
        if args.iso:
            if not shutil.which("xorriso"):
                parser.error("xorriso required for --iso")
            iso = out / "X360Linux-ELF-Linux-UNVERIFIED.iso"
            subprocess.run(["xorriso", "-as", "mkisofs", "-J", "-R",
                            "-V", "X360LINUX", "-o", str(iso), str(root)],
                           check=True)
            print("Experimental Linux ISO: " + str(iso))
    with (out/"SHA256SUMS").open("w",encoding="ascii") as hashes:
        for path in sorted(out.glob("X360Linux-*")):
            with path.open("rb") as fd:
                digest = hashlib.file_digest(fd, "sha256").hexdigest()
            hashes.write(f"{digest}  {path.name}\n")
    (out/"README-FIRST.txt").write_text(README, encoding="ascii")
    print("Debian Ports USB ext4 boot package built; real Xbox USB switch_root still unverified.")

if __name__=="__main__":
    main()
