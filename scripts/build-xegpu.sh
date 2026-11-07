#!/usr/bin/env bash
set -euo pipefail

if (( $# != 1 )); then
  echo "Usage: bash scripts/build-xegpu.sh /path/to/prepared/linux-6.18.58" >&2
  exit 2
fi

kernel_dir=$(cd "$1" && pwd)
repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
gpu_dir="$repo_root/external/xenos-linux-gpu/kernel/xegpu"

[[ -s "$kernel_dir/.config" ]] || { echo "Kernel .config missing; run build-kernel.sh first." >&2; exit 1; }
[[ -s "$gpu_dir/Makefile" ]] || { echo "xegpu submodule not initialized." >&2; exit 1; }

command -v xenon-gcc >/dev/null || { echo "Missing xenon-gcc." >&2; exit 1; }
jobs="${JOBS:-2}"
[[ "$jobs" =~ ^[1-9][0-9]*$ ]] || { echo "JOBS must be positive integer." >&2; exit 2; }

make -C "$kernel_dir" ARCH=powerpc CROSS_COMPILE=xenon- M="$gpu_dir" -j "$jobs" modules

[[ -s "$gpu_dir/xegpu.ko" ]] || { echo "xegpu.ko missing; build or config failed." >&2; exit 1; }
echo "Experimental module built: $gpu_dir/xegpu.ko"
echo "Do not load this module outside the intended Xbox 360 kernel."
