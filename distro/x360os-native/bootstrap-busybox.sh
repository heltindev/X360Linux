#!/bin/bash
set -euo pipefail
work=/root/x360os-native-toolchain
src=/root/x360os-native-work
mkdir -p "$src"
cd "$src"
if [ ! -s busybox-1.36.1.tar.bz2 ]; then curl --fail --location --retry 2 -o busybox-1.36.1.tar.bz2 https://busybox.net/downloads/busybox-1.36.1.tar.bz2; fi
sha256sum busybox-1.36.1.tar.bz2
if [ ! -d busybox-1.36.1 ]; then tar xf busybox-1.36.1.tar.bz2; fi
cd busybox-1.36.1
MUSL="$work/sysroot/bin/musl-gcc"
test -x "$MUSL"
if [ ! -f .config ]; then
 make ARCH=powerpc CROSS_COMPILE=powerpc-linux-gnu- defconfig >"$src/busybox-config.log" 2>&1
 python3 - <<'PY'
from pathlib import Path
p=Path(".config")
s=p.read_text()
assert "# CONFIG_STATIC is not set" in s
s=s.replace("# CONFIG_STATIC is not set","CONFIG_STATIC=y")
for name in ["MDEV","UDHCPC","IFCONFIG","MOUNT","SH","ASH","GREP","TEE","READLINK","UNAME","INSmod".upper()]:
 if f"CONFIG_{name}=y" not in s:
  if f"# CONFIG_{name} is not set" in s:
   s=s.replace(f"# CONFIG_{name} is not set",f"CONFIG_{name}=y")
p.write_text(s)
PY
fi
# Old CBQ Linux tc API is absent from newer host kernel headers; we do not use tc.
sed -i 's/^CONFIG_TC=y$/# CONFIG_TC is not set/' .config
echo "BUILDING native PowerPC static BusyBox..."
make -j4 ARCH=powerpc CROSS_COMPILE=powerpc-linux-gnu- CC="$MUSL" EXTRA_CFLAGS="-mlong-double-64 -idirafter /usr/powerpc-linux-gnu/include -idirafter /usr/include" >"$src/busybox-build.log" 2>&1 || { tail -70 "$src/busybox-build.log"; exit 1; }
file busybox
qemu-ppc-static ./busybox | head -6 || :
qemu-ppc-static ./busybox --list | grep -E '^(sh|mdev|udhcpc|mount|ifconfig|insmod|uname|grep|route)$'
echo "BUSYBOX PPC MUSL OK"
