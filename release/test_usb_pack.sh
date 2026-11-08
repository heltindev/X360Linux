#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# Run as root in a private mount namespace on the build runner.
set -euo pipefail

package=$1
state=$(mktemp -d)
disk=
cleanup() {
  umount -R "$state/root" 2>/dev/null || true
  umount -R "$state/mounts" 2>/dev/null || true
  umount "$state/usb" 2>/dev/null || true
  if [[ -n "$disk" ]]; then losetup -d "$disk" || true; fi
  rm -rf "$state"
}
trap cleanup EXIT

mkdir "$state/root" "$state/mounts" "$state/usb"
truncate -s 2G "$state/pendrive.img"
printf 'label: dos\n\nstart=2048, type=c\n' | sfdisk "$state/pendrive.img"
disk=$(losetup --find --show --partscan "$state/pendrive.img")
udevadm settle
partition="${disk}p1"
mkfs.fat -F 32 "$partition"

usb="$state/usb"
mount -t vfat "$partition" "$usb"
unzip -q "$package" -d "$usb"
sync
umount "$usb"

BB=busybox
. distro/rootfs/iso-root.sh
mount -t tmpfs tmpfs "$state/mounts"
mount -t vfat -o ro "$partition" "$usb"
test -s "$usb/xenon.elf"
grep -qx X360LINUX-USB-ROOT-V1 "$usb/X360Linux/USB-ROOT.ID"
mount -t vfat -o remount,rw,umask=0077 "$partition" "$usb"
image="$usb/X360Linux/X360Linux.iso"
data="$usb/X360Linux/USB-DATA.ext4"
mount_iso_root "$image" "$data" "$state/mounts" "$state/root"
test -x "$state/root/usr/bin/bash"
test -x "$state/root/usr/bin/icewm-session"
test -x "$state/root/usr/lib/x360linux/start-desktop"
test -x "$state/root/usr/lib/x360linux/x360-fb-bridge"
test -x "$state/root/usr/bin/Xvfb"
grep -Fq '/usr/lib/x360linux/x360-fb-bridge' "$state/root/usr/lib/x360linux/start-desktop"
test -x "$state/root/usr/bin/startx"
test -x "$state/root/usr/lib/xorg/Xorg"
test -s "$state/root/etc/X11/x360linux.conf"
grep -Fq '/usr/lib/x360linux/start-desktop' "$state/root/sbin/init"
test ! -e "$usb/X360Linux/CONSOLE-ONLY"
grep -qx ID=debian "$state/root/etc/os-release"
echo X360LINUX_FAT32_PERSISTENCE_OK > "$state/root/root/iso-test"
test ! -e "$state/mounts/base/root/iso-test"
mkdir -p "$state/root/run"
busybox mount -o move "$state/mounts" "$state/root/run"
test -s "$state/root/run/iso/X360Linux/system.ext4"
busybox mount -o move "$state/root/run" "$state/mounts"
umount "$state/root" "$state/mounts/data" "$state/mounts/base" "$state/mounts/iso"
umount "$usb"
mount -t vfat "$partition" "$usb"
mount_iso_root "$image" "$data" "$state/mounts" "$state/root"
grep -x X360LINUX_FAT32_PERSISTENCE_OK "$state/root/root/iso-test"
