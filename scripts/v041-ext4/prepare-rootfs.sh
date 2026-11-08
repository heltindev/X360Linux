#!/usr/bin/env bash
set -euo pipefail
umask 022
base="${1:?Provide WSL path to PEN DRIVE}"
root='/root/x360linux-v04-rootfs-build'
work="$(cd "$(dirname "$0")" && pwd)"
boot="$base/BOOT-DIRETO"
dest="$boot/distros/ubuntu-x360"
image="$dest/rootfs.ext4"
pending="$dest/rootfs.ext4.building"
original="$boot/casper/filesystem.squashfs"
mkdir -p "$dest"
test -x "$root/usr/bin/gnome-session"
test -x "$root/sbin/init"
test ! -e "$pending"
test ! -e "$image"
echo '===== Customize preinstalled Ubuntu PowerPC rootfs ====='
python3 - "$root" "$work" <<'PY'
from pathlib import Path
import os,sys,shutil
r=Path(sys.argv[1])
s=Path(sys.argv[2])
passwd=r/"etc/passwd"; group=r/"etc/group"; shadow=r/"etc/shadow"; gshadow=r/"etc/gshadow"
p=passwd.read_text()
assert not any(x.startswith("ubuntu:") for x in p.splitlines())
assert not any(x.startswith("ubuntu:") for x in group.read_text().splitlines())
assert not any(x.startswith("ubuntu:") for x in shadow.read_text().splitlines())
passwd.write_text(p+"ubuntu:x:1000:1000:Live desktop user:/home/ubuntu:/bin/bash\n")
g=group.read_text()
g+="ubuntu:x:1000:\n"
for name in ("audio","video","plugdev","cdrom","floppy","adm","netdev","nopasswdlogin","admin"):
 lines=g.splitlines(keepends=True)
 for i,line in enumerate(lines):
  parts=line.rstrip("\n").split(":")
  if parts[0]==name:
   members=parts[3].split(",") if parts[3] else []
   if "ubuntu" not in members:members.append("ubuntu")
   parts[3]=",".join(members)
   lines[i]=":".join(parts)+"\n"
   break
 g="".join(lines)
group.write_text(g)
shadow.write_text(shadow.read_text()+"ubuntu:!:20766:0:99999:7:::\n")
shadow.chmod(0o600)
if gshadow.exists():
 gshadow.write_text(gshadow.read_text()+"ubuntu:!::\n")
 gshadow.chmod(0o600)
home=r/"home/ubuntu"
assert not home.exists(),"Ubuntu home exists; refusing overwrite"
shutil.copytree(r/"etc/skel",home,symlinks=True)
os.chown(home,1000,1000)
for dp,dirs,files in os.walk(home):
 for name in dirs+files:
  path=Path(dp)/name
  if not path.is_symlink():os.chown(path,1000,1000)
(home/".dmrc").write_text("[Desktop]\nSession=gnome\nLanguage=en_US.UTF-8\n")
os.chown(home/".dmrc",1000,1000)
(home/".dmrc").chmod(0o600)
(r/"etc/hostname").write_text("x360linux\n")
hosts=r/"etc/hosts"
if hosts.is_file():
 hs=hosts.read_text()
 if "127.0.1.1" in hs:hs="\n".join("127.0.1.1 x360linux" if x.startswith("127.0.1.1") else x for x in hs.splitlines())+"\n"
 else:hs+="\n127.0.1.1 x360linux\n"
 hosts.write_text(hs)
# The USB ext4 root is mounted by the external initramfs.
fstab=r/"etc/fstab"
fstab.write_text("# X360Linux: rootfs.ext4 on removable USB (initramfs mounts it).\n"
 "proc /proc proc defaults 0 0\n"
 "sysfs /sys sysfs defaults 0 0\n"
 "tmpfs /tmp tmpfs defaults,noatime,mode=1777,size=48m 0 0\n")
# Preserve the previously patched installer suppression and live GDM config.
uq=r/"etc/init/ubiquity.conf"; assert "auto-start disabled" in uq.read_text()
gdm=r/"etc/gdm/custom.conf";assert "AutomaticLogin=ubuntu" in gdm.read_text()
# Existing Ubuntu 10.10 Plymouth script module: activate the experimental green theme.
theme=r/"lib/plymouth/themes/x360linux"
theme.mkdir(parents=True,exist_ok=True)
legacy=s/"theme"
assert (legacy/"x360linux.script").is_file(), "Missing local Plymouth prototype"
for name in ("x360linux.script","x360linux.plymouth"):
 shutil.copy2(legacy/name,theme/name)
alternative=r/"etc/alternatives/default.plymouth"
if alternative.is_symlink() or alternative.is_file():alternative.unlink()
alternative.parent.mkdir(parents=True,exist_ok=True)
alternative.symlink_to("/lib/plymouth/themes/x360linux/x360linux.plymouth")
# Early boot progress is only telemetry. The graphical bar starts in Linux userspace.
ready=r/"usr/local/bin/x360linux-desktop-ready"
ready.parent.mkdir(parents=True,exist_ok=True)
ready.write_text("#!/bin/sh\n"
 "mkdir -p /var/log/x360linux\n"
 "date -u '+%Y-%m-%dT%H:%M:%SZ' > /var/log/x360linux/desktop-ready\n"
 "logger -t X360Linux 'Desktop session started (boot milestone: 100%)' 2>/dev/null || :\n")
ready.chmod(0o755)
autostart=r/"etc/xdg/autostart/x360linux-desktop-ready.desktop"
autostart.write_text("[Desktop Entry]\nType=Application\n"
 "Name=X360Linux Desktop Ready\nExec=/usr/local/bin/x360linux-desktop-ready\n"
 "NoDisplay=true\nX-GNOME-Autostart-enabled=true\n")
# Disabling common optional heavy services may reduce overhead, not a proven speed boost.
# Keep DHCP, NetworkManager, dbus, graphics, fans and audio.
removed=[]
for level in "2345":
 location=r/("etc/rc"+level+".d")
 if not location.is_dir():continue
 for link in location.iterdir():
  if link.is_symlink() and link.name.startswith("S") and link.name[3:] in ("cups","avahi-daemon","atd"):
   link.unlink()
   removed.append(str(link.relative_to(r)))
(r/"etc/x360linux-release").write_text("X360Linux v0.5-dev\n"
 "arch=powerpc32-be\nroot=USB-FAT32/EXT4-loop\ninstaller=disabled\n"
 "desktop=GNOME2\nplymouth=green-userspace\n"
 "hardware=NOT_VERIFIED_CORONA_PHISON\n")
print("UNCOMPRESSED_ROOT_PREPARED",flush=True)
print("OPTIONAL_STARTUP_LINKS_DISABLED",removed,flush=True)
PY
