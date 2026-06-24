"""
write_plan_lock.py — Write plan lock files to prevent sprint loop from running
while a per-chat plan is active.

Two lock mechanisms are written simultaneously:
  1. Session-keyed: .local/supervisor/plan-locks/<session_id>.json  (race-safe)
  2. Shared fallback: .local/supervisor/active-plan-lock.json  (backwards compat)

Both are consumed by check_continuation.py (Check 1b) which returns
ACTIVE_PLAN_INCOMPLETE and blocks the sprint loop until the plan is closed.

Status values:
  IN_PROGRESS    — Plan is active; sprint loop is blocked.
  COMPLETE       — Plan done; sprint loop available in FUTURE sessions.
  TERMINAL_CLOSED — Plan done THIS session; sprint loop also blocked for this session.
                   Use --terminal (not --complete) when closing a plan within the session
                   that executed it, to prevent the ledger from starting automatically.

Usage:
  # Mark a plan as active (blocks sprint loop):
  python tools/supervisor/write_plan_lock.py --plan-path plans/polished-giggling-tome.md

  # Update last completed taskcard:
  python tools/supervisor/write_plan_lock.py --plan-path plans/foo.md --last-taskcard Phase-3-complete

  # Mark the plan as complete (unblocks sprint loop in future sessions):
  python tools/supervisor/write_plan_lock.py --plan-path plans/foo.md --complete

  # Mark the plan as terminal-closed (blocks ledger in this session too):
  python tools/supervisor/write_plan_lock.py --plan-path plans/foo.md --terminal

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

# Files that must NEVER be used as active_plan_path.
# These are governance-protected files that cannot serve as execution plans.
FORBIDDEN_AS_ACTIVE_PLAN = [
    "plans/master-plan-memory.md",
]

# TC-AMD-MACH-001: Temp/pytest path markers — shared lock must NOT be written for these.
# Pytest tests call write_plan_lock() with tmp_path fixtures, corrupting the shared
# active-plan-lock.json. Only the session-keyed lock is written for temp paths.
import tempfile as _tempfile
_TEMP_MARKERS = (
    _tempfile.gettempdir().lower().replace("\\", "/"),
    "/tmp/pytest",
    "appdata/local/temp",
    "pytest",
)


def _is_temp_path(p: str) -> bool:
    """Return True if plan_path looks like a pytest temp or system temp directory."""
    pl = p.lower().replace("\\", "/")
    return any(m in pl for m in _TEMP_MARKERS)


def cleanup_orphaned_tmp_files() -> None:
    """TC-AMD-MACH-003: Remove orphaned .tmp files left by crashed atomic writes.

    If a process dies between .write_text(".tmp") and os.replace(), a .tmp file
    persists indefinitely. This function is called at the start of write_lock()
    to keep the lock directories clean.

    Exception-safe: deletion errors are logged to stderr and silently ignored.
    """
    for search_dir in (_plan_locks_dir, _shared_lock_path.parent):
        if not search_dir.exists():
            continue
        for tmp_file in search_dir.glob("*.tmp"):
            try:
                tmp_file.unlink()
                print(f"[write_plan_lock] Removed orphaned .tmp: {tmp_file}", file=sys.stderr)
            except Exception as exc:
                print(
                    f"[write_plan_lock] WARNING: could not remove orphaned .tmp {tmp_file}: {exc}",
                    file=sys.stderr,
                )


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


def validate_plan_binding(target_path: str, intent: str = "harden") -> tuple[bool, str]:
    """Return (allowed: bool, reason: str).

    Reads all active (non-expired) session-keyed lock files and checks:
    1. If target_path is in forbidden_mutation_paths of any active lock -> blocked.
    2. TC-PG-007: If ANY lock has status == TERMINAL_CLOSED and its plan_path
       matches target_path -> blocked (regardless of binding_contract).
    3. TC-PG-007: Calls plan_identity.validate_plan_mutability() as fallback
       for plans with front-matter terminal locks (survives lock file expiry).
    4. If no matching lock exists or all locks are cleared -> allowed.

    # TC-PG-004: snoopy-juggling-seal.md is no longer hardcoded here.
    # Dynamic exclusion via universal TERMINAL_CLOSED scan replaces the
    # former hardcoded forbidden_mutation_paths entry.
    """
    norm_target = str(target_path).replace("\\", "/")
    if not _plan_locks_dir.exists():
        return True, "no_lock_dir"
    for lf in sorted(_plan_locks_dir.glob("*.json")):
        try:
            lock = json.loads(lf.read_text(encoding="utf-8"))
        except Exception:
            continue

        # Check explicit forbidden_mutation_paths from binding_contract
        bc = lock.get("binding_contract", {})
        forbidden = bc.get("forbidden_mutation_paths", [])
        for fp in forbidden:
            if norm_target.endswith(str(fp).replace("\\", "/")):
                return False, f"forbidden_mutation_path:{fp}"

        # TC-PG-007: Universal terminal lock enforcement — block writes to any
        # plan with a TERMINAL_CLOSED lock regardless of which session wrote it.
        if lock.get("status") == "TERMINAL_CLOSED":
            lock_plan = str(lock.get("plan_path", "")).replace("\\", "/")
            if lock_plan and (norm_target.endswith(lock_plan) or norm_target == lock_plan):
                return (
                    False,
                    f"TERMINAL_PLAN_MUTATION_REJECTED: plan '{target_path}' has "
                    f"TERMINAL_CLOSED lock from session "
                    f"'{lock.get('session_id', 'unknown')}' "
                    f"(locked at {lock.get('updated_at', 'unknown')})",
                )

    # TC-PG-007: Also check plan identity front-matter if plan_identity module available
    try:
        _here_dir = Path(__file__).resolve().parent
        if str(_here_dir) not in sys.path:
            sys.path.insert(0, str(_here_dir))
        from plan_identity import validate_plan_mutability  # type: ignore[import]
        allowed, reason = validate_plan_mutability(Path(target_path))
        if not allowed:
            return False, reason
    except ImportError:
        pass  # plan_identity not yet available — graceful degradation

    return True, "allowed"


def write_lock(plan_path: str, last_taskcard: str | None = None, complete: bool = False,
               terminal: bool = False, session_id: str | None = None,
               track_type: str | None = "product", binding: bool = False,
               audit_gate: bool = False) -> None:
    # TC-AMD-MACH-003: Clean up orphaned .tmp files from previously crashed atomic writes
    cleanup_orphaned_tmp_files()
    # B3: normalize path separators so Windows backslashes don't prevent matching
    plan_path = str(plan_path).replace("\\", "/")

    # Guard: block governance-protected files from being used as active plans
    for forbidden in FORBIDDEN_AS_ACTIVE_PLAN:
        if plan_path.endswith(forbidden.replace("\\", "/")):
            raise ValueError(
                f"Cannot register '{plan_path}' as active_plan_path — "
                f"'{forbidden}' is a protected ledger file and cannot be an execution plan."
            )

    # --audit-gate: call lifecycle_audit before writing TERMINAL_CLOSED.
    # If audit requires iteration → write ITERATION_REQUIRED instead of TERMINAL_CLOSED.
    # Only applies when --terminal is set. Backward compat: --terminal without --audit-gate unchanged.
    if terminal and audit_gate:
        try:
            from lifecycle_audit import run_lifecycle_audit  # type: ignore[import]
            audit_result = run_lifecycle_audit(repo_root=_repo_root)
            audit_verdict = audit_result.get("verdict", "AUDIT_PASS")
            if audit_verdict == "AUDIT_REQUIRES_ITERATION":
                status = "ITERATION_REQUIRED"
                print(
                    "[write_plan_lock] --audit-gate: lifecycle audit verdict=AUDIT_REQUIRES_ITERATION "
                    "-> writing ITERATION_REQUIRED (plan will iterate)"
                )
            else:
                status = "TERMINAL_CLOSED"
                print("[write_plan_lock] --audit-gate: lifecycle audit verdict=AUDIT_PASS -> TERMINAL_CLOSED")
        except ImportError:
            # lifecycle_audit not installed yet — fall back to ITERATION_REQUIRED (D6 safety)
            print(
                "[write_plan_lock] WARNING: --audit-gate requested but lifecycle_audit not importable; "
                "falling back to ITERATION_REQUIRED",
                file=sys.stderr,
            )
            status = "ITERATION_REQUIRED"
        except Exception as exc:
            print(
                f"[write_plan_lock] WARNING: lifecycle_audit raised {exc}; falling back to ITERATION_REQUIRED",
                file=sys.stderr,
            )
            status = "ITERATION_REQUIRED"
    else:
        status = "TERMINAL_CLOSED" if terminal else ("COMPLETE" if complete else "IN_PROGRESS")

    # B2: get session_id BEFORE writing either file so both files have it
    sid = session_id or _get_session_id()
    lock = {
        "plan_path": plan_path,
        "status": status,
        "last_taskcard": last_taskcard,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "session_id": sid,
        "track_type": track_type,  # GAP-WF-004: machinery track skips product-track locks
    }
    if binding:
        lock["binding_contract"] = {
            "native_plan_path": plan_path,
            "active_plan_path": plan_path,
            "global_fallback_allowed": False,
            "ledger_path": "plans/master-plan-memory.md",
            "execution_may_create_plan": False,
            "hardening_may_change_plan_path": False,
            "forbidden_mutation_paths": [
                "plans/master-plan-memory.md",
                # TC-PG-004: snoopy-juggling-seal.md removed — dynamic exclusion
                # via TERMINAL_CLOSED scan in validate_plan_binding() replaces
                # the hardcoded entry. All non-active plans are now protected
                # dynamically, not just snoopy.
            ],
        }

    # 1. Write shared fallback lock (backwards compatibility) — now includes session_id
    # TC-AMD-MACH-001: Skip shared lock for pytest/temp paths to prevent contamination.
    # Tests call write_plan_lock() with tmp_path fixtures; writing the shared lock with
    # a temp path causes check_continuation.py to return ACTIVE_PLAN_INCOMPLETE for all
    # real sprints. Session-keyed lock is still written for test isolation.
    _wrote_shared = False
    if _is_temp_path(str(plan_path)):
        print(
            f"[write_plan_lock] SKIPPING shared lock: plan_path is temp/pytest ({plan_path})",
            file=sys.stderr,
        )
    else:
        # TC-AMD-FIX-003: Atomic write via temp+rename for crash safety
        _shared_lock_path.parent.mkdir(parents=True, exist_ok=True)
        _shared_tmp = _shared_lock_path.with_suffix(".tmp")
        _shared_tmp.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
        os.replace(str(_shared_tmp), str(_shared_lock_path))
        print(f"[write_plan_lock] {_shared_lock_path} written \u2014 status={status}, plan={plan_path!r}")
        _wrote_shared = True

    # 2. Write session-keyed lock (race-safe; one file per (session, plan) pair)
    # TC-LOCK-002 (FF-LOCK-HEAL-20260624): Use plan_path hash in filename to support
    # multi-plan sessions. Old {sid}.json files remain readable by check_continuation
    # (it globs *.json). Plan A's TERMINAL_CLOSED persists when Plan B starts.
    import hashlib
    _plan_hash = hashlib.sha256(plan_path.encode()).hexdigest()[:8]
    _plan_locks_dir.mkdir(parents=True, exist_ok=True)
    keyed_path = _plan_locks_dir / f"{sid}-{_plan_hash}.json"

    # F-006 / TC-PG-007: Overwrite protection — do NOT overwrite a TERMINAL_CLOSED
    # lock with IN_PROGRESS. This prevents the lock-overwrite scenario where a
    # subsequent plan operation destroys the terminal state of a completed plan.
    if keyed_path.exists() and status == "IN_PROGRESS":
        try:
            existing = json.loads(keyed_path.read_text(encoding="utf-8"))
            if existing.get("status") == "TERMINAL_CLOSED":
                print(
                    f"[write_plan_lock] BLOCKED: refusing to overwrite TERMINAL_CLOSED "
                    f"lock at {keyed_path.name} with IN_PROGRESS for plan {plan_path!r}",
                    file=sys.stderr,
                )
                return
        except Exception:
            pass  # If read fails, proceed with write

    # TC-AMD-FIX-003: Atomic write via temp+rename for crash safety
    _keyed_tmp = keyed_path.with_suffix(".tmp")
    _keyed_tmp.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    os.replace(str(_keyed_tmp), str(keyed_path))
    print(f"[write_plan_lock] {keyed_path} written \u2014 session={sid!r}")

    # TC-AMD-CONV-002: Post-write verification — read both locks and warn on mismatch.
    # Only runs when shared lock was written (skipped for temp/pytest paths).
    if _wrote_shared:
        try:
            _shared_readback = json.loads(_shared_lock_path.read_text(encoding="utf-8"))
            _keyed_readback = json.loads(keyed_path.read_text(encoding="utf-8"))
            if _shared_readback.get("status") != _keyed_readback.get("status"):
                print(
                    f"[write_plan_lock] WARNING: lock mismatch after write — "
                    f"shared={_shared_readback.get('status')}, keyed={_keyed_readback.get('status')}",
                    file=sys.stderr,
                )
        except Exception:
            pass  # Verification is best-effort

    # TC-PG-007: When terminal-closing a plan, append plan_terminal_lock block to the
    # plan file itself for durable lock detection beyond session-keyed lock expiry.
    if terminal and status in ("TERMINAL_CLOSED", "ITERATION_REQUIRED"):
        _append_terminal_lock_to_plan(plan_path, sid, status, datetime.now(timezone.utc).isoformat())


def _append_terminal_lock_to_plan(
    plan_path: str,
    session_id: str,
    status: str,
    locked_at: str,
) -> None:
    """TC-PG-007: Append a plan_terminal_lock HTML comment to the plan file.

    This durable marker lets plan_identity.validate_plan_mutability() detect
    the terminal lock directly from the plan file — even after session-keyed
    lock files expire or are overwritten.

    Appends only if no such block already exists (idempotent).
    Non-blocking: write failure is logged to stderr and ignored.
    """
    try:
        p = Path(plan_path)
        if not p.is_absolute():
            p = _repo_root / p
        if not p.exists():
            return  # Non-existent plan — skip silently

        existing = p.read_text(encoding="utf-8", errors="replace")
        if "<!--plan_terminal_lock:" in existing:
            return  # Already has a terminal lock block — idempotent

        terminal_block = (
            "\n\n"
            "<!--plan_terminal_lock:\n"
            f"  status: {status}\n"
            f'  locked_at: "{locked_at}"\n'
            f'  locked_by: "{session_id}"\n'
            "  successor_required_for_future_changes: true\n"
            '  mutation_policy: "no further plan/hardening/execution writes"\n'
            "-->\n"
        )
        p.write_text(existing + terminal_block, encoding="utf-8")
        print(f"[write_plan_lock] terminal lock block appended to plan file: {p.name}")
    except Exception as exc:
        # Log to stderr but do not block — terminal lock in lock file is primary
        print(f"[write_plan_lock] WARNING: could not append terminal lock to plan file: {exc}",
              file=sys.stderr)


def clear_lock(session_id: str | None = None) -> None:
    removed = []
    if _shared_lock_path.exists():
        _shared_lock_path.unlink()
        removed.append(str(_shared_lock_path))
    sid = session_id or _get_session_id()
    # TC-LOCK-002: Clear both old {sid}.json and new {sid}-{hash}.json patterns
    if _plan_locks_dir.is_dir():
        for keyed_path in _plan_locks_dir.glob(f"{sid}*.json"):
            keyed_path.unlink()
            removed.append(str(keyed_path))
    if removed:
        for p in removed:
            print(f"[write_plan_lock] cleared: {p}")
    else:
        print(f"[write_plan_lock] No lock files to clear")


def cleanup_completed_locks(older_than_hours: float = 24.0) -> int:
    """B6: Remove COMPLETE/TERMINAL_CLOSED lock files older than older_than_hours.
    Returns count of files removed."""
    from datetime import timedelta
    if not _plan_locks_dir.exists():
        return 0
    cutoff = datetime.now(timezone.utc) - timedelta(hours=older_than_hours)
    removed = 0
    for f in sorted(_plan_locks_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if data.get("status") not in ("COMPLETE", "TERMINAL_CLOSED"):
                continue
            ts = data.get("updated_at", "2000-01-01T00:00:00+00:00")
            updated = datetime.fromisoformat(ts)
            if updated.tzinfo is None:
                updated = updated.replace(tzinfo=timezone.utc)
            if updated < cutoff:
                f.unlink()
                removed += 1
                print(f"[write_plan_lock] cleaned up: {f.name}")
        except Exception as e:
            print(f"[write_plan_lock] SKIP {f.name}: {e}", file=sys.stderr)
    print(f"[write_plan_lock] --cleanup-completed: removed {removed} lock(s) older than {older_than_hours}h")
    return removed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Write active-plan-lock.json to block sprint loop while a plan is active"
    )
    parser.add_argument("--plan-path", type=str, default=None,
                        help="Relative plan file path, e.g. plans/polished-giggling-tome.md")
    parser.add_argument("--last-taskcard", type=str, default=None,
                        help="Last completed taskcard/phase ID (for progress tracking)")
    parser.add_argument("--complete", action="store_true",
                        help="Mark the plan as COMPLETE, unblocking the sprint loop for future sessions")
    parser.add_argument("--terminal", action="store_true",
                        help="Mark the plan as TERMINAL_CLOSED: done this session; "
                             "blocks ledger work in this session (POST_PLAN_TERMINAL stop)")
    parser.add_argument("--track-type", type=str, default="product",
                        help="Track type for this plan lock (default: product). "
                             "Machinery-track checks skip product-track locks. "
                             "Set to 'machinery' for machinery-track plans.")
    parser.add_argument("--clear", action="store_true",
                        help="Delete the lock file entirely (emergency reset)")
    parser.add_argument("--cleanup-completed", action="store_true",
                        help="Remove COMPLETE/TERMINAL_CLOSED lock files older than --older-than hours")
    parser.add_argument("--older-than", type=float, default=24.0,
                        help="Age threshold in hours for --cleanup-completed (default: 24)")
    parser.add_argument("--binding", action="store_true",
                        help="Include binding_contract in lock file to enforce plan path ownership "
                             "and block wrong-plan writes via validate_plan_binding()")
    parser.add_argument("--audit-gate", action="store_true",
                        help="When used with --terminal: call lifecycle_audit before closing. "
                             "If audit requires iteration, writes ITERATION_REQUIRED instead of "
                             "TERMINAL_CLOSED so check_continuation.py returns CONTINUE. "
                             "Backward compat: --terminal without --audit-gate is unchanged.")
    args = parser.parse_args(argv)

    if args.clear:
        clear_lock()
        return 0

    if args.cleanup_completed:
        cleanup_completed_locks(older_than_hours=args.older_than)
        return 0

    if not args.plan_path:
        print("ERROR: --plan-path is required unless --clear or --cleanup-completed is given",
              file=sys.stderr)
        return 1

    write_lock(args.plan_path, last_taskcard=args.last_taskcard,
               complete=args.complete, terminal=args.terminal,
               track_type=args.track_type, binding=args.binding,
               audit_gate=getattr(args, "audit_gate", False))
    return 0





if __name__ == "__main__":
    sys.exit(main())
