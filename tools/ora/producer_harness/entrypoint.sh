#!/bin/sh
# Manual Xvfb startup, bypassing xvfb-run's own SIGUSR1-based readiness
# handshake -- found unreliable under this host's container environment
# (Xvfb starts and stays healthy; xvfb-run's own wrapper shell hangs
# forever waiting for a signal that never arrives). Polls xdpyinfo directly
# instead, with a bounded number of attempts so a genuine Xvfb failure
# fails fast rather than hanging silently the same way.
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
