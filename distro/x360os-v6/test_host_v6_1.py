#!/usr/bin/env python3
"""Host-only source tests for X360OS 6.1; NOT real Xbox hardware validation."""
import ast
from pathlib import Path

base = Path(__file__).resolve().parent
home = (base / "home-stable.py").read_text(encoding="utf-8")
gamepad = (base / "controller-games.py").read_text(encoding="utf-8")
builder = (base / "build-v6.1-ppc.sh").read_text(encoding="utf-8")
doom = (base / "x360os-doom").read_text(encoding="utf-8")
session = (base / "x360os-session-light").read_text(encoding="utf-8")
ast.parse(home)
ast.parse(gamepad)
assert "('DOOM', 'Play the free Freedoom campaign'" in home
assert "def classic_desktop" in home
assert "self.win.hide()" in home
assert "def in_game(self):" in gamepad
assert "self.hold('up'" in gamepad
assert "self.hold('ctrl'" not in gamepad  # bound to gamepad A in the button mapping
assert "0:'ctrl', 1:'space', 2:'shift'" in gamepad
assert "if [ -x /usr/bin/openbox ]" in session
assert "elif [ -x /usr/bin/metacity ]" in session
assert "x360os-sound-check" in session
assert "PrBoom" in (base / "v6.1.0-TESTING.md").read_text()
assert "prboom" in doom and "freedoom.wad" in doom
assert "Chocolate Doom" in (base / "v6.1.0-TESTING.md").read_text()
assert "dpkg-deb -x" in builder and "mksquashfs" in builder
assert "grep -q '^CONFIG_SND_XENON=y'" in builder
assert "free" in (base / "x360os-doom.desktop").read_text().lower()
print("PASS: X360OS 6.1 source syntax, game/keyboard mapping, Openbox fallback, image builder")
