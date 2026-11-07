#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Build baseline static PowerPC32 big-endian BusyBox for the 64-bit Xenon Linux kernel.
# This avoids PPC64/glibc instruction compatibility observed during the first hardware test.
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
out="${OUT_DIR:-$repo/distro/out}"
work="${WORK_DIR:-$repo/distro/work}"
bb_version="1.37.0"
bb_src="$work/busybox-$bb_version"

for cmd in curl tar make python3 powerpc-linux-gnu-gcc powerpc-linux-gnu-readelf; do
    command -v "$cmd" >/dev/null || { echo "Install $cmd" >&2; exit 1; }
done
mkdir -p "$work" "$out"
if [[ ! -f "$bb_src/Makefile" ]]; then
    curl -fL --retry 3 -o "$work/busybox-$bb_version.tar.bz2" \
        "https://busybox.net/downloads/busybox-$bb_version.tar.bz2"
    tar -xjf "$work/busybox-$bb_version.tar.bz2" -C "$work"
fi
make -C "$bb_src" ARCH=powerpc CROSS_COMPILE=powerpc-linux-gnu- defconfig
python3 - "$bb_src/.config" <<'PY'
import pathlib, sys
p=pathlib.Path(sys.argv[1])
text=p.read_text()
text=text.replace("# CONFIG_STATIC is not set", "CONFIG_STATIC=y")
# Xenon can run 32-bit userspace; baseline PPC avoids requiring 64-bit or
# AltiVec/VSX instructions that may not exist or be usable on this console.
text=text.replace('CONFIG_EXTRA_CFLAGS=""', 'CONFIG_EXTRA_CFLAGS="-mcpu=powerpc -mno-altivec -mno-vsx"')
# BusyBox 1.37.0 has an upstream non-x86 SHA-NI compile regression:
# https://lists.busybox.net/pipermail/busybox/2024-September/090946.html
# The Xenon PPC64 CPU has no x86 SHA-NI; use portable SHA routines.
text=text.replace("CONFIG_SHA1_HWACCEL=y", "# CONFIG_SHA1_HWACCEL is not set")
text=text.replace("CONFIG_SHA256_HWACCEL=y", "# CONFIG_SHA256_HWACCEL is not set")
# Minimal initramfs does not need the legacy 'tc' networking applet.
# Its old CBQ API is absent from newer kernel headers.
text=text.replace("CONFIG_TC=y", "# CONFIG_TC is not set")
p.write_text(text)
PY
make -C "$bb_src" ARCH=powerpc CROSS_COMPILE=powerpc-linux-gnu- oldconfig </dev/null
make -C "$bb_src" ARCH=powerpc CROSS_COMPILE=powerpc-linux-gnu- -j "${JOBS:-2}"
test -s "$bb_src/busybox"
powerpc-linux-gnu-readelf -h "$bb_src/busybox" | grep -q 'Machine:.*PowerPC'
powerpc-linux-gnu-readelf -h "$bb_src/busybox" | grep -q 'Class:.*ELF32'
powerpc-linux-gnu-readelf -h "$bb_src/busybox" | grep -q 'Data:.*big endian'
if powerpc-linux-gnu-readelf -l "$bb_src/busybox" | grep -q 'INTERP'; then
    echo "BusyBox is dynamic; refusing to package without shared libraries" >&2
    exit 1
fi
python3 "$repo/distro/pack_initramfs.py" \
    --busybox "$bb_src/busybox" --init "$repo/distro/rootfs/init" \
    --output "$out/initramfs.cpio.gz"
(cd "$out" && sha256sum initramfs.cpio.gz > SHA256SUMS)
printf '%s\n' "Experimental X360Linux PowerPC32 big-endian userspace on a 64-bit Xenon kernel." \
    "Requires a separate, compatible Free60-patched Linux ELF32 kernel." \
    "The initramfs is a BusyBox shell, NOT a full Linux desktop." \
    "BusyBox copyright and license: https://busybox.net/license.html (GPL-2.0)." \
    > "$out/READ-ME-FIRST.txt"
