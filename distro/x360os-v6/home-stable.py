#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
"""X360OS v6 controller/keyboard-friendly GTK2 home (Ubuntu 10.10 PowerPC)."""
from __future__ import print_function
import os
import subprocess
import gtk
import gobject
import signal
import atexit

BG = '#0B141D'
CARD = '#1B2D36'
GREEN = '#38D97C'
WHITE = '#ECF5F2'
MUTED = '#91ACA9'
APPS = [
    ('Browser', 'Open websites', ['firefox']),
    ('Files', 'USB and folders', ['nautilus', '--no-desktop']),
    ('Applications', 'Ubuntu programs', None),
    ('Network', 'Ethernet settings', ['nm-connection-editor']),
    ('Videos', 'Watch local media', ['totem']),
    ('Music', 'Listen to music', ['rhythmbox']),
    ('DOOM', 'Play the free Freedoom campaign', ['/usr/bin/x360os-doom']),
    ('Settings', 'System preferences', ['gnome-control-center']),
    ('Desktop', 'Classic Ubuntu mode', None),
]
EXTRA = [
    ('Text Editor', ['gedit']),
    ('PDF Reader', ['evince']),
    ('DOOM / Freedoom', ['/usr/bin/x360os-doom']),
    ('Terminal', ['gnome-terminal']),
    ('System Monitor', ['gnome-system-monitor']),
    ('Screenshot', ['gnome-screenshot']),
    ('PDF Viewer', ['evince']),
    ('Media Player', ['totem']),
    ('Music', ['rhythmbox']),
    ('File Manager', ['nautilus', '--no-desktop']),
]

def find_executable(name):
    if os.path.sep in name:
        return os.path.isfile(name) and os.access(name, os.X_OK)
    for p in os.environ.get('PATH', '/usr/bin:/bin').split(os.pathsep):
        if os.access(os.path.join(p, name), os.X_OK):
            return True
    return False

def memory_info():
    values = {}
    try:
        for line in open('/proc/meminfo'):
            key, value = line.split(':', 1)
            values[key] = int(value.strip().split()[0])
        total = values.get('MemTotal', 0) / 1024
        free = (values.get('MemFree', 0) + values.get('Buffers', 0)
                + values.get('Cached', 0)) / 1024
        return '%d MB free / %d MB' % (free, total)
    except Exception:
        return 'Memory unavailable'

def network_info():
    # A link is not proof of DHCP, DNS, or internet access.
    try:
        interfaces = [n for n in os.listdir('/sys/class/net') if n != 'lo']
        wifi = [n for n in interfaces if n.startswith(('wlan', 'wl', 'ra'))]
        for n in interfaces:
            f = '/sys/class/net/%s/operstate' % n
            if os.path.exists(f) and open(f).read().strip() == 'up':
                return '%s link active (internet unverified)' % n
        if wifi:
            return '%s found: select Network to connect' % wifi[0]
        if interfaces:
            return '%s disconnected; internal Wi-Fi needs driver' % interfaces[0]
    except (OSError, IOError):
        pass
    return 'No network interface: Wi-Fi driver may be missing'

class Home(object):
    def __init__(self):
        self.win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.win.set_title('X360OS Home')
        self.win.set_decorated(False)
        self.win.set_border_width(12)
        self.win.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(BG))
        self.win.connect('destroy', gtk.main_quit)
        self.win.connect('key-press-event', self.on_key)
        self.win.set_default_size(1100, 680)
        self.win.fullscreen()

        outer = gtk.VBox(False, 14)
        self.win.add(outer)
        head = gtk.HBox(False, 10)
        logo = gtk.Label()
        logo.set_markup('<span foreground="%s" size="xx-large" weight="bold">X360OS</span>  '
                        '<span foreground="%s" size="large">v6 • POWERPC</span>' % (GREEN, MUTED))
        head.pack_start(logo, False, False, 12)
        head.pack_end(self.label('Xbox 360  |  Lightweight desktop', 14, MUTED), False, False, 12)
        outer.pack_start(head, False, False, 8)

        self.status = self.label('', 12, MUTED)
        outer.pack_start(self.status, False, False, 0)

        table = gtk.Table(3, 3, True)
        outer.pack_start(table, True, True, 0)
        self.buttons = []
        for index, item in enumerate(APPS):
            name, sub, command = item
            btn = gtk.Button()
            btn.set_relief(gtk.RELIEF_NONE)
            btn.set_can_focus(True)
            btn.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(CARD))
            btn.modify_bg(gtk.STATE_PRELIGHT, gtk.gdk.color_parse('#245340'))
            btn.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.color_parse('#2B845A'))
            label = gtk.Label()
            label.set_justify(gtk.JUSTIFY_CENTER)
            label.set_markup('<span foreground="%s" size="x-large" weight="bold">%s</span>'
                             '\n<span foreground="%s" size="medium">%s</span>' %
                             (WHITE, name, MUTED, sub))
            btn.add(label)
            btn.connect('clicked', self.activate, name, command)
            btn.connect('focus-in-event', self.focus_changed, True)
            btn.connect('focus-out-event', self.focus_changed, False)
            table.attach(btn, index % 3, index % 3 + 1,
                         index // 3, index // 3 + 1,
                         xpadding=9, ypadding=9)
            self.buttons.append(btn)

        footer = self.label('D-pad: navigate    A: open    Back: Home    X: mouse    F10: desktop', 12, MUTED)
        outer.pack_end(footer, False, False, 10)
        self.win.show_all()
        self.buttons[0].grab_focus()
        self.install_return_signal()
        self.refresh_status()
        gobject.timeout_add(5000, self.refresh_status)

    def label(self, message, size, color):
        label = gtk.Label()
        label.set_markup('<span foreground="%s" size="%d000">%s</span>' % (color, size, message))
        return label

    def focus_changed(self, btn, event, active):
        btn.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('#205D43' if active else CARD))
        return False

    def refresh_status(self):
        self.status.set_text('%s    |    %s' % (memory_info(), network_info()))
        self.status.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse(MUTED))
        return True

    def notify(self, title, message):
        dialog = gtk.MessageDialog(self.win, gtk.DIALOG_MODAL,
                                   gtk.MESSAGE_INFO, gtk.BUTTONS_OK, message)
        dialog.set_title(title)
        dialog.run()
        dialog.destroy()

    def launch(self, command, args=None):
        args = args or []
        if not command:
            return
        if not find_executable(command[0]):
            self.notify('Not installed', '%s is unavailable in this Ubuntu image.' % command[0])
            return
        try:
            subprocess.Popen(command + args, close_fds=True)
        except Exception as err:
            self.notify('Unable to open', str(err))

    def activate(self, btn, name, command):
        if name == 'Browser':
            self.browser_prompt()
        elif name == 'Applications':
            self.apps_prompt()
        elif name == 'Desktop':
            self.classic_desktop()
        elif name == 'Network' and not find_executable('nm-connection-editor'):
            self.launch(['gnome-control-center'])
        else:
            self.launch(command)

    def apps_prompt(self):
        dialog = gtk.Dialog('Ubuntu Applications', self.win, gtk.DIALOG_MODAL,
                            (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        dialog.set_default_size(580, 450)
        box = gtk.VBox(False, 6)
        for name, command in EXTRA:
            btn = gtk.Button(name)
            btn.connect('clicked', lambda widget, c=command: self.launch(c))
            box.pack_start(btn, True, True, 1)
        dialog.vbox.pack_start(box, True, True, 6)
        dialog.show_all()
        dialog.run()
        dialog.destroy()

    def browser_prompt(self):
        dialog = gtk.Dialog('Open website', self.win, gtk.DIALOG_MODAL,
                            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                             gtk.STOCK_OK, gtk.RESPONSE_OK))
        dialog.set_default_size(720, 420)
        info = self.label('Enter a website address using the on-screen keyboard', 13, WHITE)
        dialog.vbox.pack_start(info, False, False, 8)
        entry = gtk.Entry()
        entry.set_text('http://example.com/')
        dialog.vbox.pack_start(entry, False, False, 8)
        keys = ['1234567890', 'qwertyuiop', 'asdfghjkl', 'zxcvbnm']
        for line in keys:
            bar = gtk.HBox(True, 3)
            for character in line:
                btn = gtk.Button(character.upper())
                btn.connect('clicked', self.type_character, entry, character)
                bar.pack_start(btn, True, True, 0)
            dialog.vbox.pack_start(bar, False, False, 3)
        bar = gtk.HBox(True, 4)
        for label, value in [('SPACE', ' '), ('.', '.'), ('/', '/'),
                             (':', ':'), ('-', '-'), ('BACK', None)]:
            btn = gtk.Button(label)
            btn.connect('clicked', self.type_character, entry, value)
            bar.pack_start(btn, True, True, 0)
        dialog.vbox.pack_start(bar, False, False, 3)
        entry.connect('activate', lambda widget: dialog.response(gtk.RESPONSE_OK))
        dialog.show_all()
        if dialog.run() == gtk.RESPONSE_OK:
            url = entry.get_text().strip()
            if url:
                if '://' not in url:
                    url = 'http://' + url
                self.launch(['firefox'], [url])
        dialog.destroy()

    def type_character(self, btn, entry, text):
        if text is None:
            pos = entry.get_position()
            if pos > 0:
                entry.delete_text(pos - 1, pos)
                entry.set_position(pos - 1)
        else:
            pos = entry.get_position()
            entry.insert_text(text, pos)
            entry.set_position(pos + len(text))

    def install_return_signal(self):
        self.state_dir = os.path.join(os.path.expanduser('~'), '.x360os')
        try:
            if not os.path.isdir(self.state_dir):
                os.makedirs(self.state_dir)
            self.pidfile = os.path.join(self.state_dir, 'home.pid')
            open(self.pidfile, 'w').write(str(os.getpid()) + '\n')
            atexit.register(self.cleanup_pidfile)
        except (IOError, OSError):
            self.pidfile = None
        signal.signal(signal.SIGUSR1, self.request_show)

    def cleanup_pidfile(self):
        try:
            if self.pidfile and open(self.pidfile).read().strip() == str(os.getpid()):
                os.unlink(self.pidfile)
        except (IOError, OSError):
            pass

    def request_show(self, signum, frame):
        gobject.idle_add(self.show_home)

    def show_home(self):
        self.win.show_all()
        self.win.fullscreen()
        self.win.present()
        self.buttons[0].grab_focus()
        return False

    def classic_desktop(self):
        # Keep X360OS alive: the desktop launcher or gamepad Back will restore it.
        self.win.hide()
        running = False
        try:
            with open(os.devnull, 'w') as devnull:
                running = subprocess.call(['pgrep', '-x', 'gnome-session'],
                                          stdout=devnull, stderr=devnull) == 0
        except OSError:
            pass
        if not running and find_executable('gnome-session'):
            try:
                subprocess.Popen(['gnome-session'], close_fds=True)
            except OSError as err:
                self.show_home()
                self.notify('Desktop could not start', str(err))

    def on_key(self, widget, event):
        if event.keyval == gtk.keysyms.F10:
            self.classic_desktop()
            return True
        if event.keyval == gtk.keysyms.F9:
            self.browser_prompt()
            return True
        return False

if __name__ == '__main__':
    Home()
    gtk.main()
