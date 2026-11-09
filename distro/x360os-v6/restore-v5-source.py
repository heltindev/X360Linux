#!/usr/bin/env python3
"""Extract only the proven v5 direct-Casper boot inputs for local v6 builds."""
from pathlib import Path
import argparse
import hashlib
import shutil
import zipfile
p = argparse.ArgumentParser()
p.add_argument('--zip', dest='archive', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
args=p.parse_args()
names=['kboot.conf','vmlinux','casper/filesystem.squashfs']
assert args.archive.is_file(), args.archive
with zipfile.ZipFile(args.archive) as z:
    assert set(names).issubset(set(z.namelist()))
    for name in names:
        target=args.output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise SystemExit('Source exists; refusing overwrite: '+str(target))
        h=hashlib.sha256()
        with z.open(name) as src, target.open('wb') as dest:
            for chunk in iter(lambda:src.read(4*1024*1024),b''):
                dest.write(chunk);h.update(chunk)
        assert target.stat().st_size==z.getinfo(name).file_size
        print('RESTORED',name,'BYTES',target.stat().st_size,'SHA256',h.hexdigest(),flush=True)
print('SOURCE_READY',args.output,flush=True)
