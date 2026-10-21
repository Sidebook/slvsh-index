#!/bin/sh
set -eu
apt-get update
apt-get install -y --no-install-recommends ca-certificates
# Official Debian/Ubuntu workaround also covers older Cloud Build base images.
sed -i -e 's|^mozilla/emSign_ECC_Root_CA_-_G3.crt|!&|' -e 's|^mozilla/Comodo_AAA_Services_root.crt|!&|' /etc/ca-certificates.conf
update-ca-certificates
