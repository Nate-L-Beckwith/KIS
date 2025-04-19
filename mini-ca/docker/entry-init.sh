#!/usr/bin/env sh
set -eu

echo "[minica-init] fixing /data perms"
chown -R 1001:1001 /data 2>/dev/null || true

# run init *inside* the unprivileged account
exec su -s /bin/sh -c "mini_ca.py init --force" myca
