#!/usr/bin/env python3
"""Replace *only* the embedded initramfs of a previously XeLL-booting Xenon ELF.

Critical discovery: the v8 'unchanged' vmlinux embeds 4.46MB of LZMA-compressed
Ubuntu/Casper initramfs, which expands to 15.9MB. Adding a second external
initrd does NOT prove the whole boot is Ubuntu-free and may conflict with it.

Free60's kernel contains a specific .init.ramfs section with 2160 leading
zero-padding bytes and an LZMA-alone stream. Linux 2.6.36's initramfs parser
permits zero-padding and LZMA streams in that section. In-place patching means
all ELF program/section headers and every byte OUTSIDE .init.ramfs stay exact.

THIS IS EXPERIMENTAL ON XBOX HARDWARE, NOT A GUARANTEED BOOTABLE IMAGE.
"""
from pathlib import Path
import gzip
import hashlib
import lzma
import struct
import sys

VERIFIED_KERNEL = "b8aa8eef938275ed5f037b884592283f561ac46b283edf4cdb1200bf2d39cec8"
EXPECTED_LZMA_HEADER = bytes.fromhex("5d 00 00 00 02 ff ff ff ff ff ff ff ff")

def digest(data):
    return hashlib.sha256(data).hexdigest()

def initramfs_section(buf):
    """Locate .init.ramfs in a big-endian 32-bit PowerPC ELF by its section table."""
    assert buf[:6] == b"\x7fELF\x01\x02", "Expected 32-bit big-endian ELF"
    header=struct.unpack_from(">16sHHIIIIIHHHHHH",buf,0)
    _, e_type, e_machine, _, e_entry, e_phoff, e_shoff, _, _, e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx=header
    assert e_type == 2 and e_machine == 20, "Not XeLL PowerPC ELF"
    assert e_entry == 0 and e_phnum == 3 and e_phentsize == 32
    assert e_shentsize == 40 and 2<e_shnum<256 and 0<e_shstrndx<e_shnum
    assert e_shoff+e_shnum*e_shentsize<=len(buf)
    nameshdr=struct.unpack_from(">IIIIIIIIII",buf,e_shoff+e_shstrndx*e_shentsize)
    names=buf[nameshdr[4]:nameshdr[4]+nameshdr[5]]
    sections={}
    for n in range(e_shnum):
        sh=struct.unpack_from(">IIIIIIIIII",buf,e_shoff+n*e_shentsize)
        namestart=sh[0]
        if namestart>=len(names):continue
        name=names[namestart:names.find(b"\x00",namestart)].decode(errors="replace")
        sections[name]=(sh[4],sh[5])
    assert ".init.ramfs" in sections
    pos,length=sections[".init.ramfs"]
    assert pos>0 and length>1_000_000 and pos+length<len(buf)
    return pos,length

def cpio_names(raw):
    assert raw.startswith(b"070701"),"X360OS archive must contain newc CPIO"
    i=0
    names=[]
    while i+110<=len(raw):
        hdr=raw[i:i+110];i+=110
        assert hdr[:6]==b"070701",f"bad newc marker at {i-110}"
        fields=[int(hdr[t:t+8],16) for t in range(6,110,8)]
        length=fields[6]
        nlen=fields[11]
        assert 1<=nlen<=8192
        path=raw[i:i+nlen]
        assert len(path)==nlen and path[-1]==0
        filename=path[:-1].decode("utf-8")
        i=(i+nlen+3)&~3
        i=(i+length+3)&~3
        assert i<=len(raw)
        if filename=="TRAILER!!!":break
        names.append(filename)
    else:
        raise ValueError("missing CPIO TRAILER")
    return names

def replace(source, initrd, destination):
    source=Path(source);initrd=Path(initrd);destination=Path(destination)
    assert source.is_file() and initrd.is_file()
    assert not destination.exists(),"Refusing to overwrite candidate kernel"
    old=source.read_bytes()
    assert digest(old)==VERIFIED_KERNEL,"Unexpected kernel; stop before ELF edit"
    off,size=initramfs_section(old)
    embedded=old[off:off+size]
    prefix=2160
    assert embedded[:prefix]==b"\0"*prefix
    assert embedded[prefix:prefix+13]==EXPECTED_LZMA_HEADER
    decoder=lzma.LZMADecompressor(format=lzma.FORMAT_ALONE)
    historical=decoder.decompress(embedded[prefix:])
    assert decoder.eof and historical.startswith(b"070701")
    names_old=cpio_names(historical)
    assert any("casper" in name.lower() or "ubuntu" in name.lower() for name in names_old), \
        "Refusing to patch kernel without confirmed embedded old live distro"
    new_raw=gzip.decompress(initrd.read_bytes())
    names_new=cpio_names(new_raw)
    required={"init","bin/busybox","bin/sh","usr/bin/x360os-ui"}
    assert required.issubset(names_new),"X360OS initramfs missing native boot files"
    banned=("casper/","etc/apt/","var/lib/dpkg/","usr/lib/xorg/",
            "usr/share/gnome/","usr/bin/python","usr/bin/gnome")
    assert not any(name.startswith(banned) for name in names_new),"Ubuntu file path found"
    filter_cfg=[{"id":lzma.FILTER_LZMA1,"dict_size":32*1024*1024,"lc":3,"lp":0,"pb":2}]
    compressed=lzma.compress(new_raw,format=lzma.FORMAT_ALONE,filters=filter_cfg)
    assert compressed[:13]==EXPECTED_LZMA_HEADER,"Kernel LZMA format changed"
    assert len(compressed)+prefix<=size,"New initramfs exceeds ELF section size"
    new_section=embedded[:prefix]+compressed+b"\0"*(size-prefix-len(compressed))
    candidate=old[:off]+new_section+old[off+size:]
    assert len(candidate)==len(old)
    assert candidate[:off]==old[:off] and candidate[off+size:]==old[off+size:]
    assert initramfs_section(candidate)==(off,size)
    # Verify LZMA EOF and that every trailing byte is harmless zero padding.
    valid=lzma.LZMADecompressor(format=lzma.FORMAT_ALONE)
    payload=valid.decompress(candidate[off+prefix:off+size])
    assert valid.eof and payload==new_raw
    assert all(c==0 for c in valid.unused_data)
    assert digest(candidate)!=digest(old)
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_bytes(candidate)
    assert destination.read_bytes()==candidate
    print("VERIFIED_ORIGINAL_XELL_KERNEL_SHA256",digest(old))
    print("OLD_EMBEDDED_CPIO_FILES",len(names_old),"UNCOMPRESSED_BYTES",len(historical))
    print("NEW_X360OS_CPIO_FILES",len(names_new),"UNCOMPRESSED_BYTES",len(new_raw))
    print("ELF_EMBEDDED_SECTION_OFF",hex(off),"BYTES",size)
    print("NEW_LZMA_BYTES",len(compressed),"ZERO_PADDING_BYTES",size-prefix-len(compressed))
    print("ELF_HEADERS_AND_ALL_NON_INITRAMFS_BYTES_UNCHANGED")
    print("X360OS_EMBEDDED_KERNEL_SHA256",digest(candidate))
    print("CANDIDATE_CREATED",destination)
    print("REAL_XBOX_360_BOOT_UNTESTED")

if __name__=="__main__":
    assert len(sys.argv)==4,"usage: patch-embedded-kernel.py VERIFIED_vmlinux initrd-x360os.gz OUTPUT_vmlinux"
    replace(sys.argv[1],sys.argv[2],sys.argv[3])
