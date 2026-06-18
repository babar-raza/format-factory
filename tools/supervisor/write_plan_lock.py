"""
write_plan_lock.py — Write plan lock files to prevent sprint loop from running
while a per-chat plan is active.

Two lock mechanisms are written simultaneously:
  1. Session-keyed: .local/supervisor/plan-locks/<session_id>.json  (race-safe)
  2. Shared fallback: .local/supervisor/active-plan-lock.json  (backwards compat)

Both are consumed by check_continuation.py (Check 1b) which returns
ACTIVE_PLAN_INCOMPLETE and blocks the sprint loop until the plan is closed.

Usage:
  # Mark a plan as active (blocks sprint loop):
  python tools/supervisor/write_plan_lock.py --plan-path plans/polished-giggling-tome.md

  # Update last completed taskcard:
  python tools/supervisor/write_plan_lock.py --plan-path plans/foo.md --last-taskcard Phase-3-complete

  # Mark the plan as complete (unblocks sprint loop):
  python tools/supervisor/write_plan_lock.py --plan-path plans/foo.md --complete

  # Clear all lock files (emergency reset):
  python tools/supervisor/write_plan_lock.py --clear
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo_root = _here.parent.parent
_shared_lock_path = _repo_root / ".local" / "supervisor" / "active-plan-lock.json"
_plan_locks_dir = _repo_root / ".local" / "supervisor" / "plan-locks"


def _get_session_id() -> str:
    """Get or create a session ID for the current process."""
    # Try to reuse the CCI session identity if available
    try:
        sys.path.insert(0, str(_here))
        from continuation_identity import get_or_create_session_identity
        return get_or_create_session_identity().session_id
    except Exception:
        pass
    # Fallback: use process ID + env-based ID
    return f"pid-{os.getpid()}"


def write_lock(plan_path: str, last_taskcard: str | None = None, complete: bool = False,
               session_id: str | None = None) -> None:
    status = "COMPLETE" if complete else "IN_PROGRESS"
    lock = {
        "plan_path": plan_path,
        "status": status,
        "last_taskcard": last_taskcard,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    # 1. Write shared fallback lock (backwards compatibility)
    _shared_lock_path.parent.mkdir(parents=True, exist_ok=True)
    _shared_lock_path.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    print(f"[write_plan_lock] {_shared_lock_path} written — status={status}, plan={plan_path!r}")

    # 2. Write session-keyed lock (race-safe; one file per session)
    sid = session_id or _get_session_id()
    lock["session_id"] = sid
    _plan_locks_dir.mkdir(parents=True, exist_ok=True)
    keyed_path = _plan_locks_dir / f"{sid}.json"
    keyed_path.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    print(f"[write_plan_lock] {keyed_path} written — session={sid!r}")


def clear_lock(session_id: str | None = None) -> None:
    removed = []
    if _shared_lock_path.exists():
        _shared_lock_path.unlink()
        removed.append(str(_shared_lock_path))
    sid = session_id or _get_session_id()
    keyed_path = _plan_locks_dir / f"{sid}.json"
    if keyed_path.exists():
        keyed_path.unlink()
        removed.append(str(keyed_path))
    if removed:
        for p in removed:
            print(f"[write_plan_lock] cleared: {p}")
    else:
        print(f"[write_plan_lock] No lock files to clear")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Write active-plan-lock.json to block sprint loop while a plan is active"
    )
    parser.add_argument("--plan-path", type=str, default=None,
                        help="Relative plan file path, e.g. plans/polished-giggling-tome.md")
    parser.add_argument("--last-taskcard", type=str, default=None,
                        help="Last completed taskcard/phase ID (for progress tracking)")
    parser.add_argument("--complete", action="store_true",
                        help="Mark the plan as COMPLETE, unblocking the sprint loop")
    parser.add_argument("--clear", action="store_true",
                        help="Delete the lock file entirely (emergency reset)")
    args = parser.parse_args(argv)

    if args.clear:
        clear_lock()
        return 0

    if not args.plan_path:
        print("ERROR: --plan-path is required unless --clear is given", file=sys.stderr)
        return 1

    write_lock(args.plan_path, last_taskcard=args.last_taskcard, complete=args.complete)
    return 0





if __name__ == "__main__":
    sys.exit(main())
