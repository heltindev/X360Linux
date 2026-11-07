/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef XWT_BOOT_H
#define XWT_BOOT_H
#include "settings.h"
int xwt_linux_files_present(const char *folder);
int xwt_boot_linux(const struct xwt_settings *settings);
#endif
