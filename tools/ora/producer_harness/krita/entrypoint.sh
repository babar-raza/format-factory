#!/bin/sh
# Manual Xvfb startup, mirroring ../entrypoint.sh's own already-verified
# approach for GIMP (xvfb-run's own SIGUSR1 handshake was found unreliable
# under this host's Docker Desktop/WSL2 backend in that earlier session).
# Reused verbatim here rather than re-deriving, since the root cause is the
# same host environment, not anything specific to GIMP.
set -e

DISPLAY_NUM=99
export DISPLAY=":${DISPLAY_NUM}"

Xvfb "$DISPLAY" -screen 0 1280x1024x24 -nolisten tcp &
XVFB_PID=$!

tries=0
max_tries=50
until xdpyinfo -display "$DISPLAY" >/dev/null 2>&1; do
    tries=$((tries + 1))
    if [ "$tries" -ge "$max_tries" ]; then
        echo "entrypoint.sh: Xvfb did not become ready after ${max_tries} attempts" >&2
        kill "$XVFB_PID" 2>/dev/null || true
        exit 1
    fi
    if ! kill -0 "$XVFB_PID" 2>/dev/null; then
        echo "entrypoint.sh: Xvfb process exited before becoming ready" >&2
        exit 1
    fi
    sleep 0.2
done

echo "entrypoint.sh: Xvfb ready on $DISPLAY after ${tries} poll attempts" >&2

"$@"
STATUS=$?

kill "$XVFB_PID" 2>/dev/null || true
exit "$STATUS"
