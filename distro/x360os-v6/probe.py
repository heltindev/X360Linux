#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
"""Read-only Xbox 360 hardware report without network credentials."""
from __future__ import print_function
import os
import glob
import platform
import time

def read(path):
    try:
        return open(path).read().strip()
    except IOError:
        return 'unavailable'

print('X360OS v6 hardware report -', time.ctime())
print('kernel:', platform.release(), 'machine:', platform.machine())
print('X DISPLAY:', 'present' if os.environ.get('DISPLAY') else 'missing')
for item in ('/sys/class/net/*', '/sys/class/input/event*'):
    for name in sorted(glob.glob(item)):
        print('DEVICE:', name)
        if '/net/' in name:
            print('  state:', read(name + '/operstate'))
            print('  driver:', os.path.realpath(name + '/device/driver'))
        else:
            print('  name:', read(name + '/device/name'))
print('USB devices:')
built_in = False
for folder in sorted(glob.glob('/sys/bus/usb/devices/*')):
    vendor = read(folder + '/idVendor')
    product = read(folder + '/idProduct')
    if vendor != 'unavailable':
        print(' ', vendor + ':' + product,
              read(folder + '/manufacturer'), read(folder + '/product'))
        if (vendor.lower(), product.lower()) == ('045e', '0765'):
            built_in = True
print('XBOX_360_INTERNAL_WIFI_DETECTED:', built_in)
print('Known internal Wi-Fi chip for Xbox 360 Slim: Marvell 88W8786U (USB 045e:0765)')
print('Legacy Xenon Linux 2.6.36 driver support for this chip: NOT CONFIRMED')
print('js devices:', ','.join(glob.glob('/dev/input/js*')) or 'NONE')
print('INPUT DRIVER STATE:')
try:
    for line in open('/proc/modules'):
        if line.startswith(('joydev ', 'evdev ', 'xpad ')):
            print('  ', line.strip())
except IOError:
    pass
try:
    for line in open('/proc/bus/input/devices'):
        if line.startswith(('N:', 'H:', 'I:', 'B:')):
            print(' ', line.strip())
except IOError:
    print('  /proc/bus/input/devices unavailable')
print('KERNEL CONFIG:')
for config in ('/boot/config-2.6.36.2-xenon', '/boot/config'):
    if os.path.isfile(config):
        for line in open(config):
            if line.startswith(('CONFIG_JOYSTICK_XPAD=', 'CONFIG_XENON_ENET=',
                                '# CONFIG_WLAN', '# CONFIG_WIRELESS',
                                'CONFIG_INPUT_JOYDEV=', 'CONFIG_INPUT_EVDEV=')):
                print(' ', line.strip())
        break
print('wireless interfaces:', ','.join(glob.glob('/sys/class/net/wlan*')) or 'NONE')
print('Routing table (interfaces only):')
try:
    for ln in open('/proc/net/route').read().splitlines():
        cols = ln.split()
        if cols:
            print(' route_interface:', cols[0])
except IOError:
    pass
print('XELL_DHCP: occurs before Linux and is separate from Linux DHCP')
print('No Wi-Fi passwords or private account data were collected.')
