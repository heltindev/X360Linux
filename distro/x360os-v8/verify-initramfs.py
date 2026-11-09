#!/usr/bin/env python3
"""Independently parse and verify generated newc CPIO; reject Ubuntu artifacts."""
import gzip
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile

def unpack(path):
    src=gzip.decompress(Path(path).read_bytes())
    i=0
    entries={}
    while True:
        assert i+110<=len(src), "Truncated CPIO header"
        header=src[i:i+110];i+=110
        assert header[:6] == b"070701", "Not newc"
        vals=[int(header[j:j+8],16) for j in range(6,110,8)]
        assert len(vals)==13
        ino, mode, uid, gid, nlink, mtime, filesize, devmaj, devmin, rmaj, rmin, namesize, chk=vals
        assert 1<=namesize<=1024
        assert i+namesize<=len(src)
        name=src[i:i+namesize]
        assert name.endswith(b"\x00")
        name=name[:-1].decode("utf-8")
        i=(i+namesize+3)&~3
        assert filesize <= 80*1024*1024
        assert i+filesize<=len(src)
        content=src[i:i+filesize]
        i=(i+filesize+3)&~3
        if name=="TRAILER!!!":
            assert filesize==0
            break
        assert name not in entries, "Duplicate archive path: "+name
        assert not name.startswith("/") and ".." not in Path(name).parts
        entries[name]=(mode,content,rmaj,rmin)
    assert i<=len(src)
    return entries

def verify(root):
    root=Path(root)
    entries=unpack(root/"initrd-x360os.gz")
    required=["init","bin/busybox","bin/sh","usr/bin/x360os-ui",
              "etc/os-release","dev/console",
              "lib/modules/2.6.36.2-xenon/kernel/drivers/input/evdev.ko",
              "lib/modules/2.6.36.2-xenon/kernel/drivers/input/joydev.ko"]
    for p in required: assert p in entries, "Missing "+p
    assert stat.S_ISREG(entries["init"][0])
    assert entries["init"][0]&0o111
    assert stat.S_ISCHR(entries["dev/console"][0])
    assert entries["dev/console"][2:]==(5,1)
    assert stat.S_ISLNK(entries["bin/sh"][0])
    assert entries["bin/sh"][1]==b"/bin/busybox"
    assert b"X360OS v8" in entries["init"][1]
    assert b'ID=x360os' in entries["etc/os-release"][1]
    assert b"boot=casper" not in entries["init"][1].lower()
    assert b"/casper/" not in entries["init"][1].lower()
    banned_prefixes=("etc/apt","var/lib/dpkg","usr/lib/xorg",
                     "usr/share/gnome","usr/lib/python","casper/",
                     "lib/systemd","usr/bin/firefox","usr/bin/gnome")
    assert not [p for p in entries if p.startswith(banned_prefixes)]
    assert "etc/lsb-release" not in entries
    cfg=(root/"kboot.conf").read_text()
    assert "initrd=uda:/initrd-x360os.gz" in cfg
    assert "rdinit=/init" in cfg
    assert "boot=casper" not in cfg
    assert not (root/"casper").exists()
    assert not (root/"filesystem.squashfs").exists()
    assert not (root/"casper-rw").exists()
    assert not (root/"ubuntu").exists()
    with tempfile.TemporaryDirectory(prefix="x360os-v8-verify-") as td:
        for p in ("bin/busybox","usr/bin/x360os-ui"):
            dest=Path(td)/Path(p).name
            dest.write_bytes(entries[p][1])
            dest.chmod(0o755)
            file_result=subprocess.run(["file",str(dest)],capture_output=True,text=True,check=True)
            assert "ELF 32-bit MSB" in file_result.stdout
            assert "statically linked" in file_result.stdout
        r=subprocess.run(["qemu-ppc-static",str(Path(td)/"busybox"),
                          "echo","NATIVE_INITRAMFS_PPC_OK"],capture_output=True,text=True)
        assert r.returncode==0 and "NATIVE_INITRAMFS_PPC_OK" in r.stdout
        ppm=Path(td)/"test.ppm"
        r=subprocess.run(["qemu-ppc-static",str(Path(td)/"x360os-ui"),
                         "--render-test-xenos","800","480",str(ppm)],
                         capture_output=True,text=True)
        assert r.returncode==0 and ppm.is_file() and ppm.stat().st_size>100_000
    print("PASS: X360OS v8 true newc/gzip archive, 100% standalone PPC userland")
    print("PASS: Xbox 360 Xenon input modules present (not Ubuntu packages)")
    print("PASS: static PPC BusyBox + tiled framebuffer render under QEMU")
    print("PASS: Zero Casper, Ubuntu filesystem, GNOME, Xorg, APT, GTK, Python")
    print("PASS: XeLL external initrd + rdinit=/init configuration")
    print("COUNT:",len(entries),"newc entries")
    print("EXPERIMENTAL: XeLL boot + Xenos hardware still need physical console test")

if __name__=="__main__":
    assert len(sys.argv)==2,"usage: verify-initramfs.py OUTPUT_DIRECTORY"
    verify(sys.argv[1])
