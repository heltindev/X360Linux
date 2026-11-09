#!/bin/bash
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
out="/mnt/c/Users/hhhel.DESKTOP-3QIFGGI/Desktop/PEN DRIVE/work/release-v8.0.0-zero-ubuntu-r2"
sh -n "$here/init"
bash -n "$here/build.sh"
bash -n "$here/build-ui.sh"
python3 -m py_compile "$here/generate-tiled-ui.py" "$here/pack-initramfs.py" "$here/verify-initramfs.py" "$here/stage-release.py"
( cd "$out" && sha256sum -c SHA256SUMS.txt )
python3 "$here/verify-initramfs.py" "$out"
echo "V8_HOST_BUILD_INTEGRITY_AND_SCRIPT_TESTS_PASSED"
