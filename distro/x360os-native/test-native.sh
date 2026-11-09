#!/bin/bash
set -euo pipefail
[ "$#" -eq 1 ] || { echo "Usage: test-native.sh OUTPUT_DIR"; exit 2; }
out="$(realpath "$1")"
squash="$out/casper/filesystem.squashfs"
test -s "$squash" && test -s "$out/vmlinux" && test -s "$out/kboot.conf"
echo "X360OS native image: validating directory, SquashFS and version..."
( cd "$out"; sha256sum -c SHA256SUMS.txt )
unsquashfs -s "$squash" | grep -q 'Compression gzip'
test "$(unsquashfs -cat "$squash" etc/os-release | grep -c '^ID=x360os$')" -eq 1
unsquashfs -cat "$squash" sbin/init | grep -q 'X360OS Native v7'
unsquashfs -cat "$squash" etc/network/udhcpc-script | grep -q 'bound|renew'
grep -q 'boot=casper nopersistent' "$out/kboot.conf"
if test -e "$out/casper-rw"; then echo "ERROR: Ubuntu persistence overlay reintroduced!" >&2; exit 1; fi
items="$(unsquashfs -l "$squash")"
if echo "$items" | grep -Eq 'squashfs-root/(etc/apt|var/lib/dpkg|usr/bin/(gnome-session|Xorg|python2.6|firefox)|usr/lib/xorg)/'; then
 echo "ERROR: Ubuntu programs found in native rootfs" >&2; exit 1
fi
tmp="$(mktemp -d -p /root x360os-native-test.XXXXXXXX)"
trap 'rm -rf "$tmp"' EXIT
for file in bin/busybox usr/bin/x360os-ui lib/modules/2.6.36.2-xenon/kernel/drivers/input/evdev.ko lib/modules/2.6.36.2-xenon/kernel/drivers/input/joydev.ko; do
 mkdir -p "$tmp/$(dirname "$file")"
 unsquashfs -cat "$squash" "$file" >"$tmp/$file"
 test -s "$tmp/$file"
done
for exe in "$tmp/bin/busybox" "$tmp/usr/bin/x360os-ui"; do
 file "$exe" | grep -q 'ELF 32-bit MSB.*statically linked'
 ! powerpc-linux-gnu-readelf -l "$exe" | grep -q INTERP
done
for mod in "$tmp/lib/modules/2.6.36.2-xenon/kernel/drivers/input/"*.ko; do
 file "$mod" | grep -q 'ELF 64-bit MSB'
done
chmod 0755 "$tmp/bin/busybox" "$tmp/usr/bin/x360os-ui"
qemu-ppc-static "$tmp/bin/busybox" echo X360OS_POWERPC32_USERSYSTEM_OK
qemu-ppc-static "$tmp/usr/bin/x360os-ui" --render-test 800 480 "$tmp/x360os-preview.ppm"
test -s "$tmp/x360os-preview.ppm"
echo "HOST TEST PASS: clean Ubuntu-free X360OS PPC32 musl/BusyBox rootfs"
echo "REAL XBOX 360 BOOT STILL UNVERIFIED — NO NAND OR E: MODIFIED"
