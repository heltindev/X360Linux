/* SPDX-License-Identifier: GPL-2.0-only */
#include "settings.h"
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Portable settings code: host-tested without Xbox hardware. */
void x360_settings_default(struct x360_settings *out) {
    memset(out, 0, sizeof(*out));
    strcpy(out->cmdline, "console=tty0 quiet loglevel=1 panic=30 maxcpus=6 coherent_pool=6M video=xenosfb rdinit=/init");
}
int x360_path_is_safe(const char *path) {
    size_t n, sep, i;
    if (!path) return 0;
    n = strlen(path);
    if (n < 4 || n >= X360_PATH_MAX || path[n - 1] != '/') return 0;
    sep = 0;
    while (sep < n && path[sep] != ':') sep++;
    if (sep < 1 || sep > 12 || sep + 1 >= n || path[sep + 1] != '/') return 0;
    for (i = 0; i < sep; ++i) {
        if (!isalnum((unsigned char)path[i]) && path[i] != '_') return 0;
    }
    for (i = sep + 2; i < n; ++i) {
        unsigned char c = (unsigned char)path[i];
        if (c < 32 || c > 126 || c == ':' || c == '\\' || c == '=' || c == ';') return 0;
        if (c == '.' && i + 1 < n && path[i + 1] == '.' &&
           (i == sep + 2 || path[i - 1] == '/') &&
           (i + 2 == n || path[i + 2] == '/')) return 0;
    }
    return 1;
}
int x360_settings_select_folder(struct x360_settings *settings, const char *folder) {
    if (!settings || !x360_path_is_safe(folder)) return -1;
    /* x360_path_is_safe() enforces X360_PATH_MAX and slash termination. */
    strcpy(settings->folder, folder);
    return 0;
}
static void trim(char *text) {
    size_t n = strlen(text);
    while (n && (text[n - 1] == '\r' || text[n - 1] == '\n' ||
                  text[n - 1] == ' ' || text[n - 1] == '\t')) text[--n] = 0;
}
int x360_settings_load(const char *filename, struct x360_settings *out) {
    char line[512];
    struct x360_settings draft;
    FILE *f = fopen(filename, "rb");
    if (!f) return -1;
    x360_settings_default(&draft);
    if (!fgets(line, sizeof(line), f)) { fclose(f); return -1; }
    trim(line);
    if (strcmp(line, "X360BOOT1")) { fclose(f); return -1; }
    while (fgets(line, sizeof(line), f)) {
        char *value;
        trim(line);
        value = strchr(line, '=');
        if (!value) continue;
        *value++ = 0;
        if (!strcmp(line, "folder")) {
            if (strlen(value) >= sizeof(draft.folder) || !x360_path_is_safe(value)) {
                fclose(f); return -1;
            }
            strcpy(draft.folder, value);
        } else if (!strcmp(line, "cmdline")) {
            if (strlen(value) >= sizeof(draft.cmdline)) { fclose(f); return -1; }
            strcpy(draft.cmdline, value);
        } else if (!strcmp(line, "autoboot")) {
            if (strcmp(value, "0") && strcmp(value, "1")) { fclose(f); return -1; }
            draft.autoboot = value[0] == '1';
        }
    }
    if (ferror(f)) { fclose(f); return -1; }
    fclose(f);
    *out = draft;
    return 0;
}
int x360_settings_save(const char *filename, const struct x360_settings *settings) {
    char temp[X360_PATH_MAX + 24];
    FILE *f;
    int ok;
    if (!x360_path_is_safe(settings->folder)) return -1;
    if (strchr(settings->cmdline, '\r') || strchr(settings->cmdline, '\n') ||
        strlen(settings->cmdline) >= X360_ARGS_MAX) return -1;
    if (snprintf(temp, sizeof(temp), "%s.tmp", filename) >= (int)sizeof(temp)) return -1;
    f = fopen(temp, "wb");
    if (!f) return -1;
    ok = fprintf(f, "X360BOOT1\nfolder=%s\ncmdline=%s\nautoboot=%d\n",
                 settings->folder, settings->cmdline, settings->autoboot ? 1 : 0) > 0;
    if (fflush(f) != 0) ok = 0;
    if (fclose(f) != 0) ok = 0;
    if (!ok) { remove(temp); return -1; }
    /* FAT targets may not implement rename-over-existing. Keep a backup,
       restore it if installing the new file fails. */
    if (rename(temp, filename) != 0) {
        char backup[X360_PATH_MAX + 24];
        if (snprintf(backup, sizeof(backup), "%s.bak", filename) >= (int)sizeof(backup)) {
            remove(temp);
            return -1;
        }
        remove(backup);
        if (rename(filename, backup) != 0) { remove(temp); return -1; }
        if (rename(temp, filename) != 0) {
            rename(backup, filename);
            remove(temp);
            return -1;
        }
        remove(backup);
    }
    return 0;
}
