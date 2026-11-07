/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef X360_BOOT_H
#define X360_BOOT_H
#include "settings.h"
int x360_linux_files_present(const char *folder);
int x360_boot_linux(const struct x360_settings *settings);
#endif
