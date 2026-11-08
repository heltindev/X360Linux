# X360Linux roadmap — v0.3 to v0.4

## Verified and reported milestones

- [x] Earlier X360Boot/Xenon experiments reached a BusyBox shell on RGH hardware.
- [x] Earlier independent Debian Ports experiments reached Debian shell on hardware.
- [x] **November 8, 2026:** The maintainer launched the **legacy `default.xex` successfully** on a real RGH Xbox 360 and reached the Linux startup/installer flow.
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
- [ ] v0.4 public download only after all essential tests pass.

**Safety:** No NAND flashes, no Xbox HDD installation, no unverified claims of modern software compatibility.

See [v0.3 legacy XEX guide](V03-LEGACY-XEX.md), [credits](CREDITS.md) and [release page](https://github.com/heltindev/X360Linux/releases/tag/v0.3.0-alpha).
