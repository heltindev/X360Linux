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
    char status[144];
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
        if (!strcmp(entry->d_name, "X360Linux"))
            ui.selected = ui.count;
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
    ui.status[0] = 0;
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
/* A on a directory containing Linux files selects and starts Linux immediately.
   Other directories can still be browsed normally. No FAT writes occur. */
static int enter_folder(void) {
    char path[X360_PATH_MAX];
    if (ui.count == 0 || ui.selected >= ui.count) return 0;
    if (!append_folder(path, sizeof(path), ui.names[ui.selected])) return 0;
    if (x360_linux_files_present(path)) {
        if (x360_settings_select_folder(&ui.boot, path) != 0) return 0;
        strcpy(ui.current, path);
        return 1;
    }
    strcpy(ui.current, path);
    refresh_folders();
    return 0;
}
static void render(void) {
    int start, end, i;
    console_clrscr();
    puts("========================================================");
    puts("                      X360LINUX");
    puts("                 Xbox 360 Linux Preview");
    puts("========================================================");
    puts("");
    printf("USB: %s\n", ui.device);
    puts("");
    if (ui.count == 0) {
        puts("No more folders here. Press B to go back.");
    } else {
        puts("Select a folder:");
    }
    start = ui.selected > 8 ? ui.selected - 8 : 0;
    end = start + 12;
    if (end > ui.count) end = ui.count;
    for (i = start; i < end; ++i) {
        printf("%c  %s%s\n", i == ui.selected ? '>' : ' ',
               ui.names[i], !strcmp(ui.names[i], "X360Linux") ? "  - Linux" : "");
    }
    puts("");
    puts("A  Open folder / Start Linux");
    puts("B  Back          D-Pad  Move          LB/RB  USB");
    puts("");
    puts("X360Linux normally starts by itself when it finds Linux files.");
    puts("At startup, press B during the countdown to keep this menu.");
    puts("This preview does not change the Xbox hard drive.");
    if (ui.status[0]) {
        puts("--------------------------------------------------------");
        puts(ui.status);
    }
}
static int pressed(const struct controller_data_s *p) {
    return p->a || p->b || p->up || p->down ||
           p->lb || p->rb || p->s1_y > STICK_TRIGGER ||
           p->s1_y < -STICK_TRIGGER;
}
/* If the standard USB Linux folder exists, boot it without user input.
   Keep a short B-to-cancel window so a broken kernel is never a boot trap.
   No files or NAND/HDD partitions are written by this function. */
static void auto_start_linux(void) {
    char folder[X360_PATH_MAX];
    struct controller_data_s pad;
    int i, rc;

    if (snprintf(folder, sizeof(folder), "%s:/X360Linux/", ui.device) >=
        (int)sizeof(folder)) return;
    if (!x360_linux_files_present(folder)) return;
    if (x360_settings_select_folder(&ui.boot, folder) != 0) return;

    console_clrscr();
    puts("========================================================");
    puts("                      X360LINUX");
    puts("========================================================");
    puts("");
    puts("Linux files found on the USB drive.");
    puts("Starting automatically in 3 seconds...");
    puts("Press B to cancel and open the boot menu.");
    puts("");
    for (i = 0; i < 30; ++i) {
        usb_do_poll();
        memset(&pad, 0, sizeof(pad));
        if (get_controller_data(&pad, 0) && pad.b) {
            snprintf(ui.status, sizeof(ui.status),
                     "Automatic boot cancelled. Press A to start Linux.");
            return;
        }
        udelay(100000);
    }

    rc = x360_boot_linux(&ui.boot);
    snprintf(ui.status, sizeof(ui.status),
             "Linux loader returned error %d. Press A to try again.", rc);
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
    /* Autostart only a validated FAT32 X360Linux/ folder; B cancels.
       No settings are loaded or saved and no NAND writes take place. */
    auto_start_linux();
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
            if (enter_folder()) {
                int rc = x360_boot_linux(&ui.boot);
                /* A loader error returns to the menu; a kernel panic cannot. */
                parent_folder();
                snprintf(ui.status, sizeof(ui.status),
                         "Linux did not start (loader error %d). Press B to retry.", rc);
            }
        } else if (pad.b) {
            parent_folder();
        } else if (pad.lb || pad.rb) {
            set_device(1);
        }
        dirty = 1;
    }
    return 0;
}
