/* SPDX-License-Identifier: GPL-2.0-only */
#include "../source/settings.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

int main(void) {
    struct x360_settings a, b;
    char path[] = "x360-config-test.tmp";
    x360_settings_default(&a);
    assert(!a.autoboot);
    assert(strstr(a.cmdline, "rdinit=/init"));
    assert(x360_path_is_safe("uda0:/Linux/"));
    assert(x360_path_is_safe("sda0:/"));
    assert(!x360_path_is_safe("uda0:/../Linux/"));
    assert(!x360_path_is_safe("uda0:/Linux\\bad/"));
    assert(!x360_path_is_safe("../"));
    assert(!x360_path_is_safe("uda0:/A\nB/"));
    assert(!x360_path_is_safe("uda0:/Linux"));
    assert(x360_settings_select_folder(&a, "uda0:/X360Linux/") == 0);
    assert(!strcmp(a.folder, "uda0:/X360Linux/"));
    assert(x360_settings_select_folder(&a, "uda0:/../bad/") == -1);
    assert(!strcmp(a.folder, "uda0:/X360Linux/"));
    assert(x360_settings_select_folder(NULL, "uda0:/X360Linux/") == -1);
    assert(x360_settings_select_folder(&a, NULL) == -1);
    a.autoboot = 1;
    assert(x360_settings_save(path, &a) == 0);
    assert(x360_settings_load(path, &b) == 0);
    assert(!strcmp(a.folder, b.folder));
    assert(!strcmp(a.cmdline, b.cmdline));
    assert(b.autoboot == 1);
    b.autoboot = 0;
    assert(x360_settings_save(path, &b) == 0);
    assert(x360_settings_load(path, &a) == 0);
    assert(a.autoboot == 0);
    remove(path);
    puts("X360Boot settings tests passed");
    return 0;
}
