#!/usr/bin/env python3
"""Fork the in-repository framebuffer UI into an Ubuntu-free X360OS native dashboard."""
from pathlib import Path

here = Path(__file__).resolve().parent
base = here.parent / "desktop" / "x360desk.c"
out = here / "x360os-ui.c"
s = base.read_text(encoding="utf-8")
assert "#include \"third_party/stb_image.h\"" in s
assert "X360LINUX" in s and "DEBIAN PORTS: EXPERIMENTAL BASE" in s
s = s.replace("X360Linux Desk v0.3", "X360OS Native v7.0")
s = s.replace("X360Linux", "X360OS")
s = s.replace("X360LINUX", "X360OS")
s = s.replace("DEBIAN PORTS: EXPERIMENTAL BASE", "NATIVE: MUSL + BUSYBOX  | NO UBUNTU")
s = s.replace("MEDIA: JPG PNG BMP + SILENT X36V", "INPUT: USB KEYBOARD + GAMEPAD", 1)
s = s.replace("X360OS - GRAPHICAL TEST", "X360OS NATIVE v7.0 - HARDWARE STATUS")
s = s.replace("DESKTOP PREVIEW  |  POWERPC XENON", "NATIVE X360OS | POWERPC XENON")
s = s.replace("Linux framebuffer media shell", "Linux Xenon framebuffer shell")
s = s.replace("DEBIAN", "X360OS")
s = s.replace("X360DESK_", "X360OS_UI_")
s = s.replace("X360DESK:", "X360OS:")
out.write_text(s, encoding="utf-8", newline="\n")
print(f"X360OS native UI source created: {out} ({s.count(chr(10))} lines)")
