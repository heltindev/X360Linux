#!/bin/bash
set -euo pipefail
work=/root/x360os-native-toolchain
mkdir -p "$work"
cd "$work"
if [ ! -s musl-1.2.5.tar.gz ]; then
 curl --fail --location --retry 2 --output musl-1.2.5.tar.gz https://musl.libc.org/releases/musl-1.2.5.tar.gz
fi
sha256sum musl-1.2.5.tar.gz
if [ ! -d musl-1.2.5 ]; then tar xf musl-1.2.5.tar.gz; fi
if [ ! -f "$work/sysroot/lib/libc.a" ]; then
 cd "$work/musl-1.2.5"
 AR=powerpc-linux-gnu-ar RANLIB=powerpc-linux-gnu-ranlib CC=powerpc-linux-gnu-gcc CFLAGS=-mlong-double-64 ./configure --target=powerpc-linux-musl --prefix="$work/sysroot" --disable-shared >"$work/musl-configure.log" 2>&1 || { tail -45 "$work/musl-configure.log"; exit 1; }
 make AR=powerpc-linux-gnu-ar RANLIB=powerpc-linux-gnu-ranlib -j4 >"$work/musl-build.log" 2>&1 || { tail -65 "$work/musl-build.log"; exit 1; }
 make AR=powerpc-linux-gnu-ar RANLIB=powerpc-linux-gnu-ranlib install >"$work/musl-install.log" 2>&1 || { tail -45 "$work/musl-install.log"; exit 1; }
fi
echo "TOOLCHAIN BUILD OK:"
find "$work/sysroot" -maxdepth 2 -name 'musl-gcc*' -o -name 'libc.a' | sort
cat > "$work/hello.c" <<'EOF'
#include <stdio.h>
#include <sys/utsname.h>
#include <unistd.h>
int main(void) {
 struct utsname u;
 if (uname(&u) != 0) return 2;
 printf("X360OS_PPC32_MUSL_OK machine=%s pid=%ld\n", u.machine, (long)getpid());
 return 0;
}
EOF
"$work/sysroot/bin/musl-gcc" -Os -static -o "$work/hello" "$work/hello.c"
file "$work/hello"
qemu-ppc-static "$work/hello"
powerpc-linux-gnu-readelf -l "$work/hello" | grep -E 'INTERP|LOAD' | head -4
echo "MUSL TOOLCHAIN SUCCESS"
