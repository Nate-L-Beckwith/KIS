#!/bin/bash

# Root CA generation script
# Usage: ./generate_rootCA.sh

set -e

SCRIPT_DIR=$(dirname "$(readlink -f \"$0\")")
cd "$SCRIPT_DIR" || exit

ROOT_CA_DIR="net-stack/myCA/rootCA"
ROOT_CA_KEY="$ROOT_CA_DIR/rootCA.key"
ROOT_CA_CERT="$ROOT_CA_DIR/rootCA.crt"

# Create the rootCA directory if it doesn't exist
mkdir -p "$ROOT_CA_DIR"

# Check if the Root CA already exists
if [ -f "$ROOT_CA_KEY" ] || [ -f "$ROOT_CA_CERT" ]; then
  read -p "Are you absolutely sure you want to overwrite the existing Root CA key or certificate? (yes/no) [1/3]: " confirm
  if [ "$confirm" != "yes" ]; then
    echo "ya, thought so."
    exit 1
  fi
  read -p "This action is irreversible. Confirm again to overwrite the Root CA files. (yes/no) [2/3]: " confirm
  if [ "$confirm" != "yes" ]; then
    echo "fool me once, etc..."
    exit 1
  fi
  read -p "Final confirmation Do you definitely want to overwrite your existing Root CA? THIS WILL BREAK SOMETHING (yes/no) [3/3]: " confirm
  if [ "$confirm" != "yes" ]; then
    echo "Almost had me tbh.."
    exit 1
  fi
fi

# Generate Root CA private key
openssl genrsa -out "$ROOT_CA_KEY" 4096

# Generate self-signed Root CA certificate
openssl req -x509 -new -nodes \
  -key "$ROOT_CA_KEY" -sha256 \
  -days 3650 -out "$ROOT_CA_CERT" \
  -subj "/C=US/ST=VT/L=Boston/O=bugfam/CN=Bugfam-Root-CA"

# Output clearly formatted
printf "\nRoot CA successfully generated:\n"
printf -- "- Root CA Certificate: %s\n" "$ROOT_CA_CERT"
printf -- "- Root CA Private Key: %s\n" "$ROOT_CA_KEY"
