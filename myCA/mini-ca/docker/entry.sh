#!/usr/bin/env sh
# tiny wrapper – forwards every CLI arg to Typer
set -eu
exec python /opt/myca/mini_ca.py "$@"
