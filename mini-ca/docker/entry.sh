#!/usr/bin/env sh
set -eu

echo "[minica] watching /data/DOMAINS …"
exec mini_ca.py watch --file /data/DOMAINS
