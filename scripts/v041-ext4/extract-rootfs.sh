#!/usr/bin/env bash
set -euo pipefail
b="${1:?Provide WSL path to PEN DRIVE}"
src="$b/BOOT-DIRETO/casper/filesystem.squashfs"
dir='/root/x360linux-v04-rootfs-build'
test -f "$src"
if test -d "$dir" && test -f "$dir/etc/lsb-release"; then echo 'REUSING_EXTRACTED_ROOT'; else
 rm -rf "$dir"
 echo 'UNPACKING_UBUNTU_ROOTFS_TO_WSL_TEMP'
 unsquashfs -d "$dir" -no-progress -processors 8 "$src" > "$b/work/extract-ubuntu-ext4.log" 2>&1
fi
echo 'UNPACK_DONE'
du -sh "$dir"
du -sk "$dir"
test -x "$dir/sbin/init"
test -x "$dir/usr/bin/gnome-session"
echo 'SPLASH_DEFAULTS'
ls -la "$dir/lib/plymouth/themes" | head -40
echo 'SPLASH_SYMLINKS'
find "$dir/lib/plymouth" -maxdepth 4 -type l -print | head -30
echo 'USERS'
grep '^ubuntu:' "$dir/etc/passwd" || :
grep '^ubuntu:' "$dir/etc/group" || :
echo 'EXTRACTION_SUCCESS'
