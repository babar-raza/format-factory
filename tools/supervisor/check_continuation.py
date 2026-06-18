"""
check_continuation.py — Deterministic continuation check for the autonomous loop.

Replaces the 7-condition manual check in CLAUDE.md with a single command.
Reads continuation-signal.json, approval-gates.md, and next-work-items.json.
Returns machine-readable JSON to stdout.

Exit codes:
  0 — CONTINUE (all conditions met)
  1 — STOP (at least one condition failed)

Usage:
  python tools/supervisor/check_continuation.py [--repo-root <path>]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_default_repo = _here.parent.parent


def check(repo_root: Path, *, session_id: str | None = None,
          track: str | None = None, chat_id: str | None = None) -> dict:
    """Run continuation conditions. Returns a verdict dict.

    session_id: if provided, rejects signals from a different session.
    track: "product" | "machinery" | None — when set, applies track-specific filtering.
    chat_id: if provided and track="machinery", validates chat_id match (per-chat isolation).
    """
    repo_root = repo_root.resolve()

    # --- Check 1: continuation-signal.json exists and is valid JSON ---
    # TC-P2-001-02: Resolve signal path based on --track parameter.
    #   --track product  → product/ subdir; fallback to legacy if not present
    #   --track machinery → machinery/ subdir; NO legacy fallback (strict isolation)
    #   no --track       → legacy path (backward compat)
    _legacy_signal = repo_root / ".local" / "supervisor" / "continuation-signal.json"
    if track == "product":
        _track_signal = repo_root / ".local" / "supervisor" / "product" / "continuation-signal.json"
        signal_path = _track_signal if _track_signal.exists() else _legacy_signal
    elif track == "machinery":
        signal_path = repo_root / ".local" / "supervisor" / "machinery" / "continuation-signal.json"
    else:
        signal_path = _legacy_signal

    if not signal_path.exists():
        return _stop("NO_SIGNAL", f"continuation-signal.json does not exist (track={track!r}, path={signal_path})")
    try:
        signal = json.loads(signal_path.read_text(encoding="utf-8"))
    except Exception as e:
        return _stop("INVALID_SIGNAL", f"continuation-signal.json is not valid JSON: {e}")

    # --- Check 0 (CCI-MVP): Session identity guard (TC-CCI-201) ---
    # Auto-resolve session_id when not explicitly provided by caller.
    if session_id is None:
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            from continuation_identity import get_or_create_session_identity
            session_id = get_or_create_session_identity().session_id
        except Exception as _cci_err:
            print(f"WARNING: CCI identity fallback: {_cci_err}", file=sys.stderr)

    # Use continuation_selector for richer session matching (TC-CCI-203)
    signal_session_id = signal.get("session_id")
    if session_id and signal_session_id:
        try:
            from continuation_identity import ContinuationIdentity
            from continuation_selector import select_continuation
            caller_identity = ContinuationIdentity(session_id=session_id)
            sel_result = select_continuation(caller_identity, signal_path)
            if sel_result.verdict == "REJECT":
                return _stop(
                    "SESSION_MISMATCH",
                    sel_result.reason or "Session mismatch (selector)",
                    iteration=signal.get("iteration", 0),
                    max_iterations=signal.get("max_iterations", 5),
                )
            # ACCEPT, WARN_LEGACY, WARN_UUID_FALLBACK → all proceed
            if sel_result.verdict in ("WARN_LEGACY", "WARN_UUID_FALLBACK"):
                print(f"WARNING [CCI]: {sel_result.reason}", file=sys.stderr)
        except ImportError:
            # Fallback to inline comparison if selector unavailable
            if session_id != signal_session_id:
                return _stop(
                    "SESSION_MISMATCH",
                    f"Signal session_id={signal_session_id!r} does not match "
                    f"caller session_id={session_id!r}. This continuation belongs to another chat.",
                    iteration=signal.get("iteration", 0),
                    max_iterations=signal.get("max_iterations", 5),
                )

    iteration = signal.get("iteration", 0)
    max_iterations = signal.get("max_iterations", 5)

    # --- Check 0b: Track M per-chat isolation (TC-P1-007 / REQ-CCI-M-003) ---
    # When running as --track machinery, validate chat_id match.
    # A different chat cannot consume a prior chat's Track M continuation state.
    if track == "machinery":
        signal_chat_id = signal.get("chat_id")
        if signal_chat_id:
            # Resolve current chat_id from parameter, env var, or local state file
            current_chat_id = chat_id
            if not current_chat_id:
                import os as _os
                current_chat_id = _os.environ.get("CLAUDE_CHAT_ID")
            if not current_chat_id:
                # Try reading from local chat-id registry
                _chat_id_path = repo_root / ".local" / "supervisor" / "machinery" / "current-chat-id.json"
                try:
                    _chat_id_data = json.loads(_chat_id_path.read_text(encoding="utf-8"))
                    current_chat_id = _chat_id_data.get("chat_id")
                except Exception:
                    pass
            if current_chat_id and current_chat_id != signal_chat_id:
                return _stop(
                    "CHAT_ID_MISMATCH",
                    (
                        f"Track M chat isolation: signal chat_id={signal_chat_id!r} "
                        f"does not match current chat_id={current_chat_id!r}. "
                        "This Track M continuation belongs to a different chat."
                    ),
                    iteration=iteration,
                    max_iterations=max_iterations,
                    signal_chat_id=signal_chat_id,
                    current_chat_id=current_chat_id,
                )
            elif not current_chat_id:
                # CLAUDE_CHAT_ID unknown — warn but do not block (advisory)
                pass  # CHAT_ID_UNKNOWN is advisory only

    # --- Check 1b: Active per-chat plan lock (PLAN_LOCK_GATE) ---
    # If a per-chat plan is loaded and not yet 100% complete, block continuation
    # entirely. Product deepening sprints MUST NOT run while a plan is active.
    #
    # Two lock mechanisms are checked (in order):
    #   1. Session-keyed locks in .local/supervisor/plan-locks/*.json (preferred — race-safe)
    #   2. Shared lock .local/supervisor/active-plan-lock.json (legacy fallback)
    supervisor_dir = repo_root / ".local" / "supervisor"
    plan_locks_dir = supervisor_dir / "plan-locks"
    _lock_candidates: list[Path] = []
    if plan_locks_dir.is_dir():
        _lock_candidates.extend(sorted(plan_locks_dir.glob("*.json")))
    _shared_lock = supervisor_dir / "active-plan-lock.json"
    if _shared_lock.exists():
        _lock_candidates.append(_shared_lock)

    for _lock_path in _lock_candidates:
        try:
            plan_lock = json.loads(_lock_path.read_text(encoding="utf-8"))
        except Exception as _lock_err:
            # Malformed lock file — block continuation to prevent silent bypass
            return _stop(
                "ACTIVE_PLAN_LOCK_CORRUPT",
                f"{_lock_path.name} exists but could not be parsed: {_lock_err}",
                iteration=signal.get("iteration", 0),
                max_iterations=signal.get("max_iterations", 5),
            )

        # --- Session-scoped lock filtering (TC-P1-005 / REQ-PLK-003, REQ-PLK-004) ---
        lock_session_id = plan_lock.get("session_id")
        if lock_session_id and session_id and lock_session_id != session_id:
            continue  # This lock belongs to a different session — skip it

        # For legacy active-plan-lock.json (no session_id field): apply existing block logic
        # For session-keyed locks with matching session_id: apply block logic below

        # --- Track-type filtering (TC-P1-005 / REQ-PLK-003) ---
        lock_track = plan_lock.get("track_type")
        if lock_track and track and lock_track != track:
            continue  # This lock belongs to a different track — skip it

        if plan_lock.get("status") != "COMPLETE":
            return _stop(
                "ACTIVE_PLAN_INCOMPLETE",
                (
                    f"Per-chat plan is active and not yet 100%% complete: "
                    f"plan={plan_lock.get('plan_path', 'unknown')!r}, "
                    f"last_taskcard={plan_lock.get('last_taskcard', 'unknown')!r}. "
                    "Complete ALL taskcards in the loaded plan before resuming "
                    "product deepening or general ledger work."
                ),
                iteration=signal.get("iteration", 0),
                max_iterations=signal.get("max_iterations", 5),
                active_plan_path=plan_lock.get("plan_path"),
                last_taskcard=plan_lock.get("last_taskcard"),
                next_action=(
                    "Read the active plan file. Find the next open taskcard after "
                    f"{plan_lock.get('last_taskcard', 'unknown')!r}. Execute it. "
                    "Run write_plan_lock.py to update last_taskcard and mark COMPLETE when done."
                ),
            )

    # --- Check 2: autonomous_continue is truthy ---
    auto_continue = signal.get("autonomous_continue", False)
    if not auto_continue:
        reason = signal.get("stop_reason") or "autonomous_continue is false"
        return _stop("AUTONOMOUS_CONTINUE_FALSE", reason,
                      iteration=iteration, max_iterations=max_iterations)

    # --- Check 3: continuation_state starts with YES ---
    cont_state = signal.get("continuation_state", "")
    if isinstance(cont_state, str) and cont_state.startswith("NO_"):
        return _stop(cont_state, f"continuation_state={cont_state}",
                      iteration=iteration, max_iterations=max_iterations)

    # --- Check 4: hard_stops_detected is empty ---
    hard_stops = signal.get("hard_stops_detected", [])
    if hard_stops:
        return _stop("HARD_STOP", f"hard_stops_detected: {hard_stops}",
                      iteration=iteration, max_iterations=max_iterations)

    # --- Check 5: iteration < max_iterations ---
    if iteration >= max_iterations:
        return _stop("MAX_ITERATIONS",
                      f"iteration {iteration} >= max_iterations {max_iterations}",
                      iteration=iteration, max_iterations=max_iterations)

    # --- Check 6: approval-gates.md contains AUTONOMOUS_CONTINUE: YES ---
    gates_path = repo_root / "reports" / "supervisor" / "approval-gates.md"
    if not gates_path.exists():
        return _stop("APPROVAL_GATE_MISSING", "approval-gates.md does not exist",
                      iteration=iteration, max_iterations=max_iterations)
    gates_text = gates_path.read_text(encoding="utf-8")
    if "AUTONOMOUS_CONTINUE: YES" not in gates_text:
        return _stop("APPROVAL_GATE_NO",
                      "approval-gates.md does not contain AUTONOMOUS_CONTINUE: YES",
                      iteration=iteration, max_iterations=max_iterations)

    # --- Check 7: canonical next-work-items.json exists ---
    # TC-P2-001-02: Resolve work items path based on track.
    _legacy_work = repo_root / ".local" / "supervisor" / "next-work-items.json"
    if track == "product":
        _track_work = repo_root / ".local" / "supervisor" / "product" / "next-work-items.json"
        work_items_path = _track_work if _track_work.exists() else _legacy_work
        work_items_rel = str(work_items_path.relative_to(repo_root)).replace("\\", "/")
    elif track == "machinery":
        work_items_path = repo_root / ".local" / "supervisor" / "machinery" / "next-work-items.json"
        work_items_rel = ".local/supervisor/machinery/next-work-items.json"
    else:
        work_items_path = _legacy_work
        work_items_rel = ".local/supervisor/next-work-items.json"

    if not work_items_path.exists():
        return _stop("NO_WORK_ITEMS",
                      f"{work_items_rel} does not exist",
                      iteration=iteration, max_iterations=max_iterations)

    # --- Check 8 (TC-GOVBLK-001): Structural GOV_BLOCK carve-out ---
    # GOV_BLOCK:monolith_detection_validator and GOV_BLOCK:validate_source_architecture
    # are STRUCTURAL failures, not transient closeout failures. They must NOT be
    # overridden by the Supreme Directive "log exit 3 and continue". The next sprint
    # MUST be an analytics separation refactor for the blocking format.
    #
    # Scoped ONLY to structural architecture validators — does not affect transient
    # or non-structural GOV_BLOCK types (schema errors, replay failures, etc.).
    #
    # Override: if the current sprint IS an analytics separation sprint (declared via
    # "govblock_resolved_by" field in the signal), skip this check.
    _STRUCTURAL_GOVBLOCK_VALIDATORS = {
        "GOV_BLOCK:monolith_detection_validator",
        "GOV_BLOCK:validate_source_architecture",
    }
    rework_items = signal.get("rework_items", [])
    if not signal.get("govblock_resolved_by"):
        structural_blocks = [
            item for item in rework_items
            if any(item.startswith(vname) or item == vname
                   for vname in _STRUCTURAL_GOVBLOCK_VALIDATORS)
        ]
        if structural_blocks:
            return _stop(
                "structural_govblock_must_be_resolved_first",
                (
                    f"Structural GOV_BLOCK detected — product deepening is blocked until "
                    f"analytics separation resolves: {structural_blocks[:3]}. "
                    "Run the analytics separation sprint (TC-HEAL-PY-{FORMAT}-001) for the "
                    "blocking format(s). Set 'govblock_resolved_by' in continuation-signal.json "
                    "once the refactor sprint is complete."
                ),
                iteration=iteration,
                max_iterations=max_iterations,
                structural_govblock_items=structural_blocks,
                next_action=(
                    "Read docs/code-quality/production-readiness-standard.md §8.1 "
                    "(Analytics Separation Protocol). Execute the analytics separation for "
                    "the blocking format. Update continuation-signal.json with "
                    "'govblock_resolved_by': 'TC-HEAL-PY-{FORMAT}-001' when done."
                ),
            )

    # --- All checks passed ---
    result = {
        "verdict": "CONTINUE",
        "iteration": iteration,
        "max_iterations": max_iterations,
        "continuation_state": cont_state,
        "session_id": signal.get("session_id"),
        "track": track,
        "next_work_items_path": work_items_rel,
        "next_sprint_path": "reports/supervisor/next-sprint.md",
        "rework_items": rework_items,
        "resume_command": f"python tools/supervisor/check_continuation.py{' --track ' + track if track else ''}",
    }
    if signal.get("evidence_continuation_failed"):
        result["warning"] = (
            f"evidence_continuation bridge failed: "
            f"{signal.get('evidence_continuation_error', 'unknown')}"
        )
    return result


def _stop(reason: str, detail: str, *, iteration: int = 0,
          max_iterations: int = 5, **extras) -> dict:
    return {
        "verdict": "STOP",
        "reason": reason,
        "detail": detail,
        "iteration": iteration,
        "max_iterations": max_iterations,
        "resume_command": None,
        **extras,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check autonomous continuation conditions")
    parser.add_argument("--repo-root", type=Path, default=_default_repo,
                        help="Repository root (default: auto-detected)")
    parser.add_argument("--session-id", type=str, default=None,
                        help="Session ID for cross-chat isolation (CCI-MVP)")
    parser.add_argument("--track", type=str, choices=["product", "machinery"], default=None,
                        help="Track type for track-specific signal paths and lock filtering")
    parser.add_argument("--chat-id", type=str, default=None,
                        help="Chat ID for Track M per-chat isolation validation")
    args = parser.parse_args(argv)

    result = check(args.repo_root, session_id=args.session_id,
                   track=args.track, chat_id=args.chat_id)
    print(json.dumps(result, indent=2))
    return 0 if result["verdict"] == "CONTINUE" else 1


if __name__ == "__main__":
    sys.exit(main())
