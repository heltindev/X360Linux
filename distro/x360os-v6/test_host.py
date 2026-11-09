#!/usr/bin/env python3
"""Host-side static tests; these do not prove Xenon/PowerPC hardware support."""
import ast
import os
import struct
from pathlib import Path
here = Path(__file__).parent
home = (here/'home.py').read_text()
controller = (here/'controller.py').read_text()
ast.parse(home)
ast.parse(controller)
assert 'class Home' in home and 'browser_prompt' in home
assert 'network_info' in home and 'gtk.main()' in home
assert 'XTestFakeRelativeMotionEvent' in controller
assert 'decode_event' in controller and 'pointer_step' in controller
assert 'x360os.desktop' in (here/'build-local.sh').read_text()
assert 'x360os-start-gnome' in (here/'build-local.sh').read_text()
assert 'etc/xdg/autostart/x360os.desktop' in (here/'build-local.sh').read_text()
assert 'x360os-start-gnome' in (here/'x360os-autostart.desktop').read_text()
assert 'gnome-session' in (here/'x360os-session').read_text()
assert 'probe.py' in (here/'x360os-session').read_text()
assert 'candidate_event_device' in controller
assert 'handle_evdev' in controller
assert 'XBOX_360_INTERNAL_WIFI_DETECTED' in (here/'probe.py').read_text()
assert '045e' in (here/'probe.py').read_text() and '0765' in (here/'probe.py').read_text()
test = ast.parse(controller)
namespace = {'struct': struct}
for node in test.body:
    if isinstance(node, ast.FunctionDef) and node.name in ('decode_event','pointer_step'):
        exec(compile(ast.Module(body=[node], type_ignores=[]), '<isolated>', 'exec'),namespace)
event = struct.pack('IhBB',12345,-12000,0x82,0)
assert namespace['decode_event'](event)==(2,0,-12000)
assert namespace['pointer_step'](0)==0
assert namespace['pointer_step'](-32000)<0
assert namespace['pointer_step'](32000)>0
# Simulate big-endian 32-bit Linux input_event packets without an Xbox.
import sys
class FakePad(object):
    def __init__(self):
        self.axes = {}
        self.actions = []
    def button(self, number, down):
        self.actions.append(('button', number, down))
    def key(self, name):
        self.actions.append(('key', name))
namespace = {'struct': struct}
for node in test.body:
    if isinstance(node, ast.FunctionDef) and node.name == 'handle_evdev':
        exec(compile(ast.Module(body=[node], type_ignores=[]), '<isolated>', 'exec'), namespace)
pad = FakePad()
endian = '>' if sys.byteorder == 'big' else '<'
namespace['handle_evdev'](pad, struct.pack(endian + 'IIHHi', 1, 0, 1, 304, 1), 0)
assert pad.actions == [('button', 0, True)], pad.actions
namespace['handle_evdev'](pad, struct.pack(endian + 'IIHHi', 1, 0, 3, 16, -1), 0)
assert pad.axes[6] == -32767
print('PASS: Python syntax, joystick and evdev mapping, startup fallback, network probe and build paths')
