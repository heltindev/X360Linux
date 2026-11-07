/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef XWT_SETTINGS_H
#define XWT_SETTINGS_H
#include <stddef.h>
#define XWT_PATH_MAX 256
#define XWT_ARGS_MAX 256

struct xwt_settings {
    char folder[XWT_PATH_MAX];
    char cmdline[XWT_ARGS_MAX];
    int autoboot;
};
void xwt_settings_default(struct xwt_settings *out);
int xwt_path_is_safe(const char *path);
int xwt_settings_load(const char *filename, struct xwt_settings *out);
int xwt_settings_save(const char *filename, const struct xwt_settings *settings);
#endif
