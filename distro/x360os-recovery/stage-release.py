#!/usr/bin/env python3
"""Copy a validated X360OS recovery build into a NEW USB boot directory and ZIP.

Never writes to a removable drive or replaces an existing installation.
"""
import argparse
import hashlib
from pathlib import Path
import shutil
import zipfile

FILES = ("vmlinux", "kboot.conf", "casper/filesystem.squashfs",
         "READ-ME-FIRST.txt", "TESTE-PTBR.txt", "SHA256SUMS.txt")

def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024 * 4), b""):
            h.update(block)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--zip", dest="archive", type=Path, required=True)
    ap.add_argument("--known-kernel", type=Path, required=True)
    args = ap.parse_args()
    assert args.build.is_dir(), "Build missing"
    assert args.known_kernel.is_file(), "Original kernel missing"
    assert not args.output.exists(), "STOP: target exists. No overwriting."
    assert not args.archive.exists(), "STOP: ZIP exists. No overwriting."
    for f in FILES:
        assert (args.build / f).is_file(), f
    assert sha(args.build / "vmlinux") == sha(args.known_kernel)
    cfg = (args.build / "kboot.conf").read_text(encoding="utf-8")
    assert "nopersistent" in cfg and "boot=casper" in cfg
    assert not (args.build / "casper-rw").exists()
    assert (args.build / "casper/filesystem.squashfs").stat().st_size > 100_000_000
    args.output.mkdir(parents=True)
    for f in FILES:
        dest = args.output / f
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(args.build / f, dest)
        assert sha(dest) == sha(args.build / f), "Corrupt copy: " + f
        print("VERIFIED", f, flush=True)
    assert not (args.output / "casper-rw").exists()
    args.archive.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(str(args.archive), "w", compression=zipfile.ZIP_STORED,
                         allowZip64=True) as z:
        for f in FILES:
            z.write(str(args.output / f), arcname=f)
    with zipfile.ZipFile(str(args.archive)) as z:
        assert z.testzip() is None, "ZIP CRC error"
        assert set(z.namelist()) == set(FILES)
    print("X360OS RECOVERY STAGED:", args.output)
    print("USB ZIP VERIFIED:", args.archive)
    print("ROOTFS SHA256:", sha(args.output / "casper/filesystem.squashfs"))
    print("BOOT FILES UNCHANGED: existing v5/v6 and E: NOT touched")

if __name__ == "__main__":
    main()
