#!/bin/bash
# X360OS Native v7 alpha, USB-only experimental rootfs, no Ubuntu packages.
set -euo pipefail
[ "$#" -eq 3 ] || { echo "Usage: build-native-rootfs.sh V5-vmlinux V5-filesystem.squashfs EMPTY-OUTPUT-DIR" >&2; exit 2; }
kernel="$(realpath "$1")"
legacy="$(realpath "$2")"
output="$(realpath -m "$3")"
here="$(cd "$(dirname "$0")" && pwd)"
repo="$(realpath "$here/..")"
toolchain=/root/x360os-native-toolchain
busybox=/root/x360os-native-work/busybox-1.36.1/busybox
ui="$toolchain/x360os-ui"
test -s "$kernel" && test -s "$legacy" && test -x "$busybox" && test -x "$ui"
expected="b8aa8eef938275ed5f037b884592283f561ac46b283edf4cdb1200bf2d39cec8"
actual="$(sha256sum "$kernel" | cut -d' ' -f1)"
[ "$actual" = "$expected" ] || { echo "STOP: original verified Xenon kernel SHA mismatch" >&2; exit 1; }
if [ -e "$output" ]; then
 [ -d "$output" ] && [ -z "$(ls -A "$output")" ] || { echo "STOP: output directory is not empty" >&2; exit 1; }
fi
mkdir -p "$output"
tmp="$(mktemp -d -p /root x360os-native-root.XXXXXXXX)"
trap 'rm -rf "$tmp"' EXIT
root="$tmp/root"
mkdir -p "$root"/{bin,sbin,usr/bin,usr/sbin,etc/network,dev,proc,sys,tmp,run,var/log,root,media/usb,mnt,lib/modules/2.6.36.2-xenon/kernel/drivers/input}
echo "INSTALLING native STATIC PowerPC BusyBox applets"
install -m 0755 "$busybox" "$root/bin/busybox"
qemu-ppc-static "$busybox" --list-full >"$tmp/applets.txt"
while IFS= read -r relative; do
 case "$relative" in ""|init|linuxrc|sbin/init|*/linuxrc|*/init) continue;; esac
 dest="$root/$relative"
 mkdir -p "$(dirname "$dest")"
 [ -e "$dest" ] || [ -L "$dest" ] || ln -s /bin/busybox "$dest"
done <"$tmp/applets.txt"
# Native PID 1 executable shell script. Avoid BusyBox's own default init.
install -D -m 0755 "$here/init" "$root/sbin/init"
install -D -m 0755 "$here/udhcpc-script" "$root/etc/network/udhcpc-script"
install -D -m 0755 "$ui" "$root/usr/bin/x360os-ui"
printf 'root:x:0:0:root:/root:/bin/sh\n' >"$root/etc/passwd"
printf 'root:x:0:\n' >"$root/etc/group"
printf 'x360os\n' >"$root/etc/hostname"
printf '# X360OS Native — filesystems mounted by PID 1\nproc /proc proc defaults 0 0\nsysfs /sys sysfs defaults 0 0\n' >"$root/etc/fstab"
printf 'NAME="X360OS"\nID=x360os\nPRETTY_NAME="X360OS Native 7.0 Alpha (Xbox 360)"\nVERSION_ID="7.0.0-alpha"\n' >"$root/etc/os-release"
ln -s /run/resolv.conf "$root/etc/resolv.conf"
# Device nodes needed before devtmpfs/mdev is mounted.
mknod -m 600 "$root/dev/console" c 5 1
mknod -m 666 "$root/dev/null" c 1 3
mknod -m 666 "$root/dev/zero" c 1 5
mknod -m 666 "$root/dev/tty" c 5 0
mknod -m 600 "$root/dev/fb0" c 29 0
# Input modules are FREE60 XENON KERNEL MODULES, not Ubuntu userspace.
# Extract exactly these two modules, not the legacy OS tree.
for mod in evdev joydev; do
 rel="lib/modules/2.6.36.2-xenon/kernel/drivers/input/$mod.ko"
 unsquashfs -cat "$legacy" "$rel" >"$root/$rel" 2>"$output/$mod-extract.log"
 test -s "$root/$rel"
 file "$root/$rel" | grep -q 'ELF 64-bit MSB'
done
echo "CHECKING: zero Ubuntu programs/packages and all static PPC executables"
test -f "$root/etc/os-release" && test -x "$root/sbin/init"
test ! -e "$root/usr/bin/python2.6"
test ! -e "$root/usr/bin/gnome-session"
test ! -e "$root/etc/apt"
test ! -e "$root/var/lib/dpkg"
test ! -e "$root/usr/bin/Xorg"
file "$root/bin/busybox" "$root/usr/bin/x360os-ui"
qemu-ppc-static "$root/bin/busybox" echo X360OS_NATIVE_BUSYBOX_OK
qemu-ppc-static "$root/usr/bin/x360os-ui" --render-test 800 480 "$tmp/native-ui.ppm" | tee "$output/ui-smoke.log"
test -s "$tmp/native-ui.ppm"
echo "PACKING native rootfs (gzip SquashFS for original Xenon kernel)"
mksquashfs "$root" "$output/filesystem.squashfs" -comp gzip -b 131072 -noappend -no-progress -processors 4 -all-root >"$output/squashfs-build.log" 2>&1
unsquashfs -s "$output/filesystem.squashfs" | grep -q 'Compression gzip'
unsquashfs -cat "$output/filesystem.squashfs" etc/os-release | grep -q 'ID=x360os'
unsquashfs -cat "$output/filesystem.squashfs" sbin/init | grep -q 'X360OS Native v7'
mkdir -p "$output/casper"
mv "$output/filesystem.squashfs" "$output/casper/filesystem.squashfs"
cp "$kernel" "$output/vmlinux"
cat > "$output/kboot.conf" <<'EOF'
#KBOOTCONFIG
; X360OS Native v7.0 ALPHA — zero Ubuntu rootfs, legacy Casper bootstrap still in kernel
; USB-only test, no persistence and NO NAND/HDD modifications.
default=X360OS NATIVE
timeout=0
X360OS NATIVE="uda:/vmlinux boot=casper nopersistent console=tty0 console=ttyS0,115200n8 video=xenonfb panic=60 maxcpus=3"
EOF
cat > "$output/READ-ME-FIRST.txt" <<'EOF'
X360OS NATIVE v7.0.0-alpha - XBOX 360 RGH/JTAG TEST
- This is an experimental Ubuntu-free ROOT FILESYSTEM (musl, BusyBox, C UI).
- The ORIGINAL XeLL compatible kernel still contains its old Casper bootstrap.
- Boot has NOT been verified on a real Xbox 360 with this new userspace.
- Make a separate FAT32 USB test drive; copy these files to its ROOT.
- Plug in console and boot with Eject to start XeLL.
- No casper-rw: deliberately nonpersistent to avoid old Ubuntu overlay files.
- Wired Ethernet experimental. Internal wireless controller/Wi-Fi not supported yet.
- No DOOM or graphical browser: native framebuffer foundation only.
- Keep the known-working v5/v6 USB intact for recovery. No NAND/HDD changes.
EOF
cat > "$output/TESTE-PTBR.txt" <<'EOF'
X360OS NATIVO v7.0.0-alpha - TESTE NO XBOX 360
NOVO SISTEMA, SEM ROOTFS UBUNTU. NAO TESTADO NO XBOX REAL.
Este teste tem BusyBox + musl + interface propria framebuffer.
O kernel antigo e o bootstrap Casper inicial foram mantidos por seguranca.
NAO COPIE arquivos casper-rw antigos da Ubuntu: eles reintroduziriam o sistema.
Teste de preferencia em OUTRO pendrive FAT32 (8GB ou mais).
Copie tudo para a raiz do pendrive e inicie com Eject pelo XeLL.
O sistema tenta abrir a interface X360OS direto, sem Xorg nem GNOME.
Se falhar, registre uma foto da tela; nao apague o pendrive antigo.
REDE: Ethernet experimental. Wi-Fi Slim e controle sem fio RF nao resolvidos.
Este projeto nao altera NAND nem disco interno do Xbox.
O DOOM ainda precisa de um port nativo, portanto nao esta incluso na v7-alpha.
EOF
( cd "$output" && sha256sum vmlinux kboot.conf casper/filesystem.squashfs > SHA256SUMS.txt )
echo "X360OS NATIVE TEST IMAGE READY: $output"
du -sh "$output"
