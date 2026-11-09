#!/bin/bash
# X360OS Recovery v7.1: preserve original working Xenon video + GDM Ubuntu runtime.
set -euo pipefail
[ "$#" -eq 3 ] || { echo "Usage: build.sh VERIFIED-V5-SQUASHFS VERIFIED-V5-VMLINUX EMPTY-OUTPUT" >&2; exit 2; }
base="$(realpath "$1")"
kernel="$(realpath "$2")"
out="$(realpath -m "$3")"
here="$(cd "$(dirname "$0")" && pwd)"
old="$here/../x360os-v6"
test -s "$base" && test -s "$kernel"
test -f "$old/home-stable.py"
expected="b8aa8eef938275ed5f037b884592283f561ac46b283edf4cdb1200bf2d39cec8"
[ "$(sha256sum "$kernel" | cut -d' ' -f1)" = "$expected" ] || { echo "STOP: Xenon kernel mismatch" >&2; exit 1; }
[ ! -e "$out" ] || { echo "STOP: output already exists; will not overwrite" >&2; exit 1; }
mkdir -p "$out"
tmp="$(mktemp -d -p /root x360os-recovery.XXXXXXXX)"
trap 'rm -rf "$tmp"' EXIT
root="$tmp/root"
echo "RESTORING original working Ubuntu Xenon Xorg/GDM graphics (COMPATIBILITY ONLY)..."
unsquashfs -d "$root" -no-progress -processors 4 "$base" >"$out/extract.log" 2>&1
# Essential real-console components must be present. Do not edit Xorg modules.
for f in usr/bin/python2.6 usr/sbin/gdm usr/lib/xorg/modules/drivers/xenosfb_drv.so etc/gdm/custom.conf etc/X11/xorg.conf usr/bin/gnome-session; do
 test -e "$root/$f" || { echo "STOP: missing previously working component $f" >&2; exit 1; }
done
grep -q '^AutomaticLoginEnable=true' "$root/etc/gdm/custom.conf"
grep -q '^AutomaticLogin=ubuntu' "$root/etc/gdm/custom.conf"
grep -q '^DefaultSession=gnome.desktop' "$root/etc/gdm/custom.conf"
test -r "$root/usr/lib/libgtk-x11-2.0.so.0"
echo "INSTALLING X360OS menu on known working X11 stack (no raw framebuffer)..."
install -D -m 0755 "$here/x360os-safe-start" "$root/usr/bin/x360os-safe-start"
install -D -m 0644 "$here/x360os-autostart.desktop" "$root/etc/xdg/autostart/x360os-autostart.desktop"
install -D -m 0644 "$old/home-stable.py" "$root/usr/share/x360os/home.py"
install -D -m 0644 "$old/controller-games.py" "$root/usr/share/x360os/controller.py"
install -D -m 0644 "$old/probe.py" "$root/usr/share/x360os/probe.py"
install -D -m 0755 "$old/x360os-input-start" "$root/usr/bin/x360os-input-start"
install -D -m 0755 "$old/x360os-toggle" "$root/usr/bin/x360os-toggle"
install -D -m 0755 "$old/x360os-install-launcher" "$root/usr/bin/x360os-install-launcher"
install -D -m 0644 "$old/x360os-home.desktop" "$root/usr/share/applications/x360os-home.desktop"
# Only load the v5 built-for-Xenon kernel modules, as root; no network wait.
python3 - "$root" <<'PY'
from pathlib import Path
import sys
r=Path(sys.argv[1])
home=r/'usr/share/x360os/home.py'
s=home.read_text(encoding='utf-8')
changes={
    'v6 • POWERPC':'v7.1 • XENON PPC',
    "'Ubuntu programs'":"'X360OS programs'",
    "'Classic Ubuntu mode'":"'Recovery desktop'",
    "'Ubuntu Applications'":"'X360OS Applications'",
    "'%s is unavailable in this Ubuntu image.'":"'Program unavailable in recovery mode: %s'",
    "('DOOM', 'Play the free Freedoom campaign', ['/usr/bin/x360os-doom']),":"('Terminal', 'Linux system tools', ['gnome-terminal']),",
    "('DOOM / Freedoom', ['/usr/bin/x360os-doom']),":"('System Monitor', ['gnome-system-monitor']),",
}
for old,new in changes.items():
    assert old in s, 'Missing expected UI source: '+old
    s=s.replace(old,new)
home.write_text(s,encoding='utf-8')
rc=r/'etc/rc.local'
src=rc.read_text()
assert src.count('\nexit 0')==1
src=src.replace('\nexit 0',
    '# X360OS: original Xenon controller input modules, best effort only\n'
    '/sbin/modprobe joydev >/dev/null 2>&1 || :\n'
    '/sbin/modprobe evdev >/dev/null 2>&1 || :\n'
    'exit 0')
rc.write_text(src)
toggle=r/'usr/bin/x360os-toggle'
t=toggle.read_text()
assert 'x360os-start-gnome' in t
toggle.write_text(t.replace('x360os-start-gnome','x360os-safe-start'))
(r/'etc/x360os-release').write_text(
 'X360OS 7.1.0-recovery-dev\n'
 'base=Ubuntu_10.10_PPC32_COMPATIBILITY_ONLY\n'
 'kernel=ORIGINAL_VERIFIED_v5_XeLL\n'
 'graphics=ORIGINAL_XORG_XENOSFB_NO_DIRECT_FB_WRITES\n'
 'session=ORIGINAL_GDM_GNOME_AUTOSTART_X360OS\n'
 'network=OPTIONAL_NO_BLOCKING_DHCP_IN_X360OS\n'
 'persistence=OFF_TEST_CANDIDATE\n'
 'console_boot=UNTESTED_V7_1\n')
# Name the console system without changing ubuntu package metadata or dependencies.
(r/'etc/issue').write_text('X360OS 7.1 Recovery (Xenon compatibility mode)\\n')
# No standalone native direct-fb app can be accidentally started from this image.
assert not (r/'usr/bin/x360os-ui').exists()
assert not (r/'usr/bin/x360desk').exists()
PY
echo "VERIFYING known-working Xorg, autologin, native UI disabled..."
grep -q '^DefaultSession=gnome.desktop' "$root/etc/gdm/custom.conf"
grep -q 'x360os-safe-start' "$root/etc/xdg/autostart/x360os-autostart.desktop"
test -x "$root/usr/bin/gnome-session"
test -x "$root/usr/bin/x360os-safe-start"
# Endian/static ELF check; legacy Python will be tested with QEMU without DISPLAY.
file "$root/usr/bin/python2.6" | grep -q 'ELF 32-bit MSB'
if command -v qemu-ppc-static >/dev/null; then
 # Full chroot: Python 2.6 imports modules via absolute guest /usr/lib paths.
 # QEMU -L alone does not guarantee correct guest filesystem for Python imports.
 install -m 0755 "$(command -v qemu-ppc-static)" "$root/usr/bin/qemu-ppc-static"
 timeout 30 chroot "$root" /usr/bin/qemu-ppc-static /usr/bin/python2.6 -c "import gtk; print('PYGTK2_IMPORT_OK')" >"$out/pygtk-smoke.log" 2>&1 || {
   cat "$out/pygtk-smoke.log"; echo "STOP: X360OS GTK2 cannot import inside its full rootfs" >&2; exit 1;
 }
 rm -f "$root/usr/bin/qemu-ppc-static"
 grep -q 'PYGTK2_IMPORT_OK' "$out/pygtk-smoke.log"
fi
echo "PACKING GZIP SquashFS for legacy Xenon Casper (no changes to kernel)..."
mksquashfs "$root" "$out/filesystem.squashfs" -comp gzip -b 131072 -noappend -no-progress -processors 4 >"$out/squashfs-build.log" 2>&1
unsquashfs -s "$out/filesystem.squashfs" | grep -q 'Compression gzip'
unsquashfs -cat "$out/filesystem.squashfs" etc/x360os-release | grep -q '7.1.0-recovery'
unsquashfs -cat "$out/filesystem.squashfs" etc/gdm/custom.conf | grep -q 'DefaultSession=gnome.desktop'
mkdir -p "$out/casper"
mv "$out/filesystem.squashfs" "$out/casper/filesystem.squashfs"
cp "$kernel" "$out/vmlinux"
cat >"$out/kboot.conf" <<'EOF'
#KBOOTCONFIG
; X360OS 7.1 RECOVERY — original Xenon kernel + Ubuntu Xorg graphics fallback
; Temporary compatibility build: no persistence or native framebuffer writes.
default=X360OS RECOVERY
timeout=0
X360OS RECOVERY="uda:/vmlinux boot=casper nopersistent console=tty0 console=ttyS0,115200n8 video=xenonfb panic=60 maxcpus=3 quiet splash"
EOF
cat >"$out/TESTE-PTBR.txt" <<'EOF'
X360OS 7.1 RECUPERACAO - PRIMEIRO TESTE GRAFICO
ATENCAO: esta versao ainda usa a base Ubuntu 10.10 internamente
para aproveitar o driver xenosfb/Xorg e o boot que ja abriram na TV.
O menu X360OS abre automaticamente, com o GNOME por tras para recuperacao.
NAO TEM o programa X360OS nativo framebuffer que desenhava blocos errados.
Copie os arquivos para OUTRO pendrive FAT32 e inicie pelo botao Eject/XeLL.
Nao adicione casper-rw de outra versao; este boot usa nopersistent.
O aviso 'DHCP failed' no XeLL pode ocorrer ANTES do Linux e nao prova falha.
Sem cabo ethernet o menu deve funcionar offline.
Se o menu nao aparecer, o Ubuntu antigo podera ser visto para recuperacao.
A versao 7.1 ainda precisa de teste real no Xbox 360.
NAND/HD INTERNO PRESERVADOS. GUARDE O BOOT ANTIGO.
EOF
cat >"$out/READ-ME-FIRST.txt" <<'EOF'
X360OS v7.1.0 Recovery DEV - hardware compatibility boot
Uses ORIGINAL Xbox 360 Xenon kernel, Casper, GDM, Xorg/xenosfb (Ubuntu-era).
Starts custom X360OS fullscreen dashboard through GNOME autostart.
Fallback remains the original graphical desktop if home app fails.
Native direct-framebuffer interface v7.0 is DISABLED after checkerboard crash.
Offline boot: no Ethernet required. XeLL DHCP occurs before Linux.
Not a fully native distribution yet. No user persistence. Unverified on console.
Use separate FAT32 test USB. Do not touch original working disk, NAND or HDD.
EOF
(cd "$out" && sha256sum vmlinux kboot.conf casper/filesystem.squashfs > SHA256SUMS.txt)
echo "X360OS RECOVERY IMAGE READY AT $out"
du -sh "$out"
