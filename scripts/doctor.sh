#!/usr/bin/env bash
set -euo pipefail

echo "X360Linux :: development environment check"
echo "-------------------------------------------"
fail=0

for f in README.md .gitmodules external/xenos-linux-gpu/README.md external/free60-kernel-patches/xenon-6.18.defconfig external/xell-reloaded/README.md; do
  if [[ -s "$f" ]]; then printf '[OK] %s\n' "$f"
  else printf '[MISSING] %s\n' "$f"; fail=1; fi
done

for command in git make patch python3; do
  if command -v "$command" >/dev/null 2>&1; then
    printf '[OK] %s\n' "$command"
  else
    printf '[MISSING] %s\n' "$command"
    fail=1
  fi
done

for command in xenon-gcc xenon-objcopy powerpc64-linux-gnu-gcc meson ninja; do
  if command -v "$command" >/dev/null 2>&1; then
    printf '[OK] optional tool: %s\n' "$command"
  else
    printf '[NOT INSTALLED] optional tool: %s\n' "$command"
  fi
done

echo "Check results concern host setup only, not hardware compatibility."
if (( fail != 0 )); then
  echo "Initialize submodules and install required host tools."
  exit 1
fi
