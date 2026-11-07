/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef X360_SETTINGS_H
#define X360_SETTINGS_H
#include <stddef.h>
#define X360_PATH_MAX 256
#define X360_ARGS_MAX 256

struct x360_settings {
    char folder[X360_PATH_MAX];
    char cmdline[X360_ARGS_MAX];
    int autoboot;
};
void x360_settings_default(struct x360_settings *out);
int x360_path_is_safe(const char *path);
/* Session-only selection: never writes to a FAT filesystem. */
int x360_settings_select_folder(struct x360_settings *settings, const char *folder);
int x360_settings_load(const char *filename, struct x360_settings *out);
int x360_settings_save(const char *filename, const struct x360_settings *settings);
#endif
