#!/usr/bin/env bash
# X360OS shell smoke tests, host only. Physical RF/gamepad testing required.
set -euo pipefail
[ "$#" -eq 2 ] || { echo "Usage: test.sh V7.1-SQUASHFS V7.2-BUILD-OUTPUT" >&2; exit 2; }
base="$(realpath "$1")"
out="$(realpath "$2")"
s="$out/casper/filesystem.squashfs"
test -s "$base" && test -s "$s" && test -s "$out/vmlinux"
(cd "$out" && sha256sum -c SHA256SUMS.txt)
test ! -e "$out/casper-rw"
unsquashfs -s "$s" | grep -q 'Compression gzip'
echo "Checking Xenon Xorg driver and display configuration unchanged..."
for f in usr/lib/xorg/modules/drivers/xenosfb_drv.so etc/X11/xorg.conf etc/init/gdm.conf usr/bin/gnome-session; do
 b="$(unsquashfs -cat "$base" "$f" | sha256sum | cut -d ' ' -f 1)"
 n="$(unsquashfs -cat "$s" "$f" | sha256sum | cut -d ' ' -f 1)"
 [ "$b" = "$n" ] || { echo "STOP: original video path changed: $f" >&2; exit 1; }
 echo "UNCHANGED: $f"
done
unsquashfs -cat "$s" etc/x360os-release | grep -q '^X360OS 7.2.0-shell-dev'
unsquashfs -cat "$s" etc/gdm/custom.conf | grep -q '^DefaultSession=x360os$'
unsquashfs -cat "$s" etc/gdm/custom.conf | grep -q '^AutomaticLogin=ubuntu$'
unsquashfs -cat "$s" etc/skel/.dmrc | grep -q '^Session=x360os$'
unsquashfs -cat "$s" usr/share/xsessions/x360os.desktop | grep -q '^Exec=/usr/bin/x360os-session$'
unsquashfs -cat "$s" usr/bin/x360os-session | grep -q '^exec /usr/bin/gnome-session'
unsquashfs -cat "$s" usr/bin/x360os-input-start | grep -q 'controller.py'
unsquashfs -cat "$s" usr/share/x360os/controller.py | grep -q 'self.mouse = True'
unsquashfs -cat "$s" usr/share/x360os/controller.py | grep -q 'XTestFakeRelativeMotionEvent'
unsquashfs -cat "$s" usr/share/x360os/controller.py | grep -q "struct.unpack(endian + 'IIHHi', data)"
unsquashfs -cat "$s" usr/share/x360os/home.py | grep -q 'X360OS'
unsquashfs -cat "$s" etc/rc.local | grep -q 'x360os-input-diagnose'
! unsquashfs -l "$s" | grep -q 'squashfs-root/usr/bin/x360os-ui$'
grep -q 'nopersistent' "$out/kboot.conf"
grep -q 'X360OS_GTK2_XTEST_CONTROLLER_IMPORT_OK' "$out/gtk-input-smoke.log"
echo "HOST TESTS PASS: original Xenon graphics preserved; X360OS default; XTest gamepad mouse active in source."
echo "PHYSICAL CONSOLE INPUT/VIDEO: NOT VERIFIED FOR v7.2."
