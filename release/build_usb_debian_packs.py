#!/usr/bin/env python3
"""Create XeLL USB packs with Debian inside a mounted ISO.

No Xbox partitions are written. The ZIP is extracted to a normal FAT32 USB
drive by the user; Linux boots Debian from X360Linux/X360Linux.iso.
"""
import argparse
import gzip
import hashlib
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

MARKER=b"X360LINUX-USB-ROOT-V1\n"
def digest(path):
    h=hashlib.sha256()
    with open(path,"rb") as fp:
        for blob in iter(lambda:fp.read(1048576),b""): h.update(blob)
    return h.hexdigest()
def is_powerpc32(path):
    with open(path,"rb") as fp: h=fp.read(52)
    return h[:6]==b"\x7fELF\x01\x02" and h[18:20]==b"\x00\x14"

def main():
    a=argparse.ArgumentParser()
    for key in ("old-rgh","old-freemyxe","kernel","dtb","launcher",
                "initramfs","userdata","iso","output-dir"):
        a.add_argument("--"+key,type=Path,required=True)
    a.add_argument("--tag",default="v0.3.0-alpha")
    args=a.parse_args()
    paths={key:getattr(args,key.replace("-","_")) for key in
           ("old-rgh","old-freemyxe","kernel","dtb","launcher",
            "initramfs","userdata","iso")}
    for name,p in paths.items():
        if not p.is_file() or p.stat().st_size<64:
            a.error("Missing: "+name)
    if not is_powerpc32(args.kernel) or not is_powerpc32(args.launcher):
        a.error("Expected ELF32 big-endian PowerPC Xenon boot files")
    with args.dtb.open("rb") as f:
        if f.read(4)!=b"\xd0\x0d\xfe\xed":a.error("Invalid Xenon DTB")
    with args.userdata.open("rb") as f:
        f.seek(1080)
        if f.read(2)!=b"\x53\xef":a.error("Invalid ext4 USB data image")
    if args.userdata.stat().st_size != 512 * 1024 * 1024:
        a.error("Expected a 512 MiB ext4 USB data image")
    with args.iso.open("rb") as f:
        f.seek(32769)
        if f.read(5)!=b"CD001":a.error("ISO9660 signature missing")
    init=gzip.decompress(args.initramfs.read_bytes())
    if b"bin/x360desk" in init or b"X360LINUX-USB-ROOT-V1" not in init:
        a.error("Initramfs contains the old GUI or lacks Debian USB boot marker")
    out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    iso_name="X360Linux.iso"
    iso_path=f"X360Linux/{iso_name}"
    # Copy ISO without holding the whole 768 MiB filesystem in RAM.
    import shutil
    shutil.copyfile(args.iso,out/iso_name)
    changes={
        "xenon.elf":args.launcher,
        "X360Linux/vmlinux":args.kernel,
        "X360Linux/xenon.dtb":args.dtb,
        "X360Linux/initramfs.cpio.gz":args.initramfs,
    }
    text=(
        f"X360Linux {args.tag} - USB Debian PowerPC alpha\n"
        "==============================================\n"
        "Debian is inside X360Linux/X360Linux.iso.\n"
        "1. Back up your USB drive. It needs at least 2 GB available, FAT32.\n"
        "2. Extract the ZIP directly to the USB root (no outer ZIP folder).\n"
        "   Keep xenon.elf at the root and all system files in X360Linux/.\n"
        "3. Boot your existing XeLL. X360Boot starts the Xenon kernel.\n"
        "4. Linux mounts the ISO automatically and saves writes in USB-DATA.ext4.\n"
        "5. Debian shows its release information and opens the shell automatically.\n"
        "   If it opens recovery, photograph the X360Linux USB error.\n"
        "6. Shut down cleanly before removing the drive.\n\n"
        "If XeLL stops at Requesting DHCP, unplug Ethernet and start XeLL again.\n"
        "After Debian appears, reconnect Ethernet; DHCP retries in the background.\n"
        "Keep both the ISO and USB-DATA.ext4 in X360Linux/.\n"
        "NO Xbox HDD writes, NAND flash, formatting or game/save changes.\n"
        "https://github.com/heltindev/X360Linux\n"
    )
    for flavour,origin in (("RGH-USB",args.old_rgh),
                           ("ABadAvatar-FreeMyXe-USB",args.old_freemyxe)):
        result=out/f"X360Linux-{args.tag}-{flavour}.zip"
        with ZipFile(origin) as old:
            assert old.testzip() is None
            info=[x for x in old.infolist() if not x.is_dir() and
                  not x.filename.endswith(".iso") and
                  not x.filename.startswith("X360MEDIA/") and
                  x.filename not in ("X360Linux/system.ext4","X360Linux/USB-DATA.ext4","X360Linux/USB-ROOT.ID",
                                     "READ-ME-FIRST.txt","X360Linux/READ-ME-FIRST.txt")]
            names={x.filename for x in info}
            if not {"xenon.elf","X360Linux/vmlinux","X360Linux/xenon.dtb",
                    "X360Linux/initramfs.cpio.gz"}.issubset(names):
                a.error("Missing boot files from previous "+flavour)
            xell=(old.read("BadUpdatePayload/xell-2f.bin") if
                  "BadUpdatePayload/xell-2f.bin" in names else None)
            with ZipFile(result,"w",compression=ZIP_DEFLATED,compresslevel=6,
                         allowZip64=True) as dst:
                for item in info:
                    name=item.filename
                    if name in changes: dst.write(changes[name],name)
                    else:dst.writestr(item,old.read(name))
                prefix=(
                    "FreeMyXe: keep your existing working exploit files.\n"
                    "Back up your old xell-2f.bin; merge BadUpdatePayload.\n"
                    "This ZIP cannot exploit or unlock a stock Xbox.\n\n"
                ) if xell is not None else ""
                dst.writestr("X360Linux/READ-ME-FIRST.txt",prefix+text)
                dst.writestr("X360Linux/USB-ROOT.ID",MARKER)
                dst.write(args.userdata,"X360Linux/USB-DATA.ext4")
                dst.write(args.iso,iso_path)
        with ZipFile(result) as verify:
            assert verify.testzip() is None
            assert verify.read("X360Linux/USB-ROOT.ID")==MARKER
            if xell is not None:
                assert verify.read("BadUpdatePayload/xell-2f.bin")==xell
            assert "X360Linux/USB-DATA.ext4" in verify.namelist()
            assert "X360Linux/system.ext4" not in verify.namelist()
            assert iso_path in verify.namelist()
            for name,p in changes.items():
                assert hashlib.sha256(verify.read(name)).hexdigest()==digest(p)
        print("VALIDATED_USB_PACK",result.name,result.stat().st_size,digest(result),flush=True)
    print("VALIDATED_ISO",iso_name,(out/iso_name).stat().st_size,digest(out/iso_name),flush=True)
if __name__=="__main__":
    main()
