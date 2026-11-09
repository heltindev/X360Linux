#!/usr/bin/env python3
"""Create a USB-only experimental Xenon kernel by replacing its LZMA initramfs.

No bootloader, NAND or console firmware changes. Original vmlinux untouched.
"""
from pathlib import Path
import gzip
import hashlib
import lzma
import os
import struct
import subprocess
import sys

base=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path.cwd().resolve()
boot=base/"BOOT-DIRETO"
original=boot/"vmlinux"
custom=boot/"distros/ubuntu-x360/initrd.gz"
dest=boot/"x360linux.elf"
assert original.is_file() and custom.is_file() and not dest.exists(), "existing kernel or target conflict"
elf=original.read_bytes()
assert elf[:6]==b"\x7fELF\x01\x02" and elf[18:20]==b"\x00\x14"
header=struct.unpack_from(">HHIIIIIHHHHHH",elf,16)
etype,machine,ver,entry,phoff,shoff,flags,ehsize,phentsize,phnum,shentsize,shnum,shstrndx=header
assert machine==20 and shentsize==40 and shnum>25
def sec(i):
    p=shoff+i*shentsize
    assert p+40<=len(elf)
    return struct.unpack_from(">IIIIIIIIII",elf,p)
strsect=sec(shstrndx)
names=elf[strsect[4]:strsect[4]+strsect[5]]
sections={}
for i in range(shnum):
    sh=sec(i)
    start=sh[0]
    end=names.find(b"\0",start)
    if end<0:continue
    name=names[start:end].decode("ascii",errors="replace")
    sections[name]=sh
assert ".init.ramfs" in sections
sh=sections[".init.ramfs"]
off,size=sh[4],sh[5]
assert off+size<len(elf) and size>4000000, "Original Xenon legacy kernel changed"
segment=elf[off:off+size]
# Known legacy Xenon image has 2,160 bytes of pre-compressed archive padding.
lzoff=2160
assert segment[lzoff:lzoff+5]==bytes.fromhex("5d00000002")
old_decoder=lzma.LZMADecompressor(format=lzma.FORMAT_ALONE)
old_initramfs=old_decoder.decompress(segment[lzoff:])
assert old_decoder.eof and old_initramfs.startswith(b"070701")
assert b"/scripts/casper\0" in old_initramfs and b"/init\0" in old_initramfs
custom_initramfs=gzip.decompress(custom.read_bytes())
assert custom_initramfs.startswith(b"070701") and b"init\0" in custom_initramfs
assert b"bin/busybox\0" in custom_initramfs and b"bin/run-init\0" in custom_initramfs
assert b"bin/fbprogress\0" in custom_initramfs
assert b"scripts/casper\0" not in custom_initramfs
# Match original 32 MiB LZMA dictionary for old 2.6 Xenon decompression.
compressed=lzma.compress(custom_initramfs,format=lzma.FORMAT_ALONE,
    filters=[{"id":lzma.FILTER_LZMA1,"dict_size":32*1024*1024,"lc":3,"lp":0,"pb":2}])
assert compressed[:5]==segment[lzoff:lzoff+5],"LZMA decoder mismatch"
assert len(compressed)<size-lzoff
verify=lzma.LZMADecompressor(format=lzma.FORMAT_ALONE)
assert verify.decompress(compressed)==custom_initramfs and verify.eof
replacement=segment[:lzoff]+compressed+b"\0"*(size-lzoff-len(compressed))
assert len(replacement)==len(segment)
new=elf[:off]+replacement+elf[off+size:]
assert len(new)==len(elf) and new[:off]==elf[:off] and new[off+size:]==elf[off+size:]
assert new[:52]==elf[:52] and hashlib.sha256(new).digest()!=hashlib.sha256(elf).digest()
stage=dest.with_suffix(".elf.building")
assert not stage.exists()
stage.write_bytes(new)
probe=subprocess.run(["readelf","-h",str(stage)],capture_output=True,text=True)
assert probe.returncode==0 and "PowerPC" in probe.stdout and "big endian" in probe.stdout
full=stage.read_bytes()
assert full==new
patch_sec=full[off:off+size]
decoded=lzma.LZMADecompressor(format=lzma.FORMAT_ALONE)
assert decoded.decompress(patch_sec[lzoff:])==custom_initramfs and decoded.eof
# Rejected when original kernel modified; validate with canonical previously verified SHA.
assert hashlib.sha256(elf).hexdigest()=="b8aa8eef938275ed5f037b884592283f561ac46b283edf4cdb1200bf2d39cec8"
os.replace(stage,dest)
print("PATCHED_XENON_KERNEL_READY",str(dest))
print("ORIGINAL_KERNEL_SHA256",hashlib.sha256(elf).hexdigest())
print("PATCHED_KERNEL_SHA256",hashlib.sha256(new).hexdigest())
print("EMBEDDED_INITRAMFS_ORIGINAL_BYTES",len(old_initramfs))
print("EMBEDDED_INITRAMFS_NEW_BYTES",len(custom_initramfs))
print("LZMA_NEW_BYTES",len(compressed),"AVAILABLE",size-lzoff)
print("ELF32_BE_HEADERS_PROGRAM_SECTIONS_PRESERVED")
print("NO_CONSOLE_HDD_NAND_CHANGES")
