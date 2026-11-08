#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# Run as root in an isolated network namespace.
set -euo pipefail

busybox=$(command -v busybox)
state=$(mktemp -d)
server=
cleanup() {
  if [[ $? -ne 0 && -f "$state/dnsmasq.log" ]]; then cat "$state/dnsmasq.log"; fi
  if [[ -n "$server" ]]; then
    kill "$server" 2>/dev/null || true
    wait "$server" 2>/dev/null || true
  fi
  ip netns del x360-dhcp-server 2>/dev/null || true
  rm -rf "$state"
}
trap cleanup EXIT

ip link add dhcp-client type veth peer name dhcp-server
ip netns add x360-dhcp-server
ip link set dhcp-server netns x360-dhcp-server
ip -n x360-dhcp-server addr add 192.0.2.1/24 dev dhcp-server
ip -n x360-dhcp-server link set dhcp-server up
ip link set dhcp-client up

ip netns exec x360-dhcp-server dnsmasq --no-daemon --conf-file=/dev/null --port=0 --bind-interfaces \
  --interface=dhcp-server --dhcp-range=192.0.2.10,192.0.2.10,255.255.255.0,1h \
  --dhcp-option=option:router,192.0.2.1 --dhcp-option=option:dns-server,192.0.2.1 \
  --leasefile-ro --log-dhcp --user=root > "$state/dnsmasq.log" 2>&1 &
server=$!
sleep 1
if ! kill -0 "$server"; then cat "$state/dnsmasq.log"; exit 1; fi

sed -e "s|/usr/lib/x360linux/busybox|$busybox|g" \
    -e "s|/etc/resolv.conf|$state/resolv.conf|g" \
    distro/debian/dhcp-event > "$state/dhcp-event"
chmod +x "$state/dhcp-event"

timeout 15s udhcpc -f -n -q -t 4 -T 2 -i dhcp-client -s "$state/dhcp-event"
ip -4 -o addr show dev dhcp-client | grep -F '192.0.2.10/24'
ip -4 route show default | grep -F 'via 192.0.2.1 dev dhcp-client'
grep -qx 'nameserver 192.0.2.1' "$state/resolv.conf"
echo X360LINUX_DHCP_LEASE_OK
