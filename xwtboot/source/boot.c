/* SPDX-License-Identifier: GPL-2.0-only */
/* Experimental Linux handoff. The loader is libxenon's, not XeLL's UI.
   Platform/device-tree preparation still comes from the libxenon runtime. */
#include "boot.h"
#include <elf/elf.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define KERNEL_MAX (64u * 1024u * 1024u)
#define DTB_MAX (64u * 1024u)
#define INITRD_MAX (32u * 1024u * 1024u)

static int file_path(char *out, size_t max, const char *folder, const char *name) {
    int n = snprintf(out, max, "%s%s", folder, name);
    return n > 0 && (size_t)n < max;
}
static int exists(const char *folder, const char *name) {
    char path[XWT_PATH_MAX + 40];
    FILE *file;
    if (!file_path(path, sizeof(path), folder, name)) return 0;
    file = fopen(path, "rb");
    if (!file) return 0;
    fclose(file);
    return 1;
}
int xwt_linux_files_present(const char *folder) {
    return xwt_path_is_safe(folder) &&
           exists(folder, "vmlinux") &&
           exists(folder, "xenon.dtb");
}
static int read_limited(const char *folder, const char *name,
                        size_t max, void **out, int *len) {
    char path[XWT_PATH_MAX + 40];
    FILE *file;
    long size;
    void *buf;
    *out = NULL;
    *len = 0;
    if (!file_path(path, sizeof(path), folder, name)) return -1;
    file = fopen(path, "rb");
    if (!file) return -1;
    if (fseek(file, 0, SEEK_END) || (size = ftell(file)) <= 0 ||
        (unsigned long)size > max || fseek(file, 0, SEEK_SET)) {
        fclose(file);
        return -1;
    }
    buf = malloc((size_t)size);
    if (!buf) { fclose(file); return -1; }
    if (fread(buf, 1, (size_t)size, file) != (size_t)size) {
        free(buf); fclose(file); return -1;
    }
    fclose(file);
    *out = buf;
    *len = (int)size;
    return 0;
}
int xwt_boot_linux(const struct xwt_settings *settings) {
    void *elf = NULL, *dtb = NULL, *initrd = NULL;
    int elf_len = 0, dtb_len = 0, initrd_len = 0, rc = -1;
    const unsigned char *h, *d;
    if (!settings || !xwt_linux_files_present(settings->folder)) {
        printf("No valid Linux directory selected (requires vmlinux + xenon.dtb).\n");
        return -1;
    }
    puts("Reading Xenon Linux ELF and device tree...");
    if (read_limited(settings->folder, "vmlinux", KERNEL_MAX, &elf, &elf_len) ||
        read_limited(settings->folder, "xenon.dtb", DTB_MAX, &dtb, &dtb_len))
        goto done;

    h = (const unsigned char *)elf;
    d = (const unsigned char *)dtb;
    if (elf_len < 52 || h[0] != 0x7f || h[1] != 'E' || h[2] != 'L' ||
        h[3] != 'F' || h[4] != 1 || h[5] != 2 || h[18] != 0 ||
        h[19] != 20) {
        puts("Refusing kernel: expected ELF32 big-endian PowerPC.");
        goto done;
    }
    if (dtb_len < 40 || d[0] != 0xd0 || d[1] != 0x0d ||
        d[2] != 0xfe || d[3] != 0xed) {
        puts("Refusing device tree: invalid FDT magic.");
        goto done;
    }
    kernel_reset_initrd();
    if (exists(settings->folder, "initramfs.cpio.gz")) {
        puts("Reading optional initramfs...");
        if (read_limited(settings->folder, "initramfs.cpio.gz",
                         INITRD_MAX, &initrd, &initrd_len)) goto done;
        if (kernel_prepare_initrd(initrd, (size_t)initrd_len)) goto done;
    }
    kernel_build_cmdline(settings->cmdline, NULL);
    puts("EXPERIMENTAL handoff to Linux. Recovery may require power cycle.");
    /* libxenon transfers control and supplies Xenon FDT to Linux.
       Real-console stability is not established by a successful host build. */
    rc = elf_runWithDeviceTree(elf, elf_len, dtb, dtb_len);
    puts("Linux ELF loader returned an error.");
done:
    free(initrd);
    free(dtb);
    free(elf);
    return rc;
}
