#!/usr/bin/env bash
set -euo pipefail

if (( $# != 1 )); then
  echo "Usage: bash kernel/build-kernel.sh /path/to/clean/linux-6.18.58" >&2
  exit 2
fi

kernel_dir=$(cd "$1" && pwd)
repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
patch_dir="$repo_root/external/free60-kernel-patches"
gpu_patch_dir="$repo_root/external/xenos-linux-gpu/kernel/patches"

for cmd in make patch awk xenon-gcc; do
  command -v "$cmd" >/dev/null || { echo "Missing required command: $cmd" >&2; exit 1; }
done

[[ -f "$kernel_dir/Makefile" ]] || { echo "Linux source tree Makefile missing." >&2; exit 1; }
[[ -f "$patch_dir/patch-6.18-xenon0.30.diff" ]] || { echo "Missing Free60 patch." >&2; exit 1; }
[[ -f "$patch_dir/xenon-6.18.defconfig" ]] || { echo "Missing Free60 kernel config." >&2; exit 1; }

read_make_var() {
  awk -v key="$1" '$1==key && $2=="=" { print $3; exit }' "$kernel_dir/Makefile"
}
version="$(read_make_var VERSION)"
patchlevel="$(read_make_var PATCHLEVEL)"
sublevel="$(read_make_var SUBLEVEL)"
if [[ "$version.$patchlevel.$sublevel" != "6.18.58" ]]; then
  echo "Expected Linux 6.18.58; got $version.$patchlevel.$sublevel. Refusing a possibly incompatible patch." >&2
  exit 1
fi

apply_patch() {
  local name="$1"
  local patchfile="$2"
  local strip="${3:-1}"
  [[ "$strip" == 0 || "$strip" == 1 ]] || { echo "Invalid patch strip level" >&2; exit 1; }
  [[ -f "$patchfile" ]] || { echo "Missing patch $patchfile" >&2; exit 1; }
  if patch --batch --dry-run -d "$kernel_dir" -p"$strip" < "$patchfile" >/dev/null 2>&1; then
    echo "Applying $name"
    patch --batch -d "$kernel_dir" -p"$strip" < "$patchfile"
  elif patch --batch --dry-run -R -d "$kernel_dir" -p"$strip" < "$patchfile" >/dev/null 2>&1; then
    echo "Already applied: $name"
  else
    echo "Cannot cleanly apply $name; verify clean Linux 6.18.58 and patch revision." >&2
    exit 1
  fi
}

apply_patch "Free60 Xenon Linux 6.18" "$patch_dir/patch-6.18-xenon0.30.diff"
apply_patch "sis190 TX fix" "$gpu_patch_dir/0001-sis190-tx-wake-race.patch" 0
apply_patch "VMX not advertised" "$gpu_patch_dir/0002-xenon-vmx-not-advertised.patch"

cp "$patch_dir/xenon-6.18.defconfig" "$kernel_dir/.config"
jobs="${JOBS:-2}"
[[ "$jobs" =~ ^[1-9][0-9]*$ ]] || { echo "JOBS must be positive integer." >&2; exit 2; }

make -C "$kernel_dir" ARCH=powerpc CROSS_COMPILE=xenon- olddefconfig
# First hardware milestone: build only the bootable kernel, not optional modules.
# Graphics and other modular drivers will be developed after Linux reaches a shell.
make -C "$kernel_dir" ARCH=powerpc CROSS_COMPILE=xenon- -j "$jobs" zImage.xenon

candidate="$kernel_dir/arch/powerpc/boot/zImage.xenon"
if [[ ! -s "$candidate" ]]; then
  echo "Build completed but expected boot image not present: $candidate" >&2
  exit 1
fi
echo "Candidate kernel: $candidate"
echo "This has NOT been booted on hardware. No NAND was written."
