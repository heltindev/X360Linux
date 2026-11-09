#!/usr/bin/env python3
"""Deterministic Linux initramfs: newc CPIO + gzip, zero external cpio tools.

Used for X360OS v8 so XeLL can load a completely new /init, with no Casper,
GNOME, Ubuntu rootfs or packages in the archive.
"""
import gzip
import io
import os
from pathlib import Path
import stat
import sys

def padding(output):
    n=(-output.tell()) % 4
    if n:
        output.write(b"\0"*n)

def entry(output, path, mode, data=b"", devmajor=0, devminor=0, rdevmajor=0, rdevminor=0, ino=1):
    name=path.encode("utf-8")+b"\0"
    # Magic + 13 8-digit hex fields, fixed 110-byte header.
    fields=(ino, mode, 0, 0, 2 if stat.S_ISDIR(mode) else 1, 0,
            len(data), devmajor, devminor, rdevmajor, rdevminor, len(name), 0)
    hdr=b"070701"+b"".join(("%08x"%i).encode("ascii") for i in fields)
    assert len(hdr)==110
    output.write(hdr)
    output.write(name)
    padding(output)
    output.write(data)
    padding(output)

def pack(root, output):
    root=Path(root)
    assert root.is_dir()
    all_paths=sorted((p for p in root.rglob("*")), key=lambda p:p.relative_to(root).as_posix())
    allowed={"init","bin/busybox","usr/bin/x360os-ui","etc/os-release",
             "lib/modules/2.6.36.2-xenon/kernel/drivers/input/evdev.ko",
             "lib/modules/2.6.36.2-xenon/kernel/drivers/input/joydev.ko"}
    paths={p.relative_to(root).as_posix() for p in all_paths}
    assert allowed.issubset(paths), allowed-paths
    assert all(not x.startswith(("etc/apt","var/lib/dpkg","usr/lib/xorg",
                "usr/lib/python","usr/share/gnome","casper/")) for x in paths)
    result=io.BytesIO()
    for i,p in enumerate(all_paths,1):
        rel=p.relative_to(root).as_posix()
        st=p.lstat()
        mode=st.st_mode
        data=b""
        if p.is_symlink():
            data=os.readlink(p).encode("utf-8")
        elif p.is_file():
            data=p.read_bytes()
        elif not p.is_dir() and not stat.S_ISCHR(mode):
            raise RuntimeError("unsupported node type "+rel)
        entry(result, rel, mode, data,
              rdevmajor=os.major(st.st_rdev) if stat.S_ISCHR(mode) else 0,
              rdevminor=os.minor(st.st_rdev) if stat.S_ISCHR(mode) else 0,
              ino=i)
    entry(result,"TRAILER!!!",0,ino=len(all_paths)+1)
    blob=result.getvalue()
    output=Path(output)
    with output.open("wb") as dest:
        with gzip.GzipFile(fileobj=dest,mode="wb",filename="",mtime=0,compresslevel=9) as gz:
            gz.write(blob)
    print("X360OS_INITRAMFS_NEWC_GZIP_CREATED",output.name,"entries=",len(all_paths),
          "cpio_size=",len(blob),"gzip_size=",output.stat().st_size)

if __name__=="__main__":
    assert len(sys.argv)==3, "usage: pack-initramfs.py ROOT_DIR OUTPUT_GZIP"
    pack(sys.argv[1],sys.argv[2])
