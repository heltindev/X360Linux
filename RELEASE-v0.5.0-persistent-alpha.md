# X360Linux v0.5.0-persistent-alpha

Release date: November 8, 2026

## Confirmed on Xbox 360 Corona Phison

- XeLL/Eject automatically selects the legacy Xenon kernel with `timeout=0`.
- The Ubuntu 10.10 desktop opens on real hardware.
- The Ubiquity **Install** desktop launcher is absent.
- No NAND flash or Xbox internal HDD modification is required.
- The experimental custom-initramfs entries remain documented as black-screen failures.

## Persistent USB design

This release adds the kernel argument `persistent` and a 3 GiB ext3 image
named and labeled `casper-rw`. The writable overlay is intended to preserve
files and settings on the USB drive.

The overlay passes host-side filesystem checks. Persistence across a physical
Xbox reboot is not yet confirmed; that is the next hardware test.

## Known messages

The boot may print:

```text
stderr error 0
can't open /dev/sr0: No medium found
```

The desktop still opens. The `sr0` warning is the live environment checking
for optical media when no disc is present.

## Files published in this tag

- automatic English `kboot.conf.example`;
- reproducible persistent SquashFS/`casper-rw` build script;
- hardware result and persistent USB documentation.

The 619 MiB SquashFS and 3 GiB persistence image are intentionally not stored
in the Git repository. GitHub automatically provides source archives for this
tag.
