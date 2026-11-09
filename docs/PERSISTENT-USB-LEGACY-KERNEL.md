# Persistent USB boot using the verified legacy kernel

## Hardware result

On November 8, 2026, both experimental ext4 entries produced a black
screen on the Xbox 360 Corona Phison. The original legacy `vmlinux`
successfully opened the Ubuntu 10.10 desktop, but that desktop was the
Casper live environment and displayed the Ubiquity **Install** launcher.

The active USB therefore uses the known-working legacy kernel with Casper
persistence instead of the unproven custom initramfs path.

## Active layout

- `vmlinux`: unchanged legacy kernel that boots on the console.
- `casper/filesystem.squashfs`: rebuilt with the Ubiquity desktop
  launcher removed.
- `casper-rw`: 3 GiB ext3 filesystem labeled `casper-rw`; stores the
  writable persistent overlay.
- `kboot.conf`: one English entry, `timeout=0`, and the kernel argument
  `persistent`.

The previous experimental `x360linux.elf` and preinstalled
`rootfs.ext4` remain on the USB for recovery and research, but they are
not selected by the active menu.

## XeLL limitation

`kboot.conf` removes the wait and immediately selects the working entry.
The words **XeLL Main Menu** come from XeLL itself and may flash briefly.
Removing that firmware screen would require changing the installed XeLL,
which is intentionally out of scope because this project does not flash
NAND.

## Verification boundary

The SquashFS, ext3 persistence image and USB copies were verified on the
PC. The legacy kernel is proven to reach the desktop. Persistence and the
removed installer launcher still require one physical reboot test on the
Xbox before being marked confirmed.
