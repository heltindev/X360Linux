# X360Linux

**USB-first Linux development for Xbox 360 RGH/JTAG.**

The current hardware-tested path boots an Ubuntu 10.10 desktop directly
from USB on an Xbox 360 Corona Phison. It uses the verified legacy Xenon
kernel, a modified Casper SquashFS without the Ubiquity installer launcher,
and a 3 GiB persistent `casper-rw` filesystem.

## Development checklist

- [ ] **1. Show 0–100% progress from XeLL/XEX until the Linux desktop opens.** Linux-side framebuffer prototypes exist; early XeLL progress is not controllable from `kboot.conf`.
- [x] **2. Boot directly into a Linux desktop without presenting the installer.** Confirmed on Corona Phison on November 8, 2026 using the legacy kernel plus persistent Casper. The custom ext4/initramfs path still black-screens.
- [ ] **3. Confirm persistence across a second physical reboot.** Create a desktop file, reboot, and verify it remains in the `casper-rw` overlay.
- [ ] **4. Enable internet without an Ethernet cable.** Identify and test a supported Wi-Fi adapter, driver and firmware.
- [ ] **5. Build the new X360Linux distribution.** Define its interface, included software, branding and update path.
- [ ] **6. Reduce boot time.** Measure XeLL, kernel and desktop startup on the console.
- [ ] **7. Replace visible Linux boot messages with a graphical loading screen.** Keep a verbose recovery mode.
- [ ] **8. Boot from `default.xex` in Aurora.** The historical XEX still black-screens on this console.

## Active USB layout

```text
BOOT-DIRETO/
├── kboot.conf                    # one automatic persistent entry, timeout=0
├── vmlinux                      # verified legacy Xenon PowerPC kernel
├── casper-rw                    # 3 GiB writable persistent ext3 overlay
├── casper/
│   └── filesystem.squashfs      # Ubuntu desktop; Install launcher removed
├── x360linux.elf                # preserved experimental kernel
└── distros/ubuntu-x360/
    ├── vmlinux
    ├── initrd.gz
    ├── ROOTFS.ID
    └── rootfs.ext4              # preserved experimental preinstalled root
```

## Confirmed hardware result

On November 8, 2026:

- experimental entries 0 and 1 produced a black screen;
- the original legacy entry 2 opened the Ubuntu desktop;
- the visible **Install** launcher was removed in the rebuilt SquashFS;
- the rebuilt system automatically opened the desktop on real hardware;
- `stderr error 0` and `can't open /dev/sr0: No medium found` were visible
  but did not prevent the desktop from opening.

The `/dev/sr0` warning means the live system looked for optical media and
found none. Persistence is prepared and PC-verified, but retention after a
physical reboot still needs confirmation.

## XeLL limitation

The active `kboot.conf` uses one English entry and `timeout=0`. The words
**XeLL Main Menu** may flash briefly because they are rendered by XeLL itself.
Removing that firmware screen would require changing the installed XeLL/NAND,
which this project intentionally does not do.

## Release

The current source/configuration release is
[**v0.5.0-persistent-alpha**](RELEASE-v0.5.0-persistent-alpha.md).
Large USB images are not committed to Git. Build instructions are provided in
[scripts/casper-persistent/build-persistent.sh](scripts/casper-persistent/build-persistent.sh).

## Documentation

[Persistent USB design](docs/PERSISTENT-USB-LEGACY-KERNEL.md) ·
[Hardware test log](docs/V041-CORONA-TEST-2026-11-08.md) ·
[Credits and licenses](docs/CREDITS.md)
