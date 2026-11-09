#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
"""Experimental wired Xbox 360 USB gamepad to X11/XTest mapper.

X switches between menu mode (A = Enter) and mouse mode (A = click).
Uses /dev/input/js*; availability of internal/wireless gamepads must be tested.
"""
from __future__ import print_function
import os
import glob
import time
import struct
import select
import ctypes

X11 = ctypes.CDLL('libX11.so.6')
XTST = ctypes.CDLL('libXtst.so.6')
X11.XOpenDisplay.argtypes = [ctypes.c_char_p]
X11.XOpenDisplay.restype = ctypes.c_void_p
X11.XKeysymToKeycode.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
X11.XKeysymToKeycode.restype = ctypes.c_ubyte
X11.XSync.argtypes = [ctypes.c_void_p, ctypes.c_int]
XTST.XTestFakeKeyEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]
XTST.XTestFakeButtonEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]
XTST.XTestFakeRelativeMotionEvent.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_ulong]

KEYS = {'enter':0xff0d, 'escape':0xff1b, 'left':0xff51,
        'up':0xff52, 'right':0xff53, 'down':0xff54,
        'f9':0xffc6, 'alt':0xffe9}

def decode_event(data):
    if len(data) != 8:
        raise ValueError('Invalid joystick event length')
    stamp, value, kind, number = struct.unpack('IhBB', data)
    return (kind & 0x7f, number, value)

def pointer_step(value):
    dead = 6500
    if -dead < value < dead:
        return 0
    scaled = float(abs(value) - dead) / (32767 - dead)
    move = 1 + int(scaled * scaled * 13)
    return -move if value < 0 else move

class Mapper(object):
    def __init__(self):
        self.display = X11.XOpenDisplay(None)
        if not self.display:
            raise RuntimeError('X display unavailable')
        self.axes = {}
        self.pressed = {}
        self.mouse = False
        self.last_nav = {}
        self.last_scroll = 0

    def sync(self):
        X11.XSync(self.display, 0)

    def key(self, name):
        code = X11.XKeysymToKeycode(self.display, KEYS[name])
        if not code:
            return
        XTST.XTestFakeKeyEvent(self.display, code, 1, 0)
        XTST.XTestFakeKeyEvent(self.display, code, 0, 0)
        self.sync()

    def click(self, button, down):
        XTST.XTestFakeButtonEvent(self.display, button, int(down), 0)
        self.sync()

    def page(self, name):
        alt = X11.XKeysymToKeycode(self.display, KEYS['alt'])
        direction = X11.XKeysymToKeycode(self.display, KEYS[name])
        if alt and direction:
            XTST.XTestFakeKeyEvent(self.display, alt, 1, 0)
            XTST.XTestFakeKeyEvent(self.display, direction, 1, 0)
            XTST.XTestFakeKeyEvent(self.display, direction, 0, 0)
            XTST.XTestFakeKeyEvent(self.display, alt, 0, 0)
            self.sync()

    def button(self, number, down):
        was = self.pressed.get(number, False)
        self.pressed[number] = down
        if number == 2 and down and not was:  # X: mode switch
            self.mouse = not self.mouse
            print('X360OS controller mouse mode:', self.mouse)
        elif number == 0:  # A
            if self.mouse:
                self.click(1, down)
            elif down and not was:
                self.key('enter')
        elif number == 1:  # B
            if self.mouse:
                self.click(3, down)
            elif down and not was:
                self.key('escape')
        elif number == 3 and down and not was:  # Y: on-screen URL keyboard
            self.key('f9')
        elif number == 4 and down and not was:
            self.page('left')
        elif number == 5 and down and not was:
            self.page('right')
        elif number in (11, 12, 13, 14) and down and not was:
            # Possible digital D-pad mapping; varies with xpad version.
            self.key({11:'up', 12:'down', 13:'left', 14:'right'}[number])

    def event(self, kind, number, value):
        if kind == 1:
            self.button(number, value != 0)
        elif kind == 2:
            self.axes[number] = value

    def repeat_nav(self, name, active):
        if not active:
            self.last_nav[name] = 0
            return
        now = time.time()
        if now - self.last_nav.get(name, 0) > 0.21:
            self.key(name)
            self.last_nav[name] = now

    def frame(self):
        x = self.axes.get(0, 0)
        y = self.axes.get(1, 0)
        if self.mouse:
            mx, my = pointer_step(x), pointer_step(y)
            if mx or my:
                XTST.XTestFakeRelativeMotionEvent(self.display, mx, my, 0)
                self.sync()
        dx = self.axes.get(6, 0)
        dy = self.axes.get(7, 0)
        self.repeat_nav('left', dx < -16000)
        self.repeat_nav('right', dx > 16000)
        self.repeat_nav('up', dy < -16000)
        self.repeat_nav('down', dy > 16000)
        # In mouse mode, right stick gives page scrolling (on drivers with axes 3/4).
        ry = self.axes.get(4, 0)
        now = time.time()
        if self.mouse and abs(ry) > 18000 and now - self.last_scroll > 0.14:
            self.click(5 if ry > 0 else 4, True)
            self.click(5 if ry > 0 else 4, False)
            self.last_scroll = now

def run():
    mapper = Mapper()
    print('X360OS input service ready; /dev/input/js* auto-discovery')
    while True:
        devices = sorted(glob.glob('/dev/input/js*'))
        if not devices:
            time.sleep(1.0)
            continue
        fd = None
        try:
            fd = os.open(devices[0], os.O_RDONLY | os.O_NONBLOCK)
            mapper.axes.clear()
            mapper.pressed.clear()
            while True:
                readable, unused, errors = select.select([fd], [], [fd], 0.035)
                if errors:
                    break
                if readable:
                    data = os.read(fd, 8)
                    if len(data) != 8:
                        break
                    mapper.event(*decode_event(data))
                mapper.frame()
        except (OSError, IOError) as error:
            print('Controller disconnected:', error)
            time.sleep(1.0)
        finally:
            if fd is not None:
                os.close(fd)

if __name__ == '__main__':
    run()
