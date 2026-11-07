#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Debian Ports powerpc BE base; optional, NOT auto-booted. No Xbox HDD writes.
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
work="${DEBIAN_WORK_DIR:-$repo/distro/work/debian-ports}"
out="${DEBIAN_OUT_DIR:-$repo/distro/out/debian-ports}"
root="$work/rootfs"
mirror="https://deb.debian.org/debian-ports"
for program in debootstrap qemu-ppc-static qemu-ppc tar sha256sum readelf; do
    command -v "$program" >/dev/null || { echo "Missing $program" >&2; exit 1; }
done
[[ "$(id -u)" -eq 0 ]] || { echo "Run as root on build runner" >&2; exit 1; }
test -s /usr/share/keyrings/debian-ports-archive-keyring.gpg || {
    echo "Missing Debian Ports signed keyring; refusing unsigned packages" >&2; exit 1;
}
mkdir -p "$work" "$out"
if [[ ! -f "$root/debootstrap/debootstrap" ]]; then
    mkdir -p "$root"
    debootstrap --foreign --variant=minbase --arch=powerpc \
        --keyring=/usr/share/keyrings/debian-ports-archive-keyring.gpg \
        unstable "$root" "$mirror"
fi
mkdir -p "$root/usr/bin"
cp "$(command -v qemu-ppc-static)" "$root/usr/bin/qemu-ppc-static"
# Child processes need binfmt_misc enabled by the CI workflow.
echo "Checking Debian PPC32 shell with qemu-user-static..."
chroot "$root" /usr/bin/qemu-ppc-static /bin/sh -c 'echo QEMU_POWERPC_SHELL_READY'
# qemu executes a PowerPC ELF (the shell), which then interprets the
# debootstrap shell script; passing the script directly to qemu is invalid.
if ! chroot "$root" /usr/bin/qemu-ppc-static /bin/sh /debootstrap/debootstrap --second-stage; then
    echo "Debian second stage failed: incomplete rootfs MUST NOT ship." >&2
    exit 1
fi
rm -f "$root/usr/bin/qemu-ppc-static"
printf '%s\n' "x360linux" > "$root/etc/hostname"
cat > "$root/etc/apt/sources.list" <<EOF
deb [signed-by=/usr/share/keyrings/debian-ports-archive-keyring.gpg] $mirror unstable main
EOF
install -D -m 0644 /usr/share/keyrings/debian-ports-archive-keyring.gpg \
    "$root/usr/share/keyrings/debian-ports-archive-keyring.gpg"
bash_path="$root/usr/bin/bash"
if [[ ! -x "$bash_path" ]]; then bash_path="$root/bin/bash"; fi
readelf -h "$bash_path" | grep -q 'Class:.*ELF32'
readelf -h "$bash_path" | grep -q 'Data:.*big endian'
readelf -h "$bash_path" | grep -q 'Machine:.*PowerPC'
qemu-ppc -cpu 750 -L "$root" "$bash_path" -c 'echo DEBIAN_PORTS_PPC32_RUNTIME_OK'
rm -f "$root/var/cache/apt/archives/"*.deb
cat > "$out/README-DEBIAN-PORTS.txt" <<'EOF'
X360Linux Debian Ports powerpc (32-bit big-endian) base filesystem.
Signed upstream source: https://deb.debian.org/debian-ports/
This is optional, NOT the active live boot OS. The real Xbox boots
Xenon Linux + static BusyBox + X360Desk by default.
Before a safe Debian boot we must test mounting an external ext4 rootfs
and the CPU instruction compatibility, RAM use and terminal on hardware.
Do NOT unpack this on FAT32 (permissions and symlinks will be lost).
No NAND flash, Xbox HDD formatting, or saved-games changes.
EOF
tar --sort=name --numeric-owner --owner=0 --group=0 -C "$root" \
    -czf "$out/debian-ports-powerpc-rootfs.tar.gz" .
(cd "$out" && sha256sum debian-ports-powerpc-rootfs.tar.gz > SHA256SUMS)
printf 'DEBIAN_PORTS_BASE_BUILD_OK size=%s\n' "$(stat -c%s "$out/debian-ports-powerpc-rootfs.tar.gz")"
