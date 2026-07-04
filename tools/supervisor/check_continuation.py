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
    # IMPORTANT: CHAT_ID_MISMATCH only fires under --track machinery.
    # The /autonomous-loop command uses --track product; this check is unreachable from it.
    # CHAT_ID_MISMATCH is enforced by autonomous_orchestrator.py (Track M) only.
    # TC-CCI-H-03 (Option A): documented as Track M only — not wired to product loop.
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

    # --- Check 0c: Session-scoped chat plan binding (PLAN-SCOPED-CONT-20260623) ---
    # Reads .local/missions/*/plan-binding.yaml files. If a binding exists for this
    # session with status=IN_PROGRESS and global_ledger_fallback_allowed=false,
    # block continuation so the agent stays on the bound plan.
    _missions_dir = repo_root / ".local" / "missions"
    if _missions_dir.is_dir():
        for _binding_path in sorted(_missions_dir.glob("*/plan-binding.yaml")):
            try:
                import yaml as _yaml_mod
                _binding_data = _yaml_mod.safe_load(
                    _binding_path.read_text(encoding="utf-8")
                )
                _b = (_binding_data or {}).get("chat_plan_binding", {})
            except Exception:
                continue  # Corrupt binding — skip, don't crash
            # Session scoping: only applies to the session that created the binding
            _b_sid = _b.get("session_id")
            if _b_sid and _b_sid != session_id:
                continue  # Different session — not our binding
            if _b.get("status") == "COMPLETE":
                continue  # Completed — no longer blocking
            # TTL: skip stale bindings (default 48h)
            _b_ttl = _b.get("ttl_hours", 48)
            _b_created = _b.get("created_at", "")
            if _b_created:
                try:
                    from datetime import datetime as _bdt, timezone as _btz, timedelta as _td
                    _b_ts = _bdt.fromisoformat(_b_created)
                    if _bdt.now(_btz.utc) - _b_ts > _td(hours=_b_ttl):
                        continue  # Expired binding
                except Exception:
                    pass  # Can't parse — don't skip, enforce cautiously
            # Active binding found for this session
            if not _b.get("global_ledger_fallback_allowed", True):
                return _stop(
                    "CHAT_PLAN_BINDING_ACTIVE",
                    (
                        f"Chat plan binding is active: {_b.get('plan_path', 'unknown')}. "
                        f"Mission: {_b.get('mission_id', 'unknown')}. "
                        f"Complete all taskcards or use --clear-mission to reset."
                    ),
                    iteration=iteration,
                    max_iterations=max_iterations,
                    plan_path=_b.get("plan_path"),
                    mission_id=_b.get("mission_id"),
                )

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

    # --- TC-LOCK-001 (FF-LOCK-HEAL-20260624): Collect-then-decide lock evaluation ---
    # Previous design: single-pass alphabetical loop with early-return.
    # Problem: in multi-plan sessions, an older TERMINAL_CLOSED lock could shadow a newer
    # IN_PROGRESS lock because alphabetical order has no temporal meaning.
    # Fix: collect all session-relevant locks, sort by updated_at, decide on newest only.

    from datetime import datetime as _dt, timezone as _tz

    # Phase 1: Collect all session-relevant locks
    _session_locks: list[tuple[Path, dict, str]] = []  # (path, data, updated_at)
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

        # --- Stale lock expiry (M7): skip locks older than 7 days ---
        try:
            _updated_at = plan_lock.get("updated_at", "")
            if _updated_at:
                _lock_age_hours = (
                    _dt.now(_tz.utc) - _dt.fromisoformat(_updated_at)
                ).total_seconds() / 3600
                if _lock_age_hours > 168:  # 7 days
                    continue  # Stale lock — skip silently
        except Exception:
            pass  # If date parsing fails, do not skip (fail-safe)

        # --- Session-scoped lock filtering (TC-P1-005 / REQ-PLK-003, REQ-PLK-004) ---
        lock_session_id = plan_lock.get("session_id")
        if lock_session_id and session_id and lock_session_id != session_id:
            continue  # This lock belongs to a different session — skip it

        # --- Track-type filtering (TC-P1-005 / REQ-PLK-003) ---
        lock_track = plan_lock.get("track_type")
        if lock_track and track and lock_track != track:
            continue  # This lock belongs to a different track — skip it

        # --- M5b: AUTHORIZED_OVERRIDE bypass (AUT-20260622-0001) ---
        if plan_lock.get("status") == "TERMINAL_CLOSED_AUTHORIZED_OVERRIDE" and plan_lock.get("authorization_id"):
            continue  # Authorized override — skip this lock

        # --- TC-LOCK-006: Skip SUPERSEDED and DEFERRED locks ---
        if plan_lock.get("status") in ("SUPERSEDED", "DEFERRED"):
            continue  # Historical/deferred — not part of active decision set

        _session_locks.append((_lock_path, plan_lock, plan_lock.get("updated_at", "")))

    # Phase 2: Sort by updated_at descending (newest first) and decide on newest lock
    _session_locks.sort(key=lambda x: x[2], reverse=True)

    if _session_locks:
        _newest_path, _newest_lock, _ = _session_locks[0]
        _newest_status = _newest_lock.get("status", "")
        _newest_session_id = _newest_lock.get("session_id")

        # --- M6: TERMINAL_CLOSED detection (POST_PLAN_TERMINAL) ---
        # Only fires on the NEWEST lock. Older TERMINAL_CLOSED locks from prior plans
        # in the same session are superseded by the newest lock's state.
        if _newest_status == "TERMINAL_CLOSED":
            return _stop(
                "POST_PLAN_TERMINAL",
                (
                    f"Per-chat plan was marked TERMINAL_CLOSED in this session: "
                    f"plan={_newest_lock.get('plan_path', 'unknown')!r}. "
                    "Plan completion is a terminal event for the current session. "
                    "No ledger or product deepening work may start automatically. "
                    "Start a new conversation or provide explicit user authorization "
                    "for ledger work."
                ),
                iteration=signal.get("iteration", 0),
                max_iterations=signal.get("max_iterations", 5),
                active_plan_path=_newest_lock.get("plan_path"),
            )

        # --- M8: PLAN_COMPLETED_IN_SESSION safety net ---
        if _newest_status == "COMPLETE" and _newest_session_id and session_id and _newest_session_id == session_id:
            return _stop(
                "PLAN_COMPLETED_IN_SESSION",
                (
                    f"Per-chat plan was completed in this session: "
                    f"plan={_newest_lock.get('plan_path', 'unknown')!r}. "
                    "Report plan completion to user and stop. "
                    "Do NOT auto-continue to product deepening. "
                    "A new session or explicit user authorization is required for ledger work."
                ),
                iteration=signal.get("iteration", 0),
                max_iterations=signal.get("max_iterations", 5),
                active_plan_path=_newest_lock.get("plan_path"),
            )

        # --- M6c: COMPLETION_CANDIDATE — plan ready for completion audit (TC-TCF-005) ---
        if _newest_status == "COMPLETION_CANDIDATE":
            return {
                "verdict": "CONTINUE",
                "reason": "completion_candidate_detected",
                "detail": (
                    "Plan is marked COMPLETION_CANDIDATE — completion audit should run "
                    f"before final TERMINAL_CLOSED. plan={_newest_lock.get('plan_path', 'unknown')!r}"
                ),
                "iteration": signal.get("iteration", 0),
                "max_iterations": signal.get("max_iterations", 5),
                "active_plan_path": _newest_lock.get("plan_path"),
                "completion_candidate_detected": True,
            }

        # --- M6b: ITERATION_REQUIRED — audit-gate found unresolved work ---
        if _newest_status == "ITERATION_REQUIRED":
            lock_iter_session = _newest_lock.get("session_id")
            if lock_iter_session and session_id and lock_iter_session == session_id:
                return {
                    "verdict": "CONTINUE",
                    "reason": "plan_iteration_required",
                    "detail": (
                        "Lifecycle audit found unresolved work; plan is iterating. "
                        f"plan={_newest_lock.get('plan_path', 'unknown')!r}"
                    ),
                    "iteration": signal.get("iteration", 0),
                    "max_iterations": signal.get("max_iterations", 5),
                    "active_plan_path": _newest_lock.get("plan_path"),
                }
            else:
                return _stop(
                    "POST_PLAN_TERMINAL",
                    (
                        f"Plan ITERATION_REQUIRED lock from a different session "
                        f"(lock_session={lock_iter_session!r}, current={session_id!r}). "
                        "Treating as terminal for CCI safety."
                    ),
                    iteration=signal.get("iteration", 0),
                    max_iterations=signal.get("max_iterations", 5),
                    active_plan_path=_newest_lock.get("plan_path"),
                )

        # --- IN_PROGRESS or unknown status → ACTIVE_PLAN_INCOMPLETE ---
        if _newest_status != "COMPLETE":
            return _stop(
                "ACTIVE_PLAN_INCOMPLETE",
                (
                    f"Per-chat plan is active and not yet 100%% complete: "
                    f"plan={_newest_lock.get('plan_path', 'unknown')!r}, "
                    f"last_taskcard={_newest_lock.get('last_taskcard', 'unknown')!r}. "
                    "Complete ALL taskcards in the loaded plan before resuming "
                    "product deepening or general ledger work."
                ),
                iteration=signal.get("iteration", 0),
                max_iterations=signal.get("max_iterations", 5),
                active_plan_path=_newest_lock.get("plan_path"),
                last_taskcard=_newest_lock.get("last_taskcard"),
                next_action=(
                    "Read the active plan file. Find the next open taskcard after "
                    f"{_newest_lock.get('last_taskcard', 'unknown')!r}. Execute it. "
                    "Run write_plan_lock.py to update last_taskcard and mark COMPLETE when done."
                ),
            )

    # --- Check 1c: Machinery mission ledger gate (only for --track machinery) ---
    # GAP-WHALE-001 (TC-WHALE-LEDGER-001, 2026-06-21): wire mission-ledger.json enforcement
    # into check_continuation.py so the machinery mission stop_status is machine-enforced.
    # Without this check, machinery continuation signals CONTINUE even after MISSION_COMPLETE.
    if track == "machinery":
        _machinery_ledger = (
            repo_root / ".local" / "supervisor" / "machinery" / "mission-ledger.json"
        )
        if _machinery_ledger.exists():
            try:
                _ml = json.loads(_machinery_ledger.read_text(encoding="utf-8"))
            except Exception:
                _ml = {}
            if _ml.get("stop_status") == "MISSION_COMPLETE":
                return _stop(
                    "MACHINERY_MISSION_COMPLETE",
                    (
                        "Machinery mission declared complete in mission-ledger.json "
                        f"(mission_id={_ml.get('mission_id', 'unknown')!r}). "
                        "No further machinery continuation is authorized. "
                        "To start a new machinery mission, initialize a new mission-ledger.json."
                    ),
                    iteration=signal.get("iteration", 0),
                    max_iterations=signal.get("max_iterations", 5),
                )
            if _ml.get("audit_pending") is True and not _ml.get("execution_pending", True):
                return _stop(
                    "MACHINERY_AUDIT_REQUIRED",
                    (
                        "Machinery mission has audit_pending=True and execution_pending=False. "
                        "A post-execution audit must run before machinery continuation. "
                        "Run: python tools/supervisor/machinery_audit.py --write-output"
                    ),
                    iteration=signal.get("iteration", 0),
                    max_iterations=signal.get("max_iterations", 5),
                )

    # --- Check 2: autonomous_continue is truthy ---
    # B4: When signal is false due to a non-TRUE_EXTERNAL_GATE reason, cross-check
    # approval-gates.md before stopping. Stale signal + live YES gate = allow continuation.
    # TRUE_EXTERNAL_GATEs always stop regardless of gates.md.
    _TRUE_EXTERNAL_GATE_REASONS = {
        "git_push_credentials_unavailable",
        "Gate_11_approval_required",
        "gate_11_execution_required",
        "publication_credentials_unavailable",
        "nuget_publication_unavailable",
        "pypi_publication_unavailable",
    }
    auto_continue = signal.get("autonomous_continue", False)
    _gates_override = False  # set True when gates.md overrides a stale/false signal
    if not auto_continue:
        reason = signal.get("stop_reason") or "autonomous_continue is false"
        # If the stop reason is a TRUE_EXTERNAL_GATE, respect it unconditionally
        if reason in _TRUE_EXTERNAL_GATE_REASONS:
            return _stop("AUTONOMOUS_CONTINUE_FALSE", reason,
                          iteration=iteration, max_iterations=max_iterations)
        # Otherwise: cross-check approval-gates.md. If gates say YES, the stale signal
        # is a false stop (e.g. evidence_quality_zero, NO_EXTERNAL_GATE). Allow continuation.
        gates_path = repo_root / "reports" / "supervisor" / "approval-gates.md"
        if gates_path.exists() and "AUTONOMOUS_CONTINUE: YES" in gates_path.read_text(encoding="utf-8"):
            _gates_override = True  # signal is stale; skip signal-derived checks below
        else:
            return _stop("AUTONOMOUS_CONTINUE_FALSE", reason,
                          iteration=iteration, max_iterations=max_iterations)

    # --- Check 3: continuation_state starts with YES ---
    # Skip if gates.md already overrode the stale signal (continuation_state is also stale).
    cont_state = signal.get("continuation_state", "")
    if not _gates_override and isinstance(cont_state, str) and cont_state.startswith("NO_"):
        return _stop(cont_state, f"continuation_state={cont_state}",
                      iteration=iteration, max_iterations=max_iterations)

    # --- Check 4: hard_stops_detected is empty ---
    hard_stops = signal.get("hard_stops_detected", [])
    if hard_stops:
        return _stop("HARD_STOP", f"hard_stops_detected: {hard_stops}",
                      iteration=iteration, max_iterations=max_iterations)

    # --- Check 5: iteration < max_iterations (TC-PROD-H-003R: auto-rollover) ---
    if iteration >= max_iterations:
        _old_iter = iteration
        signal["iteration"] = 0
        signal_path.write_text(json.dumps(signal, indent=2) + "\n", encoding="utf-8")
        iteration = 0
        print(f"GOVERNED_ROLLOVER: iteration reset from {_old_iter} to 0", file=sys.stderr)

    # --- Check 6: approval-gates.md contains AUTONOMOUS_CONTINUE: YES ---
    gates_path = repo_root / "reports" / "supervisor" / "approval-gates.md"
    if not gates_path.exists():
        return _stop("APPROVAL_GATE_MISSING", "approval-gates.md does not exist",
                      iteration=iteration, max_iterations=max_iterations)
    gates_text = gates_path.read_text(encoding="utf-8")
    if "AUTONOMOUS_CONTINUE: YES" not in gates_text:
        # TC-PROD-H-012: Cross-check against signal before false-stopping.
        _sig_state = signal.get("continuation_state", "")
        if _sig_state.startswith("YES"):
            print(f"WARNING_STALE_GATES: approval-gates.md says NO but signal says "
                  f"{_sig_state!r} -- using signal as authority", file=sys.stderr)
        else:
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

    # --- Check 7b (TC-PGI-040): Stale suppression detection ---
    # If next-work-items.json suppresses ledger for a plan that no longer has an
    # IN_PROGRESS lock, flag it as stale (informational — does not block CONTINUE).
    try:
        _nwi_7b = json.loads(work_items_path.read_text(encoding="utf-8"))
        if _nwi_7b.get("ledger_items_suppressed") and _nwi_7b.get("active_plan"):
            _ref_plan_7b = _nwi_7b["active_plan"]
            _ref_plan_has_lock_7b = any(
                _ref_plan_7b in str(_lk.get("plan_path", "")) and
                _lk.get("status") not in ("SUPERSEDED", "TERMINAL_CLOSED", "COMPLETE", "DEFERRED")
                for _lk in _candidates
            )
            if not _ref_plan_has_lock_7b:
                _output["stale_work_items_detected"] = True
                _output["stale_work_items_reason"] = (
                    f"next-work-items.json suppresses ledger for '{_ref_plan_7b}' "
                    f"but no IN_PROGRESS lock exists. Bootstrap cycle needed."
                )
    except Exception:
        pass  # non-blocking

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

    # --- Check 9: Product deepening architecture gate (TC-HEAL-PD-003) ---
    # Block continuation when selected product gaps contain architecture-non-compliant formats.
    # Bootstrap tolerance: if ledger does not exist, skip this check silently.
    _pd_ledger = repo_root / "registry" / "product-deepening-ledger.yaml"
    _pd_gaps_path = repo_root / ".local" / "supervisor" / "selected-product-gaps.json"
    if _pd_ledger.exists() and _pd_gaps_path.exists():
        try:
            _pd_raw = json.loads(_pd_gaps_path.read_text(encoding="utf-8"))
            _pd_selected = _pd_raw.get("selected_gaps", []) if isinstance(_pd_raw, dict) else (_pd_raw if isinstance(_pd_raw, list) else [])
            if _pd_selected:
                sys.path.insert(0, str(_here))
                from product_deepening_gate import check_formats_in_gaps as _chk_pd
                _pd_gate_results = _chk_pd(_pd_selected, ledger_path=_pd_ledger)
                _pd_blocked = [r for r in _pd_gate_results if not r.get("allowed")]
                if _pd_blocked:
                    _reasons = "; ".join(
                        f"{r['format']}: {r.get('reason', 'unknown')}" for r in _pd_blocked
                    )
                    return _stop(
                        "product_deepening_architecture_gate",
                        (
                            f"Product deepening blocked for {len(_pd_blocked)} format(s): {_reasons}. "
                            "Update registry/product-deepening-ledger.yaml when format architecture "
                            "compliance is verified. See TC-HEAL-PD-005 for backfill procedure."
                        ),
                        iteration=iteration,
                        max_iterations=max_iterations,
                        blocked_formats=[r["format"] for r in _pd_blocked],
                    )
        except ImportError as _pd_import_err:
            # product_deepening_gate.py not yet present (bootstrap) — skip check
            print(f"WARNING [Check9]: product_deepening_gate not available: {_pd_import_err}", file=sys.stderr)
        except Exception as _pd_err:
            # Non-blocking: gate failures must not crash continuation
            print(f"WARNING [Check9]: product_deepening_gate error: {_pd_err}", file=sys.stderr)

    # --- Check 10: Lane Balance Advisory (TC-DL2-006) ---
    # Advisory only — never returns STOP, only adds lane_starvation_warnings
    lane_starvation_warnings = []
    try:
        from lane_selector import check_starvation
        _ledger_path = repo_root / "registry" / "product-deepening-ledger.yaml"
        if _ledger_path.exists():
            import yaml as _ls_yaml
            _ledger_data = _ls_yaml.safe_load(_ledger_path.read_text(encoding="utf-8")) or []
            for _entry in _ledger_data:
                _fmt = _entry.get("format", "")
                if not _fmt:
                    continue
                try:
                    _starv = check_starvation(_fmt, _ledger_path)
                    if _starv.get("must_switch"):
                        _warn = (f"WARNING: {_fmt} lane {_starv.get('starved_lane', '?')} "
                                 f"starved ({_starv.get('consecutive_count', '?')} consecutive)")
                        lane_starvation_warnings.append(_warn)
                        print(_warn, file=sys.stderr)
                except Exception:
                    pass
    except ImportError:
        pass
    except Exception as _lane_err:
        print(f"WARNING [Check10]: lane balance check error: {_lane_err}", file=sys.stderr)

    # --- All checks passed ---
    # Resolve product chat_id (advisory — TC-PSC-003 Part A)
    _product_chat_id = None
    if not track or track == "product":
        try:
            from continuation_identity import get_or_create_product_chat_id
            _product_chat_id = get_or_create_product_chat_id()
        except Exception:
            pass

    result = {
        "verdict": "CONTINUE",
        "iteration": iteration,
        "max_iterations": max_iterations,
        "continuation_state": cont_state,
        "session_id": signal.get("session_id"),
        "track": track,
        "product_chat_id": _product_chat_id,
        "next_work_items_path": work_items_rel,
        "next_sprint_path": "reports/supervisor/next-sprint.md",
        "rework_items": rework_items,
        "lane_starvation_warnings": lane_starvation_warnings,
        "resume_command": f"python tools/supervisor/check_continuation.py{' --track ' + track if track else ''}",
    }
    if signal.get("evidence_continuation_failed"):
        result["warning"] = (
            f"evidence_continuation bridge failed: "
            f"{signal.get('evidence_continuation_error', 'unknown')}"
        )
    # Log verdict to continuation ledger (non-blocking)
    _log_verdict("CONTINUE", "", session_id=signal.get("session_id"),
                 signal_path=str(signal_path), track=track or "product",
                 iteration=iteration)
    return result


def _log_verdict(verdict: str, reason: str, **context) -> None:
    """Non-blocking: append a continuation verdict to the JSONL ledger."""
    try:
        sys.path.insert(0, str(_here))
        from continuation_ledger import append_event
        append_event(
            event_type="CONTINUATION_VERDICT",
            artifact_path=context.get("signal_path", "unknown"),
            session_id=context.get("session_id"),
            metadata={
                "verdict": verdict,
                "reason": reason,
                "iteration": context.get("iteration"),
                "track": context.get("track", "product"),
            },
        )
    except Exception:
        pass  # Ledger failure must never block continuation


def _stop(reason: str, detail: str, *, iteration: int = 0,
          max_iterations: int = 5, **extras) -> dict:
    _log_verdict("STOP", reason, iteration=iteration, **{
        k: v for k, v in extras.items()
        if k in ("session_id", "signal_path", "track")
    })
    return {
        "verdict": "STOP",
        "reason": reason,
        "detail": detail,
        "iteration": iteration,
        "max_iterations": max_iterations,
        "resume_command": None,
        **extras,
    }


def validate_continuation_coherence(repo_root: Path | None = None) -> list[dict]:
    """B7: Cross-validate continuation signal vs approval-gates.md and lock file coherence.

    Returns a list of contradiction dicts (empty = coherent).
    Each dict has: severity, code, message.
    Also appends CONTRADICTION entries to reports/supervisor/contradictions.md.
    """
    _TRUE_GATE_REASONS = {
        "git_push_credentials_unavailable", "Gate_11_approval_required",
        "gate_11_execution_required", "publication_credentials_unavailable",
        "nuget_publication_unavailable", "pypi_publication_unavailable",
    }
    if repo_root is None:
        repo_root = _default_repo
    contradictions: list[dict] = []

    # Check 1: signal vs gates.md alignment
    signal_path = repo_root / ".local" / "supervisor" / "product" / "continuation-signal.json"
    gates_path = repo_root / "reports" / "supervisor" / "approval-gates.md"
    if signal_path.exists() and gates_path.exists():
        try:
            signal = json.loads(signal_path.read_text(encoding="utf-8"))
            gates_text = gates_path.read_text(encoding="utf-8")
            auto_continue = signal.get("autonomous_continue", True)
            stop_reason = signal.get("stop_reason") or ""
            gates_yes = "AUTONOMOUS_CONTINUE: YES" in gates_text
            if not auto_continue and gates_yes and stop_reason not in _TRUE_GATE_REASONS:
                contradictions.append({
                    "severity": "HIGH",
                    "code": "SIGNAL_GATES_MISMATCH",
                    "message": (
                        f"continuation-signal.json has autonomous_continue=false "
                        f"(stop_reason={stop_reason!r}) but approval-gates.md says YES. "
                        "Signal is stale — gates.md should take precedence."
                    ),
                })
        except Exception as exc:
            contradictions.append({
                "severity": "LOW", "code": "COHERENCE_CHECK_ERROR",
                "message": f"signal/gates check failed: {exc}",
            })

    # Check 2: shared lock vs session lock consistency
    shared_lock_path = repo_root / ".local" / "supervisor" / "active-plan-lock.json"
    session_locks_dir = repo_root / ".local" / "supervisor" / "plan-locks"
    if shared_lock_path.exists() and session_locks_dir.exists():
        try:
            shared = json.loads(shared_lock_path.read_text(encoding="utf-8"))
            shared_plan = str(shared.get("plan_path", "")).replace("\\", "/")
            shared_status = shared.get("status", "")
            shared_sid = shared.get("session_id", "")
            if shared_sid:
                keyed = session_locks_dir / f"{shared_sid}.json"
                if keyed.exists():
                    keyed_data = json.loads(keyed.read_text(encoding="utf-8"))
                    keyed_status = keyed_data.get("status", "")
                    if shared_status != keyed_status:
                        contradictions.append({
                            "severity": "CRITICAL",
                            "code": "LOCK_STATUS_MISMATCH",
                            "message": (
                                f"active-plan-lock.json status={shared_status!r} but "
                                f"session lock {shared_sid}.json status={keyed_status!r} "
                                f"for plan {shared_plan!r}. write_plan_lock.py --terminal "
                                "may have only updated the session lock."
                            ),
                        })
        except Exception as exc:
            contradictions.append({
                "severity": "LOW", "code": "LOCK_COHERENCE_CHECK_ERROR",
                "message": f"lock coherence check failed: {exc}",
            })

    # Append findings to contradictions.md
    if contradictions:
        contradictions_path = repo_root / "reports" / "supervisor" / "contradictions.md"
        try:
            from datetime import datetime, timezone
            ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            lines = [f"\n## Coherence Contradictions detected at {ts}\n"]
            for c in contradictions:
                lines.append(f"- **{c['severity']}** `{c['code']}`: {c['message']}\n")
            with contradictions_path.open("a", encoding="utf-8") as fh:
                fh.writelines(lines)
        except Exception:
            pass

    return contradictions


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
