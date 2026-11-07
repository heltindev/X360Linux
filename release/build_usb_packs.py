#!/usr/bin/env python3
"""Build beginner USB ZIPs for X360Linux, with the actual ISO included.

Only the normal XeLL/X360Boot files boot from USB. The enclosed ISO is
an optional optical image, NOT read by the launcher or an installer.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import tarfile
import zipfile

LINUX = ("X360Linux/vmlinux", "X360Linux/xenon.dtb",
         "X360Linux/initramfs.cpio.gz")
REQUIRED = ("xenon.elf", *LINUX)
MAX_ISO = 1024 * 1024 * 1024  # FAT32-safe, conservative check

def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()

def read_and_check(path: Path, what: str) -> bytes:
    if not path.is_file():
        raise FileNotFoundError(f"{what} not found: {path}")
    data = path.read_bytes()
    if len(data) < 32:
        raise ValueError(f"Empty {what}: {path}")
    return data

def is_ppc32(data: bytes) -> bool:
    return (len(data) >= 52 and data[:6] == b"\x7fELF\x01\x02" and
            data[18:20] == b"\x00\x14")

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ("base-rgh", "base-freemyxe", "launcher", "kernel",
                 "dtb", "initramfs", "iso", "output-dir"):
        parser.add_argument("--" + flag, required=True, type=Path)
    parser.add_argument("--debian-rootfs", type=Path,
                        help="Optional real, completed and verified Debian Ports rootfs tar.gz")
    parser.add_argument("--tag", default="v0.3.0-alpha")
    args = parser.parse_args()
    iso = read_and_check(args.iso, "ISO image")
    if not 32774 < len(iso) <= MAX_ISO or iso[32769:32774] != b"CD001":
        parser.error("Expected a validated ISO9660 image (not a generic file)")
    launcher = read_and_check(args.launcher, "launcher")
    kernel = read_and_check(args.kernel, "Xenon kernel")
    dtb = read_and_check(args.dtb, "device tree")
    initrd = read_and_check(args.initramfs, "initramfs")
    if not is_ppc32(launcher) or not is_ppc32(kernel):
        parser.error("Launcher and kernel must be PowerPC32 big-endian ELF images")
    if dtb[:4] != b"\xd0\x0d\xfe\xed" or initrd[:2] != b"\x1f\x8b":
        parser.error("Invalid DTB or gzip initramfs")
    debian = None
    if args.debian_rootfs:
        debian = read_and_check(args.debian_rootfs, "Debian Ports base")
        with tarfile.open(args.debian_rootfs, "r:gz") as tf:
            names = tf.getnames()
            if not any(n.endswith("/usr/bin/bash") or n == "./usr/bin/bash" for n in names):
                parser.error("Debian base lacks actual /usr/bin/bash")
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    iso_name = f"X360Linux-{args.tag}-XeLL-UNTESTED.iso"
    # ISO duplication inside the ZIP is intentional and explicitly requested.
    (output / iso_name).write_bytes(iso)
    changes = {"xenon.elf": launcher,
               "X360Linux/vmlinux": kernel,
               "X360Linux/xenon.dtb": dtb,
               "X360Linux/initramfs.cpio.gz": initrd}
    for flavor, original in (("RGH-USB", args.base_rgh),
                             ("ABadAvatar-FreeMyXe-USB", args.base_freemyxe)):
        pack = output / f"X360Linux-{args.tag}-{flavor}.zip"
        with zipfile.ZipFile(original) as z:
            if z.testzip() is not None:
                parser.error(f"Source ZIP is corrupt: {original}")
            entries = {x.filename: (x, z.read(x.filename))
                       for x in z.infolist() if not x.is_dir()}
        if not set(REQUIRED).issubset(entries):
            parser.error(f"Source ZIP missing XeLL/boot files: {original}")
        old_xell = entries.get("BadUpdatePayload/xell-2f.bin", (None, None))[1]
        message = (
            f"X360Linux {args.tag} - corrected TV interface + ISO pack\n"
            "============================================================\n"
            "1. Keep your original Xbox 360 RGH/JTAG and the WORKING XeLL.\n"
            "2. Extract this ZIP to the ROOT of the FAT32 USB drive.\n"
            "3. Start XeLL. X360Boot opens Linux automatically after 3 seconds.\n"
            "   Press B during the countdown to cancel.\n"
            "4. If Linux graphics work, the X360Desk interface should appear.\n"
            "   USB controller: left stick = pointer, D-pad = selection, A = open, B = back.\n"
            "5. USB photo files go in X360MEDIA/PHOTOS; silent X36V videos\n"
            "   go in X360MEDIA/VIDEOS.\n"
            "\nIMPORTANT ABOUT THE ISO FILE:\n"
            f"The included {iso_name} is the SAME Linux boot image packaged\n"
            "for experimental XeLL optical boot. You DO NOT have to move it or\n"
            "open it. Linux boots from xenon.elf and X360Linux/ on the USB drive.\n"
            "\nDEBIAN BASE:\n"
            + ("The ISO contains a real signed Debian Ports powerpc rootfs\n"
               "for future development. It is NOT the booted system yet.\n"
               "Do not unpack the ISO or Debian rootfs onto FAT32.\n"
               if debian else
               "Debian Ports rootfs remains experimental and is not included\n"
               "in this build. The active OS is Xenon kernel + BusyBox.\n")
            + "\nNO NAND FLASH. NO HDD FORMATTING. Saves/games are not changed.\n"
            "No MP4/audio support, full desktop or persistence promised.\n"
            "Source/credits: https://github.com/heltindev/X360Linux\n"
        )
        if flavor != "RGH-USB":
            message = (
                "ABadAvatar / FreeMyXe only: your exploit MUST already work.\n"
                "Keep existing FreeMyXe files, MERGE BadUpdatePayload rather than\n"
                "deleting that directory. Back up any old xell-2f.bin first.\n"
                "This ZIP does NOT exploit or unlock a stock Xbox 360.\n\n"
            ) + message
        changes["READ-ME-FIRST.txt"] = message.encode("utf-8")
        with zipfile.ZipFile(pack, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as new:
            for path, (meta, old_data) in entries.items():
                # Preserve source-specific FreeMyXe payload, old file metadata.
                if path in changes:
                    new.writestr(meta, changes[path])
                else:
                    new.writestr(meta, old_data)
            new.writestr(iso_name, iso)
            new.writestr("X360MEDIA/PHOTOS/", "")
            new.writestr("X360MEDIA/VIDEOS/", "")
            # Debian base is already INSIDE the ISO. Never duplicate an
            # 80+ MB tarball next to the ISO in the beginner ZIP.
        with zipfile.ZipFile(pack) as verify:
            if verify.testzip() is not None:
                parser.error(f"Repacked ZIP is corrupted: {pack}")
            for path, data in changes.items():
                if verify.read(path) != data:
                    parser.error(f"Mismatch in {path}")
            if verify.read(iso_name) != iso:
                parser.error("ISO missing or different inside beginner pack")
            if old_xell is not None and verify.read("BadUpdatePayload/xell-2f.bin") != old_xell:
                parser.error("Old exploit XeLL file was unexpectedly modified")
            # The ISO is byte-for-byte verified above, including its
            # optional Debian Ports contents assembled by make_system_image.
        print(f"VERIFIED {pack.name}: {pack.stat().st_size} bytes, sha256={sha256(pack.read_bytes())}")
    print(f"VERIFIED ISO: {iso_name} sha256={sha256(iso)}")

if __name__ == "__main__":
    main()
