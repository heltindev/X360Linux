# X360Linux roadmap

The priority is **a real boot on Xbox 360 hardware**, not extra features or a polished desktop that cannot start.

## 1. First Linux boot
- [x] Cross-compile X360Boot native ELF for Xbox 360.
- [x] Cross-compile a minimal PowerPC64 big-endian Linux userspace.
- [x] Cross-compile XeLL as a known initial loader.
- [ ] Successfully build and package a matching Xbox 360 Linux kernel.
- [ ] Boot Linux on an actual RGH/JTAG Xbox 360.
- [ ] Reach a shell and save the boot logs.

## 2. Make it reliable
- [ ] Test FAT32 USB loading and saved X360Boot configuration.
- [ ] Test the console's CPU, memory, USB, SATA/HDD and networking.
- [ ] Validate video output and GPU acceleration.
- [ ] Test sound and controller support.
- [ ] Test on more Xbox 360 motherboard revisions.

## 3. Build our own distribution
- [ ] Set up an Xbox 360-native root filesystem with shell and tools.
- [ ] Add a small desktop and package management.
- [ ] Publish a complete Linux boot folder and ISO after successful hardware tests.

## 4. Later
- [ ] Optional XEX launcher for consoles able to execute it.
- [ ] Easy installation and configuration without modifying NAND.
- [ ] Continue as an open-source community project.

**Hardware compatibility must be tested before describing any milestone as fully working.**
