FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl xz-utils libgl1 libglib2.0-0 tesseract-ocr \
    && dpkg --compare-versions "$(dpkg-query -W -f='${Version}' ca-certificates)" ge '20250419~deb12u2' \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip --use-deprecated=legacy-certs --cert /etc/ssl/certs/ca-certificates.crt \
       install --no-cache-dir --upgrade 'pip>=26.2.2' 'certifi>=2026.10.19'
COPY security /opt/slvsh-security
RUN sh /opt/slvsh-security/install-node.sh && python /opt/slvsh-security/check_trust.py && node /opt/slvsh-security/check_trust.mjs
