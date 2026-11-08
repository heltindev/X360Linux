# Boot splash prototype - NOT shipped in v0.4.0-alpha

This Plymouth script is a source-only experiment. It renders a dark-green screen, a progress bar and a number from 0 to 100 percent based on the Plymouth userspace boot progress callback.

Limitations: It CANNOT cover the 2011 XeLL DHCP/status screen or kernel output before the framebuffer and Plymouth daemon become active. Plymouth's progress is an estimate, not a complete hardware loading percentage. The config files have not been loaded or tested on an Xbox 360 yet.

Integration (after validating matching Xenon bootchain): install both files in /lib/plymouth/themes/x360linux/, switch default.plymouth symlink in a disposable SquashFS copy, test framebuffer availability and kernel quiet/splash arguments. Keep recovery path for console logs and rollback the theme if the screen stays blank. Avoid changing NAND or replacing the tested xell.bin without a validated replacement.
