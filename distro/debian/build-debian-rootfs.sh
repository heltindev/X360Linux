#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Debian Ports powerpc BE filesystem with the X360Linux desktop.
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
printf '%s\n' "x360linux" > "$root/etc/hostname"
cat > "$root/etc/apt/sources.list" <<EOF
deb [signed-by=/usr/share/keyrings/debian-ports-archive-keyring.gpg] $mirror unstable main
EOF
install -D -m 0644 /usr/share/keyrings/debian-ports-archive-keyring.gpg \
    "$root/usr/share/keyrings/debian-ports-archive-keyring.gpg"
# Package installation inside the build chroot must not start host-facing daemons.
printf '#!/bin/sh\nexit 101\n' > "$root/usr/sbin/policy-rc.d"
chmod 0755 "$root/usr/sbin/policy-rc.d"
# Run package scripts with procfs and PTYs inside the isolated CI mount namespace.
mkdir -p "$root/proc" "$root/dev/pts"
mount -t proc -o nosuid,nodev,noexec proc "$root/proc"
mount -t devpts -o nosuid,noexec devpts "$root/dev/pts"
cleanup_chroot_mounts() {
    umount "$root/dev/pts" 2>/dev/null || true
    umount "$root/proc" 2>/dev/null || true
}
trap cleanup_chroot_mounts EXIT
chroot "$root" /usr/bin/apt-get update

# Xorg requires udev, but X360Linux runs under its own minimal BusyBox PID 1.
# Full systemd 262 postinst crashes under QEMU PPC32; avoid pulling it in
# through udev's alternate sysusers/tmpfiles dependencies.
chroot "$root" /usr/bin/env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    systemd-standalone-sysusers systemd-standalone-tmpfiles \
    icewm pcmanfm udev xauth xinit xterm xfonts-base x11-utils x11-xserver-utils \
    xserver-xorg-core xserver-xorg-input-libinput xserver-xorg-video-fbdev xvfb
if chroot "$root" /usr/bin/dpkg-query -W -f='${Status}' systemd 2>/dev/null | grep -q 'install ok installed'; then
    echo "Unexpected full systemd dependency in minimal Xbox Debian build" >&2
    exit 1
fi

install -D -m 0644 "$repo/distro/debian/x360linux.conf" "$root/etc/X11/x360linux.conf"
install -D -m 0755 "$repo/distro/debian/start-desktop" "$root/usr/lib/x360linux/start-desktop"
install -D -m 0755 "$repo/distro/debian/desktop-session" "$root/usr/lib/x360linux/desktop-session"
install -D -m 0644 "$repo/distro/debian/icewm-menu" "$root/root/.icewm/menu"
sh -n "$root/usr/lib/x360linux/start-desktop"
sh -n "$root/usr/lib/x360linux/desktop-session"
chroot "$root" /usr/lib/xorg/Xorg -version
chroot "$root" /usr/bin/env HOME=/root xvfb-run -a -s '-screen 0 800x600x24' /bin/sh -eu -c '
    /usr/lib/x360linux/desktop-session &
    desktop=$!
    trap "kill $desktop 2>/dev/null || true" EXIT
    for attempt in $(seq 1 15); do
        if xprop -root _NET_SUPPORTING_WM_CHECK | grep -q "window id"; then
            echo X360LINUX_ICEWM_SESSION_OK
            exit 0
        fi
        kill -0 "$desktop" || exit 1
        sleep 1
    done
    exit 1
'
chroot "$root" /usr/bin/env DEBIAN_FRONTEND=noninteractive apt-get purge -y xvfb
cleanup_chroot_mounts
trap - EXIT
rm -f "$root/usr/sbin/policy-rc.d" "$root/usr/bin/qemu-ppc-static"
find "$root/var/lib/apt/lists" -maxdepth 1 -type f -delete
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
The USB ISO starts this Debian filesystem and an IceWM desktop.
The console is available as a fallback.
Do NOT unpack this on FAT32 (permissions and symlinks will be lost).
No NAND flash, Xbox HDD formatting, or saved-games changes.
EOF
tar --sort=name --numeric-owner --owner=0 --group=0 -C "$root" \
    -czf "$out/debian-ports-powerpc-rootfs.tar.gz" .
(cd "$out" && sha256sum debian-ports-powerpc-rootfs.tar.gz > SHA256SUMS)
printf 'DEBIAN_PORTS_BASE_BUILD_OK size=%s\n' "$(stat -c%s "$out/debian-ports-powerpc-rootfs.tar.gz")"
