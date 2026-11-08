#!/usr/bin/env bash
# Build Linux/Xenon + BusyBox + signed Debian on an Ubuntu WSL2 filesystem.
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo"
[[ "$(uname -s)" == Linux ]] || { echo "Ubuntu Linux/WSL2 required"; exit 1; }
case "$repo" in /mnt/*) echo "Use a Linux filesystem under ~/X360Linux-local, not /mnt/c"; exit 1;; esac
[[ "$EUID" -ne 0 ]] || { echo "Run as normal Linux user, not root"; exit 1; }
for cmd in sudo git curl python3 sha256sum; do
  command -v "$cmd" >/dev/null || { echo "Missing tool: $cmd"; exit 1; }
done
git diff --quiet && git diff --cached --quiet || { echo "Commit source edits before building"; exit 1; }
git submodule update --init --recursive
sha="$(git rev-parse HEAD)"
work="$repo/.local-build"
out="$repo/dist/local-inputs"
mkdir -p "$work" "$out/kernel" "$out/recovery" "$out/debian"
echo "Source commit: $sha"
sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
  gcc-powerpc-linux-gnu libc6-dev-powerpc-cross binutils-powerpc-linux-gnu \
  qemu-user qemu-user-static binfmt-support make bzip2 curl python3 \
  debootstrap debian-ports-archive-keyring ca-certificates tar xz-utils docker.io
# The first local build sets up Docker Engine automatically inside Ubuntu.
if ! docker info >/dev/null 2>&1; then
  sudo service docker start || true
fi
DOCKER=(docker)
if ! docker info >/dev/null 2>&1; then
  DOCKER=(sudo docker)
  sudo docker info >/dev/null || {
    echo "Docker could not start in WSL2. Check Windows virtualization/WSL2." >&2
    exit 1
  }
fi
deb="$work/debian-ports-archive-keyring_2026.02.04_all.deb"
if [[ ! -s "$deb" ]]; then
  curl -fLsS --retry 3 -o "$deb" \
    https://deb.debian.org/debian/pool/main/d/debian-ports-archive-keyring/debian-ports-archive-keyring_2026.02.04_all.deb
fi
echo "9b3feecd398b14969acc3141d42ed493f322c5a2140a33d4fda4bef2ea9441a6  $deb" | sha256sum -c -
sudo dpkg -i "$deb"
sudo update-binfmts --enable qemu-ppc
archive="$work/linux-6.18.58.tar.xz"
if [[ ! -s "$archive" ]]; then
  curl -fL --retry 3 -o "$archive" \
    https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.18.58.tar.xz
fi
[[ -s "$work/linux-6.18.58/Makefile" ]] || tar -xf "$archive" -C "$work"
# The exact Free60 toolchain already used by GitHub, running locally.
"${DOCKER[@]}" run --rm --network bridge -v "$repo:/workspace" -w /workspace \
  -e JOBS="${JOBS:-6}" free60/libxenon:latest bash -euc '
export DEVKITXENON=/usr/local/xenon
export PATH=/usr/local/xenon/bin:/usr/local/xenon/usr/bin:$PATH
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
  curl xz-utils bc bison flex libssl-dev libelf-dev file patch
bash kernel/build-kernel.sh /workspace/.local-build/linux-6.18.58
make -C launcher
install -D /workspace/.local-build/linux-6.18.58/arch/powerpc/boot/zImage.xenon dist/local-inputs/kernel/vmlinux
install -D external/xell-reloaded/source/lv2/linux/xenon.dtb dist/local-inputs/kernel/xenon.dtb
install -D launcher/x360boot.elf32 dist/local-inputs/kernel/xenon.elf
'
bash distro/build-rootfs.sh
cp distro/out/{initramfs.cpio.gz,busybox-static-ppc32} "$out/recovery/"
# A private mount namespace avoids touching host mounts.
sudo unshare --mount --propagation private \
  env DEBIAN_WORK_DIR="$work/debian-work" DEBIAN_OUT_DIR="$work/debian-output" \
  bash distro/debian/build-debian-rootfs.sh
sudo cp "$work/debian-output/debian-ports-powerpc-rootfs.tar.gz" "$out/debian/"
sudo chown "$(id -u):$(id -g)" "$out/debian/debian-ports-powerpc-rootfs.tar.gz"
printf '%s\n' "$sha" > "$out/SOURCE_COMMIT.txt"
(cd "$out" && sha256sum kernel/{vmlinux,xenon.dtb,xenon.elf} \
  recovery/{initramfs.cpio.gz,busybox-static-ppc32} \
  debian/debian-ports-powerpc-rootfs.tar.gz > SHA256SUMS)
(cd "$out" && sha256sum -c SHA256SUMS)
python3 - "$out" <<'PY'
from pathlib import Path
import sys, gzip, tarfile
p=Path(sys.argv[1])
h=(p/"kernel/vmlinux").read_bytes()[:52]
assert h[:6]==b"\x7fELF\x01\x02" and h[18:20]==b"\x00\x14"
raw=gzip.decompress((p/"recovery/initramfs.cpio.gz").read_bytes())
assert b"X360LINUX-USB-ROOT-V1" in raw and b"bin/x360desk" not in raw
with tarfile.open(p/"debian/debian-ports-powerpc-rootfs.tar.gz","r:gz") as tf:
  names=set(tf.getnames())
  assert "./usr/bin/bash" in names
  assert "./usr/lib/x360linux/start-desktop" in names
  assert not any(s.startswith("./proc/") and s.split("/")[2].isdigit() for s in names)
print("LOCAL_LINUX_VERIFIED")
PY
file="$repo/dist/X360Linux-local-inputs-${sha:0:8}.tar.gz"
tar -C "$out" -czf "$file" .
sha256sum "$file"
echo "SUCCESS: $file"
