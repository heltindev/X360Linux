#!/usr/bin/env bash
set -euo pipefail
[ "$#" -eq 3 ] || { echo "Usage: build-v6.1-ppc.sh BASE-SQUASHFS PPC-PACKAGES OUTPUT-DIR"; exit 2; }
base="$(realpath "$1")"
pkgs="$(realpath "$2")"
out="$(realpath -m "$3")"
here="$(cd "$(dirname "$0")" && pwd)"
test -s "$base"
mkdir -p "$out"
test ! -e "$out/filesystem.squashfs" || { echo "Refusing overwrite" >&2; exit 1; }
tmp="$(mktemp -d -p /tmp x360os-games.XXXXXXXX)"
trap 'rm -rf "$tmp"' EXIT
echo "UNPACKING X360OS v6.0.2 ROOTFS..."
unsquashfs -d "$tmp/root" -no-progress -processors 4 "$base" >"$out/extract.log" 2>&1
root="$tmp/root"
grep -q '^X360OS 6.0.2-dev' "$root/etc/x360os-release"
grep -q '^CONFIG_JOYSTICK_XPAD=y' "$root/boot/config-2.6.36.2-xenon"
grep -q '^CONFIG_SND_XENON=y' "$root/boot/config-2.6.36.2-xenon"
grep -q '^CONFIG_XENON_ENET=y' "$root/boot/config-2.6.36.2-xenon"
grep -q '^# CONFIG_WIRELESS is not set' "$root/boot/config-2.6.36.2-xenon"
test -e "$root/usr/lib/libSDL-1.2.so.0"
test -e "$root/usr/bin/python2.6"
test -e "$root/usr/lib/xorg/modules/drivers/xenosfb_drv.so"
echo "INSTALLING known-era Ubuntu PPC32 packages from PC archives..."
for package in \
  libobparser21_3.4.11.1-1_powerpc.deb \
  libobrender21_3.4.11.1-1_powerpc.deb \
  openbox_3.4.11.1-1_powerpc.deb \
  libsdl-net1.2_1.2.7-2_powerpc.deb \
  libmikmod2_3.1.11-a-6ubuntu4.1_powerpc.deb \
  libsmpeg0_0.4.5+cvs20030824-2.2_powerpc.deb \
  libsdl-mixer1.2_1.2.8-6build1_powerpc.deb \
  chocolate-doom_1.3.0-1_powerpc.deb \
  prboom_2.5.0+dfsg1-5ubuntu1_powerpc.deb \
  freedoom_0.6.4-5_all.deb
do
 deb="$pkgs/$package"
 test -s "$deb" || { echo "Missing $package" >&2; exit 1; }
 arch="$(dpkg-deb -f "$deb" Architecture)"
 [ "$arch" = powerpc ] || [ "$arch" = all ] || { echo "Wrong architecture $arch" >&2; exit 1; }
 dpkg-deb -x "$deb" "$root"
 echo "OK $package"
done
test -x "$root/usr/bin/openbox"
test -x "$root/usr/games/chocolate-doom"
test -x "$root/usr/games/prboom"
test -s "$root/usr/share/games/doom/freedoom.wad"
python3 - "$root/usr/share/games/doom/freedoom.wad" <<'PY'
import sys
with open(sys.argv[1], 'rb') as f:
    assert f.read(4) == b'IWAD', 'Invalid Freedoom WAD'
PY
install -D -m 0644 "$here/home-stable.py" "$root/usr/share/x360os/home.py"
install -D -m 0644 "$here/controller-games.py" "$root/usr/share/x360os/controller.py"
install -D -m 0755 "$here/x360os-session-light" "$root/usr/bin/x360os-session"
install -D -m 0755 "$here/x360os-doom" "$root/usr/bin/x360os-doom"
install -D -m 0755 "$here/x360os-sound-check" "$root/usr/bin/x360os-sound-check"
install -D -m 0644 "$here/x360os-doom.desktop" "$root/usr/share/applications/x360os-doom.desktop"
install -D -m 0755 "$here/x360os-doom.desktop" "$root/etc/skel/Desktop/DOOM-Freedoom.desktop"
install -D -m 0644 "$here/v6.1.0-TESTING.md" "$root/usr/share/doc/x360os/README-v6.1.md"
python3 - "$root" <<'PY'
from pathlib import Path
import sys
root=Path(sys.argv[1])
script=root/'usr/bin/x360os-install-launcher'
txt=script.read_text()
assert txt.count('exit 0') == 1
txt=txt.replace('exit 0', '''if [ -d "$HOME/Desktop" ] && [ -r /usr/share/applications/x360os-doom.desktop ]; then
 cp /usr/share/applications/x360os-doom.desktop "$HOME/Desktop/DOOM-Freedoom.desktop" 2>/dev/null || :
 chmod 0755 "$HOME/Desktop/DOOM-Freedoom.desktop" 2>/dev/null || :
fi
exit 0''')
script.write_text(txt)
(root/'etc/x360os-release').write_text(
'X360OS 6.1.0-dev\n'
'base=Ubuntu_10.10_PowerPC32_Casper\n'
'kernel=UNCHANGED_from_X360Linux_v5\n'
'window_manager=Openbox_3.4.11.1_with_GNOME_fallback\n'
'game=PrBoom_2.5.0_with_FreeDOOM_0.6.4\n'
'other_game_engine=Chocolate_Doom_1.3_for_owned_IWAD\n'
'audio=ALSA_Xenon_compiled_hardware_unverified\n'
'network=Ethernet_and_DHCP_present_internal_WLAN_UNSUPPORTED\n'
'input=USB_xpad_builtin_controller_RF_unverified\n'
'hardware_test=NOT_DONE\n')
PY
echo "VERIFYING package architectures and shared-library loader..."
for exe in "$root/usr/bin/openbox" "$root/usr/games/prboom" "$root/usr/games/chocolate-doom"; do
 file "$exe" | grep -q 'ELF 32-bit MSB.*PowerPC'
 readelf -l "$exe" | grep -q '/lib/ld.so.1'
 echo "ELF OK $exe"
done
if command -v qemu-ppc-static >/dev/null; then
 for prog in usr/bin/openbox usr/games/prboom usr/games/chocolate-doom; do
  QEMU_LD_PREFIX="$root" timeout 15 qemu-ppc-static -L "$root" "$root/$prog" -version >"$out/$(basename "$prog").smoke.log" 2>&1 || :
  if grep -Eq 'error while loading shared libraries|cannot open shared object file' "$out/$(basename "$prog").smoke.log"; then
    cat "$out/$(basename "$prog").smoke.log"
    echo "STOP: missing runtime dependency" >&2
    exit 1
  fi
 done
fi
echo "BUILDING X360OS v6.1 GZIP SquashFS..."
mksquashfs "$root" "$out/filesystem.squashfs" -comp gzip -b 131072 -noappend -no-progress -processors 4 >"$out/squashfs-build.log" 2>&1
unsquashfs -s "$out/filesystem.squashfs" | grep -q 'Compression gzip'
unsquashfs -cat "$out/filesystem.squashfs" etc/x360os-release | grep -q 'X360OS 6.1.0-dev'
unsquashfs -cat "$out/filesystem.squashfs" usr/share/x360os/home.py | grep -q "'DOOM'"
sha256sum "$base" "$out/filesystem.squashfs" >"$out/IMAGE-SHA256SUMS.txt"
echo "SUCCESS: $out/filesystem.squashfs"
