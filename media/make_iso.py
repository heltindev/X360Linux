#!/usr/bin/env python3
"""Build an ISO9660 *launcher* for XeLL -> XWT Boot on Xbox 360.

This is NOT an x86 bootable ISO, Linux distribution or NAND installer.
"""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--boot-elf", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if not args.boot_elf.is_file() or args.boot_elf.stat().st_size < 128:
        parser.error("Missing or invalid XeLL-loadable ELF32 input")
    if not shutil.which("xorriso"):
        parser.error("Install xorriso to create ISO9660 images")
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="xwtiso-") as work:
        root = Path(work)
        shutil.copyfile(args.boot_elf, root / "xenon.elf")
        (root / "README.TXT").write_text(
            "XWT BOOT (EXPERIMENTAL)\n"
            "For Xbox 360 with existing XeLL loader.\n"
            "XeLL reads xenon.elf from the disc and starts the XWT Boot manager.\n"
            "The Linux kernel/root filesystem are separate and must be placed\n"
            "in a folder on a supported FAT32 USB/HDD device.\n"
            "This disc is NOT a Linux ISO, NAND flasher or recovery image.\n",
            encoding="ascii",
        )
        subprocess.run(
            ["xorriso", "-as", "mkisofs", "-J", "-R",
             "-V", "XWT_BOOT", "-o", str(output), str(root)],
            check=True,
        )
    print(f"Launcher ISO created: {output}")
    print("NOT a Linux distribution or a verified hardware boot image.")

if __name__ == "__main__":
    main()
