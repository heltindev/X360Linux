# X360Linux v0.4: DHCP offline and progress-bar investigation

This work was created AFTER v0.4.0-alpha was released. The current published ZIP has NOT been changed. The two fixes are NOT implemented in the public binaries.

## XeLL DHCP before Ubuntu

The verified historical xell.bin contains strings "* network init" and "* requesting dhcp...". It appears to perform network operations while searching for USB/TFTP executables before booting the Linux kernel. Ubuntu's DHCP configuration cannot suppress this early stage.

Proposed fix: first reproduce and time the error on the physical RGH Xbox, identify matching XeLL source, then skip DHCP when Ethernet carrier is absent or prioritize USB boot with a bounded network timeout. A new loader must be tested with the known-working XEX; NEVER flash NAND.

## Progress splash

The Ubuntu 10.10 PowerPC live rootfs has the Plymouth script renderer and frame-buffer.so. A source-only prototype is available at [distro/plymouth/x360linux](../distro/plymouth/x360linux/README.md) with a dark background, green bar, and estimated 0-100% based on the Plymouth progress callback.

Plymouth starts AFTER XeLL and early kernel initialization; it cannot cover XeLL screens on its own. Kernel quiet/splash requires correct 2011 bootloader argument support, not yet verified. To show 0-100% for the full boot requires combining real measured milestones in XeLL, kernel and userspace. Logs must remain accessible through a diagnostic mode.

## Tests still needed

- Photograph the DHCP screen and record boot time without Ethernet.
- Check whether old XeLL supports safe USB-priority or no-DHCP settings; never assume the current Free60 kboot.conf applies to the legacy image.
- Verify Plymouth theme syntax in Ubuntu 10.10 engine, Xenon framebuffer drawing, input and GDM handoff.
- Confirm no installer, no networking dependency, no freezes, and compare startup times.
- Update v0.4 release only AFTER confirming physical hardware startup.

## Issues

- [Offline no-cable boot](https://github.com/heltindev/X360Linux/issues/1)
- [0-100% splash](https://github.com/heltindev/X360Linux/issues/2)

The base v0.3 and current v0.4 public assets remain unchanged.
