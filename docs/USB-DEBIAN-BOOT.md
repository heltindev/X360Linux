# X360Linux v0.3 USB boot

The ZIP contains a Debian Ports PowerPC ISO and a writable data image. The Xbox 360 runs Debian from the ISO on the USB drive. The XeLL installation you already use starts the process.

1. Use a FAT32 USB drive with at least 2 GB free.
2. Extract the correct ZIP directly to the USB root. Keep `xenon.elf` next to the `X360Linux/` folder.
3. Connect the USB drive and start XeLL. Wait for the IceWM desktop to open. A USB keyboard and mouse can be used to open the menu and applications.
4. Shut down cleanly before unplugging. `X360Linux/USB-DATA.ext4` holds the changes made inside Debian, so back it up before updating.

The launcher loads the Xenon kernel and initramfs. Linux mounts `X360Linux/X360Linux.iso` read-only and uses `USB-DATA.ext4` as its writable layer. The direct ext4 build tested on Xbox hardware is available under [v0.2.0-alpha](https://github.com/heltindev/X360Linux/releases/tag/v0.2.0-alpha).

## Desktop and terminal recovery

The Debian ISO attempts to open IceWM automatically. Xbox 360 hardware testing showed the X.Org fbdev driver failed with `No devices detected` and `no screens found`. The current experimental build first starts a local **software X11 (Xvfb) desktop** and draws its pixels directly to the Xbox `/dev/fb0` using a native PowerPC bridge. It requires no other computer, display-streaming server, internet connection, or commands at the console. Input from USB keyboard/mouse is forwarded via XTest. If that framebuffer method cannot start, it tries classic X.Org fbdev as a fallback and returns to a recovery terminal if graphics still fail. This new path is pending validation on real Xbox 360 hardware.\n\nIf the graphical boot fails, a report is written automatically to `X360Linux/BOOT-DIAGNOSTICS.txt` on the FAT32 USB drive. That text file can be read in Windows without typing commands on the Xbox.

For console-only boot, create an empty file named `CONSOLE-ONLY` inside the `X360Linux/` folder on the pendrive.

## Ethernet and DHCP

If XeLL hangs at `Requesting DHCP`, unplug the Ethernet cable and start XeLL again. Reconnect it after the Debian prompt appears. Debian runs Ethernet DHCP in the background and retries if the cable is disconnected. To check its status, run `cat /run/x360linux-network.log`.

The [Xbox 360 Wi-Fi 11g project](https://github.com/sergiolimasks/xbox360-wifi-11g) changes the stock Xbox kernel Wi-Fi driver. Free60 publishes a [separate experimental Linux driver](https://github.com/Free60Project/linux-xbox360-wifi) for the Marvell adapter in some Xbox 360 S units.

If a BusyBox recovery shell appears, photograph the last `X360Linux USB:` error. The ISO and wired DHCP need confirmation on Xbox hardware.
