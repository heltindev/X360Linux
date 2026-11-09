#!/usr/bin/env bash
# X360OS v7.2: custom Xbox fullscreen session plus wired-USB controller mouse.
# Deliberately preserve known-working Xenon v5 kernel and Xorg/xenosfb video drivers.
set -euo pipefail
[ "$#" -eq 3 ] || { echo "Usage: build.sh V7.1-ROOTFS ORIGINAL-VMLINUX NEW-OUTPUT-DIR" >&2; exit 2; }
base="$(realpath "$1")"
kernel="$(realpath "$2")"
out="$(realpath -m "$3")"
here="$(cd "$(dirname "$0")" && pwd)"
test -s "$base" && test -s "$kernel"
test -r "$here/home.py" && test -r "$here/controller.py"
[ "$(sha256sum "$kernel" | cut -d' ' -f1)" = "b8aa8eef938275ed5f037b884592283f561ac46b283edf4cdb1200bf2d39cec8" ] ||
  { echo "STOP: ORIGINAL V5 XENON KERNEL DOES NOT MATCH" >&2; exit 1; }
[ ! -e "$out" ] || { echo "STOP: output exists; no overwrite." >&2; exit 1; }
mkdir -p "$out"
temp="$(mktemp -d -p /root x360os-shell.XXXXXXXX)"
trap 'rm -rf "$temp"' EXIT
root="$temp/root"
echo "EXTRACTING VERIFIED V7.1 COMPATIBILITY ROOTFS..."
unsquashfs -d "$root" -no-progress -processors 4 "$base" >"$out/extract.log" 2>&1
grep -q '^X360OS 7.1.0-recovery-dev' "$root/etc/x360os-release"
for f in usr/bin/python2.6 usr/sbin/gdm usr/lib/xorg/modules/drivers/xenosfb_drv.so usr/bin/metacity usr/bin/gnome-session etc/X11/xorg.conf; do
 test -e "$root/$f" || { echo "STOP: missing original graphic/runtime dependency: $f" >&2; exit 1; }
done
echo "INSTALLING X360OS DIRECT SESSION + USB CONTROLLER POINTER..."
install -D -m 0755 "$here/x360os-session" "$root/usr/bin/x360os-session"
install -D -m 0644 "$here/x360os.desktop" "$root/usr/share/xsessions/x360os.desktop"
install -D -m 0755 "$here/x360os-input-start" "$root/usr/bin/x360os-input-start"
install -D -m 0755 "$here/x360os-input-diagnose" "$root/usr/bin/x360os-input-diagnose"
install -D -m 0644 "$here/home.py" "$root/usr/share/x360os/home.py"
install -D -m 0644 "$here/controller.py" "$root/usr/share/x360os/controller.py"
python3 - "$root" <<'PY'
from pathlib import Path
import sys
root=Path(sys.argv[1])
gdm=root/'etc/gdm/custom.conf'
cfg=gdm.read_text()
assert 'DefaultSession=gnome.desktop' in cfg
assert 'AutomaticLogin=ubuntu' in cfg
cfg=cfg.replace('DefaultSession=gnome.desktop','DefaultSession=x360os')
gdm.write_text(cfg)
skel=root/'etc/skel'
skel.mkdir(parents=True,exist_ok=True)
(skel/'.dmrc').write_text('[Desktop]\nSession=x360os\n')
# If a default Ubuntu home exists, set its session without touching user files on USB.
if (root/'home/ubuntu').is_dir():
    (root/'home/ubuntu/.dmrc').write_text('[Desktop]\nSession=x360os\n')
rc=root/'etc/rc.local'
s=rc.read_text()
assert s.count('\nexit 0') == 1
s=s.replace('\nexit 0',
  '\n# X360OS: log real input devices before the desktop starts; no secrets\n'
  '/usr/bin/x360os-input-diagnose >/dev/null 2>&1 || :\n'
  'exit 0')
rc.write_text(s)
(root/'etc/x360os-release').write_text(
 'X360OS 7.2.0-shell-dev\n'
 'user_interface=X360OS_CUSTOM_SESSION_NO_GNOME_PANEL\n'
 'graphics=ORIGINAL_XENON_XORG_XENOSFB\n'
 'kernel=VERIFIED_XELL_V5_2.6.36.2\n'
 'controller=USB_XPAD_JOYDEV_EVDEV_XTEST_MOUSE_DEFAULT_ON\n'
 'internal_RF_controller=NOT_VALIDATED\n'
 'base=Ubuntu_10.10_PPC32_COMPATIBILITY_UNDER_THE_HOOD\n'
 'persistence=OFF_FOR_TEST\n'
 'hardware_boot=UNTESTED_V7_2\n'
 )
(root/'etc/issue').write_text('X360OS 7.2 - Xbox 360 PowerPC\n')
# This image does NOT include the broken v7 native raw-framebuffer renderer.
assert not (root/'usr/bin/x360os-ui').exists()
assert not (root/'usr/bin/x360desk').exists()
PY
grep -q '^DefaultSession=x360os$' "$root/etc/gdm/custom.conf"
grep -q '^Exec=/usr/bin/x360os-session$' "$root/usr/share/xsessions/x360os.desktop"
grep -q 'self.mouse = True' "$root/usr/share/x360os/controller.py"
# The legacy recovery autostart survives for a GNOME fallback session.
test -r "$root/etc/xdg/autostart/x360os-autostart.desktop"
test -x "$root/usr/bin/gnome-session"
echo "POWERPC2.6 CHECK (original guest filesystem in QEMU chroot)..."
if command -v qemu-ppc-static >/dev/null; then
 install -m 0755 "$(command -v qemu-ppc-static)" "$root/usr/bin/qemu-ppc-static"
 timeout 35 chroot "$root" /usr/bin/qemu-ppc-static /usr/bin/python2.6 -c \
  "import gtk,ctypes,sys;ctypes.CDLL('libXtst.so.6');sys.path.insert(0,'/usr/share/x360os');import controller;assert controller.pointer_step(25000)>0;print('X360OS_GTK2_XTEST_CONTROLLER_IMPORT_OK')" \
  >"$out/gtk-input-smoke.log" 2>&1 || { cat "$out/gtk-input-smoke.log"; echo "FAILED: PPC GTK2+XTest controller loader" >&2; exit 1; }
 timeout 35 chroot "$root" /usr/bin/qemu-ppc-static /usr/bin/python2.6 -m py_compile \
  /usr/share/x360os/home.py /usr/share/x360os/controller.py >"$out/python-smoke.log" 2>&1 || {
  cat "$out/python-smoke.log"; echo "FAILED: PPC python source compile" >&2; exit 1; }
 rm -f "$root/usr/bin/qemu-ppc-static"
 grep -q 'X360OS_GTK2_XTEST_CONTROLLER_IMPORT_OK' "$out/gtk-input-smoke.log"
fi
echo "BUILDING ORIGINAL XENON COMPATIBLE SQUASHFS..."
mksquashfs "$root" "$out/filesystem.squashfs" -comp gzip -b 131072 -noappend -no-progress -processors 4 >"$out/squashfs-build.log" 2>&1
unsquashfs -s "$out/filesystem.squashfs" | grep -q 'Compression gzip'
unsquashfs -cat "$out/filesystem.squashfs" etc/x360os-release | grep -q '^X360OS 7.2.0-shell-dev'
unsquashfs -cat "$out/filesystem.squashfs" etc/gdm/custom.conf | grep -q '^DefaultSession=x360os'
mkdir -p "$out/casper"
mv "$out/filesystem.squashfs" "$out/casper/filesystem.squashfs"
cp "$kernel" "$out/vmlinux"
cat >"$out/kboot.conf" <<'EOF'
#KBOOTCONFIG
; X360OS v7.2 custom Xbox session. ORIGINAL Free60 kernel + Xorg driver.
; Never write to NAND, Xbox internal HDD or use an old casper-rw overlay.
default=X360OS
timeout=0
X360OS="uda:/vmlinux boot=casper nopersistent console=tty0 console=ttyS0,115200n8 video=xenonfb panic=60 maxcpus=3 quiet splash"
EOF
cat >"$out/TESTE-PTBR.txt" <<'EOF'
X360OS v7.2 - TESTE NA TV (XBOX 360 RGH/JTAG)
O sistema agora TENTA abrir diretamente uma sessao grafica X360OS.
O Ubuntu antigo ainda esta nas bibliotecas de compatibilidade e como recuperacao.
A base de video xenosfb/Xorg e o kernel que deram imagem foram preservados.
Testar OUTRO pendrive FAT32; copiar o CONTEUDO da pasta para a raiz.
Nao copiar nenhum casper-rw antigo. Nao foi gravado em E:, NAND ou HDD.
CONTROLE: no controle USB 360 com fio, o ANALOGICO ESQUERDO move mouse,
A clique esquerdo, B clique direito, X alterna modo menu/mouse, F10 resgate.
Controle sem fio do console pode NAO aparecer como dispositivo Linux xpad:
o cabo Play&Charge NAO transforma controle sem fio em controle USB.
Se o controle nao mexer, ver em /home/ubuntu/.x360os/controller.log
e /var/log/x360os-input-hardware.txt (sessao temporaria, nao salva ao reiniciar).
Se a interface nao abrir, ha fallback para desktop GNOME.
O XeLL pode dizer DHCP failed ANTES do Linux e isso nao bloqueia a rede offline.
A v7.2 NAO foi testada no console. Mantenha a versao anterior funcionando.
EOF
cat >"$out/READ-ME-FIRST.txt" <<'EOF'
X360OS 7.2.0-dev Xbox 360 - Custom Shell and Controller Pointer
Default session is X360OS fullscreen. GDM/Xorg/XenosFB boot known to show video.
Ubuntu 10.10 PPC32 remains inside solely as transitional compatibility libraries;
THIS IS NOT YET A FULLY UBUNTU-FREE DISTRIBUTION.
USB gamepad mouse mapper defaults ON, requires a Linux-recognized USB controller.
Internal Xbox proprietary wireless RF is NOT guaranteed by the xpad driver.
Optional Ethernet only. No old casper-rw persistence; no Xbox NAND/HDD writes.
If X360OS home exits, GNOME recovery can appear. F10 enters recovery manually.
ALPHA TEST ONLY; physical Xbox v7.2 boot and input UNVERIFIED.
EOF
(cd "$out" && sha256sum vmlinux kboot.conf casper/filesystem.squashfs >SHA256SUMS.txt)
echo "BUILD SUCCESS: $out"
du -sh "$out"
