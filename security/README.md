# CA trust verification

The 2026-10-20 eMudhra compromise affects clients that do not consume browser
revocation lists: https://emudhra.we-have-a-problem.com/ .
`blocked-roots.json` records the four published affected/cross-signing root
fingerprints from its `roots.json`; these certificates are never installed.

`check_trust.py` checks the OS/Python store, patched pip's vendored store, and
certifi when installed. `check_trust.mjs` checks Node's default, bundled and
system stores and requires patched Node 24. Both verify all twelve published PEM chains offline against each actual CA bundle. `chains.b64` is the unmodified publisher chains.zip encoded as base64. `--live` additionally requires successful normal HTTPS handshakes. `--probe-live-chains` optionally probes the external test endpoints; DNS, timeout, hostname and expiry errors never count as successful negative tests. External test endpoints timed out during validation, so deployment uses offline chain verification plus live normal HTTPS.

The API and devcontainer refresh Debian CA packages before pip bootstrap.
The frontend build uses Node 24.22.1 and refreshes its OS CA packages. Builds
fail if an affected root remains trusted. Backend builds always pull the base
image and disable build caching. Cloud SDK uses the refreshed OS CA file.

The devcontainer is also the maintained environment for index generation;
rebuild it with `--pull --no-cache` after this update. It does not install uv,
so no bundled uv store is in use. External host tools and Google's managed
Firebase serving infrastructure are outside these container images.
