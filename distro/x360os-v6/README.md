# X360OS v6 — Xbox 360 console-style Ubuntu

**Status: local development prototype. NOT tested on a real Xbox yet.** The existing v5.0.0 release stays unchanged.

X360OS v6 reuses the working 32-bit big-endian PowerPC Ubuntu 10.10 Casper system and the original Xenon Linux 2.6.36.2 kernel. It does **not** install Steam or replace XeLL.

## What's implemented in source

- Dark green 10-foot-style GTK2 home screen: Browser, Files, Apps, Network, Videos, Music, Documents, Settings, Desktop.
- Controller input daemon for USB /dev/input/js* using X11/XTest. D-pad moves focus; A opens. X switches to analog mouse mode; A/B click in mouse mode; Y opens the on-screen browser URL keyboard. Buttons and axis mapping **require Xbox hardware calibration**.
- Browser action opens bundled legacy Firefox 3.6, with an on-screen URL keyboard. It is **not** a modern or secure web browser.
- Ethernet settings via bundled NetworkManager. Actual Xbox 360 networking/DNS/HTTPS is **not yet tested**.
- Existing Ubuntu tools remain: Nautilus, Gedit, Evince, Totem, Rhythmbox, GNOME Terminal, System Monitor, and Control Center.
- A lightweight X session launches Metacity, the home screen and controller daemon without the full GNOME session. F10 exits into the classic GNOME desktop for recovery.
- The old automatic XeLL kernel boot is unchanged, and no NAND or internal HDD modifications are performed.

## Local build (never GitHub Actions)

Use WSL Ubuntu with `squashfs-tools` installed on a Windows computer that contains the working v5 `BOOT-DIRETO` folder.

```bash
bash distro/x360os-v6/build-local.sh "/mnt/c/Users/USERNAME/Desktop/PEN DRIVE/BOOT-DIRETO" "/mnt/c/Users/USERNAME/Desktop/PEN DRIVE/work/release-v6"
```

Then produce a separate, **unverified** USB development ZIP:

```bash
python3 distro/x360os-v6/pack-local.py --v5-boot "PATH/TO/X360Linux-v5.0.0-USB-BOOT.zip" --v5-persistence "PATH/TO/X360Linux-v5.0.0-USB-PERSISTENCE.zip" --new-squashfs "PATH/TO/release-v6/filesystem.squashfs" --output "PATH/TO/release-v6/X360OS-v6.0.0-DEV-UNTESTED.zip"
```

`python3 distro/x360os-v6/test_host.py` runs non-hardware sanity checks. The build must fail rather than overwrite an existing output.

## Acceptance tests on Xbox hardware

1. First boot opens the X360OS home; F10 can recover classic Ubuntu.
2. Wired controller appears in `/dev/input/js*`; D-pad, A, B and mouse mode function.
3. Browser opens; it loads a simple website if the old TLS stack permits it.
4. Ethernet gets an IP, DNS works, and a simple HTTP/HTTPS request succeeds.
5. Settings and files survive a cold reboot, with the Casper overlay tested.
6. Measure idle RAM and browser RAM on 512 MB hardware before optimizing.
7. Verify audio, shutdown safety and power behavior.

**Known limitation:** Ubuntu 10.10 is end-of-life. Do not sign in to personal accounts on its Firefox 3.6 browser. Modern browsing is a separate porting/kernel-upgrade milestone. The console's internal wireless controller support is unknown.

For upstream X360OS roadmap, see [X360OS ROADMAP](../../docs/X360OS-ROADMAP.md).
