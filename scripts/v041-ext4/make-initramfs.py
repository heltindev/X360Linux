#!/usr/bin/env python3
"""Build an external PowerPC32 initramfs from the original Ubuntu 10.10 BusyBox."""
from pathlib import Path
import gzip
import os
import stat
import subprocess
import sys

base = Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path.cwd().resolve()
source = Path(__file__).resolve().parent
target = base / "BOOT-DIRETO/distros/ubuntu-x360/initrd.gz"
squash = base / "BOOT-DIRETO/casper/filesystem.squashfs"

assert source.joinpath("init").is_file()
assert squash.is_file()
target.parent.mkdir(parents=True, exist_ok=True)
bb = subprocess.run(
    ["unsquashfs", "-cat", str(squash), "bin/busybox"],
    capture_output=True, check=True
).stdout
assert bb[:4] == b"\x7fELF" and bb[4] == 1 and bb[5] == 2, "Not PPC32 ELF Big Endian"
assert 1800000 > len(bb) > 1000000, "Unexpected busybox size"
assert b"losetup" in bb and b"mdev" in bb, "Required BusyBox applet absent"

members = []
def add(name, mode, content=b"", major=0, minor=0):
    members.append((name, mode, content, major, minor))
dir_mode = stat.S_IFDIR | 0o755
regular = stat.S_IFREG | 0o755
for folder in (".", "bin", "sbin", "lib", "dev", "dev/pts", "proc", "sys", "run", "bootusb", "newroot"): 
    add(folder, dir_mode)
add("bin/busybox", regular, bb)
fbprogress = source / "fbprogress"
assert fbprogress.is_file(), "Compile the static PPC framebuffer tool first."
fb = fbprogress.read_bytes()
assert fb.startswith(b"\x7fELF") and fb[4] == 1 and fb[5] == 2, "Progress tool must be PPC32 big-endian ELF"
add("bin/fbprogress", regular, fb)
for name in ("sh", "mount", "umount", "readlink", "mdev", "mkdir",
             "basename", "cat", "sleep", "losetup", "mknod", "cp", "touch",
             "stat"): 
    add("bin/" + name, stat.S_IFLNK | 0o777, b"busybox")
# Ubuntu 10.10 klibc run-init works with the 2.6.36 era kernel and
# replaces the switch_root applet absent in the original BusyBox.
runinit = subprocess.run(
    ["unsquashfs", "-cat", str(squash), "usr/lib/klibc/bin/run-init"],
    capture_output=True, check=True
).stdout
libname = "klibc-NuvhEL-8fn5VKNGwkJGStDUEMoY.so"
klibc = subprocess.run(
    ["unsquashfs", "-cat", str(squash), "lib/" + libname],
    capture_output=True, check=True
).stdout
assert runinit.startswith(b"\x7fELF") and klibc.startswith(b"\x7fELF")
add("bin/run-init", regular, runinit)
add("lib/" + libname, regular, klibc)
add("init", regular, (source / "init").read_bytes())
# These special nodes permit recovery even before /dev is mounted.
add("dev/console", stat.S_IFCHR | 0o600, b"", 5, 1)
add("dev/null", stat.S_IFCHR | 0o666, b"", 1, 3)
add("dev/tty0", stat.S_IFCHR | 0o600, b"", 4, 0)
add("dev/loop0", stat.S_IFBLK | 0o600, b"", 7, 0)

def align(out):
    out.extend(b"\x00" * (-len(out) % 4))
def write_entry(out, inode, name, mode, content=b"", major=0, minor=0):
    filename = name.encode() + b"\x00"
    fields = (inode, mode, 0, 0, 2 if stat.S_ISDIR(mode) else 1, 0,
              len(content), 0, 0, major, minor, len(filename), 0)
    out.extend(b"070701" + b"".join(("%08x" % value).encode() for value in fields))
    out.extend(filename)
    align(out)
    out.extend(content)
    align(out)

blob = bytearray()
for n, (name, mode, content, major, minor) in enumerate(members, 1):
    write_entry(blob, n, name, mode, content, major, minor)
write_entry(blob, len(members) + 1, "TRAILER!!!", 0)
assert blob[:6] == b"070701" and blob.rfind(b"TRAILER!!!") > len(blob) - 140
with target.open("wb") as raw:
    with gzip.GzipFile(filename="", mode="wb", fileobj=raw, compresslevel=9, mtime=0) as z:
        z.write(blob)
with gzip.open(target, "rb") as z:
    assert z.read() == blob
print("INITRAMFS_CREATED", target, target.stat().st_size)
print("INITRAMFS_PPC32_BUSYBOX", len(bb), "for older Linux ABI")
print("INIT_SCRIPT_STATIC_SYNTAX")
chk = subprocess.run(["dash", "-n", str(source / "init")], capture_output=True, text=True)
assert chk.returncode == 0, chk.stderr
print("INIT_SCRIPT_DASH_SYNTAX_OK")
