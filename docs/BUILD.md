# Build — experimental kernel and GPU

> **No bootable release is provided.** The commands below have been written for reproducible experiments but have not yet been validated in a complete cross-build by X360Linux. Never flash NAND.

## Host requirements

Use a Linux development workstation with Git, GNU Make, patch, bc, bison, flex, Python 3, compiler dependencies and sufficient disk space.

The **Free60 Xenon cross-toolchain** is not the same as the distribution `powerpc64-linux-gnu` compiler. Install it from [Free60Project/libxenon](https://github.com/Free60Project/libxenon). For Linux user space, the upstream GPU project uses `powerpc64-linux-gnu-gcc` with a ppc64 big-endian sysroot.

On the host:

```bash
git clone --recurse-submodules https://github.com/heltindev/X360Linux.git
cd X360Linux
bash scripts/doctor.sh
python3 scripts/validate.py
```

## Kernel baseline

The Xenos GPU reference used **Linux 6.18.58** with Free60 `patch-6.18-xenon0.30.diff`, the matching `xenon-6.18.defconfig`, plus GPU project fixes for the `sis190` TX race and VMX reporting.

Get a clean, integrity-verified `linux-6.18.58` source archive from [kernel.org](https://www.kernel.org/) and extract outside this repository, into a *disposable source tree*.

```bash
JOBS=4 bash scripts/build-kernel.sh /absolute/path/linux-6.18.58
```

The script refuses a mismatched Linux version, checks patches with `patch --dry-run`, applies the Free60 and two upstream GPU fixes, installs the Free60 defconfig, runs `olddefconfig`, then attempts the Xenon image and modules.

Expected candidate: `arch/powerpc/boot/zImage.xenon`. The bootloader may require a specific ELF32-wrapped payload rather than the raw kernel file; consult XeLL documentation and verify before boot testing.

## Xenos GPU module

Only after the kernel has successfully built:

```bash
JOBS=4 bash scripts/build-xegpu.sh /absolute/path/linux-6.18.58
```

The intended output is `external/xenos-linux-gpu/kernel/xegpu/xegpu.ko`, built against the **same exact kernel tree**. Do not mix a 4 KB-page module with a 64 KB-page kernel.

This is not enough to start a desktop. The GPU experiment additionally relies on its userspace `xeinit` tool, Mesa patch stack, big-endian Xorg glamor patch, matching Xorg configuration and a configured root filesystem. See [GPU-INTEGRATION.md](GPU-INTEGRATION.md).

## Cross-build limits

- No routine here sets up a bootable NFS root or audio stack.
- No script downloads or publishes Microsoft firmware, keys or NAND dumps.
- Do not use an unverified `vmlinux` or `zImage` as `updflash.bin` or `updxell.bin`.
- Never skip failed patch checks; first match the upstream revision and source version.
- **Successful compilation is not hardware validation.** Always record all source revisions and redacted logs.
