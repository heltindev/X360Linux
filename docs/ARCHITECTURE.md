# Architecture

## XWT Boot: separated execution environments

The preferred future boot architecture is:

```text
Hardware power-on -> existing RGH/JTAG/boot entry -> initial ELF loader
                                                 |
                                                 v
                           XWT Boot ELF (LibXenon, own screen + settings)
                                                 |
                   +-----------------------------+
                   |  Load Linux ELF + FDT + initramfs
                   v
                              Free60-patched Xenon Linux
                                                 |
                                   X360Linux minimal userspace
```

**An ELF cannot start itself on powered-off Xbox 360 hardware.** Some earlier loader or boot exploit is required for the first jump. Once XWT Boot is executing, it uses LibXenon's own Linux ELF functions, not a live XeLL menu/session. It is therefore a **separate ELF application**, not an additional operating system.

XWT Boot persists the selected Linux folder, command-line parameters and optional autoboot in a FAT volume configuration file. It uses `elf_runWithDeviceTree` for direct handoff, but hardware validation has not yet been performed.

The native **ISO9660 launcher** optionally carries the XWT ELF for a compatible XeLL initial CD/DVD boot. A **Linux operating system ISO** requires an independently working kernel plus rootfs and is not available yet.



X360Linux is an integration workspace that ties together existing Xbox 360 Linux research. It does not replace XeLL, the Linux kernel or Mesa.

## Boot path

```text
Existing RGH/JTAG (or supported softmod) entry point
        |
        v
XeLL-Reloaded (hardware init, ELF loader, kboot.conf, TFTP/USB)
        |
        v
Free60-patched Linux 6.18.x for Xenon PowerPC64 big-endian
        |
        +-- kernel drivers (Ethernet, storage, USB, framebuffer)
        |
        +-- GPU module: xegpu.ko + userspace xeinit
        |
        v
PowerPC64 root filesystem (upstream example: Debian unstable via NFS)
        |
        +-- Mesa freedreno Xenos variant / EGL / GLES2
        +-- Xorg modesetting + glamor big-endian patch
        +-- IceWM and Linux applications
```

## Three independent compatibility questions

1. **Does XeLL load the kernel image?** Valid ELF32 wrapper, device tree, boot args and media paths matter.
2. **Does the kernel boot?** Free60 Xenon platform patches and matching binary/module revisions matter.
3. **Does the GPU work safely?** The Xenos DRM driver, xegpu, contiguous pool allocation, Mesa command validation and graphics mode matter.

A successful loader handoff does not prove userspace or graphics support.

## Memory and CPU

The Xbox 360 has approximately **512 MiB total memory shared with graphics**; the upstream Linux experiment reported **458 MB visible to Linux** and approximately 200 MB available with its 64 KB-page IceWM environment. This is not an unconditional promise for every board or configuration.

Xenon uses PowerPC64 big-endian ELFv1. VMX128 is **not ordinary AltiVec**: do not advertise unsupported instructions to general software. The GPU reference project uses `-mcpu=970 -mtune=cell -mno-altivec` for standard user-space builds.

## Integration model

- `external/xell-reloaded` — upstream bootloader source (read-only reference).
- `external/free60-kernel-patches` — Free60 kernel patch/config source.
- `external/xenos-linux-gpu` — upstream GPU module, Mesa patches, Xorg patch, configuration and test evidence.
- `scripts/` — original guarded host-side build helpers.
- `config/` — sample boot configuration, **not** a firmware update.
- `docs/` — original guides and project compatibility tracking.

Git submodules pin specific upstream commits. Update pointers only with a source/compatibility review.
