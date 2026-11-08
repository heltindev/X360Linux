#!/usr/bin/env bash
set -euo pipefail
umask 022
base="${1:?Usage: bash build-v04-xex-live.sh PATH_TO_BOOT_DIRETO}"
source_image="$base/casper/filesystem.squashfs"
version="X360Linux-v0.4.0-alpha-XEX-LIVE-UNTESTED"
stage="$base/$version"
dev="$base/v0.4-dev"
mkdir -p "$stage/casper" "$dev"
cp "$0" "$dev/build-v04-xex-live.sh"
log="$dev/build-v04.log"
exec > >(tee "$log") 2>&1
echo '==== X360Linux v0.4 experimental live USB local build ===='
echo 'SOURCE_DIR:' "$base"
test -s "$source_image"
test -s "$base/default.xex"
test -s "$base/xell.bin"
test -s "$base/vmlinux"
test -s "$base/readme.txt"
echo '==== SHA256 original boot files ===='
sha256sum "$base/default.xex" "$base/xell.bin" "$base/vmlinux" "$source_image"
test "$(sha256sum "$base/default.xex" | cut -d' ' -f1)" = '414492ce7ded99d9d8efe7e35407168cdf4f357c0b4bbff0cf6f27e473a7b2ec'
test "$(sha256sum "$base/xell.bin" | cut -d' ' -f1)" = '6f15f922796a5ad9187b0e6d20cda19e9d18e9e2e6584ecd2c06cd47f37ed1a8'
test "$(sha256sum "$base/vmlinux" | cut -d' ' -f1)" = 'b8aa8eef938275ed5f037b884592283f561ac46b283edf4cdb1200bf2d39cec8'
test "$(sha256sum "$source_image" | cut -d' ' -f1)" = '73863d53ad02d8fdd74ad1ba22b7269df0df67b6e00fcc828234be81a1224de6'
echo 'BASELINE_SHA256_OK'
echo '==== Checking filesystem and free disk space ===='
df -h /tmp "$base"
unsquashfs -s "$source_image" | grep -E '(Filesystem size|Compression|Block size|Number of inodes)'
tmp="$(mktemp -d /tmp/x360-v04-build.XXXXXXXX)"
trap 'rm -rf "$tmp"' EXIT
root="$tmp/rootfs"
mkdir -p "$root"
echo '==== Extracting preloaded 2011 Ubuntu Xenon OS (no network downloads) ===='
unsquashfs -d "$root" -processors 8 -no-progress "$source_image" > "$dev/extract-v04.log" 2>&1
test -x "$root/usr/bin/Xorg"
test -x "$root/usr/bin/gnome-session"
test -x "$root/usr/sbin/gdm-binary"
test -f "$root/usr/lib/xorg/modules/drivers/xenosfb_drv.so"
test -f "$root/etc/init/ubiquity.conf"
test -f "$root/etc/init/gdm.conf"
echo 'ORIGINAL_GRAPHICAL_SOFTWARE_PRESENT'
echo '==== Applying conservative live desktop boot patch ===='
python3 - "$root" "$dev/patch-v04.json" <<'PY'
from pathlib import Path
import sys,json,re
root=Path(sys.argv[1])
manifest=Path(sys.argv[2])
ubiquity=root/"etc/init/ubiquity.conf"
txt=ubiquity.read_text()
regex=r"(?ms)^start on \(starting gdm\s+or starting kdm\s+or starting xdm\s+or starting uxlaunch\)\s*\n"
patched,num=re.subn(regex,"# X360Linux v0.4: auto-start disabled; do not force the installer.\n",txt)
assert num==1,"Failed to identify historical installer Upstart start stanza"
assert "start on" not in patched
ubiquity.write_text(patched)
gdm=root/"etc/gdm/custom.conf"
assert not gdm.exists(),"Refusing to overwrite unexpected existing GDM custom config"
gdm.write_text("""# X360Linux v0.4 â€” automatically enter preinstalled Linux desktop.
# The Ubuntu live user is created by casper at startup.
[daemon]
AutomaticLoginEnable=true
AutomaticLogin=ubuntu
TimedLoginEnable=false
DefaultSession=gnome.desktop
""")
gdm.chmod(0o644)
autostart=[
"etc/xdg/autostart/bluetooth-applet.desktop",
"etc/xdg/autostart/update-notifier.desktop",
"etc/xdg/autostart/print-applet.desktop",
"usr/share/gnome/autostart/gnome-screensaver.desktop",
]
modified=[]
for rel in autostart:
 p=root/rel
 if not p.is_file():continue
 text=p.read_text(errors="replace")
 assert "[Desktop Entry]" in text,rel
 if re.search(r"(?m)^X-GNOME-Autostart-enabled=",text):
  text=re.sub(r"(?m)^X-GNOME-Autostart-enabled=.*$", "X-GNOME-Autostart-enabled=false",text)
 else:text=text.replace("[Desktop Entry]","[Desktop Entry]\nX-GNOME-Autostart-enabled=false",1)
 p.write_text(text)
 modified.append(rel)
# Keep essential Xbox cooling, power, dbus, networking, display and sound services.
slow_services={"pbbuttonsd","kerneloops","speech-dispatcher","ntp","bluetooth","rsync","saned","binfmt-support"}
disabled=[]
for runlevel in "2345":
 d=root/("etc/rc"+runlevel+".d")
 if not d.is_dir():continue
 for item in d.iterdir():
  if not item.is_symlink() or not item.name.startswith("S"):continue
  if any(item.name[3:]==service for service in slow_services):
   disabled.append(str(item.relative_to(root)))
   item.unlink()
# Store a marker inside the live filesystem to validate that this image is v0.4.
marker=root/"etc/x360linux-release"
marker.write_text("X360Linux 0.4.0-alpha\nboot=XEX-XeLL-casper-GDM\ninstall=disabled\ndesktop=GNOME2-live\ntesting=UNVERIFIED_ON_HARDWARE\n")
marker.chmod(0o644)
manifest.write_text(json.dumps({"version":"0.4.0-alpha","base":"Ubuntu 10.10 Xenon PowerPC32",
 "installer_upstart_disabled":True,"gdm_autologin":"ubuntu","gdm_session":"gnome.desktop",
 "autostarts_disabled":modified,"sysv_start_links_disabled":disabled,
 "note":"No NAND changes, no USB persistence proven. Not a modern Debian rootfs."},indent=2)+"\n")
print("INSTALLER_DISABLED_GDM_AUTOLOGIN_CONFIGURED")
print("XDG_AUTOSTART_DISABLED",modified)
print("SYSV_START_SERVICES_DISABLED",disabled)
PY
echo '==== Compressing modified preloaded live root filesystem to SquashFS ===='
mksquashfs "$root" "$tmp/filesystem.squashfs" -noappend -no-progress -comp gzip -b 131072 -processors 8 -Xcompression-level 6
echo '==== Verify compressed Xenon live filesystem contents ===='
unsquashfs -s "$tmp/filesystem.squashfs" | grep -E '(Compression gzip|Block size 131072|Filesystem size)'
unsquashfs -cat "$tmp/filesystem.squashfs" etc/init/ubiquity.conf | grep -q 'X360Linux v0.4: auto-start disabled'
! unsquashfs -cat "$tmp/filesystem.squashfs" etc/init/ubiquity.conf | grep -q '^start on '
unsquashfs -cat "$tmp/filesystem.squashfs" etc/gdm/custom.conf | grep -q 'AutomaticLoginEnable=true'
unsquashfs -cat "$tmp/filesystem.squashfs" etc/gdm/custom.conf | grep -q 'AutomaticLogin=ubuntu'
unsquashfs -cat "$tmp/filesystem.squashfs" etc/x360linux-release | grep -q 'testing=UNVERIFIED_ON_HARDWARE'
unsquashfs -ll "$tmp/filesystem.squashfs" | grep -F '/usr/lib/xorg/modules/drivers/xenosfb_drv.so' > /dev/null
echo 'SQUASHFS_INTEGRITY_AND_DESKTOP_CONFIG_VERIFIED'
cp "$base/default.xex" "$base/xell.bin" "$base/vmlinux" "$base/readme.txt" "$stage/"
cp "$tmp/filesystem.squashfs" "$stage/casper/filesystem.squashfs"
cat > "$stage/LEIA-ME-PRIMEIRO.txt" <<'TXT'
X360Linux v0.4.0-alpha - XEX Linux LIVE pronto no pendrive (EXPERIMENTAL)
=======================================================================
TODO O SISTEMA LINUX JA ESTA DENTRO DO ARQUIVO casper/filesystem.squashfs.
Nao e preciso fazer download ou instalar Linux no console.

RGH/JTAG:
1. Use um pendrive FAT32 e extraia TODOS os arquivos desta pasta na RAIZ.
2. Abra default.xex pelo Aurora. O XEX executa XeLL, que tenta carregar Linux.
3. A tela de instalacao automatica foi desativada neste SquashFS.
4. O GDM esta configurado para entrar como usuario ubuntu no desktop GNOME.
5. Se a tela ficar preta, anote mensagens/foto do boot e mantenha a v0.3.

ABadAvatar:
- Use um pendrive so para ABadAvatar e OUTRO pendrive FAT32 para Linux.
- Coloque estes MESMOS arquivos no pendrive Linux.
- Necessita de ambiente que permita executar arquivos XEX homebrew.
- ESTE TESTE nao foi validado em hardware ABadAvatar.

IMPORTANTE:
* v0.4 e uma tentativa de boot direto, NAO e garantia de desktop funcional.
* O sistema LIVE e somente leitura (nao ha persistencia garantida).
* O Ubuntu 10.10 de 2011 esta obsoleto; nao use logins privados.
* NUNCA grave NAND ou instale no HD interno do Xbox 360.
* NUNCA renomeie xell.bin para updflash.bin ou updxell.bin.
* Nada foi compilado ou executado pelo Xbox nesta preparacao no PC.
* O XEX, XeLL e kernel originais foram preservados por SHA-256.
TXT
cat > "$stage/THIRD-PARTY-NOTICE.txt" <<'TXT'
X360Linux v0.4 is a modified live filesystem based on third-party
Ubuntu 10.10 Xenon PowerPC, GNU/Linux, XeLL and a historical XEX launcher.
These files are not newly built from verified corresponding source.
Upstream source, copyright, redistribution and GPL compliance must be
audited before representing these binaries as a fully redistributable
up-to-date distribution. Do not assume repository license covers them.
TXT
(
 cd "$stage"
 sha256sum default.xex xell.bin vmlinux casper/filesystem.squashfs > SHA256SUMS.txt
)
echo '==== Files ready for direct USB root extraction ===='
du -h "$stage/casper/filesystem.squashfs"
ls -lah "$stage"
echo 'V04_USB_FOLDER_READY'
