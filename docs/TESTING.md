# Getting started — X360Linux on Xbox 360

**Choose your version:**

- **[v0.3.0-alpha — Debian USB](https://github.com/heltindev/X360Linux/releases/tag/v0.3.0-alpha)**. See the [USB Debian guide](USB-DEBIAN-BOOT.md) for startup and recovery.

- **[v0.1.0-alpha — X360Boot menu test](https://github.com/heltindev/X360Linux/releases/tag/v0.1.0-alpha):** the menu has appeared on a real Xbox 360. This version does not include Linux boot files.
- **[v0.2.0-alpha — experimental Linux shell boot](https://github.com/heltindev/X360Linux/releases/tag/v0.2.0-alpha):** includes the Xenon kernel, device tree, BusyBox shell, and optional ISO. The Linux kernel and BusyBox `#` shell prompt have now **been confirmed on real RGH hardware**. Keyboard input and controlling TTY are still being tested.

## Which ZIP do I need?

**If your Xbox 360 has RGH or JTAG:** download the ZIP named **RGH-USB**.

**If you already have ABadAvatar/BadUpdate with FreeMyXe:** download the ZIP named **ABadAvatar-FreeMyXe-USB**. This is **not** a standalone exploit and does not unlock a stock console.

## RGH/JTAG — 4 steps

1. Prepare a USB drive with **FAT32**. Formatting erases files: make a backup first.
2. **Extract your ZIP directly onto the USB drive.** You should see `xenon.elf` at the top of the drive.
3. Plug it into your Xbox 360 and start your existing **XeLL** (often with **Eject**).
4. If the standard `X360Linux/` folder is present, **X360Boot automatically starts Linux after about three seconds**. No button is required. Press **B** during the countdown only if you need to return to the menu.

**For the updated v0.2.0-alpha:** the standard USB folder is detected automatically. X360Boot starts Linux without pressing A. **B cancels during the 3-second window**; if you cancel, press **A** on `X360Linux` to start manually. The bar shows preparation steps, not guaranteed boot success.

## ABadAvatar/BadUpdate + FreeMyXe — 4 steps

1. **Keep your existing exploit/FreeMyXe files** on the FAT32 USB drive. Do not delete them.
2. Extract your **ABadAvatar-FreeMyXe** ZIP onto that same USB drive. **Merge** the `BadUpdatePayload` folder instead of replacing it. Back up an existing `xell-2f.bin` before replacing it.
3. Run your normal exploit and choose **Launch XeLL** in FreeMyXe.
4. After XeLL launches X360Boot, it should detect `X360Linux/` and begin the Linux boot automatically. **B during the 3-second countdown** keeps the menu available.

These steps are specifically for **FreeMyXe**. Other software exploit setups may require their own XeLL configuration.

## What should be on the USB drive?

For **v0.2.0-alpha RGH/JTAG**, extracting the ZIP creates:

```text
USB drive/
├── xenon.elf
├── X360Linux/
│   ├── vmlinux
│   ├── xenon.dtb
│   └── initramfs.cpio.gz
└── READ-ME-FIRST.txt
```

The **ABadAvatar-FreeMyXe ZIP** adds `BadUpdatePayload/xell-2f.bin` without including the rest of the exploit. It must be merged into your **existing** exploit setup.

## What about the ISO?

The optional `.iso` on v0.2 is an **experimental ISO9660 image** containing Linux boot files for compatible XeLL optical boot methods. It is **not** a PC installer. **Do not copy the ISO file to a USB drive expecting it to start**; extract one of the USB ZIP packs instead.

## Controller and Linux status

- **Autostart:** if the standard Linux files are present, X360Boot waits three seconds and begins booting automatically. Press **B** to cancel. The menu still supports D-pad, A, B and LB/RB. No settings or Xbox HDD contents are written. The progress bar only shows preparation stages, not Linux execution.
- **Inside Linux**, the PowerPC32 BusyBox `#` shell prompt has been reached on real RGH hardware. Connect a **USB keyboard** to test commands. The earlier `can't access tty` message comes from `/dev/console`; the updated `cttyhack` shell may fix job control, but this needs hardware verification. Controller input, graphics acceleration, audio, network and storage persistence remain unverified.
- **Debian PPC64**, a desktop, browser and image/video players are future work. This alpha tests a minimal **PowerPC32 BusyBox** userspace with a **64-bit Xenon kernel**, after a CPU illegal instruction in the older PowerPC64 build.

## How to report a test

If Linux opens a shell, run:

```sh
uname -a
cat /proc/cpuinfo
cat /proc/meminfo
dmesg
```

A photo of the screen or a boot log is useful if the Linux boot fails or freezes. Share the Xbox model and XeLL setup if known, but **never share console keys, firmware dumps or private identifiers**.

**Safety:** Do not flash to NAND, rename files to `updxell.bin` or `updflash.bin`, or format your Xbox 360 internal HDD.

Source licenses and dependencies: [Credits & licenses](CREDITS.md).
