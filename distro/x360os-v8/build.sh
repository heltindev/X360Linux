#!/bin/bash
# X360OS v8: independent Free60 Linux + newc/gzip initramfs (NO Ubuntu runtime).
set -euo pipefail
[ "$#" -eq 3 ] || { echo "Usage: build.sh VERIFIED-XENON-vmlinux VERIFIED-FREE60-MODULE-SOURCE-SQUASHFS NEW-EMPTY-OUTPUT" >&2; exit 2; }
kernel="$(realpath "$1")"
modulesource="$(realpath "$2")"
out="$(realpath -m "$3")"
here="$(cd "$(dirname "$0")" && pwd)"
ui=/root/x360os-native-toolchain/x360os-v8-ui
busybox=/root/x360os-native-work/busybox-1.36.1/busybox
test -s "$kernel" && test -s "$modulesource" && test -x "$ui" && test -x "$busybox"
[ "$(sha256sum "$kernel" | cut -d ' ' -f 1)" = \
  b8aa8eef938275ed5f037b884592283f561ac46b283edf4cdb1200bf2d39cec8 ] || {
  echo "STOP: kernel SHA256 does not match our known-booting Xenon kernel!" >&2; exit 1;
}
[ ! -e "$out" ] || { echo "STOP: output folder exists. Never overwrite a working image." >&2; exit 1; }
mkdir -p "$out"
temp="$(mktemp -d -p /root x360os-v8.XXXXXXXX)"
trap 'rm -rf "$temp"' EXIT
root="$temp/initramfs"
mkdir -p "$root"/{bin,sbin,usr/bin,usr/sbin,etc,dev,dev/input,proc,sys,tmp,run,root,var/log,media/usb,lib/modules/2.6.36.2-xenon/kernel/drivers/input}
echo "Building X360OS INITRAMFS root from BusyBox and dedicated PowerPC executable (NO Ubuntu)..."
install -m 0755 "$busybox" "$root/bin/busybox"
install -m 0755 "$ui" "$root/usr/bin/x360os-ui"
install -m 0755 "$here/init" "$root/init"
qemu-ppc-static "$root/bin/busybox" --list-full >"$temp/applets"
qemu-ppc-static "$root/bin/busybox" --list >"$temp/applet-names"
for tool in sh mount mdev insmod mkdir hostname ls head cat dmesg sleep uname; do
 if ! grep -qx "$tool" "$temp/applet-names"; then
  echo "STOP: needed BusyBox command missing: $tool" >&2; exit 1;
 fi
done
while IFS= read -r path; do
 case "$path" in ""|init|linuxrc|sbin/init|*/linuxrc|*/init) continue;; esac
 dest="$root/$path"
 mkdir -p "$(dirname "$dest")"
 if [ ! -e "$dest" ] && [ ! -L "$dest" ]; then ln -s /bin/busybox "$dest"; fi
done <"$temp/applets"
test -L "$root/bin/sh" && test -L "$root/bin/mount"
# The old Ubuntu rootfs is a SOURCE OF MATCHING FREE60 KERNEL .ko FILES ONLY.
# No other Ubuntu file is ever copied into the new system.
for mod in joydev evdev; do
 rel="lib/modules/2.6.36.2-xenon/kernel/drivers/input/$mod.ko"
 unsquashfs -cat "$modulesource" "$rel" >"$root/$rel" 2>"$out/module-$mod-extract.log"
 test -s "$root/$rel"
 file "$root/$rel" | grep -q 'ELF 64-bit MSB'
done
mknod -m 600 "$root/dev/console" c 5 1
mknod -m 666 "$root/dev/null" c 1 3
mknod -m 666 "$root/dev/zero" c 1 5
mknod -m 666 "$root/dev/tty" c 5 0
mknod -m 600 "$root/dev/fb0" c 29 0
printf 'root:x:0:0:root:/root:/bin/sh\n' >"$root/etc/passwd"
printf 'root:x:0:\n' >"$root/etc/group"
printf 'x360os\n' >"$root/etc/hostname"
printf 'NAME="X360OS"\nID=x360os\nPRETTY_NAME="X360OS Native 8.0 (Xbox 360)"\nVERSION_ID="8.0.0-alpha"\n' >"$root/etc/os-release"
printf 'X360OS Native v8.0 -- Xbox 360 (Free60 Kernel)\n' >"$root/etc/issue"
# Symlink only from a native binary; no glibc loader or Ubuntu packages.
test ! -e "$root/usr/bin/python2.6"
test ! -e "$root/usr/bin/gnome-session"
test ! -e "$root/etc/apt"
test ! -e "$root/usr/bin/Xorg"
test ! -e "$root/etc/casper.conf"
file "$root/bin/busybox" "$root/usr/bin/x360os-ui" | grep -E 'ELF 32-bit MSB'
qemu-ppc-static "$root/bin/busybox" echo X360OS_NATIVE_BOOT_ROOT_OK
echo "Creating original X360OS initrd-x360os.gz (newc cpio+gzip)"
python3 "$here/pack-initramfs.py" "$root" "$out/initrd-x360os.gz"
cp "$kernel" "$out/vmlinux"
cat >"$out/kboot.conf" <<'EOF'
#KBOOTCONFIG
; X360OS v8.0 - REAL NATIVE POWERPC LINUX SYSTEM - NO UBUNTU, NO CASPER
; Free60 XeLL loads a separate initramfs with our /init, not an Ubuntu distro.
; Original XeLL-compatible vmlinux is preserved without modification.
default=X360OS
timeout=0
X360OS="uda:/vmlinux initrd=uda:/initrd-x360os.gz rdinit=/init root=/dev/ram0 console=tty0 console=ttyS0,115200n8 video=xenonfb panic=60 maxcpus=3"
EOF
cat >"$out/TESTE-PTBR.txt" <<'EOF'
X360OS NATIVO 8.0 ALPHA — TESTE REAL DO ZERO
Este USB nao inclui Ubuntu, Casper, GNOME, Xorg, GDM, Python,
Openbox, pacotes APT ou filesystem.squashfs.
O vmlinux e o kernel Free60 que ja iniciou no Xbox.
O NOVO initrd-x360os.gz tem nosso sistema inteiro (BusyBox/musl/C em PowerPC).
XeLL deve carregar vmlinux+initrd automaticamente e entrar no X360OS.
Video: novo renderizador para blocos 32x32 do chip Xenos.
Controle: suporta input Linux via USB; controle SEM FIO INTERNO nao confirmado.
Internet: nao e necessaria. 'DHCP failed' do XeLL nao bloqueia USB.
EXPERIMENTAL: NENHUM teste real desta v8 foi feito no Xbox.
USAR OUTRO PENDRIVE FAT32, NAO SUBSTITUIR O PENDRIVE FUNCIONAL.
Copiar TODOS os arquivos desta pasta para a RAIZ do USB (sem pasta extra).
INICIAR PELO EJECT / XeLL.
Se aparecer erro, tirar foto. Preserve as imagens e pendrive anteriores.
Nao inclui jogos, Firefox nem som funcional por enquanto.
NAND E HDD INTERNO NAO SAO MODIFICADOS.
EOF
cat >"$out/READ-ME-FIRST.txt" <<'EOF'
X360OS v8.0.0-alpha — First Independent Linux Distribution for Xbox 360
NO Ubuntu rootfs, Casper loader, GNOME, Xorg, GDM, GTK, Python, systemd or APT.
Boot: Free60 XeLL -> verified Xenon vmlinux -> custom X360OS cpio initramfs
     -> /init -> native static PPC32 BusyBox/musl + Xenos tiled framebuffer UI.
The original vmlinux is the tested kernel; not a rewrite of Linux itself.
The Xenos GPU has a 32x32 tiled 32-bpp surface; renderer implements XeLL
xenos_pset32 address mapping, as opposed to the corrupt linear v7 renderer.
This native UI is experimental on a real console, despite host tests passing.
USB controllers work only if kernel exposes matching /dev/input events.
Wireless RF controller support and networking/audio/3D are not complete.
Test with separate FAT32 USB and Eject/XeLL. Do not overwrite known-working USB.
No writes to Xbox NAND or internal HDD. No installation or commands needed.
EOF
(cd "$out" && sha256sum vmlinux kboot.conf initrd-x360os.gz >SHA256SUMS.txt)
echo "X360OS v8 BOOTABLE CANDIDATE READY: $out"
ls -lh "$out"/vmlinux "$out"/initrd-x360os.gz "$out"/kboot.conf
