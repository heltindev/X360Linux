#!/usr/bin/env python3
"""Independently check the changed ELF section and removal of old Ubuntu initramfs."""
from pathlib import Path
import hashlib
import gzip
import lzma
import runpy
import subprocess
import sys

def digest(b):return hashlib.sha256(b).hexdigest()

def main(original, original_native_initrd, outdir):
    out=Path(outdir)
    original=Path(original).read_bytes()
    rebuilt=(out/"vmlinux").read_bytes()
    assert len(rebuilt)==len(original)
    p=runpy.run_path(str(Path(__file__).with_name("patch-embedded-kernel.py")))
    locate=p["initramfs_section"]
    filenames=p["cpio_names"]
    offset,sz=locate(original)
    assert locate(rebuilt)==(offset,sz)
    assert original[:offset]==rebuilt[:offset]
    assert original[offset+sz:]==rebuilt[offset+sz:]
    assert original[offset:offset+2160]==rebuilt[offset:offset+2160]
    # Confirm the old guest was Ubuntu+Casper, and the new one isn't.
    old=lzma.decompress(original[offset+2160:offset+sz],format=lzma.FORMAT_ALONE)
    old_names=filenames(old)
    assert any("casper" in x.lower() for x in old_names)
    encoded=rebuilt[offset+2160:offset+sz]
    decoder=lzma.LZMADecompressor(format=lzma.FORMAT_ALONE)
    new=decoder.decompress(encoded)
    assert decoder.eof and all(z==0 for z in decoder.unused_data)
    native=gzip.decompress(Path(original_native_initrd).read_bytes())
    assert new==native,"The embedded root filesystem must be byte-identical to tested native X360OS CPIO"
    names=filenames(new)
    assert {"init","bin/sh","bin/busybox","usr/bin/x360os-ui"}.issubset(names)
    banned=("casper/","etc/apt","var/lib/dpkg","usr/lib/xorg","usr/share/gnome",
            "usr/bin/python","usr/lib/python","usr/bin/gnome")
    assert not any(x.startswith(banned) for x in names)
    cfg=(out/"kboot.conf").read_bytes()
    assert cfg.startswith(b"#KBOOTCONFIG\n")
    assert b"uda:/vmlinux" in cfg and b"rdinit=/init" in cfg and b"console=tty0" in cfg
    assert b"initrd=" not in cfg and b"boot=casper" not in cfg
    assert not any((out/name).exists() for name in ("casper","casper-rw","initrd-x360os.gz","filesystem.squashfs"))
    # The original XeLL ELF segment layout must remain byte-for-byte identical.
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p1=Path(d)/"old.elf";p2=Path(d)/"new.elf"
        p1.write_bytes(original);p2.write_bytes(rebuilt)
        for mode in ("-h","-l","-SW"):
            a=subprocess.check_output(["powerpc-linux-gnu-readelf",mode,str(p1)])
            b=subprocess.check_output(["powerpc-linux-gnu-readelf",mode,str(p2)])
            assert a==b,"ELF metadata changed: "+mode
    checks=(out/"SHA256SUMS.txt").read_text().splitlines()
    for line in checks:
        sha,name=line.split(None,1)
        assert digest((out/name).read_bytes())==sha
    print("PASS kernel ELF32 PPC headers + load segments IDENTICAL to original XeLL kernel")
    print("PASS old Ubuntu/Casper embedded root removed and replaced by X360OS CPIO")
    print("PASS no external initrd/Casper/rootfs package required")
    print("PASS .init.ramfs fixed size with correct LZMA decompression and zero padding")
    print("PASS native X360OS initramfs files:",len(names))
    print("PASS SHA256 checks and TV console kernel arguments")
    print("XBOX PHYSICAL BOOT: STILL UNTESTED")

if __name__=="__main__":
    assert len(sys.argv)==4,"usage: verify-v9.py ORIGINAL_VMLINUX VERIFIED_NATIVE_INITRD OUTPUT_DIR"
    main(sys.argv[1],sys.argv[2],sys.argv[3])
