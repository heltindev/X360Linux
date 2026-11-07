#!/usr/bin/env python3
"""Static repository validation; never touches a console or network."""
from pathlib import Path
import configparser
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md", "assets/x360linux-banner.svg", ".gitmodules",
    "docs/BUILD.md", "docs/BOOT-SAFETY.md", "docs/GPU-INTEGRATION.md",
    "docs/ARCHITECTURE.md", "docs/COMPATIBILITY.md",
    "docs/UPSTREAM-AND-LICENSES.md", "docs/ROADMAP.md",
    "CONTRIBUTING.md", "config/kboot.conf.example",
    "scripts/build-kernel.sh", "scripts/build-xegpu.sh",
]
issues = []
for relative in REQUIRED:
    item = ROOT / relative
    if not item.is_file() or item.stat().st_size == 0:
        issues.append(f"Missing or empty: {relative}")

try:
    ET.parse(ROOT / "assets/x360linux-banner.svg")
except (ET.ParseError, FileNotFoundError) as exc:
    issues.append(f"Invalid banner SVG: {exc}")

gitmodules = ROOT / ".gitmodules"
if gitmodules.is_file():
    content = gitmodules.read_text(encoding="utf-8")
    for source in ("arelyx/xenos-linux-gpu", "Free60Project/linux-kernel-xbox360", "Free60Project/xell-reloaded"):
        if source not in content:
            issues.append(f"Missing Git submodule: {source}")

if issues:
    print("X360Linux validation failed:")
    for issue in issues:
        print(f" - {issue}")
    sys.exit(1)

print("X360Linux: static project files validated (not a hardware or build test).")
