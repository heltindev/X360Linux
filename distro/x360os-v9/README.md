# X360OS v9.0 — Xbox 360 genuine native embedded boot experiment

## Root cause uncovered after v8 failed to start on the real console

The earlier v8 carried no *external* Ubuntu filesystem, but the **original 11.7MB Xenon kernel (`vmlinux`) still contained its own embedded compressed Ubuntu/Casper root environment.** That was a substantial oversight.

We examined the exact original kernel used by the successful Ubuntu video test. Its ELF32 PowerPC big-endian section `.init.ramfs` occupies **4,456,709 bytes** (offset `0x5ee790`), starting with **2,160 zero padding bytes**, followed by LZMA-alone compressed content. That content decompresses to **15,888,384 bytes** of newc CPIO, including **316 old archive entries** with Ubuntu/Casper paths. The original kernel's `CONFIG_INITRAMFS_SOURCE=""` extracted from the Ubuntu rootfs is misleading for the actual kernel binary; the ELF itself is the evidence.

### What v9 actually changes

`patch-embedded-kernel.py` verifies the exact original Xenon kernel SHA256, parses ELF section headers and substitutes **the entire built-in LZMA Ubuntu/Casper archive** with a smaller standalone X360OS newc archive packed in LZMA-alone. Only the bytes belonging to `.init.ramfs` change. The section's original size, alignment, exact first 2160 zero bytes, load addresses, file length and all other ELF bytes are retained.

The new archive contains **437 entries** and decompresses to **2,159,328 bytes**: a standalone `/init`, static PPC32 musl + BusyBox, Free60 input kernel modules and the original C-based **X360OS** dashboard with Xenos 32x32 tile addressing. It has **no Ubuntu/Casper/GNOME/Xorg/GTK/Python/APT/dpkg root filesystem files**. We use the Free60 Linux kernel and Xenon-compatible kernel modules, not the Ubuntu distribution. The **kernel executable is a new experimental patched file, not the unmodified proven-v5 binary**, but its non-initramfs bytes and metadata are unchanged.

This completely removes the need for an **external** `initrd=...` argument, whose loading was never confirmed to work on this console. The boot chain is simply:

```text
Xbox 360 Eject -> XeLL -> uda:/vmlinux (same ELF32 PPC layout,
                                      replaced built-in .init.ramfs)
                -> kernel unpacks original X360OS-only LZMA CPIO
                -> /init (X360OS PID 1)
                -> /usr/bin/x360os-ui (PowerPC C, native Xenos framebuffer)
```

`kboot.conf` uses `rdinit=/init console=tty0 loglevel=7`; messages should appear on the TV rather than being routed primarily to the serial console. Boot does not require Ethernet or Wi-Fi, and the XeLL's DHCP warning occurs before Linux.

## Independent verification

`verify-v9.py` checks the original ELF against the patched version, verifies all ELF headers and sections, compares all bytes outside the embedded initramfs, decompresses both LZMA streams, confirms old Ubuntu files no longer exist in the guest archive, checks X360OS CPIO equals the already tested native v8 CPIO, and validates SHA256s and the new `kboot.conf`.

The original Free60 `vmlinux` file is never overwritten; `patch-embedded-kernel.py` refuses an unknown kernel and overwrites no files.

**Limitations:** No physical boot test has been possible yet for this v9. This is an engineering attempt to correct a demonstrated issue, not a guarantee of hardware success. The framebuffer pitch/tile implementation, internal Xbox wireless gamepad, audio, Wi-Fi and program launcher still need real-console testing. Legacy PPC kernel compatibility with static musl 1.2.5 also needs hardware confirmation. The 3.67MB of remaining `.init.ramfs` space is padded with zeros as allowed by the Linux 2.6.36 initramfs parser; its physical boot behavior is unverified.

## Build on the PC (not GitHub Actions)

```sh
python3 distro/x360os-v9/build-v9.py ORIGINAL-XELL-VMLINUX NATIVE-X360OS-INITRD-GZIP NEW-OUTPUT-DIR
python3 distro/x360os-v9/verify-v9.py ORIGINAL-XELL-VMLINUX NATIVE-X360OS-INITRD-GZIP NEW-OUTPUT-DIR
```

The native initramfs input comes from v8's musl/BusyBox/C PowerPC source build; **it is not reused from Ubuntu**. The original Free60 kernel itself was previously patched for Xenon and retains its Linux licensing. All commands run on the local workstation with WSL, never on GitHub Actions.

### First real-console test

Use a **different FAT32 pendrive**, copy the contents of the v9 output folder to its root and boot XeLL via Eject. Do **not** copy old `casper`, `casper-rw` or `initrd-x360os.gz`, and do not flash the NAND or change Xbox internal HDD. A user should not need to type commands.

If the console does not load, a photo of the **last visible message** will reveal whether the failure is XeLL's ELF load, Linux initramfs unpack, an early `/init` error, or framebuffer initialization. Preserve the working video USB as a recovery option.

Source references: [Free60 XeLL/Xenos loader](https://github.com/Free60Project/xell-reloaded) and [Linux 2.6.36 `init/initramfs.c`](https://github.com/torvalds/linux/blob/v2.6.36/init/initramfs.c).
