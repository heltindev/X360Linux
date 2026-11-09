#!/bin/bash
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
out="/root/x360os-native-toolchain/x360os-v8-ui"
compiler="/root/x360os-native-toolchain/sysroot/bin/musl-gcc"
test -x "$compiler"
test -s "$here/x360os-ui.c"
echo "Compiling X360OS 8 native Xenos tiled framebuffer (static PPC32 BE)..."
"$compiler" -O2 -std=c11 -Wall -Wextra -Wno-unused-function \
 -mcpu=powerpc -mno-altivec -mno-vsx -mlong-double-64 -static \
 -idirafter /usr/powerpc-linux-gnu/include -idirafter /usr/include \
 -I "$here/../desktop" -o "$out" "$here/x360os-ui.c" -lm
file "$out"
powerpc-linux-gnu-readelf -l "$out" | grep -E 'LOAD|INTERP' | head -8
echo "Comparing the exact rendered RGB picture for linear vs Xbox 360 tile layout..."
for size in 800x480 1280x720; do
 width="$(echo "$size" | cut -dx -f1)"; height="$(echo "$size" | cut -dx -f2)"
 qemu-ppc-static "$out" --render-test "$width" "$height" "/root/x360os-native-toolchain/v8-linear-$size.ppm"
 qemu-ppc-static "$out" --render-test-xenos "$width" "$height" "/root/x360os-native-toolchain/v8-xenos-$size.ppm"
 cmp "/root/x360os-native-toolchain/v8-linear-$size.ppm" "/root/x360os-native-toolchain/v8-xenos-$size.ppm"
 echo "PASS: Xenos 32x32 tiled -> linear RGB output matches at $size"
done
echo "X360OS v8 native framebuffer UI compilation and tile tests passed"
