# Getting started — X360Linux on Xbox 360

**Choose your version:**

- **[v0.1.0-alpha — X360Boot menu test](https://github.com/heltindev/X360Linux/releases/tag/v0.1.0-alpha):** the menu has appeared on a real Xbox 360. This version does not include Linux boot files.
- **[v0.2.0-alpha — experimental Linux shell boot](https://github.com/heltindev/X360Linux/releases/tag/v0.2.0-alpha):** includes the Xenon kernel, device tree, BusyBox shell, and optional ISO. The Linux shell has **not yet been verified on real Xbox 360 hardware**.

## Which ZIP do I need?

**If your Xbox 360 has RGH or JTAG:** download the ZIP named **RGH-USB**.

**If you already have ABadAvatar/BadUpdate with FreeMyXe:** download the ZIP named **ABadAvatar-FreeMyXe-USB**. This is **not** a standalone exploit and does not unlock a stock console.

## RGH/JTAG — 4 steps

1. Prepare a USB drive with **FAT32**. Formatting erases files: make a backup first.
2. **Extract your ZIP directly onto the USB drive.** You should see `xenon.elf` at the top of the drive.
3. Plug it into your Xbox 360 and start your existing **XeLL** (often with **Eject**).
4. When **X360Boot** opens, you are ready to test the menu.

**For v0.2.0-alpha only:** open the `X360Linux` folder using **A**, press **X** to save the folder, and press **Y** to try starting Linux. The first Linux boot is **experimental and may freeze**.

## ABadAvatar/BadUpdate + FreeMyXe — 4 steps

1. **Keep your existing exploit/FreeMyXe files** on the FAT32 USB drive. Do not delete them.
2. Extract your **ABadAvatar-FreeMyXe** ZIP onto that same USB drive. **Merge** the `BadUpdatePayload` folder instead of replacing it. Back up an existing `xell-2f.bin` before replacing it.
3. Run your normal exploit and choose **Launch XeLL** in FreeMyXe.
4. If XeLL loads `xenon.elf`, **X360Boot** will open. For v0.2, open `X360Linux` with **A**, press **X** to save and **Y** to try Linux.

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

- The **X360Boot menu already supports the Xbox 360 controller**: D-pad to move, A to enter a folder, B to go back, X to save the Linux folder, Y to try booting.
- **Inside Linux**, Xbox 360 controller support, graphics, audio, network and HDD persistence are still unverified. The first goal is to reach a command-line shell.
- **Debian PPC64**, a desktop, browser and image/video players are future work. This alpha uses a minimal BusyBox shell.

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
