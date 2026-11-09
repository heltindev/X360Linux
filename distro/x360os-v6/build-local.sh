#!/usr/bin/env bash
# Build a PC-only Xbox 360 X360OS v6 candidate from the v5 hardware-tested USB image.
# Never changes the USB, NAND, internal Xbox HDD, or verified kernel.
set -euo pipefail
if [ "$#" -ne 2 ]; then
  echo "Usage: bash build-local.sh BOOT-DIRETO-DIR RELEASE-V6-DIR" >&2
  exit 2
fi
base="$(realpath "$1")"
out="$(realpath -m "$2")"
src="$base/casper/filesystem.squashfs"
here="$(cd "$(dirname "$0")" && pwd)"
test -s "$src"
test -s "$base/vmlinux"
test -s "$base/kboot.conf"
for x in unsquashfs mksquashfs python3; do command -v "$x" >/dev/null; done
mkdir -p "$out"
if [ -e "$out/filesystem.squashfs" ]; then
  echo "Refusing to overwrite an existing v6 image: $out/filesystem.squashfs" >&2
  exit 1
fi
echo "SOURCE: $src"
echo "VERSION: X360OS 6.0.2-dev"
echo "WORKSTATION BUILD ONLY; NOT VERIFIED ON THE XBOX"
unsquashfs -s "$src" | grep -q 'Compression gzip'
tmp="$(mktemp -d -p /tmp x360os-v6.XXXXXXXX)"
trap 'rm -rf "$tmp"' EXIT
echo "EXTRACTING ORIGINAL UBUNTU ROOTFILESYSTEM..."
unsquashfs -d "$tmp/root" -no-progress -processors 4 "$src" >"$out/extract.log" 2>&1
root="$tmp/root"
test -x "$root/usr/bin/python2.6"
test -x "$root/usr/bin/gnome-session"
test -f "$root/usr/lib/xorg/modules/drivers/xenosfb_drv.so"
test -e "$root/usr/bin/firefox"
test -d "$root/usr/lib/python2.6/dist-packages"
test -e "$root/usr/lib/libXtst.so.6"
# No apt-get on the end-user console: use existing GTK2, Python2, X11 and Firefox.
install -D -m 0644 "$here/home.py" "$root/usr/share/x360os/home.py"
install -D -m 0644 "$here/controller.py" "$root/usr/share/x360os/controller.py"
install -D -m 0755 "$here/x360os-session" "$root/usr/bin/x360os-session"
install -D -m 0644 "$here/x360os.desktop" "$root/usr/share/xsessions/x360os.desktop"
# 2010 GDM can ignore DefaultSession or use an old persistent user preference.
# GNOME XDG autostart also starts the home screen on such systems.
install -D -m 0755 "$here/x360os-start-gnome" "$root/usr/bin/x360os-start-gnome"
install -D -m 0755 "$here/x360os-input-start" "$root/usr/bin/x360os-input-start"
install -D -m 0644 "$here/x360os-autostart.desktop" "$root/etc/xdg/autostart/x360os.desktop"
install -D -m 0644 "$here/probe.py" "$root/usr/share/x360os/probe.py"
install -D -m 0755 "$here/x360os-toggle" "$root/usr/bin/x360os-toggle"
install -D -m 0755 "$here/x360os-install-launcher" "$root/usr/bin/x360os-install-launcher"
install -D -m 0644 "$here/x360os-home.desktop" "$root/usr/share/applications/x360os-home.desktop"
install -D -m 0755 "$here/x360os-home.desktop" "$root/etc/skel/Desktop/X360OS.desktop"
install -D -m 0644 "$here/99-x360os-input.rules" "$root/etc/udev/rules.d/99-x360os-input.rules"
# Do not install a modern .ko: xpad and xenon Ethernet are built into 2.6.36.2.
test -s "$root/lib/modules/2.6.36.2-xenon/kernel/drivers/input/joydev.ko"
test -s "$root/lib/modules/2.6.36.2-xenon/kernel/drivers/input/evdev.ko"
grep -q '^CONFIG_JOYSTICK_XPAD=y$' "$root/boot/config-2.6.36.2-xenon"
grep -q '^CONFIG_XENON_ENET=y$' "$root/boot/config-2.6.36.2-xenon"
grep -q '^# CONFIG_WIRELESS is not set$' "$root/boot/config-2.6.36.2-xenon"
python3 - "$root" <<'PY'
from pathlib import Path
import sys
root=Path(sys.argv[1])
gdm=root/'etc/gdm/custom.conf'
txt=gdm.read_text()
assert '[daemon]' in txt and 'AutomaticLogin=ubuntu' in txt
assert 'DefaultSession=gnome.desktop' in txt, 'Unexpected GDM baseline; refusing patch'
gdm.write_text(txt.replace('DefaultSession=gnome.desktop','DefaultSession=x360os'))
# Load the existing matching joydev/evdev .ko modules as root at boot.
modules=root/'etc/modules'
modtxt=modules.read_text()
for module in ('joydev', 'evdev'):
    if module not in [line.strip() for line in modtxt.splitlines()]:
        modtxt += '\n' + module + '\n'
modules.write_text(modtxt)
# rc.local provides a second boot-stage attempt if old module-init-tools startup fails.
rc=root/'etc/rc.local'
rctxt=rc.read_text()
assert rctxt.rstrip().endswith('exit 0'), 'Unexpected rc.local: refusing patch'
rctxt=rctxt.replace('\nexit 0', '''\n# X360OS: load the ORIGINAL 2.6.36.2 Xenon input modules as root.
/sbin/modprobe joydev >/dev/null 2>&1 || :
/sbin/modprobe evdev >/dev/null 2>&1 || :
exit 0''')
rc.write_text(rctxt)
(root/'etc/x360os-release').write_text(
    'X360OS 6.0.2-dev\n'
    'base=Ubuntu_10.10_PowerPC32_Casper\n'
    'kernel=UNCHANGED_from_X360Linux_v5\n'
    'ui=PyGTK2_10-foot_screen\n'
    'input=xpad_builtin_plus_root_autoload_joydev_evdev_XTest\n'
    'network=NetworkManager_present_internal_Marvell_WiFi_driver_missing\n'
    'browser=legacy_Firefox_3.6_unsafe_for_sensitive_accounts\n'
    'hardware_test=NOT_DONE\n')
PY
echo "BUILDING COMPATIBLE GZIP SQUASHFS..."
mksquashfs "$root" "$out/filesystem.squashfs" \
  -comp gzip -b 131072 -noappend -no-progress -processors 4 \
  > "$out/squashfs-build.log" 2>&1
unsquashfs -s "$out/filesystem.squashfs" | grep -q 'Compression gzip'
unsquashfs -cat "$out/filesystem.squashfs" etc/gdm/custom.conf | grep -q 'DefaultSession=x360os'
unsquashfs -cat "$out/filesystem.squashfs" etc/xdg/autostart/x360os.desktop | grep -q 'x360os-start-gnome'
unsquashfs -cat "$out/filesystem.squashfs" usr/bin/x360os-input-start | grep -q 'modprobe'
unsquashfs -cat "$out/filesystem.squashfs" etc/modules | grep -q '^joydev$'
unsquashfs -cat "$out/filesystem.squashfs" etc/modules | grep -q '^evdev$'
unsquashfs -cat "$out/filesystem.squashfs" etc/rc.local | grep -q 'modprobe joydev'
unsquashfs -cat "$out/filesystem.squashfs" usr/share/applications/x360os-home.desktop | grep -q 'x360os-toggle'
unsquashfs -cat "$out/filesystem.squashfs" usr/bin/x360os-toggle | grep -q 'SIGUSR1' || unsquashfs -cat "$out/filesystem.squashfs" usr/bin/x360os-toggle | grep -q 'USR1'
unsquashfs -cat "$out/filesystem.squashfs" usr/share/x360os/probe.py | grep -q 'XBOX_360_INTERNAL_WIFI_DETECTED'
unsquashfs -cat "$out/filesystem.squashfs" etc/x360os-release | grep -q 'hardware_test=NOT_DONE'
unsquashfs -cat "$out/filesystem.squashfs" usr/share/x360os/controller.py | grep -q 'class Mapper'
sha256sum "$src" "$out/filesystem.squashfs" "$base/vmlinux" > "$out/IMAGE-SHA256SUMS.txt"
echo "SUCCESS: $out/filesystem.squashfs"
echo "NEXT: package a separate development ZIP, test on a spare USB, retain v5 recovery."
