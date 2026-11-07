#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Build an *already installed* Debian Ports PowerPC rootfs on an ext4 file.
# The file lives inside X360Linux/ on the USB FAT32 partition.
# Does not mount disks or write to any connected Xbox device.
set -euo pipefail
if [[ $# -ne 3 ]]; then
    echo "Usage: $0 debian-ports-rootfs.tar.gz static-ppc-busybox output-system.ext4" >&2
    exit 2
fi
source_tar="$(realpath "$1")"
rescue_bin="$(realpath "$2")"
output="$(realpath -m "$3")"
for tool in mkfs.ext4 e2fsck tar readelf qemu-ppc; do
    command -v "$tool" >/dev/null || { echo "Missing $tool" >&2; exit 1; }
done
[[ -s "$source_tar" && -s "$rescue_bin" ]] || { echo "Missing Debian or static rescue BusyBox" >&2; exit 1; }
readelf -h "$rescue_bin" | grep -q 'Machine:.*PowerPC'
readelf -h "$rescue_bin" | grep -q 'Data:.*big endian'
if readelf -l "$rescue_bin" | grep -q 'INTERP'; then
    echo "Rescue BusyBox must be STATIC to avoid a broken Linux PID1" >&2
    exit 1
fi
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
root="$work/root"
mkdir -p "$root"
tar -xzpf "$source_tar" -C "$root" --no-same-owner
mkdir -p "$root/sbin" "$root/etc" "$root/root" "$root/bootusb"
install -D -m 0755 "$rescue_bin" "$root/usr/lib/x360linux/busybox"
cat > "$root/sbin/init" <<'EOF'
#!/bin/sh
# First boot starts the actual Debian filesystem from the USB ext4 image.
# The kernel already mounted /proc, /sys, /dev and the FAT32 USB boot drive.
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export PATH
export HOME=/root
BB=/usr/lib/x360linux/busybox
hostname x360linux
echo
echo "=================================================="
echo " X360Linux | Debian Ports powerpc (USB installation)"
echo " This Linux system lives on the USB drive, not Xbox HDD."
echo "=================================================="
echo "Debian USB console (terminal hotfix)."
echo "Use a USB keyboard to test: cat /etc/os-release"
echo "To preserve files, shut down cleanly before unplugging the USB."
echo
# Linux PID 1 must never exit, or the kernel would panic.
while :; do
  "$BB" setsid "$BB" cttyhack /bin/bash -i
  echo "Shell exited; returning to the Debian console..."
  "$BB" sleep 2
done
EOF
chmod 0755 "$root/sbin/init"
cat > "$root/etc/issue" <<'EOF'
X360Linux Debian Ports | running entirely from USB
EOF
cat > "$root/etc/fstab" <<'EOF'
# X360Linux: never mount the internal Xbox 360 HDD.
/proc     /proc     proc     defaults                0 0
/sys      /sys      sysfs    defaults                0 0
/dev      /dev      devtmpfs defaults                0 0
EOF
cat > "$root/root/.bashrc" <<'EOF'
export PS1='X360Linux:\w # '
echo "Debian PowerPC shell ready. Your files are saved in the USB ext4 image."
EOF
# Exercise the installed BusyBox under the name used by init.
sh -n "$root/sbin/init"
installed_busybox="$root$(sed -n 's/^BB=//p' "$root/sbin/init")"
qemu-ppc -cpu 750 "$installed_busybox" sleep 0
qemu-ppc -cpu 750 "$installed_busybox" setsid /bin/true
qemu-ppc -cpu 750 "$installed_busybox" cttyhack /bin/true
printf '%s\n' "X360LINUX_DEBIAN_CONSOLE_APPLETS_OK"

# Validate the actual Debian runtime before putting it inside an ext4 image.
bash_path="$root/usr/bin/bash"
[[ -x "$bash_path" ]] || bash_path="$root/bin/bash"
readelf -h "$bash_path" | grep -q 'Class:.*ELF32'
readelf -h "$bash_path" | grep -q 'Data:.*big endian'
readelf -h "$bash_path" | grep -q 'Machine:.*PowerPC'
qemu-ppc -cpu 750 -L "$root" "$bash_path" -c 'echo X360LINUX_DEBIAN_SHELL_OK'
mkdir -p "$(dirname "$output")"
# mkfs.ext4 -d copies files into the image without root mounts, retaining
# symlinks and Unix file modes even though the eventual USB boot partition
# is FAT32. 768MiB is DISK storage, NOT system RAM consumption.
truncate -s 768M "$output"
mkfs.ext4 -q -F -b 4096 -L X360LINUX -d "$root" "$output"
e2fsck -fn "$output"
echo "EXT4_USB_ROOT_READY=$output"
du -h "$output"
