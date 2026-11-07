# Boot safety & recovery

> [!CAUTION]
> An experimental kernel or GPU module can freeze the console. This workspace **never writes NAND** or installs a softmod. Use it only when you already have a known-good XeLL boot path and recovery plan.

## Minimum conditions

1. Have a verified modded console with a functioning XeLL version that supports the intended boot method.
2. Record its revision and bootloader version. Back up the current configuration outside this repository.
3. Use external USB / TFTP / NFS experiments; do not replace the normal console system partition.
4. Do **not** place files called `updflash.bin` or `updxell.bin` alongside your experimental files. XeLL uses these special names for updates.
5. Never publish CPU/DVD keys, NAND contents, firmware, network credentials or personal identifiers.
6. Check that your `kboot.conf` refers to the correct bootable payload and NFS address; the example contains placeholder values.
7. Keep a way to power-cycle or recover from hangs without destructive system modifications.

## Safe verification sequence

- XeLL appears: photograph/version/log only, no write action.
- XeLL locates the kernel: verify file and ELF format.
- Linux starts: capture serial/netconsole/TV output if possible.
- Shell starts: collect `uname -a`, `/proc/meminfo` and `dmesg` (redact private data).
- GPU starts: check module and video output only after a stable Linux boot.
- Run graphics tests in small batches; a wedged shader may require power cycling.

## Never assume

A successful GitHub Actions run proves only syntax/static files. A compiled `xegpu.ko` proves only a cross-build. A booting kernel proves neither stable drivers nor safe GPU reset. No 100% functional label should be used before broad real-console testing.

For additional caveats and original setup procedures, refer to [arelyx setup](https://github.com/arelyx/xenos-linux-gpu/blob/main/docs/setup.md).
