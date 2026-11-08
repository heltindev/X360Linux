#!/usr/bin/env python3
"""Inspect prebuilt X360Linux ZIPs before publishing a ready-to-copy release."""
from pathlib import Path
from zipfile import ZipFile, BadZipFile
import argparse
import hashlib
import sys

BASE = {"xenon.elf", "X360Linux/vmlinux", "X360Linux/xenon.dtb",
        "X360Linux/initramfs.cpio.gz", "X360Linux/X360Linux.iso",
        "X360Linux/USB-DATA.ext4", "X360Linux/USB-ROOT.ID",
        "X360Linux/READ-ME-FIRST.txt"}
MARKER = b"X360LINUX-USB-ROOT-V1\n"
def verify(path: Path) -> str:
    if not path.is_file():
        raise ValueError(f"missing ZIP: {path}")
    with ZipFile(path) as archive:
        names = archive.namelist()
        if len(set(names)) != len(names):
            raise ValueError("duplicate archive paths")
        if not BASE.issubset(names):
            raise ValueError(f"missing boot components: {BASE - set(names)}")
        if any(name.startswith("/") or ".." in Path(name).parts for name in names):
            raise ValueError("unsafe or nested archive path")
        if archive.read("X360Linux/USB-ROOT.ID") != MARKER:
            raise ValueError("USB marker mismatch")
        if archive.getinfo("X360Linux/USB-DATA.ext4").file_size != 512 * 1024 * 1024:
            raise ValueError("missing 512 MiB USB persistence image")
        with archive.open("X360Linux/USB-DATA.ext4") as data:
            data.read(1080)
            if data.read(2) != b"\x53\xef":
                raise ValueError("invalid ext4 persistence signature")
        with archive.open("X360Linux/X360Linux.iso") as data:
            data.read(32769)
            if data.read(5) != b"CD001":
                raise ValueError("invalid ISO9660 signature")
        if archive.getinfo("X360Linux/X360Linux.iso").file_size < 100 * 1024 * 1024:
            raise ValueError("Debian desktop ISO is unexpectedly small")
        if path.name.endswith("-RGH-USB.zip") and "BadUpdatePayload/xell-2f.bin" in names:
            raise ValueError("RGH pack contains FreeMyXe payload")
        if "ABadAvatar-FreeMyXe" in path.name and "BadUpdatePayload/xell-2f.bin" not in names:
            raise ValueError("FreeMyXe pack lacks XeLL payload")
        bad = archive.testzip()
        if bad:
            raise ValueError(f"corrupted ZIP member: {bad}")
    h = hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda: f.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("directory", type=Path)
    p.add_argument("--tag", default="v0.3.0-alpha")
    args = p.parse_args()
    paths = [args.directory / f"X360Linux-{args.tag}-{kind}.zip"
             for kind in ("RGH-USB", "ABadAvatar-FreeMyXe-USB")]
    checks = []
    try:
        for path in paths:
            digest = verify(path)
            print(f"VERIFIED_READY_TO_COPY {path.name}: {path.stat().st_size} bytes", flush=True)
            checks.append(f"{digest}  {path.name}")
    except (ValueError, BadZipFile, OSError) as exc:
        print(f"RELEASE_VERIFICATION_FAILED: {exc}", file=sys.stderr)
        return 1
    (args.directory / "SHA256SUMS").write_text("\n".join(checks) + "\n", encoding="ascii")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
