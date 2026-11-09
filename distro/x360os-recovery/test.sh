#!/bin/bash
# Host-only checks: do not claim real Xbox boot success.
set -euo pipefail
[ "$#" -eq 2 ] || { echo "Usage: test.sh verified-v5-squashfs recovery-output"; exit 2; }
base="$(realpath "$1")"
out="$(realpath "$2")"
sq="$out/casper/filesystem.squashfs"
test -s "$base" && test -s "$sq"
( cd "$out" && sha256sum -c SHA256SUMS.txt )
test ! -e "$out/casper-rw"
unsquashfs -s "$sq" | grep -q 'Compression gzip'
for file in usr/lib/xorg/modules/drivers/xenosfb_drv.so etc/X11/xorg.conf etc/init/gdm.conf usr/bin/gnome-session; do
 tmp="$(mktemp -p /root)"
 oldsum="$(unsquashfs -cat "$base" "$file" | sha256sum | cut -d' ' -f1)"
 newsum="$(unsquashfs -cat "$sq" "$file" | sha256sum | cut -d' ' -f1)"
 rm -f "$tmp"
 [ "$oldsum" = "$newsum" ] || { echo "Video compatibility file changed: $file" >&2; exit 1; }
 echo "UNCHANGED $file"
done
unsquashfs -cat "$sq" etc/gdm/custom.conf | grep -q '^DefaultSession=gnome.desktop'
unsquashfs -cat "$sq" etc/gdm/custom.conf | grep -q '^AutomaticLogin=ubuntu'
unsquashfs -cat "$sq" etc/xdg/autostart/x360os-autostart.desktop | grep -q '^Exec=/usr/bin/x360os-safe-start$'
unsquashfs -cat "$sq" usr/bin/x360os-safe-start | grep -q 'GNOME desktop'
unsquashfs -cat "$sq" etc/x360os-release | grep -q '7.1.0-recovery-dev'
if unsquashfs -l "$sq" | grep -qE '(usr/bin/x360os-ui|usr/bin/x360desk)$'; then
 echo "FAILED: direct framebuffer code not disabled" >&2; exit 1
fi
grep -q 'nopersistent' "$out/kboot.conf"
grep -q 'quiet splash' "$out/kboot.conf"
grep -q 'PYGTK2_IMPORT_OK' "$out/pygtk-smoke.log"
echo "PASS HOST: kernel/graphics original, GNOME fallback, X360OS autostart, no raw framebuffer."
echo "NOT VALIDATED: real Xbox 360 XeLL boot/display/input/audio/internet."
