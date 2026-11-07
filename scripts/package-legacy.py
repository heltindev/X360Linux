#!/usr/bin/env python3
"""Package an explicitly supplied historical Xbox 360 Linux directory.

No firmware modification or device access. Never package extra files, keys,
NAND dumps or unexpected symlinks. Expects a specific five-file snapshot.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = [
    "default.xex",
    "readme.txt",
    "vmlinux",
    "xell.bin",
    "casper/filesystem.squashfs",
]
ZIP_NOTICE = ROOT / "legacy" / "README-FIRST.txt"


def checksum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="Historical LINUX 360 folder")
    parser.add_argument("archive", type=Path, help="ZIP output outside the repository")
    args = parser.parse_args()
    source = args.directory.resolve()
    archive = args.archive.resolve()

    if not source.is_dir() or not ZIP_NOTICE.is_file():
        parser.error("Legacy folder or project README-FIRST.txt not found.")
    if source == archive.parent or ROOT == archive.parent:
        parser.error("Output should be outside the legacy source and Git checkout.")
    if archive.exists():
        parser.error("Archive already exists; refusing to overwrite.")
    actual = sorted(p.relative_to(source).as_posix() for p in source.rglob("*") if p.is_file())
    if actual != sorted(EXPECTED):
        parser.error(f"Unexpected legacy inventory. Expected {EXPECTED}; found {actual}")
    for name in EXPECTED:
        if (source / name).is_symlink():
            parser.error(f"Refusing to archive symbolic link: {name}")
    # These are big, already-compressed images. ZIP_STORED is fast and lossless.
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_STORED, allowZip64=True) as output:
        output.write(ZIP_NOTICE, arcname="README-FIRST.txt")
        for name in EXPECTED:
            output.write(source / name, arcname=name)
    print(f"Created: {archive}")
    print(f"Bytes: {archive.stat().st_size}")
    print(f"SHA256: {checksum(archive)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
