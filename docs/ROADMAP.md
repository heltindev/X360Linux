# X360Linux development roadmap

**Current goal:** Make the BusyBox shell fully interactive with a USB keyboard, then work toward an actual graphical distribution. The kernel and `#` shell prompt have already been verified on a real Xbox 360; console input and TTY behavior still need testing.

## 1. First Linux boot (current milestone)

- [x] Compile the native Xbox 360 X360Boot ELF launcher.
- [x] Open the X360Boot menu with the Xbox 360 controller on real RGH hardware.
- [x] Compile an experimental Linux 6.18.58 Xenon kernel and device tree.
- [x] Start the Linux kernel on real Xbox 360 hardware; it reached the initramfs at `/init`.
- [x] Identify the original BusyBox PowerPC64 illegal-instruction failure.
- [x] Build a conservative static PowerPC32 BusyBox and smoke-test it under PowerPC emulation.
- [x] Simplify X360Boot: detect the X360Linux folder and autostart after a short, B-to-cancel delay.
- [x] **Reach the PowerPC32 BusyBox `#` shell prompt on a real RGH Xbox 360** (photo verified).
- [ ] **Verify USB keyboard interaction and controlling TTY**, with BusyBox `cttyhack`.
- [ ] Confirm reliable reboot, logs and failure recovery.

## 2. Reliability and storage

- [ ] Validate wired and wireless Xbox 360 controllers inside Linux, separately from X360Boot.
- [ ] Test USB keyboard, mouse and storage in the Linux system.
- [ ] Initialize wired Ethernet automatically with DHCP.
- [ ] Add persistent storage so settings and files survive power-off.
- [ ] Test safe internal HDD access without formatting Xbox partitions or deleting games.
- [ ] Improve video, audio, graphics and other hardware support across Xbox 360 models.

## 3. Our own lightweight X360Linux distribution

- [ ] Evaluate Debian PPC64 big-endian packages without assuming they work on Xenon.
- [x] Implement the initial C framebuffer desktop, image viewer, silent X36V player and Linux input mapping.
- [ ] Test X360Desk framebuffer, gamepad cursor and media on a physical RGH console; optimize for 512 MB RAM.
- [x] Build an initial JPG/PNG/BMP image viewer, silent raw X36V player and analog-stick cursor.
- [ ] Add actual MP4/H.264 decode, sound, production video performance and a full desktop after console tests.
- [ ] Add software installation and updates.
- [ ] Investigate a compatible web browser with modern TLS.
- [ ] Make beginner-friendly USB releases and consider an HDD installer only after persistence is safe and tested.

## 4. Final milestone — XEX

- [ ] Only after the XeLL Linux boot and distribution work reliably, develop a `default.xex` launcher.
- [ ] Test an XEX-to-Linux handoff from Aurora on physical Xbox 360 hardware.
- [ ] Keep a known-working XeLL recovery route.

**Important:** A green GitHub Actions build or a progress percentage does not prove Linux boots successfully. The launcher reports file-preparation milestones; kernel failures must remain visible for debugging. Never flash test files to NAND.
