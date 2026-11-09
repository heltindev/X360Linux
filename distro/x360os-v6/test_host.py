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
assert 'gnome-session' in (here/'x360os-session').read_text()
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
print('PASS: Python syntax, controller decoding, dead zones, session and build paths')
