#!/bin/bash

# Usage: ./generate-certs.sh <domain>

if [ -z "$1" ]; then
    echo "Usage: $0 <domain>"
    exit 1
fi

DOMAIN=$1
SCRIPT_DIR=$(dirname "$(realpath "$0")")
CA_CERT="$SCRIPT_DIR/rootCA/rootCA.crt"
CA_KEY="$SCRIPT_DIR/rootCA/rootCA.key"
CERT_DIR="$SCRIPT_DIR/certs/$DOMAIN"

mkdir -p "$CERT_DIR"

cat << EOF > "$CERT_DIR/$DOMAIN.conf"
[req]
default_bits       = 4096
prompt             = no
default_md         = sha256
req_extensions     = req_ext
distinguished_name = dn

[dn]
CN = $DOMAIN.bugfam.local

[req_ext]
subjectAltName = @alt_names

[alt_names]
DNS.1 = $DOMAIN.bugfam.local
DNS.2 = *.$DOMAIN.bugfam.local
EOF

# Generate private key and CSR
openssl req -new -keyout "$CERT_DIR/$DOMAIN.key" \
  -out "$CERT_DIR/$DOMAIN.csr" \
  -config "$CERT_DIR/$DOMAIN.conf" -nodes

# Sign the CSR with your CA
openssl x509 -req -in "$CERT_DIR/$DOMAIN.csr" \
  -CA "$CA_CERT" -CAkey "$CA_KEY" -CAcreateserial \
  -out "$CERT_DIR/$DOMAIN.crt" -days 3650 -sha256 -extensions req_ext \
  -extfile "$CERT_DIR/$DOMAIN.conf"

# Output clearly formatted
printf "\nCertificate generated for domain '%s' in folder '%s':\n" "$DOMAIN" "$CERT_DIR"
printf -- "- Certificate: %s/%s.crt\n" "$CERT_DIR" "$DOMAIN"
printf -- "- Private key: %s/%s.key\n" "$CERT_DIR" "$DOMAIN"
printf -- "- CSR: %s/%s.csr\n" "$CERT_DIR" "$DOMAIN"
printf -- "- Config: %s/%s.conf\n" "$CERT_DIR" "$DOMAIN"
