#!/usr/bin/env python3
"""Stage a verified Xbox 360 X360OS V9 kernel-only USB test, no old USB edits."""
from pathlib import Path
import hashlib
import shutil
import zipfile

ROOT=Path(r"C:\Users\hhhel.DESKTOP-3QIFGGI\Desktop\PEN DRIVE")
SOURCE=ROOT/"work"/"release-v9.0.0-embedded-native-r2"
TARGET=ROOT/"BOOT-DIRETO-X360OS-v9-EMBUTIDO-SEM-UBUNTU"
ARCHIVE=SOURCE/"X360OS-v9.0.0-EMBEDDED-NATIVE-USB-TEST.zip"
FILES=("vmlinux","kboot.conf","READ-ME-FIRST.txt","TESTE-PTBR.txt","SHA256SUMS.txt")

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(4*1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

assert SOURCE.is_dir(),"No verified v9 image"
assert not TARGET.exists(),"Refusing to overwrite target folder"
assert not ARCHIVE.exists(),"Refusing to overwrite ZIP"
assert all((SOURCE/f).is_file() for f in FILES)
assert not any((SOURCE/f).exists() for f in ("initrd-x360os.gz","casper","casper-rw","filesystem.squashfs"))
cfg=(SOURCE/"kboot.conf").read_bytes()
assert cfg.startswith(b"#KBOOTCONFIG\n")
assert b"rdinit=/init" in cfg and b"initrd=" not in cfg and b"boot=casper" not in cfg
assert sha(SOURCE/"vmlinux")!=sha(ROOT/"BOOT-DIRETO"/"vmlinux")
TARGET.mkdir(parents=True)
for file in FILES:
    shutil.copy2(SOURCE/file,TARGET/file)
    assert sha(SOURCE/file)==sha(TARGET/file)
    print("COPIED VERIFIED",file,flush=True)
with zipfile.ZipFile(ARCHIVE,"w",compression=zipfile.ZIP_STORED,allowZip64=True) as archive:
    for file in FILES:archive.write(TARGET/file,file)
with zipfile.ZipFile(ARCHIVE,"r") as archive:
    assert archive.testzip() is None
    assert set(archive.namelist())==set(FILES)
print("STAGED_BOOT_PATH",TARGET,flush=True)
print("ZIP_TESTED",ARCHIVE,flush=True)
print("NEW_KERNEL_SHA256",sha(TARGET/"vmlinux"),flush=True)
print("ORIGINAL_BOOT_FOLDERS, USB E:, NAND AND XBOX HDD: NEVER TOUCHED",flush=True)
