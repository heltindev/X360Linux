# X360Linux roadmap — v0.3 to v0.4

## Verified and reported milestones

- [x] Earlier X360Boot/Xenon experiments reached a BusyBox shell on RGH hardware.
- [x] Earlier independent Debian Ports experiments reached Debian shell on hardware.
- [x] **November 8, 2026 CORRECTION:** Corona Phison RGH starts NAND XeLL via Eject. The legacy Aurora `default.xex` goes to a **black screen**; prior XEX success claim was inaccurate.
- [ ] A direct USB graphical desktop without installer is **not yet confirmed** for that legacy XEX package.
- [ ] USB persistence, keyboard/mouse, controller, wired Internet, sound and video require individual tests.

## v0.4 — direct boot distribution

**Goal:** Aurora `default.xex` → compatible XeLL → kernel → initramfs → USB Linux root filesystem → graphical desktop. No manual Linux install, NAND changes or console commands.

1. **Freeze tested boot files.** Keep SHA-256 verified copies of legacy `default.xex`, `xell.bin`, `vmlinux` and `casper/filesystem.squashfs`. Never mix them with the unrelated experimental Debian release binaries.
2. **Observe the actual startup.** Record full boot log and determine what launches the installer (Ubuntu Ubiquity or other), the kernel arguments, video/USB detection and exact Xbox model.
3. **Direct Linux from USB.** Experiment on a filesystem *copy* to disable installer auto-start, mount rootfs automatically, and have a safe recovery console when desktop startup fails.
4. **Persistent settings.** Test ext4 USB persistence without formatting Xbox internal storage; save, power down and restart with file verification.
5. **Modern distro.** Test maintainable, signed **Debian Ports 32-bit big-endian PowerPC** userspace, subject to Xenon kernel/ABI compatibility and upstream support. The 2011 Ubuntu 10.10 archive itself is not a secure production base.
6. **Desktop and RAM.** Target **Openbox + LXPanel + PCManFM (not IceWM)**, X.Org/framebuffer as supported, within 512 MiB RAM.
7. **Hardware features.** Validate keyboard, USB mouse, Ethernet/DHCP, Xbox gamepad-as-pointer, native audio, then video acceleration. Each one must be proven on the Xbox 360 before release.
8. **Local development only.** Work in `BOOT-DIRETO/v0.4-dev` on Windows + WSL2. No GitHub Actions requirement. Preserve the prior 3.3 GB unverified Debian image untouched.

## Release gates

- [ ] Direct USB desktop shown in a video or real-console logs.
- [ ] Usable keyboard/mouse and successful clean shutdown.
- [ ] Root filesystem and settings survive complete power cycle.
- [ ] Accurate hardware compatibility table and source-license audit.
- [ ] Stable v0.4 public release only after essential hardware tests. The alpha preview is experimental and labelled untested.

**Safety:** No NAND flashes, no Xbox HDD installation, no unverified claims of modern software compatibility.

See [v0.3 legacy XEX guide](V03-LEGACY-XEX.md), [credits](CREDITS.md) and [release page](https://github.com/heltindev/X360Linux/releases/tag/v0.3.0-alpha).


## Technical investigation - v0.4 experiment 01 (2026-11-08)

Inspection of the historical Ubuntu 10.10 SquashFS found
etc/init/ubiquity.conf. Its Upstart installer job is enabled when
kernel command-line flags include only-ubiquity, maybe-ubiquity or
automatic-ubiquity. The actual Xbox kernel command line has NOT yet been
observed in a physical test.

A local experimental COPY of the filesystem disables only the automatic
start condition for that installer job. The XEX, XeLL and kernel stay
unchanged. This is not proof that GDM or a graphical desktop boots.

## v0.4.0-alpha build status (2026-11-08)

- [x] Preserve v0.3 XEX, XeLL and kernel checksums.
- [x] Repack the already-preloaded Ubuntu live SquashFS with Ubiquity disabled.
- [x] Enable GDM automatic ubuntu live login and trim optional background services.
- [x] Verify rebuilt SquashFS contents and packaged USB ZIP on the Windows PC.
- [ ] Confirm direct-to-graphical-desktop boot on a real RGH Xbox 360.
- [ ] Measure startup time, then identify actual bottlenecks before further optimization.
- [ ] Verify USB keyboard, mouse, Xbox gamepad, networking and audio.
- [ ] Implement and validate writable USB persistence.
- [ ] Validate two-pendrive ABadAvatar startup.

This experimental 2011 Ubuntu live image is not a persistent Debian installation.

## v0.4 offline DHCP and 0-100% splash - TODO

- [ ] Fix no-cable DHCP delay at the XeLL stage; see issue #1.
- [ ] Prototype graphical 0-100% Linux Plymouth progress after framebuffer initialization; see issue #2.
- [ ] Keep logs visible in a diagnostic mode, and measure boot on real hardware before updating binaries.

See [engineering notes](V04-DHCP-SPLASH.md). Current alpha ZIP is NOT modified.

## Real-world v0.4 status and multi-distro architecture

A complete 0-100% splash, USB persistence, usable Wi-Fi, faster startup, generic ISO boot and a multi-distro selector are **NOT implemented**. The Linux rootfs is compressed SquashFS, not an uncompressed ext4 install. Use the **Corona Eject XeLL** as the baseline: Aurora XEX fails.

See [verified status and new architecture](V04-STATUS-AND-MULTIDISTRO.md). Hardware blocker: https://github.com/heltindev/X360Linux/issues/3.

## v0.4.1-dev preinstalled ext4 stage (PC-built, hardware untested)

- [x] Build 3-GiB unpacked Ubuntu PowerPC ext4 root image.
- [x] Build PPC32 custom external initrd with USB detection, loop root mount and rescue shell.
- [x] Add XeLL normal/diagnostic/legacy menu and framebuffer milestone progress bar.
- [x] Clean obsolete local logs, caches and verified duplicate expanded packages.
- [ ] Test actual Corona Phison GUI and writable rootfs via Eject XeLL.
- [ ] Fix Aurora XEX black screen, early XeLL DHCP delay and wireless drivers.
- [ ] Validate 0-100% from XeLL through desktop and measure actual boot time.
- [ ] Add another compatible Xenon PowerPC Linux userland.

[Detailed implementation](V041-EXT4-BOOT-EXPERIMENTAL.md).

## Local USB boot repair verification

The PowerPC initrd now accepts an explicit distro name and root marker; the XeLL menu passes these arguments. Plymouth callback ordering was fixed in the source and local ext4 Ubuntu image. These are PC-verified changes, not a confirmed successful boot on Corona Phison RGH. Wireless networking, XeLL offline DHCP, faster boot and Aurora default.xex remain open. [Details](V041-REPAIR-LOG.md).

## Corona Phison boot test 2026-11-08

- [x] Physical Eject XeLL menu and legacy Ubuntu Live/installer boot confirmed.
- [x] Experimental embedded-initramfs PowerPC kernel and preinstalled ext4 image prepared on PC and USB.
- [ ] Verify that the new kernel reaches the preinstalled Ubuntu desktop on Corona Phison.
- [ ] Verify persistence, input drivers, startup speed and Wi-Fi.
- [ ] Fix Aurora default.xex black screen.

[Details](V041-CORONA-TEST-2026-11-08.md).
