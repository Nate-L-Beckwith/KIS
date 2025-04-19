#!/usr/bin/env sh
set -eu

UID_MYCA=${UID_MYCA:-1001}
GID_MYCA=${GID_MYCA:-1001}

DATA_DIR=/data
CA_DIR="${DATA_DIR}/rootCA"
DOMAINS_FILE="${DATA_DIR}/DOMAINS"

echo "[minica‑init] ensuring perms on ${DATA_DIR}"
chown "${UID_MYCA}:${GID_MYCA}" "${DATA_DIR}" || true

##############################################################################
# create a short script that will run *as myca* (no scary nested quoting)
##############################################################################
INIT_SCRIPT=$(mktemp)

cat > "${INIT_SCRIPT}" <<'EOSH'
#!/usr/bin/env sh
set -eu

# NOTE: the variables below are substituted *before* we switch user
CA_DIR="${CA_DIR}"
DOMAINS_FILE="${DOMAINS_FILE}"
DATA_DIR="${DATA_DIR}"
UID_MYCA="${UID_MYCA}"
GID_MYCA="${GID_MYCA}"

if [ ! -f "${CA_DIR}/rootCA.key" ] || [ ! -f "${CA_DIR}/rootCA.crt" ]; then
  echo "[minica‑init] generating root CA …"
  mini_ca.py init
else
  echo "[minica‑init] root CA already exists – skipping"
fi

# make sure the watcher file exists and is writable
touch "${DOMAINS_FILE}"

# final ownership sweep
chown -R "${UID_MYCA}:${GID_MYCA}" "${DATA_DIR}"
EOSH

chmod +x "${INIT_SCRIPT}"

##############################################################################
# run it as the unprivileged myca user
##############################################################################
su -s /bin/sh -c "${INIT_SCRIPT}" myca

rm -f "${INIT_SCRIPT}"
echo "[minica‑init] done – volume ready"
