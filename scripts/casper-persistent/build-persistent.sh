#!/bin/sh
set -eu

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 ORIGINAL_SQUASHFS OUTPUT_SQUASHFS OUTPUT_CASPER_RW" >&2
    exit 2
fi

original=$1
output=$2
cow=$3
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT INT TERM

unsquashfs -d "$work/root" "$original"

# The working legacy kernel already opens the live desktop. Remove the
# Ubiquity launcher so the result behaves as a persistent USB system.
rm -f "$work/root/usr/share/applications/ubiquity-gtkui.desktop"
printf '%s\n' 'X360Linux persistent Casper system; installer launcher removed.' \
    > "$work/root/etc/x360linux-persistent-release"

mksquashfs "$work/root" "$output" \
    -comp gzip -b 131072 -noappend

truncate -s 3G "$cow"
mkfs.ext3 -F -L casper-rw "$cow"
e2fsck -fn "$cow"

unsquashfs -cat "$output" etc/x360linux-persistent-release
if unsquashfs -ll "$output" |
    grep -q 'usr/share/applications/ubiquity-gtkui.desktop'; then
    echo "Installer launcher is still present" >&2
    exit 1
fi
