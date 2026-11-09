#!/bin/bash
# Compile X360OS framebuffer UI for PowerPC32 big-endian, no X11.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
headers="$here/../desktop"
compiler=/root/x360os-native-toolchain/sysroot/bin/musl-gcc
output=/root/x360os-native-toolchain/x360os-ui
test -x "$compiler"
test -s "$here/x360os-ui.c"
"$compiler" -Os -std=c11 -Wall -Wextra -Wno-unused-function \
 -mcpu=powerpc -mno-altivec -mno-vsx -mlong-double-64 -static \
 -idirafter /usr/powerpc-linux-gnu/include -idirafter /usr/include \
 -I "$headers" -o "$output" "$here/x360os-ui.c" -lm
file "$output"
qemu-ppc-static "$output" --render-test 800 480 /root/x360os-native-toolchain/ui-smoke.ppm
echo "X360OS native framebuffer build and render test passed."
