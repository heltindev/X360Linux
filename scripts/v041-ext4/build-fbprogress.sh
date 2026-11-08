#!/usr/bin/env bash
set -euo pipefail
p="$(cd "$(dirname "$0")" && pwd)"
powerpc-linux-gnu-gcc -Os -ffreestanding -nostdlib -static -fno-stack-protector -fno-pie -no-pie -Wl,-e,_start -Wl,--build-id=none -o "$p/fbprogress" "$p/fbprogress.c" -lgcc
file "$p/fbprogress"
readelf -l "$p/fbprogress" | grep -E 'INTERP|LOAD'
qemu-ppc-static "$p/fbprogress" 35
echo FB_PROGRESS_STATIC_PPC_EXIT_SUCCESS
