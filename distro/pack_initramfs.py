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
    p.add_argument("--desktop", type=Path, help="Optional compiled PPC32 X360Desk ELF")
    p.add_argument("--demo-dir", type=Path, help="Directory with original photo/video demos")
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
                 "sbin","root","dev/pts","dev/input","media","media/usb",
                 "usr/share","usr/share/x360linux",
                 "usr/share/x360linux/photos","usr/share/x360linux/videos"):
        add(path, mode=stat.S_IFDIR | 0o755)
    add("bin/busybox", busybox, stat.S_IFREG | 0o755)
    if args.desktop:
        app = args.desktop.read_bytes()
        if len(app) < 10000 or app[:6] != b"\x7fELF\x01\x02" or app[18:20] != b"\x00\x14":
            p.error("X360Desk must be a big-endian PowerPC32 ELF")
        add("bin/x360desk", app, stat.S_IFREG | 0o755)
    if args.demo_dir:
        for sub in ("photos", "videos"):
            folder = args.demo_dir / sub
            for item in sorted(folder.iterdir()):
                if item.is_file():
                    add("usr/share/x360linux/" + sub + "/" + item.name,
                        item.read_bytes(), stat.S_IFREG | 0o644)
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
