# Roadmap — from experimental integration to practical Linux

The goal is **progressively verified, reliable function**, not a premature claim of 100% compatibility.

## XWT Boot & native Linux pipeline (experimental)

- [x] Create source for an independent LibXenon `xwtboot.elf32` app with a controller menu, FAT folder selection and saved boot parameters.
- [x] Add Actions that cross-compile a reference XeLL and the XWT Boot ELF.
- [x] Add an ISO9660 XWT Boot launcher image generator (not Linux).
- [x] Add a PowerPC64 big-endian BusyBox initramfs source/build workflow.
- [x] Add a manual workflow for combined Xenon Linux kernel + userspace + candidate ISO.
- [ ] Obtain passing **all** rootfs and complete kernel cross-builds.
- [ ] Test XWT Boot interface, FAT settings and Linux ELF/FDT handoff on real hardware.
- [ ] Confirm custom X360Linux boot media reaches an interactive Linux shell.
- [ ] Validate Ethernet, video, audio and multiple Xbox 360 motherboard revisions.

## Milestone 0 · Foundation

- [x] Create attractive GitHub project landing page with transparent status.
- [x] Pin Free60 XeLL, Xenon Linux patch and Xenos GPU projects as Git submodules.
- [x] Publish safe, reproducible host-side kernel/module build helpers.
- [x] Document exact upstream version and license boundaries.
- [ ] Cross-build Linux 6.18.58 end-to-end and archive redacted logs.
- [ ] Add an auditable build artifact manifest with checksums.

## Milestone 1 · First boot

- [ ] Confirm compatible XeLL boot entry and kernel ELF format on a real console.
- [ ] Boot to Linux shell and capture full kernel messages.
- [ ] Verify USB keyboard, storage, Ethernet, RAM and safe shutdown.
- [ ] Test hardware variants individually.

## Milestone 2 · GPU acceleration

- [ ] Build `xegpu.ko` for our kernel, initialize EDRAM and load the module.
- [ ] Build Xenos-forked Mesa and big-endian Xorg/glamor.
- [ ] Display a hardware-accelerated IceWM desktop on a real Xbox.
- [ ] Re-run GLES2 and Piglit tests with reproducible measurements.
- [ ] Investigate GPU resets, hangs and security of command submission.

## Milestone 3 · Daily usability

- [ ] Verify audio output by listening on connected TV and headphones.
- [ ] Implement resilient USB/storage mounting and simple networking setup.
- [ ] Find a low-memory browser path that handles forms and real websites.
- [ ] Test video playback and controller/gamepad support.
- [ ] Package a compact rootfs that fits within practical memory limits.

## Milestone 4 · Safe distribution

- [ ] Script a reversible USB or network boot package with checksums.
- [ ] Confirm clear recovery path and **no NAND-writing installer**.
- [ ] Release only after hardware compatibility tables and repeated boot tests.
- [ ] Record software/component provenance and license notices.
- [ ] Provide user-friendly, multilingual installation instructions.

## Long-term research (not promised)

- Better graphics-driver architecture; GPU reset and alternative HDMI modes.
- Stability of 4 KB-page kernels and memory improvements.
- Broader OpenGL capability, sound, network and application compatibility.

Every checkbox must be grounded in **test evidence from X360Linux**, not just upstream claims.
