#!/usr/bin/env sh
# ------------------------------------------------------------------
#  entry‑init.sh – bootstrap the root CA inside the minica image
#  This version has **zero** reliance on mktemp / heredocs, so it
#  works the same whether you build the image yourself or pull it.
# ------------------------------------------------------------------
set -eu

# ------------------------------------------------------------------
# 1. make sure the named volume is owned by the runtime user (myca)
# ------------------------------------------------------------------
UID_MYCA=1001
GID_MYCA=1001
DATA_DIR=/data

echo "[minica‑init] ensuring perms on ${DATA_DIR}"
#  ─ chmod / chown will fail the very first time because /data is empty.
#    That’s fine – swallow the error with `|| true`.
chown -R "${UID_MYCA}:${GID_MYCA}" "${DATA_DIR}" 2>/dev/null || true

# ------------------------------------------------------------------
# 2. short‑circuit if a root CA already exists
# ------------------------------------------------------------------
if [ -f "${DATA_DIR}/rootCA/rootCA.key" ] && \
   [ -f "${DATA_DIR}/rootCA/rootCA.crt" ]; then
    echo "[minica‑init] root CA already exists – skipping"
    exit 0
fi

echo "[minica‑init] generating new root CA …"

# ------------------------------------------------------------------
# 3. run the actual CLI as the unprivileged user
# ------------------------------------------------------------------
#     · single‑quoted command → no shell‑escaping surprises
#     · `--force` guarantees idempotence if you *do* want rotation
exec su myca -s /bin/sh -c 'mini_ca.py init --force'
