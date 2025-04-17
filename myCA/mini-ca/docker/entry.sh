#!/bin/sh
set -e

CMD="$1"; shift || true

case "$CMD" in
  init|"")                      # default == no args
    # ensure writable dirs inside the mounted volume
    [ -d "$MYCA_ROOT" ]  || mkdir -p "$MYCA_ROOT"
    [ -d "$MYCA_CERTS" ] || mkdir -p "$MYCA_CERTS"
    python /opt/myca/gen_root_ca.py ${FORCE:+--force}
    exec sleep infinity         # keep the container around for exec/debug
    ;;
  issue)
    exec python /opt/myca/gen_certs.py "$@"
    ;;
  watch)
    exec python /opt/myca/watch_domains.py "$@"
    ;;
  *)
    echo "Unknown command '$CMD'"; exit 1
esac
