# X360Linux development roadmap

**Current goal:** Start an interactive Linux shell on a real Xbox 360 through XeLL. Only verified console behavior is marked as working.

## 1. First Linux boot (current milestone)

- [x] Compile the native Xbox 360 X360Boot ELF launcher.
- [x] Open the X360Boot menu with the Xbox 360 controller on real RGH hardware.
- [x] Compile an experimental Linux 6.18.58 Xenon kernel and device tree.
- [x] Start the Linux kernel on real Xbox 360 hardware; it reached the initramfs at `/init`.
- [x] Identify the original BusyBox PowerPC64 illegal-instruction failure.
- [x] Build a conservative static PowerPC32 BusyBox and smoke-test it under PowerPC emulation.
- [x] Simplify X360Boot: highlight the X360Linux folder, press A once, attempt Linux boot.
- [ ] **Prove that the new PowerPC32 BusyBox reaches a usable interactive shell on a real Xbox 360.**
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
- [ ] Build a low-memory desktop suitable for 512 MB RAM.
- [ ] Add picture viewing, practical video playback and controller-friendly navigation.
- [ ] Add software installation and updates.
- [ ] Investigate a compatible web browser with modern TLS.
- [ ] Make beginner-friendly USB releases and consider an HDD installer only after persistence is safe and tested.

## 4. Final milestone — XEX

- [ ] Only after the XeLL Linux boot and distribution work reliably, develop a `default.xex` launcher.
- [ ] Test an XEX-to-Linux handoff from Aurora on physical Xbox 360 hardware.
- [ ] Keep a known-working XeLL recovery route.

**Important:** A green GitHub Actions build or a progress percentage does not prove Linux boots successfully. The launcher reports file-preparation milestones; kernel failures must remain visible for debugging. Never flash test files to NAND.
