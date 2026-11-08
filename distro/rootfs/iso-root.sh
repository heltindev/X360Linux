#!/bin/sh
# SPDX-License-Identifier: Apache-2.0

mount_iso_root() {
  iso_image=$1
  data_image=$2
  state_dir=$3
  merged_root=$4

  [ -s "$iso_image" ] && [ -s "$data_image" ] || return 1
  $BB mkdir -p "$state_dir/iso" "$state_dir/base" "$state_dir/data" || return 1
  $BB mount -t iso9660 -o loop,ro "$iso_image" "$state_dir/iso" || return 1
  $BB mount -t ext4 -o loop,ro,noload "$state_dir/iso/X360Linux/system.ext4" "$state_dir/base" || return 1
  $BB mount -t ext4 -o loop,rw,noatime "$data_image" "$state_dir/data" || return 1
  $BB mkdir -p "$state_dir/data/upper" "$state_dir/data/work" || return 1
  $BB mount -t overlay -o "lowerdir=$state_dir/base,upperdir=$state_dir/data/upper,workdir=$state_dir/data/work" overlay "$merged_root"
}
