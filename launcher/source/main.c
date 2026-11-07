/* SPDX-License-Identifier: GPL-2.0-only */
/* X360Boot - independent user-facing ELF boot manager (not Linux, not XeLL).
   A compatible loader must execute this ELF once before it takes control. */
#include "boot.h"
#include "settings.h"
#include <console/console.h>
#include <diskio/ata.h>
#include <diskio/disc_io.h>
#include <input/input.h>
#include <libfat/fat.h>
#include <time/time.h>
#include <usb/usbmain.h>
#include <xenon_soc/xenon_power.h>
#include <xenos/xenos.h>
#include <dirent.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

#define MAX_FOLDERS 40
#define STICK_TRIGGER 22000

extern int bdev_enum(int handle, const char **name);
static struct {
    char names[MAX_FOLDERS][120];
    int count;
    int selected;
    char current[X360_PATH_MAX];
    char device[24];
    int handle;
    struct x360_settings boot;
} ui;

static int append_folder(char *out, size_t capacity, const char *name) {
    int n = snprintf(out, capacity, "%s%s/", ui.current, name);
    return n > 0 && (size_t)n < capacity && x360_path_is_safe(out);
}
static void refresh_folders(void) {
    struct dirent *entry;
    DIR *dir;
    ui.count = 0;
    ui.selected = 0;
    dir = opendir(ui.current);
    if (!dir) return;
    while ((entry = readdir(dir)) && ui.count < MAX_FOLDERS) {
        char absolute[X360_PATH_MAX], shortname[120];
        struct stat info;
        size_t n = strlen(entry->d_name);
        if (n < 1 || n >= sizeof(shortname) ||
            !strcmp(entry->d_name, ".") || !strcmp(entry->d_name, "..")) continue;
        if (!append_folder(absolute, sizeof(absolute), entry->d_name)) continue;
        if (entry->d_type != DT_DIR) {
            /* Some mounted FAT drivers report DT_UNKNOWN. */
            if (stat(absolute, &info) || !S_ISDIR(info.st_mode)) continue;
        }
        strcpy(ui.names[ui.count++], entry->d_name);
    }
    closedir(dir);
}
static int set_device(int next) {
    const char *name = NULL;
    int handle = bdev_enum(next ? ui.handle : -1, &name);
    if (handle < 0 && next) handle = bdev_enum(-1, &name);
    if (handle < 0 || !name || strlen(name) >= sizeof(ui.device)) return -1;
    ui.handle = handle;
    strcpy(ui.device, name);
    if (snprintf(ui.current, sizeof(ui.current), "%s:/", name) >= (int)sizeof(ui.current)) return -1;
    x360_settings_default(&ui.boot);
    /* Loading/saving configuration on this libfat build is suspended.
       Selecting a folder must never write to the USB drive. */
    refresh_folders();
    return 0;
}
static void parent_folder(void) {
    size_t n = strlen(ui.current);
    size_t root = strlen(ui.device) + 2;
    if (n <= root) return;
    if (ui.current[n - 1] == '/') --n;
    while (n > root && ui.current[n - 1] != '/') --n;
    ui.current[n] = 0;
    refresh_folders();
}
static void enter_folder(void) {
    char path[X360_PATH_MAX];
    if (ui.count == 0 || ui.selected >= ui.count) return;
    if (!append_folder(path, sizeof(path), ui.names[ui.selected])) return;
    strcpy(ui.current, path);
    refresh_folders();
}
static int select_current(void) {
    if (!x360_linux_files_present(ui.current)) {
        puts("This folder needs vmlinux and xenon.dtb. Press B to go back.");
        return -1;
    }
    if (x360_settings_select_folder(&ui.boot, ui.current) != 0) {
        puts("Invalid Linux directory. Press B to go back.");
        return -1;
    }
    puts("Linux folder selected IN MEMORY. Press Y to try Linux.");
    return 0;
}
static void render(void) {
    int start, end, i;
    console_clrscr();
    puts("=============================================================");
    puts("    X360BOOT                                 EXPERIMENTAL");
    puts("    Xbox 360 native Linux boot manager | libxenon / PowerPC");
    puts("=============================================================");
    printf("Device : %s\n", ui.device);
    printf("Browse : %s\n", ui.current);
    printf("Linux  : %s\n", ui.boot.folder[0] ? ui.boot.folder : "(not selected)");
    printf("Boot on next launch: %s\n", ui.boot.autoboot ? "ON (cancel with B)" : "OFF");
    puts("-------------------------------------------------------------");
    if (ui.count == 0) {
        if (x360_linux_files_present(ui.current)) {
            puts("LINUX FILES FOUND in this folder!");
            puts("Press X to select this folder, then Y to try booting Linux.");
        } else {
            puts("No folders inside this directory. Press B to go back.");
        }
    }
    start = ui.selected > 8 ? ui.selected - 8 : 0;
    end = start + 16;
    if (end > ui.count) end = ui.count;
    for (i = start; i < end; ++i) {
        printf("%c [DIR] %s\n", i == ui.selected ? '>' : ' ', ui.names[i]);
    }
    puts("-------------------------------------------------------------");
    puts("D-Pad : navigate  | A: enter directory | B: parent/cancel");
    puts("X     : select Linux folder (memory only; NO USB writes)");
    puts("Y     : START LINUX (experimental handoff)");
    puts("START : disabled temporarily | LB/RB: next drive");
    puts("-------------------------------------------------------------");
    puts("Linux directory must contain vmlinux + xenon.dtb.");
    puts("Optional: initramfs.cpio.gz. Config saving is disabled for safety.");
    puts("Never flash NAND. Keep a working recovery method.");
}
static int pressed(const struct controller_data_s *p) {
    return p->a || p->b || p->x || p->y || p->up || p->down ||
           p->lb || p->rb || p->start || p->s1_y > STICK_TRIGGER ||
           p->s1_y < -STICK_TRIGGER;
}
int main(void) {
    struct controller_data_s pad;
    int was_pressed = 0, dirty = 1;
    memset(&ui, 0, sizeof(ui));
    ui.handle = -1;
    xenos_init(VIDEO_MODE_AUTO);
    console_init();
    xenon_make_it_faster(XENON_SPEED_FULL);
    usb_init();
    usb_do_poll();
    xenon_ata_init();
    xenon_atapi_init();
    fatInitDefault();
    if (set_device(0) != 0) {
        puts("X360Boot requires a readable FAT USB/HDD device.");
        puts("Insert a FAT32 drive and reboot using the known-good loader.");
        for (;;) { usb_do_poll(); udelay(100000); }
    }
    /* Never auto-boot or load any saved configuration in the test build. */
    for (;;) {
        if (dirty) { render(); dirty = 0; }
        usb_do_poll();
        memset(&pad, 0, sizeof(pad));
        if (!get_controller_data(&pad, 0)) { udelay(30000); continue; }
        if (!pressed(&pad)) { was_pressed = 0; udelay(30000); continue; }
        if (was_pressed) { udelay(30000); continue; }
        was_pressed = 1;
        if (pad.down || pad.s1_y < -STICK_TRIGGER) {
            if (ui.selected + 1 < ui.count) ++ui.selected;
        } else if (pad.up || pad.s1_y > STICK_TRIGGER) {
            if (ui.selected > 0) --ui.selected;
        } else if (pad.a) {
            enter_folder();
        } else if (pad.b) {
            parent_folder();
        } else if (pad.lb || pad.rb) {
            set_device(1);
        } else if (pad.x) {
            select_current();
        } else if (pad.start) {
            puts("Auto-boot and USB config saving are disabled for this test.");
        } else if (pad.y) {
            if (ui.boot.folder[0]) {
                int r = x360_boot_linux(&ui.boot);
                printf("Boot failed: %d. Press B to return to the menu.\n", r);
            } else {
                puts("Select the Linux directory with X first.");
            }
        }
        dirty = 1;
    }
    return 0;
}
