#!/usr/bin/env python3
"""Download known-era Ubuntu 10.10 powerpc/all packages to a local staging directory.

Run on the developer PC only, never on the Xbox 360. No packages are installed
in the PC OS. See build-v6.1-ppc.sh for offline unpacking and verification.
"""
from pathlib import Path
from urllib.request import urlretrieve
import argparse

ARCHIVE = "https://old-releases.ubuntu.com/ubuntu/pool/"
PACKAGES = {
  "chocolate-doom_1.3.0-1_powerpc.deb": "multiverse/c/chocolate-doom/",
  "freedoom_0.6.4-5_all.deb": "universe/f/freedoom/",
  "prboom_2.5.0+dfsg1-5ubuntu1_powerpc.deb": "universe/p/prboom/",
  "openbox_3.4.11.1-1_powerpc.deb": "universe/o/openbox/",
  "libobparser21_3.4.11.1-1_powerpc.deb": "universe/o/openbox/",
  "libobrender21_3.4.11.1-1_powerpc.deb": "universe/o/openbox/",
  "libsdl-net1.2_1.2.7-2_powerpc.deb": "universe/s/sdl-net1.2/",
  "libsdl-mixer1.2_1.2.8-6build1_powerpc.deb": "universe/s/sdl-mixer1.2/",
  "libsmpeg0_0.4.5+cvs20030824-2.2_powerpc.deb": "universe/s/smpeg/",
  "libmikmod2_3.1.11-a-6ubuntu4.1_powerpc.deb": "main/libm/libmikmod/",
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    args.destination.mkdir(parents=True, exist_ok=True)
    for name, subdir in PACKAGES.items():
        dst = args.destination / name
        if dst.exists() and dst.stat().st_size:
            print("Already downloaded:", name, flush=True)
            continue
        temp = dst.with_name(dst.name + ".part")
        if temp.exists():
            raise SystemExit("Interrupted .part file exists; examine first: " + str(temp))
        print("Downloading", name, flush=True)
        urlretrieve(ARCHIVE + subdir + name, str(temp))
        if temp.stat().st_size < 10000:
            raise SystemExit("Archive download suspiciously small: " + str(temp))
        temp.rename(dst)
        print("OK", name, flush=True)

if __name__ == "__main__":
    main()
