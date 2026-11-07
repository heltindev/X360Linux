#!/usr/bin/env python3
"""Generate a deterministic Linux 'newc' initramfs with static PowerPC BusyBox.

This packages Linux userspace only; does not create a kernel or bootable ISO.
"""
import argparse
import gzip
from pathlib import Path
import stat

def newc(name, data=b"", mode=0o100644, rmajor=0, rminor=0, ino=1):
    n = name.encode("utf-8") + b"\0"
    fields = (ino, mode, 0, 0, 1, 0, len(data), 0, 0,
              rmajor, rminor, len(n), 0)
    header = b"070701" + b"".join(f"{v:08x}".encode("ascii") for v in fields)
    out = header + n
    out += b"\0" * (-len(out) % 4)
    out += data
    out += b"\0" * (-len(data) % 4)
    return out

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--busybox", type=Path, required=True)
    p.add_argument("--init", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    busybox = args.busybox.read_bytes()
    if (len(busybox) < 10_000 or busybox[:6] != b"\x7fELF\x01\x02" or
            busybox[18:20] != b"\x00\x14"):
        p.error("Expected a 32-bit big-endian PowerPC Linux BusyBox ELF")
    init = args.init.read_bytes()
    records = []
    ino = 1
    def add(path, data=b"", mode=stat.S_IFREG | 0o644, major=0, minor=0):
        nonlocal ino
        records.append(newc(path, data, mode, major, minor, ino))
        ino += 1
    for path in ("bin","dev","etc","proc","sys","tmp","run","usr","usr/bin",
                 "sbin","root","dev/pts"):
        add(path, mode=stat.S_IFDIR | 0o755)
    add("bin/busybox", busybox, stat.S_IFREG | 0o755)
    for applet in ("sh","mount","mkdir","hostname","echo","cat","dmesg","uname",
                   "ls","ps","free","reboot","poweroff","sleep"):
        add("bin/" + applet, b"busybox", stat.S_IFLNK | 0o777)
    add("init", init, stat.S_IFREG | 0o755)
    add("dev/console", b"", stat.S_IFCHR | 0o600, 5, 1)
    add("dev/null", b"", stat.S_IFCHR | 0o666, 1, 3)
    add("etc/issue", b"X360Linux experimental Linux shell\n")
    add("TRAILER!!!")
    target = args.output.resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("wb") as fd:
        with gzip.GzipFile(filename="", mode="wb", fileobj=fd, mtime=0, compresslevel=9) as gz:
            for item in records:
                gz.write(item)
    print(f"Created Linux initramfs: {target} ({target.stat().st_size} bytes)")
    print("NOT independently bootable: requires Xenon Linux kernel + device tree.")

if __name__ == "__main__":
    main()
