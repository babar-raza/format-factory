"""terminal_closure_validators.py — TC-TCF-007: Terminal closure governance validators.

Provides V-TCF-001, V-TCF-002, V-TCF-003 validators that plug into
governance_validator_runner.py via a try-except import block.

V-TCF-001: FAIL when LIFECYCLE_HARDENING/MACHINERY_HARDENING sprint claims terminal
           completion but lifecycle_audit finds open taskcards in the plan.
           (Broader than V60 which is WARN-only for RELEASE_GATE items only.)

V-TCF-002: WARN when sprint claims plan_terminal_closed=True but no
           terminal_closure_record.json exists in .local/evidences/plan-closures/.

V-TCF-003: WARN when active-plan-lock.json shows closure was triggered by a
           premature pattern (queue exhaustion, iteration limit, closeout-only sprint).

All validators follow the standard result schema:
  {"validator": str, "result": "PASS"|"WARN"|"FAIL", "message": str,
   "items": list, "blocks_sprint": bool}
"""

from __future__ import annotations

import json
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Declaration item types that assert terminal plan closure
_TERMINAL_CLAIM_TYPES = frozenset({"LIFECYCLE_HARDENING", "MACHINERY_HARDENING"})

# Premature closure trigger keywords in lock metadata
_PREMATURE_TRIGGER_PATTERNS = (
    "MAX_ITERATIONS",
    "GOVERNED_ROLLOVER",
    "QUEUE_EXHAUSTION",
    "CLOSEOUT_ONLY",
)


def _std_result(validator_id: str, result: str, message: str,
                items: list | None = None, blocks_sprint: bool = False) -> dict:
    return {
        "validator": validator_id,
        "result": result,
        "message": message,
        "items": items or [],
        "blocks_sprint": blocks_sprint and result == "FAIL",
    }


def validate_no_open_taskcards_at_terminal(
    declaration: dict, repo_root: Path | None = None
) -> dict:
    """V-TCF-001: FAIL if a LIFECYCLE_HARDENING/MACHINERY_HARDENING sprint declares
    terminal completion while lifecycle_audit detects open taskcards in the plan.

    This is broader than V60 (which only warns on RELEASE_GATE items).
    """
    validator_id = "V-TCF-001"
    if repo_root is None:
        repo_root = _REPO_ROOT

    # Check if this declaration has terminal-claim items
    work_items = declaration.get("work_items", [])
    terminal_items = [
        w for w in work_items
        if w.get("type") in _TERMINAL_CLAIM_TYPES
        and (w.get("plan_terminal_closed") or w.get("terminal_closure_claimed"))
    ]
    if not terminal_items:
        return _std_result(validator_id, "PASS", "No terminal closure claims in this declaration")

    # Read lifecycle audit results to check for open taskcards
    audit_path = repo_root / ".local" / "supervisor" / "lifecycle-audit-results.json"
    if not audit_path.exists():
        return _std_result(
            validator_id, "WARN",
            "Terminal closure claimed but no lifecycle-audit-results.json found. "
            "Run lifecycle_audit before declaring terminal closure.",
        )

    try:
        audit = json.loads(audit_path.read_text(encoding="utf-8", errors="replace"))
    except Exception as exc:
        return _std_result(validator_id, "WARN", f"lifecycle-audit-results.json unreadable: {exc}")

    open_tcs = audit.get("open_taskcards", [])
    if open_tcs:
        return _std_result(
            validator_id, "FAIL",
            f"Terminal closure claimed for {len(terminal_items)} item(s) but lifecycle_audit "
            f"found {len(open_tcs)} open taskcard(s): {open_tcs[:5]}. "
            "TERMINAL_CLOSED requires all mandatory taskcards to be closed.",
            items=open_tcs,
            blocks_sprint=True,
        )

    verdict = audit.get("verdict", "UNKNOWN")
    if verdict == "AUDIT_REQUIRES_ITERATION":
        audit_findings = [f.get("description", "")[:80] for f in audit.get("findings", [])[:3]]
        return _std_result(
            validator_id, "FAIL",
            f"Terminal closure claimed but lifecycle_audit verdict=AUDIT_REQUIRES_ITERATION. "
            f"Top findings: {audit_findings}",
            items=audit_findings,
            blocks_sprint=True,
        )

    return _std_result(
        validator_id, "PASS",
        f"Lifecycle audit verdict={verdict} with no open taskcards. Terminal closure valid."
    )


def validate_terminal_closure_has_contract(
    declaration: dict, repo_root: Path | None = None
) -> dict:
    """V-TCF-002: WARN if sprint claims plan_terminal_closed=True but no
    terminal_closure_record.json exists in .local/evidences/plan-closures/.
    """
    validator_id = "V-TCF-002"
    if repo_root is None:
        repo_root = _REPO_ROOT

    work_items = declaration.get("work_items", [])
    terminal_items = [
        w for w in work_items
        if w.get("type") in _TERMINAL_CLAIM_TYPES
        and (w.get("plan_terminal_closed") or w.get("terminal_closure_claimed"))
    ]
    if not terminal_items:
        return _std_result(validator_id, "PASS", "No terminal closure claims to verify")

    closures_dir = repo_root / ".local" / "evidences" / "plan-closures"
    if not closures_dir.exists():
        return _std_result(
            validator_id, "WARN",
            "Terminal closure claimed but .local/evidences/plan-closures/ does not exist. "
            "TC-TCF-004: terminal_closure_record.json should be written by write_plan_lock.py --terminal.",
        )

    records = list(closures_dir.rglob("terminal_closure_record.json"))
    if not records:
        return _std_result(
            validator_id, "WARN",
            "Terminal closure claimed but no terminal_closure_record.json found in "
            ".local/evidences/plan-closures/. "
            "The --terminal flag should auto-write this evidence artifact (TC-TCF-004).",
        )

    # Find the most recent record
    latest = max(records, key=lambda p: p.stat().st_mtime)
    try:
        record = json.loads(latest.read_text(encoding="utf-8", errors="replace"))
        audit_verdict = record.get("audit_verdict", "NOT_RUN")
        if audit_verdict == "NOT_RUN":
            return _std_result(
                validator_id, "WARN",
                f"terminal_closure_record.json exists ({latest.name}) but audit_verdict=NOT_RUN. "
                "This plan was closed without running the lifecycle audit. "
                "Consider using --audit-gate or --completion-candidate before --terminal.",
            )
        return _std_result(
            validator_id, "PASS",
            f"Terminal closure record exists with audit_verdict={audit_verdict}.",
        )
    except Exception as exc:
        return _std_result(validator_id, "WARN", f"terminal_closure_record.json unreadable: {exc}")


def validate_no_premature_closure_triggers(
    declaration: dict, repo_root: Path | None = None
) -> dict:
    """V-TCF-003: WARN if active-plan-lock.json closure trigger was queue exhaustion,
    iteration limit, or closeout-only sprint pattern.

    Cross-checks zero-task-counter.json and the active lock's metadata for
    known premature closure patterns.
    """
    validator_id = "V-TCF-003"
    if repo_root is None:
        repo_root = _REPO_ROOT

    # Only applies to LIFECYCLE_HARDENING/MACHINERY_HARDENING declarations
    work_items = declaration.get("work_items", [])
    hardening_items = [w for w in work_items if w.get("type") in _TERMINAL_CLAIM_TYPES]
    if not hardening_items:
        return _std_result(validator_id, "PASS", "Not a terminal hardening declaration; guard not applicable")

    warnings: list[str] = []

    # Check zero-task-counter
    counter_path = repo_root / ".local" / "supervisor" / "zero-task-counter.json"
    if counter_path.exists():
        try:
            counter = json.loads(counter_path.read_text(encoding="utf-8", errors="replace"))
            count = int(counter.get("count", 0))
            if count >= 3 and not counter.get("mission_complete_declared"):
                warnings.append(
                    f"zero-task-counter.json count={count} without mission_complete_declared: "
                    "possible queue exhaustion masquerading as completion"
                )
        except Exception:
            pass

    # Check continuation signal for iteration limit pattern
    signal_path = repo_root / ".local" / "supervisor" / "continuation-signal.json"
    if signal_path.exists():
        try:
            signal = json.loads(signal_path.read_text(encoding="utf-8", errors="replace"))
            stop_reason = signal.get("stop_reason") or ""
            for pat in _PREMATURE_TRIGGER_PATTERNS:
                if pat in stop_reason.upper():
                    warnings.append(f"continuation-signal stop_reason='{stop_reason}' matches premature pattern '{pat}'")
        except Exception:
            pass

    # Check active-plan-lock for suspicious last_taskcard=None
    lock_path = repo_root / ".local" / "supervisor" / "active-plan-lock.json"
    if lock_path.exists():
        try:
            lock = json.loads(lock_path.read_text(encoding="utf-8", errors="replace"))
            if lock.get("status") == "TERMINAL_CLOSED" and lock.get("last_taskcard") is None:
                plan_name = Path(lock.get("plan_path", "")).name
                warnings.append(
                    f"Active lock for '{plan_name}' is TERMINAL_CLOSED with last_taskcard=None — "
                    "suggests bulk closure without taskcard-by-taskcard progression"
                )
        except Exception:
            pass

    if warnings:
        return _std_result(
            validator_id, "WARN",
            f"Premature closure pattern(s) detected ({len(warnings)}): {warnings[0]}",
            items=warnings,
        )

    return _std_result(validator_id, "PASS", "No premature closure trigger patterns detected")
