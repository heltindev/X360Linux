/* SPDX-License-Identifier: GPL-2.0-only */
#include "../source/settings.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

int main(void) {
    struct xwt_settings a, b;
    char path[] = "xwt-config-test.tmp";
    xwt_settings_default(&a);
    assert(!a.autoboot);
    assert(strstr(a.cmdline, "rdinit=/init"));
    assert(xwt_path_is_safe("uda0:/Linux/"));
    assert(xwt_path_is_safe("sda0:/"));
    assert(!xwt_path_is_safe("uda0:/../Linux/"));
    assert(!xwt_path_is_safe("uda0:/Linux\\bad/"));
    assert(!xwt_path_is_safe("../"));
    assert(!xwt_path_is_safe("uda0:/A\nB/"));
    assert(!xwt_path_is_safe("uda0:/Linux"));
    strcpy(a.folder, "uda0:/X360Linux/");
    a.autoboot = 1;
    assert(xwt_settings_save(path, &a) == 0);
    assert(xwt_settings_load(path, &b) == 0);
    assert(!strcmp(a.folder, b.folder));
    assert(!strcmp(a.cmdline, b.cmdline));
    assert(b.autoboot == 1);
    b.autoboot = 0;
    assert(xwt_settings_save(path, &b) == 0);
    assert(xwt_settings_load(path, &a) == 0);
    assert(a.autoboot == 0);
    remove(path);
    puts("XWT Boot settings tests passed");
    return 0;
}
