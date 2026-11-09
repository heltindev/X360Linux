# X360OS v6.0.1 - boot menu repair and network investigation

**The v6.0 USB test opened classic Ubuntu rather than X360OS.** Ubuntu 10.10's GDM may ignore the chosen session due to saved settings. The new build includes a GNOME autostart fallback that opens X360OS even if GDM loads GNOME, and stores logs under the ubuntu home directory: .x360os/home.log, .x360os/controller.log, and .x360os/hardware.txt.

**Controller:** a joystick or gamepad exposed by the kernel can now be read through both /dev/input/js* and /dev/input/event*. The mapper sends D-pad, A/B, and analog stick mouse interactions through X11/XTest. Xbox 360 wireless pads paired through the console's internal radio are NOT confirmed to be exposed by the legacy kernel. This needs physical testing; an external supported USB controller/receiver is the realistic first test.

**Wi-Fi:** Xbox 360 Slim/Corona's internal module uses Marvell 88W8786U, USB ID 045e:0765. It has no verified compatible USB driver in the preserved Xenon Linux 2.6.36.2 image. NetworkManager/DHCP are present in Ubuntu, but they cannot make unsupported hardware appear. A suitable kernel/driver/firmware port is necessary for internal wireless, or a tested external adapter. The updated desktop distinguishes network interfaces from actual internet availability.

**XeLL DHCP:** XeLL's DHCP attempt happens BEFORE Ubuntu. When using only wireless networking it may have no Ethernet link. Editing Ubuntu network settings won't repair the XeLL bootloader's network stack. We do not flash NAND to suppress it.

**stdin/stderr error 0:** if displayed during XeLL before Linux takes over, the desktop has no control over it. Keeping quiet/splash Linux options will not suppress XeLL startup messages. The exact message should be photographed to determine its source. The bootloader and kernel are unchanged.

This is a PC-built development test, NOT a verified working console release. Keep the functional v5 USB intact. Test v6.0.1 on a second FAT32 USB drive.
