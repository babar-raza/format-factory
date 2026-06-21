"""
cci_migration.py — CCI Legacy State Migration (TC-CCI-015)

Scans .local/supervisor/ state files for missing session_id and either stamps
them from the active session or quarantines them.

Usage:
  python tools/supervisor/cci_migration.py [--dry-run]

Options:
  --dry-run   Print planned actions without writing.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_here = Path(__file__).resolve().parent
_repo_root = _here.parent.parent

STATE_DIR = _repo_root / ".local" / "supervisor"
QUARANTINE_DIR = STATE_DIR / "quarantine"
MIGRATION_LOG = STATE_DIR / "cci-migration-log.jsonl"
ACTIVE_SESSION_PATH = STATE_DIR / "active-session.json"

# State files that should carry session_id
TARGET_FILES = [
    "active-continuation.json",
    "orchestrator-state.json",
    "orchestrator-heartbeat.json",
    "stop-reason.json",
]

MAX_SESSION_AGE_HOURS = 2.0


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def _append_log(entry: dict) -> None:
    MIGRATION_LOG.parent.mkdir(parents=True, exist_ok=True)
    with MIGRATION_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def _get_active_session_id() -> Optional[str]:
    """Load session_id from active-session.json if it is recent enough."""
    data = _load_json(ACTIVE_SESSION_PATH)
    if not data:
        return None
    session_id = data.get("session_id")
    if not session_id:
        return None
    # Check staleness
    try:
        from datetime import timezone as _tz
        created = datetime.fromisoformat(data.get("created_at", ""))
        age_hours = (datetime.now(_tz.utc) - created).total_seconds() / 3600
        if age_hours > MAX_SESSION_AGE_HOURS:
            return None
    except Exception:
        pass
    return session_id


def run_migration(dry_run: bool = False) -> dict:
    """
    Scan TARGET_FILES for missing session_id.

    For each file missing session_id:
    - If active-session.json is fresh: stamp the session_id
    - Otherwise: quarantine the file

    Returns a summary dict with counts.
    """
    session_id = _get_active_session_id()
    results = {
        "scanned": 0,
        "already_ok": 0,
        "stamped": 0,
        "quarantined": 0,
        "not_found": 0,
        "errors": 0,
        "dry_run": dry_run,
        "active_session_id": session_id,
        "run_at": _now_iso(),
    }

    for filename in TARGET_FILES:
        path = STATE_DIR / filename
        if not path.exists():
            results["not_found"] += 1
            continue

        results["scanned"] += 1
        data = _load_json(path)

        if data is None:
            print(f"  ERROR: could not parse {filename}", file=sys.stderr)
            results["errors"] += 1
            continue

        existing_sid = data.get("session_id")
        if existing_sid:
            results["already_ok"] += 1
            print(f"  OK    {filename}: session_id={existing_sid!r}")
            continue

        # Missing session_id
        if session_id:
            action = "STAMP"
            detail = f"stamped session_id={session_id!r}"
        else:
            action = "QUARANTINE"
            detail = "no fresh active session; quarantined"

        print(f"  {action} {filename}: {detail}" + (" [DRY RUN]" if dry_run else ""))

        log_entry = {
            "timestamp": _now_iso(),
            "file": filename,
            "action": action,
            "session_id_stamped": session_id if action == "STAMP" else None,
            "dry_run": dry_run,
        }

        if not dry_run:
            try:
                if action == "STAMP":
                    data["session_id"] = session_id
                    data["cci_migrated_at"] = _now_iso()
                    _save_json(path, data)
                    results["stamped"] += 1
                else:
                    # Quarantine: move to quarantine dir with timestamp prefix
                    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
                    dest = QUARANTINE_DIR / f"{ts}_{filename}"
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    # Write quarantine copy, then replace original with tombstone
                    shutil.copy2(str(path), str(dest))
                    tombstone = {
                        "cci_quarantined": True,
                        "quarantine_reason": "no_session_id",
                        "original_path": str(path),
                        "quarantine_dest": str(dest),
                        "quarantined_at": _now_iso(),
                    }
                    _save_json(path, tombstone)
                    results["quarantined"] += 1
                    log_entry["quarantine_dest"] = str(dest)
                _append_log(log_entry)
            except Exception as e:
                print(f"  ERROR during {action} of {filename}: {e}", file=sys.stderr)
                results["errors"] += 1
        else:
            # dry-run: log intent only
            _append_log(log_entry)
            if action == "STAMP":
                results["stamped"] += 1
            else:
                results["quarantined"] += 1

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="CCI legacy state migration (TC-CCI-015)")
    parser.add_argument("--dry-run", action="store_true", help="Print plan without writing")
    args = parser.parse_args()

    mode = "DRY RUN" if args.dry_run else "LIVE"
    print(f"CCI Migration ({mode})")
    print(f"  State dir: {STATE_DIR}")
    print(f"  Target files: {TARGET_FILES}")
    print()

    results = run_migration(dry_run=args.dry_run)

    print()
    print("=== Summary ===")
    print(f"  Scanned:     {results['scanned']}")
    print(f"  Already OK:  {results['already_ok']}")
    print(f"  Stamped:     {results['stamped']}")
    print(f"  Quarantined: {results['quarantined']}")
    print(f"  Not found:   {results['not_found']}")
    print(f"  Errors:      {results['errors']}")

    if results["errors"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
