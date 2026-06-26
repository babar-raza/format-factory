"""
reopen_plan_lock.py — Governed reopening of TERMINAL_CLOSED plan locks.

Transitions a TERMINAL_CLOSED (or COMPLETE) plan lock back to IN_PROGRESS,
preserving the original closure in the lock's closure_history array and
appending to .local/supervisor/reopening-register.json.

Modes:
  --same-plan (default): Reopen the same plan in-place.
      Use when missed requirements belong to the original mission scope.

  --successor <new-plan-path>: Mark the original as SUPERSEDED_BY_SUCCESSOR
      and do NOT reopen it. Use when new work is genuinely outside the
      original mission scope.

Usage:
  # Reopen a terminally closed plan:
  python tools/supervisor/reopen_plan_lock.py \\
    --plan-path C:/Users/prora/.claude/plans/some-plan.md \\
    --reason "Missed in-scope requirement TC-XXX found post-closure" \\
    --trigger MISSED_REQUIREMENT

  # Create a successor plan instead:
  python tools/supervisor/reopen_plan_lock.py \\
    --plan-path C:/Users/prora/.claude/plans/old-plan.md \\
    --successor C:/Users/prora/.claude/plans/new-plan.md \\
    --reason "New out-of-scope work discovered" \\
    --trigger OUT_OF_SCOPE_WORK

Exit codes:
  0 — success
  1 — error (plan not found, wrong status, etc.)

Created: 2026-06-23
Task: TC-TCF-007 (eager-snuggling-sifakis)
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo_root = _here.parent.parent
_plan_locks_dir = _repo_root / ".local" / "supervisor" / "plan-locks"
_shared_lock_path = _repo_root / ".local" / "supervisor" / "active-plan-lock.json"
_reopening_register_path = _repo_root / ".local" / "supervisor" / "reopening-register.json"

VALID_TRIGGERS = [
    "MISSED_REQUIREMENT",
    "REGRESSION",
    "AUDIT_FINDING",
    "WRONG_MISSION",
    "EVIDENCE_INVALIDATION",
    "INCOMPLETE_VERIFICATION",
    "OUT_OF_SCOPE_WORK",
    "AUTONOMOUS_OPEN_TASKCARD_DETECTION",
    "DEFECTIVE_CLOSURE_MACHINERY",
    "OTHER",
]


def _get_session_id() -> str:
    try:
        sys.path.insert(0, str(_here))
        from continuation_identity import get_or_create_session_identity
        return get_or_create_session_identity().session_id
    except Exception:
        import os
        return f"pid-{os.getpid()}"


def _find_lock_files(plan_path: str) -> list[Path]:
    """Find all lock files (session-keyed + shared) referencing this plan."""
    norm = plan_path.replace("\\", "/")
    found = []
    if _plan_locks_dir.exists():
        for f in sorted(_plan_locks_dir.glob("*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                lp = str(data.get("plan_path", "")).replace("\\", "/")
                if lp == norm or norm.endswith(lp) or lp.endswith(norm):
                    found.append(f)
            except Exception:
                continue
    if _shared_lock_path.exists():
        try:
            data = json.loads(_shared_lock_path.read_text(encoding="utf-8"))
            lp = str(data.get("plan_path", "")).replace("\\", "/")
            if lp == norm or norm.endswith(lp) or lp.endswith(norm):
                found.append(_shared_lock_path)
        except Exception:
            pass
    return found


def reopen_plan(
    plan_path: str,
    reason: str,
    trigger: str = "MISSED_REQUIREMENT",
    evidence: str | None = None,
    successor_path: str | None = None,
) -> dict:
    """Reopen a TERMINAL_CLOSED plan or create a successor.

    Returns a dict with the reopening record.
    """
    now = datetime.now(timezone.utc).isoformat()
    sid = _get_session_id()
    norm_plan = plan_path.replace("\\", "/")
    plan_name = Path(norm_plan).stem

    lock_files = _find_lock_files(norm_plan)
    if not lock_files:
        raise ValueError(f"No lock files found for plan: {plan_path}")

    # Validate at least one lock is TERMINAL_CLOSED or COMPLETE
    reopenable = []
    for lf in lock_files:
        data = json.loads(lf.read_text(encoding="utf-8"))
        if data.get("status") in ("TERMINAL_CLOSED", "COMPLETE"):
            reopenable.append((lf, data))

    if not reopenable:
        statuses = [json.loads(lf.read_text()).get("status") for lf in lock_files]
        raise ValueError(
            f"Cannot reopen: no TERMINAL_CLOSED or COMPLETE lock found. "
            f"Current statuses: {statuses}"
        )

    new_status = "SUPERSEDED_BY_SUCCESSOR" if successor_path else "IN_PROGRESS"

    # Process each reopenable lock
    for lf, data in reopenable:
        # Preserve original closure in closure_history
        history = data.get("closure_history", [])
        history.append({
            "status": data["status"],
            "closed_at": data.get("updated_at"),
            "closed_by_session": data.get("session_id"),
            "reopened_at": now,
            "reopened_by_session": sid,
            "reopening_reason": reason,
            "reopening_trigger": trigger,
        })

        # TC-LOCK-003 (FF-LOCK-HEAL-20260624): Mark old lock as SUPERSEDED instead of
        # overwriting its session_id. Then create a new lock via write_plan_lock.write_lock()
        # which uses the proper {sid}-{plan_hash}.json filename.
        old_session_id = data.get("session_id")

        # Mark old lock file as SUPERSEDED (preserve original session_id)
        data["closure_history"] = history
        data["status"] = "SUPERSEDED"
        data["superseded_by_session"] = sid
        data["superseded_at"] = now
        data["reopened_from_session"] = old_session_id
        data["reopening_reason"] = reason
        if successor_path:
            data["successor_plan_path"] = successor_path.replace("\\", "/")
        # DO NOT change data["session_id"] — keep the original owner for traceability

        lf.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print(f"[reopen_plan_lock] {lf.name}: marked SUPERSEDED (original session={old_session_id!r})")

        # Create new lock via write_lock (proper filename with current session_id)
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from write_plan_lock import write_lock
        _track = data.get("track_type", "product")
        if successor_path:
            write_lock(successor_path.replace("\\", "/"), session_id=sid, track_type=_track)
        else:
            write_lock(norm_plan, session_id=sid, track_type=_track)
        print(f"[reopen_plan_lock] new lock created for session={sid!r}, status={new_status}")

    # Write reopening register entry
    reopening_id = f"REOPEN-{plan_name}-{now.replace(':', '').replace('-', '')[:15]}"
    record = {
        "reopening_id": reopening_id,
        "original_closure_id": f"{reopenable[0][1].get('session_id', 'unknown')}-{plan_name}",
        "mission_id": None,
        "plan_path": norm_plan,
        "reopened_at": now,
        "trigger": trigger,
        "reason": reason,
        "evidence": evidence,
        "invalidated_closure_conditions": [],
        "prior_closure_preserved": True,
        "new_status": new_status,
        "successor_plan_path": successor_path.replace("\\", "/") if successor_path else None,
        "reopened_by_session": sid,
    }

    # Append to register
    register: list[dict] = []
    if _reopening_register_path.exists():
        try:
            register = json.loads(_reopening_register_path.read_text(encoding="utf-8"))
        except Exception:
            register = []

    # Idempotency: don't create duplicate entries for same plan + same trigger
    already_exists = any(
        r.get("plan_path") == norm_plan and r.get("trigger") == trigger and r.get("reason") == reason
        for r in register
    )
    if not already_exists:
        register.append(record)
        _reopening_register_path.parent.mkdir(parents=True, exist_ok=True)
        _reopening_register_path.write_text(json.dumps(register, indent=2) + "\n", encoding="utf-8")
        print(f"[reopen_plan_lock] Reopening record appended to {_reopening_register_path.name}")
    else:
        print("[reopen_plan_lock] Reopening record already exists (idempotent skip)")

    if successor_path:
        print(f"[reopen_plan_lock] Original plan marked SUPERSEDED_BY_SUCCESSOR. "
              f"Successor: {successor_path}")
    else:
        print("[reopen_plan_lock] Plan reopened. Original closure preserved in closure_history.")

    return record


def classify_work_scope(
    new_work_description: str,
    original_plan_path: str,
    trigger: str,
) -> str:
    """TC-TCF-006: Classify whether new work is IN_SCOPE or OUT_OF_SCOPE of a closed plan.

    IN_SCOPE when:
      - trigger is a known in-scope type (e.g. MISSED_REQUIREMENT, REGRESSION, AUDIT_FINDING)
      - OR new_work_description references a TC-* ID that appears in the original plan file

    OUT_OF_SCOPE when:
      - trigger is OUT_OF_SCOPE_WORK
      - OR no TC-ID overlap with original plan and trigger is not an in-scope type

    Returns "IN_SCOPE" or "OUT_OF_SCOPE".
    """
    import re as _re

    _IN_SCOPE_TRIGGERS = frozenset({
        "MISSED_REQUIREMENT",
        "REGRESSION",
        "AUDIT_FINDING",
        "INCOMPLETE_VERIFICATION",
        "AUTONOMOUS_OPEN_TASKCARD_DETECTION",
        "EVIDENCE_INVALIDATION",
        "DEFECTIVE_CLOSURE_MACHINERY",
    })

    # Explicit out-of-scope trigger
    if trigger == "OUT_OF_SCOPE_WORK":
        return "OUT_OF_SCOPE"

    # Known in-scope triggers → always IN_SCOPE
    if trigger in _IN_SCOPE_TRIGGERS:
        return "IN_SCOPE"

    # For other triggers (WRONG_MISSION, OTHER), check TC-ID overlap
    _tc_pattern = _re.compile(r"\bTC-[A-Z0-9]+-[A-Z0-9-]+", _re.IGNORECASE)
    new_tc_ids = set(_tc_pattern.findall(new_work_description))
    if not new_tc_ids:
        return "OUT_OF_SCOPE"

    try:
        plan_text = Path(original_plan_path).read_text(encoding="utf-8", errors="replace")
        plan_tc_ids = set(_tc_pattern.findall(plan_text))
        if new_tc_ids & plan_tc_ids:
            return "IN_SCOPE"
    except Exception:
        pass

    return "OUT_OF_SCOPE"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Governed reopening of TERMINAL_CLOSED plan locks"
    )
    parser.add_argument("--plan-path", required=True,
                        help="Path to the plan file to reopen")
    parser.add_argument("--reason", required=True,
                        help="Reason for reopening (free text)")
    parser.add_argument("--trigger", default="MISSED_REQUIREMENT",
                        choices=VALID_TRIGGERS,
                        help="Reopening trigger type")
    parser.add_argument("--evidence", default=None,
                        help="Path to evidence supporting the reopening")
    parser.add_argument("--successor", default=None,
                        help="Path to successor plan (if using successor mode instead of same-plan reopen)")
    parser.add_argument("--json", dest="output_json", action="store_true",
                        help="Print reopening record as JSON")

    args = parser.parse_args(argv)

    try:
        record = reopen_plan(
            plan_path=args.plan_path,
            reason=args.reason,
            trigger=args.trigger,
            evidence=args.evidence,
            successor_path=args.successor,
        )
        if args.output_json:
            print(json.dumps(record, indent=2))
        return 0
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: unexpected failure: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
