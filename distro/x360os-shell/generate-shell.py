#!/usr/bin/env python3
"""Fork tested X360OS GTK2 home + XTest controller without touching user's custom home.py."""
from pathlib import Path

here = Path(__file__).resolve().parent
prior = here.parent / "x360os-v6"
home = (prior / "home-stable.py").read_text(encoding="utf-8")
controller = (prior / "controller-games.py").read_text(encoding="utf-8")

home_changes = [
    ("v6 • POWERPC", "v7.2 • XENON"),
    ("'Ubuntu programs'", "'X360OS programs'"),
    ("'Classic Ubuntu mode'", "'Recovery desktop (F10)'"),
    ("'Ubuntu Applications'", "'X360OS Applications'"),
    ("'Classic Ubuntu mode'", "'Recovery desktop (F10)'"),
    ("'%s is unavailable in this Ubuntu image.'", "'%s is not available in this X360OS compatibility image.'"),
    ("('DOOM', 'Play the free Freedoom campaign', ['/usr/bin/x360os-doom']),",
     "('Terminal', 'System diagnostics', ['gnome-terminal']),"),
    ("('DOOM / Freedoom', ['/usr/bin/x360os-doom']),",
     "('Diagnostics', ['/usr/bin/gnome-terminal']),"),
    ("('Desktop', 'Classic Ubuntu mode', None),",
     "('Desktop', 'Recovery desktop (F10)', None),"),
    ("'Xbox 360  |  Lightweight desktop'", "'XBOX 360 | X360OS SHELL'"),
    ("'D-pad: navigate    A: open    Back: Home    X: mouse    F10: desktop'",
     "'USB pad: left stick mouse | A click | B right click | X menu/mouse | F10 recovery'"),
]
for old, new in home_changes:
    if old not in home:
        if old == "'Classic Ubuntu mode'" or old == "('Desktop', 'Classic Ubuntu mode', None),":
            continue
        raise AssertionError("Missing home source: " + old)
    home = home.replace(old, new)
# Make the pointer default, and add clear diagnostics if no input device was enumerated.
controller_changes = [
    ("self.mouse = False", "self.mouse = True  # X360OS 7.2: cursor ON by default"),
    ("'NO INPUT DEVICE: kernel may not expose the Xbox wireless pad.'",
     "'NO INPUT DEVICE: check joydev/evdev + USB cable or receiver. Internal Xbox RF may be unsupported.'"),
    ("print('INPUT:', path, 'mode:', 'evdev' if evdev else 'joystick')",
     "print('INPUT DEVICE CONNECTED:', path, 'mode:', 'evdev' if evdev else 'joystick')"),
    ("print('X360OS controller bridge: joystick + gamepad evdev discovery')",
     "print('X360OS 7.2 controller bridge: LEFT STICK=mouse, A=left click, B=right click; X toggles menu/mouse')"),
]
for old, new in controller_changes:
    assert old in controller, "Missing controller source: " + old
    controller = controller.replace(old, new)
# Python2.6 syntax, no fstrings; preserve PPC big-endian input decoding.
assert "struct.unpack(endian + 'IIHHi', data)" in controller
assert "XTST.XTestFakeRelativeMotionEvent" in controller
assert "self.mouse = True" in controller
assert "self.win.fullscreen()" in home
(here / "home.py").write_text(home, encoding="utf-8", newline="\n")
(here / "controller.py").write_text(controller, encoding="utf-8", newline="\n")
print("GENERATED: standalone X360OS home.py", len(home.splitlines()), "lines")
print("GENERATED: USB gamepad/evdev XTest mouse controller.py", len(controller.splitlines()), "lines")
