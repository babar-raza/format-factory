"""
watch_for_bundle.py — Format Factory Bundle Watcher Daemon
Polls a watch directory for new evidence bundle ZIPs and automatically
triggers the full supervisor pipeline when one appears.

No external dependencies — stdlib only.

Exit codes:
  0 — clean shutdown (SIGINT / KeyboardInterrupt)
  9 — unexpected error

Usage:
  python tools/supervisor/watch_for_bundle.py
  python tools/supervisor/watch_for_bundle.py --watch-dir .local/evidence
  python tools/supervisor/watch_for_bundle.py --interval 5 --log-file .local/watch.log
  python tools/supervisor/watch_for_bundle.py --once   # single check, exit
"""

import argparse
import json
import signal
import subprocess
import sys
import time
import zipfile
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent
STATE_FILE = REPO_ROOT / ".supervisor" / "state" / "watcher.json"

# Default watch roots — each is scanned recursively for *.zip
DEFAULT_WATCH_ROOTS = [
    REPO_ROOT / ".local",           # all subdirs — agents may drop bundles anywhere
    REPO_ROOT / "evidence-bundles",
]

DEFAULT_INTERVAL = 10  # seconds between polls


def log(msg: str, log_file=None) -> None:
    line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    if log_file:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(line + "\n")


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    existing = load_state()
    existing.update(state)
    STATE_FILE.write_text(json.dumps(existing, indent=2), encoding="utf-8")


def find_bundles(watch_roots: list[Path]) -> list[Path]:
    """Return all *.zip files under watch_roots (recursive) sorted by mtime descending."""
    bundles = []
    for root in watch_roots:
        if root.is_dir():
            bundles.extend(root.glob("**/*.zip"))
    bundles.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return bundles


def is_write_complete(path: Path, settle_secs: float = 1.5) -> bool:
    """Return True if file size is stable across settle_secs — writer has finished."""
    try:
        size1 = path.stat().st_size
        time.sleep(settle_secs)
        size2 = path.stat().st_size
        return size1 == size2 and size1 > 0
    except Exception:
        return False


def is_valid_zip(path: Path) -> bool:
    try:
        with zipfile.ZipFile(path, "r"):
            return True
    except Exception:
        return False


def trigger_pipeline(bundle_path: Path, log_file=None) -> int:
    """Run supervisor_loop.py run-on-latest on the given bundle. Returns exit code."""
    loop_script = SCRIPT_DIR / "supervisor_loop.py"
    cmd = [
        sys.executable,
        str(loop_script),
        "run-on-latest",
        "--bundle", str(bundle_path),
    ]
    log(f"TRIGGER: {' '.join(cmd)}", log_file)
    result = subprocess.run(cmd, cwd=str(REPO_ROOT))
    return result.returncode


def check_once(watch_roots: list[Path], log_file=None) -> bool:
    """
    Check watch_roots (recursively) for a bundle newer than the last processed one.
    Returns True if a new bundle was found and processed, False otherwise.
    """
    state = load_state()
    last_processed_mtime = state.get("last_processed_mtime", 0.0)
    last_processed_path = state.get("last_processed_path", "")

    bundles = find_bundles(watch_roots)
    if not bundles:
        return False

    newest = bundles[0]
    newest_mtime = newest.stat().st_mtime

    # Already processed this one
    if str(newest.resolve()) == last_processed_path and newest_mtime <= last_processed_mtime:
        return False

    # New or updated bundle detected
    log(f"NEW BUNDLE DETECTED: {newest.name} (mtime={datetime.fromtimestamp(newest_mtime).isoformat()})", log_file)

    # Wait for write to finish
    log("Waiting for write to settle...", log_file)
    if not is_write_complete(newest):
        log("File size still changing — skipping this poll cycle", log_file)
        return False

    # Validate it's a real ZIP
    if not is_valid_zip(newest):
        log(f"SKIP: {newest.name} is not a valid ZIP — will retry next poll", log_file)
        return False

    # Record we are processing it (before trigger, so a crash doesn't loop)
    save_state({
        "last_processed_path": str(newest.resolve()),
        "last_processed_mtime": newest_mtime,
        "last_trigger_timestamp": datetime.now().isoformat(),
        "last_trigger_status": "in_progress",
    })

    rc = trigger_pipeline(newest, log_file)

    save_state({
        "last_trigger_exit_code": rc,
        "last_trigger_status": "complete" if rc == 0 else f"failed_{rc}",
    })

    if rc == 0:
        log(f"PIPELINE: COMPLETE (exit 0) — outputs in reports/supervisor/", log_file)
    elif rc == 3:
        log(f"PIPELINE: CRITICAL CONTRADICTIONS (exit 3) — see reports/supervisor/approval-gates.md", log_file)
    else:
        log(f"PIPELINE: FAILED (exit {rc})", log_file)

    return True


def resolve_watch_roots(explicit: Path | None) -> list[Path]:
    """Return list of roots to scan. If --watch-dir given, use it alone; else use defaults."""
    if explicit:
        return [explicit.resolve()]
    return DEFAULT_WATCH_ROOTS


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Watch for new Format Factory evidence bundles and trigger supervisor pipeline"
    )
    parser.add_argument(
        "--watch-dir",
        type=Path,
        default=None,
        help=f"Root directory to scan recursively for *.zip bundles (default: {DEFAULT_WATCH_ROOTS[0]})",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=DEFAULT_INTERVAL,
        help=f"Poll interval in seconds (default: {DEFAULT_INTERVAL})",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        help="Optional log file path (in addition to stdout)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Check once and exit (no loop)",
    )
    args = parser.parse_args()

    watch_roots = resolve_watch_roots(args.watch_dir)
    for root in watch_roots:
        root.mkdir(parents=True, exist_ok=True)

    log_file = str(args.log_file) if args.log_file else None

    log(f"WATCHER STARTED", log_file)
    for root in watch_roots:
        log(f"  Watch root:   {root} (recursive)", log_file)
    log(f"  Poll interval: {args.interval}s", log_file)
    log(f"  State file:   {STATE_FILE}", log_file)
    if log_file:
        log(f"  Log file:     {log_file}", log_file)

    # Show last processed bundle from state
    state = load_state()
    if state.get("last_processed_path"):
        log(f"  Last processed: {Path(state['last_processed_path']).name} ({state.get('last_trigger_timestamp', '?')})", log_file)
    else:
        log("  Last processed: (none — first run)", log_file)

    if args.once:
        found = check_once(watch_roots, log_file)
        log(f"WATCHER: --once mode complete ({'new bundle processed' if found else 'no new bundle'})", log_file)
        return 0

    # Register clean shutdown on SIGINT/SIGTERM
    _running = [True]

    def _stop(sig, frame):
        _running[0] = False
        log("WATCHER: shutdown signal received", log_file)

    signal.signal(signal.SIGINT, _stop)
    try:
        signal.signal(signal.SIGTERM, _stop)
    except (OSError, AttributeError):
        pass  # SIGTERM not available on all platforms

    log(f"WATCHER: polling every {args.interval}s — press Ctrl+C to stop", log_file)

    while _running[0]:
        try:
            check_once(watch_roots, log_file)
        except Exception as e:
            log(f"ERROR during poll: {e}", log_file)

        # Sleep in small increments so SIGINT is responsive
        deadline = time.monotonic() + args.interval
        while _running[0] and time.monotonic() < deadline:
            time.sleep(0.5)

    log("WATCHER: stopped cleanly", log_file)
    return 0


if __name__ == "__main__":
    sys.exit(main())
