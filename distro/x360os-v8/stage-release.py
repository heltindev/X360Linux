#!/usr/bin/env python3
"""Stage X360OS v8 native-only USB files without modifying E:, NAND or old builds."""
from pathlib import Path
import hashlib
import shutil
import zipfile
import sys

ROOT=Path(r"C:\Users\hhhel.DESKTOP-3QIFGGI\Desktop\PEN DRIVE")
BUILD=ROOT/"work"/"release-v8.0.0-zero-ubuntu-r2"
TARGET=ROOT/"BOOT-DIRETO-X360OS-v8-NATIVO-SEM-UBUNTU"
ZIP=BUILD/"X360OS-v8.0.0-NATIVE-ZERO-UBUNTU-USB-TEST.zip"
KNOWN=ROOT/"BOOT-DIRETO"/"vmlinux"
FILES=("vmlinux","initrd-x360os.gz","kboot.conf",
       "READ-ME-FIRST.txt","TESTE-PTBR.txt","SHA256SUMS.txt")

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(4*1024*1024),b""):
            h.update(block)
    return h.hexdigest()

def run():
    assert BUILD.is_dir() and KNOWN.is_file()
    assert not TARGET.exists(), "STOP: target directory already exists!"
    assert not ZIP.exists(), "STOP: output ZIP already exists!"
    for name in FILES:
        assert (BUILD/name).is_file(), "Missing "+name
    assert sha(KNOWN)==sha(BUILD/"vmlinux")
    cfg=(BUILD/"kboot.conf").read_text()
    assert "initrd=uda:/initrd-x360os.gz" in cfg
    assert "rdinit=/init" in cfg and "boot=casper" not in cfg
    assert not (BUILD/"casper").exists()
    assert not (BUILD/"filesystem.squashfs").exists()
    assert (BUILD/"initrd-x360os.gz").stat().st_size<10_000_000
    TARGET.mkdir(parents=True,exist_ok=False)
    for item in FILES:
        shutil.copy2(BUILD/item,TARGET/item)
        assert sha(BUILD/item)==sha(TARGET/item), "Bad copy: "+item
        print("COPIED AND SHA256 VERIFIED:",item,flush=True)
    with zipfile.ZipFile(ZIP,mode="w",compression=zipfile.ZIP_STORED,allowZip64=True) as z:
        for item in FILES: z.write(TARGET/item,arcname=item)
    with zipfile.ZipFile(ZIP) as z:
        assert z.testzip() is None
        assert set(z.namelist())==set(FILES)
    print("X360OS_NATIVE_V8_RELEASE_STAGED",TARGET,flush=True)
    print("ZIP_TESTED",ZIP,flush=True)
    print("INITRD_SHA256",sha(TARGET/"initrd-x360os.gz"),flush=True)
    print("EXISTING USB E:, WORKING BOOT FOLDERS, NAND, HDD UNCHANGED",flush=True)

if __name__=="__main__":
    run()
