# X360Linux v5.0.0 — Persistent USB Direct Boot

Release date: November 8, 2026

## What works on real hardware

Tested on an Xbox 360 Corona Phison:

- boot from XeLL/Eject;
- automatic selection with `timeout=0`;
- Ubuntu desktop opens without a menu choice or manual command;
- Ubiquity **Install** launcher removed;
- persistent `casper-rw` file included;
- no NAND flash and no Xbox internal HDD modification.

The working kernel is **Linux 2.6.36.2-xenon** for 32-bit big-endian PowerPC/Xenon.

## Download assets

Download and extract all three ZIP packages into the same FAT32 USB root:

1. `X360Linux-v5.0.0-USB-BOOT.zip`
2. `X360Linux-v5.0.0-USB-PERSISTENCE.zip`
3. `X360Linux-v5.0.0-USB-EXPERIMENTAL-ROOTFS.zip`

Allow folders to merge. Do not place the ZIP files themselves on the Xbox USB drive.

The BOOT package contains the verified direct-boot path. The PERSISTENCE package contains `casper-rw`. The EXPERIMENTAL-ROOTFS package preserves the custom ext4 image for development; it is not used by the confirmed default boot.

Use `SHA256SUMS.txt` to verify downloaded packages.

## Known messages

The boot may show:

```text
stderr error 0
can't open /dev/sr0: No medium found
```

These messages did not prevent the desktop from opening. The `sr0` message is the live environment checking for optical media when no disc is present.

## Current test status

Direct boot to the desktop is physically confirmed. Persistence is prepared and host-verified, but retention across a second physical Xbox reboot is not yet confirmed.

## Safety scope

This release only uses files on the USB drive. It does not flash NAND and does not modify the Xbox internal HDD.
