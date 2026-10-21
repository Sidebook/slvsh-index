# CA trust verification

The 2026-10-20 eMudhra compromise affects clients that do not consume browser
revocation lists: https://emudhra.we-have-a-problem.com/ .
`blocked-roots.json` records the four published affected/cross-signing root
fingerprints from its `roots.json`; these certificates are never installed.

`check_trust.py` checks the OS/Python store, patched pip's vendored store, and
certifi when installed. `check_trust.mjs` checks Node's default, bundled and
system stores and requires patched Node 24. Both accept `--live` to require
successful normal HTTPS handshakes and certificate-verification failures for
all 12 published compromised-chain test hosts. DNS, timeout, hostname and
expiry errors do not count as successful negative tests.

The API and devcontainer refresh Debian CA packages before pip bootstrap.
The frontend build uses Node 24.22.1 and refreshes its OS CA packages. Builds
fail if an affected root remains trusted. Backend builds always pull the base
image and disable build caching. Cloud SDK uses the refreshed OS CA file.

The devcontainer is also the maintained environment for index generation;
rebuild it with `--pull --no-cache` after this update. It does not install uv,
so no bundled uv store is in use. External host tools and Google's managed
Firebase serving infrastructure are outside these container images.
