#!/usr/bin/env bash
set -euo pipefail
base="${1:?Provide WSL path to PEN DRIVE}"
root='/root/x360linux-v04-rootfs-build'
image='/root/x360linux-ubuntu-ext4-v04.1.img'
out="$base/BOOT-DIRETO/distros/ubuntu-x360"
previous="$out/rootfs.ext4.building"
export LC_ALL=C
test -f "$root/etc/x360linux-release"
test -d "$root/home/ubuntu"
test -x "$root/usr/bin/gnome-session"
test ! -e "$image"
test ! -e "$out/rootfs.ext4"
# Cleanup is restricted to our known INCOMPLETE file left by interrupted mkfs.
if test -e "$previous";then
 echo 'REMOVING_PREVIOUS_INCOMPLETE_IMAGE'
 rm -f -- "$previous"
fi
echo 'CREATING_3G_EXT4_ON_LINUX_FILESYSTEM'
truncate -s 3G "$image"
mke2fs -F -q -t ext4 -b 4096 -m 0 -L X360ROOT \
 -O '^64bit,^metadata_csum,^metadata_csum_seed,^orphan_file,^encrypt,^casefold,^verity,^project,^quota' \
 -E lazy_itable_init=0,lazy_journal_init=0 \
 -d "$root" "$image"
echo 'RUNNING_FILESYSTEM_CHECK'
set +e
e2fsck -f -n "$image" > "$base/work/X360Linux-v05-source/e2fsck-ubuntu-v05.log" 2>&1
check=$?
set -e
if test "$check" -ne 0;then
 tail -45 "$base/work/X360Linux-v05-source/e2fsck-ubuntu-v05.log"
 exit 1
fi
echo 'VERIFYING_LEGACY_FEATURE_COMPATIBILITY'
tune2fs -l "$image" | grep -E '(Filesystem features:|Filesystem volume name:|Block count:|Block size:)'
echo 'VERIFYING_INSTALLED_DESKTOP'
debugfs -R 'stat /home/ubuntu' "$image" 2>&1 | grep -E '(Inode|Mode:)' | head -3
debugfs -R 'stat /usr/bin/gnome-session' "$image" 2>&1 | grep -E '(Inode|Mode:)' | head -3
echo 'COPYING_COMPLETE_IMAGE_TO_WINDOWS_FOR_USB'
cp -- "$image" "$out/rootfs.ext4.copying"
test "$(stat -c %s "$out/rootfs.ext4.copying")" = "$(stat -c %s "$image")"
echo 'VERIFYING_WINDOWS_COPY_SHA256'
a="$(sha256sum "$image"|cut -d' ' -f1)"
b="$(sha256sum "$out/rootfs.ext4.copying"|cut -d' ' -f1)"
test "$a" = "$b"
mv "$out/rootfs.ext4.copying" "$out/rootfs.ext4"
printf 'X360LINUX-UBUNTU-EXT4-V05\n' > "$out/ROOTFS.ID"
cp "$base/BOOT-DIRETO/vmlinux" "$out/vmlinux"
echo "ROOTFS_CREATED_BYTES=$(stat -c %s "$out/rootfs.ext4")"
echo "ROOTFS_SHA256=$a"
echo 'EXT4_PREINSTALLED_IMAGE_READY_STATICALLY_VERIFIED'
