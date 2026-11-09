#!/usr/bin/env python3
"""Pack an isolated v6 USB candidate; does not publish or modify user's USB."""
import argparse
import hashlib
import shutil
import zipfile
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--v5-boot', type=Path, required=True)
    ap.add_argument('--v5-persistence', type=Path, required=True)
    ap.add_argument('--new-squashfs', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    for p in (args.v5_boot, args.v5_persistence, args.new_squashfs):
        assert p.is_file(), p
    if args.output.exists():
        raise SystemExit('Refusing to overwrite: %s' % args.output)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    readme = """X360OS v6.0 DEVELOPMENT BUILD - XBOX 360 RGH/JTAG
THIS VERSION HAS NOT YET BEEN BOOT-TESTED ON REAL XBOX HARDWARE.
1. Keep a backup of your known-working X360Linux v5 USB.
2. Prepare a different 8 GB+ FAT32 USB drive (formatting erases data).
3. Extract THIS ZIP to the USB drive root (not the unopened ZIP file).
4. Plug the drive into an RGH/JTAG Xbox 360 with XeLL.
5. Start via Eject. A successful boot should show the green X360OS home.
6. Use D-pad to navigate, A to open, X to toggle controller mouse mode.
7. Press F10 on a USB keyboard to switch to classic Ubuntu if the shell opens.

BROWSER NOTE: Firefox 3.6 in the old Ubuntu is obsolete; do not use passwords.
CONTROLLER NOTE: wired/USB xpad support still needs Xbox hardware validation.
NETWORK NOTE: NetworkManager is included; connectivity is not yet proven.
Do not use this as a verified production release. No NAND/HDD changes.
"""
    with zipfile.ZipFile(args.v5_boot, 'r') as v5, \
         zipfile.ZipFile(args.v5_persistence, 'r') as persist, \
         zipfile.ZipFile(args.output, 'w', allowZip64=True) as final:
        # Preserve ONLY the proven XeLL/Kboot/Casper boot path, not experimental ext4 entries.
        for name in ('kboot.conf','vmlinux'):
            with v5.open(name) as src, final.open(name, 'w', force_zip64=True) as dest:
                shutil.copyfileobj(src, dest, 4*1024*1024)
            print('Reused v5', name, flush=True)
        with args.new_squashfs.open('rb') as src:
            info = zipfile.ZipInfo('casper/filesystem.squashfs')
            info.compress_type = zipfile.ZIP_STORED
            with final.open(info, 'w', force_zip64=True) as dest:
                shutil.copyfileobj(src, dest, 4*1024*1024)
        print('Added v6 rootfs', flush=True)
        with persist.open('casper-rw') as src:
            info = zipfile.ZipInfo('casper-rw')
            info.compress_type = zipfile.ZIP_DEFLATED
            with final.open(info, 'w', force_zip64=True) as dest:
                shutil.copyfileobj(src, dest, 4*1024*1024)
        print('Included unused fresh v5 persistence image (NOT user data)', flush=True)
        final.writestr('READ-ME-FIRST.txt', readme, compress_type=zipfile.ZIP_DEFLATED)
    with zipfile.ZipFile(args.output) as final:
        assert final.testzip() is None
        assert set(final.namelist()) == {
            'kboot.conf','vmlinux','casper/filesystem.squashfs','casper-rw','READ-ME-FIRST.txt'
        }
        assert final.getinfo('casper-rw').file_size == 3 * 1024**3
    h = hashlib.sha256()
    with args.output.open('rb') as f:
        for chunk in iter(lambda: f.read(4*1024*1024), b''):
            h.update(chunk)
    print('DONE', args.output, 'bytes', args.output.stat().st_size, 'SHA256', h.hexdigest())
if __name__ == '__main__':
    main()
