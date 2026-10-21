#!/bin/sh
set -eu
case "$(uname -m)" in
  x86_64) node_arch=x64; node_sha=6c172a9ab6718f7b801fb5a7bd486af2ee5e32758086a04b84fcce2aa77095e6 ;;
  aarch64|arm64) node_arch=arm64; node_sha=dbabf7a1cbf947e6059ffad2c27b80041db97dea1e553b62afdee7f13fca336e ;;
  *) echo 'Unsupported Node architecture' >&2; exit 1 ;;
esac
curl --fail --show-error --silent https://nodejs.org/dist/v24.22.1/node-v24.22.1-linux-${node_arch}.tar.xz -o /tmp/slvsh-node.tar.xz
printf '%s  %s\n' "$node_sha" /tmp/slvsh-node.tar.xz | sha256sum -c -
tar -xJf /tmp/slvsh-node.tar.xz -C /usr/local --strip-components=1
rm /tmp/slvsh-node.tar.xz
