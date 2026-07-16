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

# Coordination plane integration (TC-SWB-004)
try:
    from coordination.coordinated_io import coordinated_write as _coordinated_write
except ImportError:
    try:
        import sys as _sys_cw
        _sys_cw.path.insert(0, str(_here))
        from coordination.coordinated_io import coordinated_write as _coordinated_write
    except ImportError:
        from contextlib import contextmanager as _cm_fallback
        @_cm_fallback
        def _coordinated_write(path, **kw):
            yield

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
                return False, "terminal_closed_plan"

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


def _should_require_audit(plan_path: str) -> bool:
    """TC-TCF-003: Return True when plan file contains tracked TC-* taskcard entries.

    When True, write_lock() automatically invokes lifecycle_audit before writing
    TERMINAL_CLOSED — same as --audit-gate but without requiring the explicit flag.
    Use --skip-audit to bypass this auto-trigger for plans without taskcard tracking.
    """
    import re as _re_tcf
    _TC_RE = _re_tcf.compile(r"\bTC-[A-Z0-9]+-[A-Z0-9-]+", _re_tcf.IGNORECASE)
    try:
        p = Path(plan_path) if Path(plan_path).is_absolute() else _repo_root / plan_path
        if not p.exists():
            return False
        return bool(_TC_RE.search(p.read_text(encoding="utf-8", errors="replace")))
    except Exception:
        return False


def _write_terminal_closure_record(
    plan_path: str,
    session_id: str,
    locked_at: str,
    plan_hash: str = "",
    audit_result: dict | None = None,
    deferred_obligation_ids: list[str] | None = None,
) -> None:
    """TC-TCF-004: Write terminal_closure_record.json when TERMINAL_CLOSED is set.

    Produces a durable evidence artifact beyond the lock file and HTML comment.
    Written to .local/evidences/plan-closures/{plan_hash}/terminal_closure_record.json.
    Non-blocking: any failure is logged to stderr but does not prevent lock write.
    """
    import hashlib as _hashlib_tcf
    record = {
        "plan_path": plan_path,
        "plan_hash": plan_hash,
        "status": "TERMINAL_CLOSED",
        "locked_at": locked_at,
        "locked_by_session": session_id,
        "closure_authorized": True,
        "audit_verdict": (audit_result or {}).get("verdict", "NOT_RUN"),
        "all_taskcards_closed": (audit_result or {}).get("all_taskcards_closed"),
        "open_taskcards": (audit_result or {}).get("open_taskcards", []),
        "guard_results": (audit_result or {}).get("guard_results", []),
        "closure_contract": (audit_result or {}).get("closure_contract"),
        # TC-MOR-001: deferred obligations registered at closure (IDs only; full
        # records are in reports/supervisor/maintenance-obligations.json)
        "deferred_obligations": deferred_obligation_ids or [],
    }
    try:
        ph = plan_hash or _hashlib_tcf.sha256(plan_path.encode()).hexdigest()[:16]
        d = _repo_root / ".local" / "evidences" / "plan-closures" / ph
        d.mkdir(parents=True, exist_ok=True)
        record_path = d / "terminal_closure_record.json"
        record_path.write_text(
            json.dumps(record, indent=2) + "\n", encoding="utf-8"
        )
        print(f"[write_plan_lock] TC-TCF-004: closure record written: {record_path}")
    except Exception as exc:
        print(
            f"[write_plan_lock] WARNING: TC-TCF-004 closure record failed: {exc}",
            file=sys.stderr,
        )


def _parse_lane_id_from_plan(plan_path: str) -> str:
    """TC-LSG-003: Parse lane_id from plan file header or YAML front matter.

    Looks for:
      - Comment header: "# lane: lane-ci-audit"
      - YAML front matter: "lane_id: lane-ci-audit"

    Returns "unknown" if not found or file cannot be read.
    """
    import re
    _LANE_RE = re.compile(r"^#\s*lane:\s*(\S+)", re.MULTILINE)
    _YAML_LANE_RE = re.compile(r"^lane_id:\s*(\S+)", re.MULTILINE)
    try:
        p = Path(plan_path) if Path(plan_path).is_absolute() else _repo_root / plan_path
        if not p.exists():
            return "unknown"
        # Read first 30 lines for efficiency
        lines = []
        with p.open(encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f):
                if i >= 30:
                    break
                lines.append(line)
        text = "".join(lines)
        # Try comment header first
        m = _LANE_RE.search(text)
        if m:
            return m.group(1)
        # Try YAML front matter
        m = _YAML_LANE_RE.search(text)
        if m:
            return m.group(1)
    except Exception:
        pass
    return "unknown"


def _init_machinery_mission_ledger(mission_id: str, plan_path: str | None) -> None:
    """TC-VWR-004-01 (velvet-swinging-wreath): Initialize or refresh mission-ledger.json
    for a new machinery mission (RC-002 fix).

    Only writes if mission_id differs from current ledger's mission_id (idempotent).
    Preserves existing entry if mission_id matches.
    """
    ledger_path = _repo_root / ".local" / "supervisor" / "machinery" / "mission-ledger.json"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    existing: dict = {}
    if ledger_path.exists():
        try:
            existing = json.loads(ledger_path.read_text(encoding="utf-8"))
        except Exception:
            existing = {}
    # Idempotent: if same mission, preserve existing
    if existing.get("mission_id") == mission_id:
        return
    new_entry = {
        "schema_version": "1.0",
        "mission_id": mission_id,
        "mission_type": "machinery_hardening",
        "authoritative_plan": plan_path or "",
        "current_iteration": 0,
        "current_stage": "EXECUTION",
        "last_completed_stage": None,
        "next_required_stage": "POST_EXECUTION_SPRINT_AUDIT",
        "active_taskcards": [],
        "rework_taskcards": [],
        "open_gaps": [],
        "closed_gaps": [],
        "audit_pending": True,
        "replan_pending": False,
        "execution_pending": False,
        "completion_audit_pending": False,
        "behavioral_iterations_required": 2,
        "current_behavioral_iterations": 0,
        "stop_status": "RUNNING",
        "stop_reason": None,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "state_digest": f"{mission_id}:iteration=0:stage=EXECUTION",
    }
    ledger_path.write_text(json.dumps(new_entry, indent=2) + "\n", encoding="utf-8")
    print(f"[write_plan_lock] Initialized machinery mission ledger for {mission_id}")


def _check_master_plan_rollup(plan_path: str, repo_root: Path) -> list[str]:
    """TC-S6P4-SYS-004: format_ids the closing plan mentions but that never
    appear in plans/master-plan.md. Best-effort text heuristic -- returns []
    on any I/O problem rather than raising (this check must never be the
    reason a plan fails to close)."""
    import re as _re

    import yaml as _yaml

    registry_path = repo_root / "registry" / "format-registry.yaml"
    master_plan_path = repo_root / "plans" / "master-plan.md"
    full_plan_path = repo_root / plan_path if not Path(plan_path).is_absolute() else Path(plan_path)
    if not (registry_path.exists() and master_plan_path.exists() and full_plan_path.exists()):
        return []

    try:
        registry_data = _yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        formats = registry_data.get("formats", registry_data)
        format_ids = ([e.get("format_id") for e in formats] if isinstance(formats, list)
                     else list(formats.keys()))
        format_ids = [f for f in format_ids if f]
    except Exception:
        return []

    try:
        plan_text = full_plan_path.read_text(encoding="utf-8", errors="replace")
        master_text = master_plan_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []

    warnings: list[str] = []
    for fmt in format_ids:
        # Word-boundary match to avoid e.g. "csv" matching inside "csvkit".
        pattern = r"\b" + _re.escape(fmt) + r"\b"
        if _re.search(pattern, plan_text, _re.IGNORECASE) and not _re.search(
                pattern, master_text, _re.IGNORECASE):
            warnings.append(f"'{fmt}' mentioned in this plan, absent from master-plan.md")
    return warnings


def write_lock(plan_path: str, last_taskcard: str | None = None, complete: bool = False,
               terminal: bool = False, session_id: str | None = None,
               track_type: str | None = "product", binding: bool = False,
               audit_gate: bool = False,
               completion_candidate: bool = False,
               skip_audit: bool = False,
               track: str | None = None) -> None:
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

    # TC-VWR-004-01: Initialize machinery mission ledger for this plan (RC-002 fix).
    # Reads mission_id from plan header. Only initializes if mission differs (idempotent).
    _wpl_mission_id: str | None = None  # reused in audit call below
    if terminal and (audit_gate or _should_require_audit(plan_path)):
        try:
            import re as _re_wpl  # noqa: PLC0415
            _plan_text = Path(plan_path).read_text(encoding="utf-8", errors="replace")[:2000]
            _mid_match = _re_wpl.search(r"\*\*mission_id:\*\*\s+(\S+)", _plan_text)
            _mid = _mid_match.group(1).strip() if _mid_match else None
            if _mid:
                _init_machinery_mission_ledger(_mid, plan_path)
                _wpl_mission_id = _mid  # pass through to lifecycle_audit call
        except Exception:
            pass  # Non-blocking

    # TC-TCF-003: Mandatory audit gate.
    # Runs lifecycle_audit before writing TERMINAL_CLOSED when:
    #   (a) --audit-gate is explicitly passed, OR
    #   (b) plan file contains TC-* taskcard entries (auto-detected by _should_require_audit)
    #       AND --skip-audit is NOT set.
    # If audit requires iteration → write ITERATION_REQUIRED instead of TERMINAL_CLOSED.
    audit_result: dict | None = None
    _auto_audit = terminal and not skip_audit and not audit_gate and _should_require_audit(plan_path)
    if terminal and (audit_gate or _auto_audit):
        _gate_label = "--audit-gate" if audit_gate else "auto-audit (TC-TCF-003)"
        try:
            from lifecycle_audit import run_lifecycle_audit, generate_behavioral_gap_taskcards  # type: ignore[import]
            audit_result = run_lifecycle_audit(repo_root=_repo_root, plan_path=plan_path, track=track, mission_id=_wpl_mission_id)
            audit_verdict = audit_result.get("verdict", "AUDIT_PASS")
            if audit_verdict == "AUDIT_REQUIRES_ITERATION":
                status = "ITERATION_REQUIRED"
                print(
                    f"[write_plan_lock] {_gate_label}: lifecycle audit verdict=AUDIT_REQUIRES_ITERATION "
                    "-> writing ITERATION_REQUIRED (plan will iterate)"
                )
                # TC-VWR-005-02 (velvet-swinging-wreath): Auto-generate gap taskcards so the
                # agent knows exactly what to fix without manual inspection of audit output.
                try:
                    _gap_tcs = generate_behavioral_gap_taskcards(audit_result, plan_path=plan_path)
                    if _gap_tcs:
                        print(
                            f"[write_plan_lock] TC-VWR-005-02: Generated {len(_gap_tcs)} gap taskcard(s)"
                            " -> .local/supervisor/gap-taskcards.json"
                        )
                except Exception as _gtc_exc:
                    print(
                        f"[write_plan_lock] WARNING: gap taskcard generation failed: {_gtc_exc}",
                        file=sys.stderr,
                    )
            else:
                status = "TERMINAL_CLOSED"
                print(f"[write_plan_lock] {_gate_label}: lifecycle audit verdict=AUDIT_PASS -> TERMINAL_CLOSED")
        except ImportError:
            # lifecycle_audit not installed yet — fall back to ITERATION_REQUIRED (D6 safety)
            print(
                f"[write_plan_lock] WARNING: {_gate_label} requested but lifecycle_audit not importable; "
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
    elif completion_candidate:
        # TC-TCF-002: COMPLETION_CANDIDATE marks plan as audit-ready but not yet closed.
        # check_continuation.py treats this as CONTINUE (allows lifecycle audit to run).
        # Prevents premature TERMINAL_CLOSED writes before audit is performed.
        status = "COMPLETION_CANDIDATE"
    else:
        status = "TERMINAL_CLOSED" if terminal else ("COMPLETE" if complete else "IN_PROGRESS")

    # V88 (TC-LHEAL-002): Validate required permanent layers before TERMINAL_CLOSED.
    # Fires only when terminal=True and plan declares required_permanent_layers
    # or plan_type: product_certification. Non-blocking if V88 itself errors.
    if status == "TERMINAL_CLOSED" and not getattr(write_lock, "_skip_v88", False):
        try:
            from governance_validators_layers import validate_required_layers_at_terminal as _v88  # noqa: PLC0415
            _v88_result = _v88(plan_path, _repo_root)
            if _v88_result.get("result") == "FAIL":
                print("\nBLOCKED: Cannot write TERMINAL_CLOSED — missing required layers:")
                for _lid in _v88_result.get("missing_layers", []):
                    print(f"  - {_lid}")
                _fix = _v88_result.get("fix_command", "see governance_validators_layers.py V88")
                _hint = _v88_result.get("hint", "create required layer(s) then retry --terminal")
                print(f"\nFix: {_fix}")
                print(f"Hint: {_hint}")
                print("\nEmergency override: --skip-v88 (audited in .local/supervisor/v88-skipped.jsonl)")
                sys.exit(2)
        except SystemExit:
            raise
        except Exception as _v88_exc:
            print(f"[write_plan_lock] V88: non-blocking check error: {_v88_exc}", file=sys.stderr)

    # TC-S6P4-SYS-004 (select-6 Phase 4, 2026-07-15): master-plan rollup check.
    # Closes SF4 -- a plan could reach TERMINAL_CLOSED with zero verification
    # that plans/master-plan.md (the authoritative document CLAUDE.md tells
    # every session to read first) reflects what was built. This is exactly
    # how 3 completed phases and 6 formats went unmentioned there. WARN only
    # (not blocking): the check is a text-mention heuristic across every
    # format_id in the registry, and a false positive must never stop an
    # unrelated machinery plan from closing. Non-blocking on its own errors.
    if status == "TERMINAL_CLOSED":
        try:
            _mp_warnings = _check_master_plan_rollup(plan_path, _repo_root)
            if _mp_warnings:
                print("\n[write_plan_lock] WARNING (SF4 check, non-blocking): "
                      "this plan mentions format(s) not found anywhere in "
                      "plans/master-plan.md -- the authoritative document may "
                      "be out of date:")
                for _w in _mp_warnings:
                    print(f"  - {_w}")
                print("  Consider adding a master-plan.md section before "
                      "considering this work portfolio-visible.")
        except Exception as _mp_exc:
            print(f"[write_plan_lock] SF4 rollup check: non-blocking error: {_mp_exc}",
                  file=sys.stderr)

    # TC-TCF-004: Write terminal closure evidence artifact before lock files.
    # Non-blocking: failure logged to stderr but does not prevent lock write.
    if status == "TERMINAL_CLOSED":
        import hashlib as _hl
        _ph = _hl.sha256(plan_path.encode()).hexdigest()[:16]
        _now_iso = datetime.now(timezone.utc).isoformat()
        _sid_for_record = session_id or _get_session_id()

        # TC-MOR-001 (pre-step): Extract deferred obligations BEFORE writing the closure
        # record so their IDs can be embedded in deferred_obligations field.
        # Non-blocking — extraction failure must not prevent TERMINAL_CLOSED write.
        _mor_obligations: list = []
        _mor_mod = None
        try:
            import importlib.util as _ilu
            _mor_spec = _ilu.spec_from_file_location(
                "maintenance_obligation_register",
                _here / "maintenance_obligation_register.py",
            )
            _mor_mod = _ilu.module_from_spec(_mor_spec)
            _mor_spec.loader.exec_module(_mor_mod)
            _mor_plan_p = (
                Path(plan_path) if Path(plan_path).is_absolute() else _repo_root / plan_path
            )
            _mor_obligations = _mor_mod.extract_from_plan(_mor_plan_p)
        except Exception as _mor_pre_exc:
            print(
                f"[write_plan_lock] TC-MOR-001: pre-extraction failed (non-blocking): {_mor_pre_exc}",
                file=sys.stderr,
            )

        _mor_obligation_ids = [o["obligation_id"] for o in _mor_obligations]

        _write_terminal_closure_record(
            plan_path=plan_path,
            session_id=_sid_for_record,
            locked_at=_now_iso,
            plan_hash=_ph,
            audit_result=audit_result,
            deferred_obligation_ids=_mor_obligation_ids,
        )

        # TC-MOR-001 (write step): Register extracted obligations to MOR.
        # Runs after closure record so closure record write is never blocked.
        try:
            if _mor_obligations and _mor_mod is not None:
                _mor_path = _repo_root / "reports" / "supervisor" / "maintenance-obligations.json"
                _mor_added, _mor_existed = _mor_mod.register_obligations(
                    _mor_obligations, plan_path, _ph, _mor_path
                )
                print(
                    f"[write_plan_lock] TC-MOR-001: {_mor_added} obligation(s) registered, "
                    f"{_mor_existed} already existed"
                )
            elif not _mor_obligations:
                print("[write_plan_lock] TC-MOR-001: no ## Deferred Work Register section found")
        except Exception as _mor_exc:
            print(
                f"[write_plan_lock] TC-MOR-001: MOR write failed (non-blocking): {_mor_exc}",
                file=sys.stderr,
            )

    # B2: get session_id BEFORE writing either file so both files have it
    sid = session_id or _get_session_id()
    # TC-LSG-003: Parse lane_id from plan file header for scope_guard integration
    lane_id = _parse_lane_id_from_plan(plan_path)
    lock = {
        "plan_path": plan_path,
        "status": status,
        "last_taskcard": last_taskcard,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "session_id": sid,
        "track_type": track_type,  # GAP-WF-004: machinery track skips product-track locks
        "lane_id": lane_id,  # TC-LSG-003: for scope_guard --lane-from-lock
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

    # TC-MA2-LOCK-001: Grouped write pattern — write BOTH .tmp files before renaming either.
    # If the second rename fails, the first file is still intact (no partial-update window).
    # Implementation: _write_both_locks() encapsulates this grouped write.

    # Prepare shared lock details
    _skip_shared = _is_temp_path(str(plan_path))
    if _skip_shared:
        print(
            f"[write_plan_lock] SKIPPING shared lock: plan_path is temp/pytest ({plan_path})",
            file=sys.stderr,
        )

    # Prepare keyed lock path
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

    lock_json = json.dumps(lock, indent=2) + "\n"

    # TC-MA2-LOCK-001-02: Grouped write — both .tmp files written before either rename
    _wrote_shared = False
    if not _skip_shared:
        _shared_lock_path.parent.mkdir(parents=True, exist_ok=True)
        _shared_tmp = _shared_lock_path.with_suffix(".tmp")
        _keyed_tmp = keyed_path.with_suffix(".tmp")
        # Phase 1: write both .tmp files
        _shared_tmp.write_text(lock_json, encoding="utf-8")
        _keyed_tmp.write_text(lock_json, encoding="utf-8")
        # Phase 2: rename both (if first rename succeeds but second fails,
        # shared lock is updated and keyed lock is in .tmp — recoverable)
        with _coordinated_write(_shared_lock_path, op="plan_lock", source="write_plan_lock"):
            os.replace(str(_shared_tmp), str(_shared_lock_path))
        with _coordinated_write(keyed_path, op="plan_lock", source="write_plan_lock"):
            os.replace(str(_keyed_tmp), str(keyed_path))
        print(f"[write_plan_lock] {_shared_lock_path} written \u2014 status={status}, plan={plan_path!r}")
        _wrote_shared = True
    else:
        # Shared skipped — write keyed lock only (single atomic write)
        _keyed_tmp = keyed_path.with_suffix(".tmp")
        _keyed_tmp.write_text(lock_json, encoding="utf-8")
        with _coordinated_write(keyed_path, op="plan_lock", source="write_plan_lock"):
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

    # TC-PGI-041 (healed by TC-HQP-003): Clear ledger suppression on plan close.
    # Original bug: only set ledger_items_suppressed_stale (new field), never cleared
    # ledger_items_suppressed (the actual blocking flag), and required path match that
    # fails when work items already point to a different stale plan.
    # Fix: always clear the suppression flag and promote gap_sourced_items on any
    # TERMINAL_CLOSED (no path match required — stale work items are always safe to unblock).
    if status == "TERMINAL_CLOSED" and not _is_temp_path(str(plan_path)):
        _repo = Path(__file__).resolve().parent.parent.parent
        _nwi_path_041 = _repo / ".local" / "supervisor" / "next-work-items.json"
        if _nwi_path_041.exists():
            try:
                _nwi_041 = json.loads(_nwi_path_041.read_text(encoding="utf-8"))
                # Clear the active plan references so ledger work becomes visible
                _nwi_041["active_plan"] = None
                _nwi_041["last_taskcard"] = None
                _nwi_041["ledger_items_suppressed"] = False
                _nwi_041["ledger_items_suppressed_stale"] = False
                _nwi_041.pop("stale_reason", None)
                # Promote gap_sourced_items to items when items only has PLAN-ACTIVE stub
                _items_041 = _nwi_041.get("items", [])
                _gap_items_041 = _nwi_041.get("gap_sourced_items", [])
                if (
                    len(_items_041) == 1
                    and _items_041[0].get("item_id") == "PLAN-ACTIVE"
                    and _gap_items_041
                ):
                    _nwi_041["items"] = _gap_items_041
                _nwi_tmp_041 = _nwi_path_041.with_suffix(".tmp")
                _nwi_tmp_041.write_text(json.dumps(_nwi_041, indent=2) + "\n", encoding="utf-8")
                import os as _os
                _os.replace(str(_nwi_tmp_041), str(_nwi_path_041))
                print(
                    f"[write_plan_lock] TC-PGI-041(healed): next-work-items.json unblocked — "
                    f"ledger_items_suppressed=False, active_plan=null, {len(_nwi_041.get('items',[]))} items promoted",
                )
            except Exception as _e_041:
                print(
                    f"[write_plan_lock] WARNING (TC-PGI-041): could not clear work items suppression: {_e_041}",
                    file=sys.stderr,
                )


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
        print("[write_plan_lock] No lock files to clear")


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


def cleanup_stale_in_progress_locks(session_id: str | None = None,
                                    older_than_hours: float = 24.0) -> dict:
    """TC-S55-004: Supersede IN_PROGRESS plan locks older than older_than_hours.

    Same-session phantom locks (created by autonomous_cycle machinery and never
    formally started) accumulate as IN_PROGRESS indefinitely. This function
    supersedes them so check_continuation.py does not return ACTIVE_PLAN_INCOMPLETE.

    Safety: only supersedes locks from the given session_id (defaults to current).
    Cross-session IN_PROGRESS locks are left untouched (they may be live plans).

    Returns: {"superseded": int, "skipped": int, "errors": int}
    """
    from datetime import timedelta
    sid = session_id or _get_session_id()
    if not _plan_locks_dir.exists():
        return {"superseded": 0, "skipped": 0, "errors": 0}
    cutoff = datetime.now(timezone.utc) - timedelta(hours=older_than_hours)
    results = {"superseded": 0, "skipped": 0, "errors": 0}
    for f in sorted(_plan_locks_dir.glob(f"{sid}*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if data.get("status") != "IN_PROGRESS":
                results["skipped"] += 1
                continue
            ts = data.get("updated_at", "2000-01-01T00:00:00+00:00")
            updated = datetime.fromisoformat(ts)
            if updated.tzinfo is None:
                updated = updated.replace(tzinfo=timezone.utc)
            if updated < cutoff:
                data["status"] = "SUPERSEDED"
                data["superseded_at"] = datetime.now(timezone.utc).isoformat()
                data["superseded_reason"] = (
                    f"Auto-cleanup TC-S55-004: IN_PROGRESS lock older than {older_than_hours}h "
                    f"(age={(datetime.now(timezone.utc) - updated).total_seconds()/3600:.1f}h)"
                )
                _tmp = f.with_suffix(".tmp")
                _tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
                os.replace(str(_tmp), str(f))
                results["superseded"] += 1
                print(f"[write_plan_lock] TC-S55-004 superseded stale IN_PROGRESS: {f.name}")
            else:
                results["skipped"] += 1
        except Exception as e:
            results["errors"] += 1
            print(f"[write_plan_lock] SKIP {f.name}: {e}", file=sys.stderr)
    print(
        f"[write_plan_lock] --cleanup-stale-in-progress: superseded={results['superseded']}, "
        f"skipped={results['skipped']}, errors={results['errors']}"
    )
    return results


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
    parser.add_argument("--cleanup-stale-in-progress", action="store_true",
                        help="TC-S55-004: Supersede same-session IN_PROGRESS locks older than --older-than hours")
    parser.add_argument("--older-than", type=float, default=24.0,
                        help="Age threshold in hours for --cleanup-completed/--cleanup-stale-in-progress (default: 24)")
    parser.add_argument("--binding", action="store_true",
                        help="Include binding_contract in lock file to enforce plan path ownership "
                             "and block wrong-plan writes via validate_plan_binding()")
    parser.add_argument("--audit-gate", action="store_true",
                        help="When used with --terminal: call lifecycle_audit before closing. "
                             "If audit requires iteration, writes ITERATION_REQUIRED instead of "
                             "TERMINAL_CLOSED so check_continuation.py returns CONTINUE. "
                             "Backward compat: --terminal without --audit-gate is unchanged.")
    parser.add_argument("--completion-candidate", action="store_true",
                        help="TC-TCF-002: Mark plan as COMPLETION_CANDIDATE (audit-ready, not yet closed). "
                             "Allows lifecycle audit to run before TERMINAL_CLOSED is written. "
                             "check_continuation.py returns CONTINUE for COMPLETION_CANDIDATE status.")
    parser.add_argument("--skip-audit", action="store_true",
                        help="TC-TCF-003: Emergency bypass — skip the mandatory auto-audit gate even when "
                             "plan contains TC-* taskcard entries. Use only when lifecycle_audit is "
                             "unavailable or the audit is known to be inapplicable.")
    parser.add_argument("--skip-v88", action="store_true",
                        help="TC-LHEAL-002: Emergency bypass — skip the V88 required-layers gate. "
                             "Use only when layer creation is genuinely impossible at terminal time. "
                             "Always audited: writes timestamp+reason to .local/supervisor/v88-skipped.jsonl.")
    parser.add_argument("--track", default=None, choices=["machinery", "product"],
                        help="Track to read continuation signal from when --audit-gate is used "
                             "(default: legacy path). Use 'machinery' for machinery-track plans "
                             "to avoid cross-track signal contamination.")
    args = parser.parse_args(argv)

    if args.clear:
        clear_lock()
        return 0

    if args.cleanup_completed:
        cleanup_completed_locks(older_than_hours=args.older_than)
        return 0

    if getattr(args, "cleanup_stale_in_progress", False):
        cleanup_stale_in_progress_locks(older_than_hours=args.older_than)
        return 0

    if not args.plan_path:
        print("ERROR: --plan-path is required unless --clear or --cleanup-completed is given",
              file=sys.stderr)
        return 1

    # TC-LHEAL-002: Wire --skip-v88 flag into write_lock via function attribute.
    # Using a function attribute avoids changing write_lock's signature.
    if getattr(args, "skip_v88", False):
        write_lock._skip_v88 = True  # type: ignore[attr-defined]
        # Audit the bypass in .local/supervisor/v88-skipped.jsonl
        try:
            from datetime import datetime, timezone  # noqa: PLC0415
            _v88_log = Path(__file__).resolve().parents[2] / ".local" / "supervisor" / "v88-skipped.jsonl"
            _v88_log.parent.mkdir(parents=True, exist_ok=True)
            import json as _json_v88  # noqa: PLC0415
            with _v88_log.open("a", encoding="utf-8") as _v88f:
                _v88f.write(_json_v88.dumps({
                    "skipped_at": datetime.now(timezone.utc).isoformat(),
                    "plan_path": args.plan_path,
                    "reason": "emergency_bypass_via_cli_flag",
                }) + "\n")
            print(f"[write_plan_lock] V88-SKIP: logged bypass to {_v88_log}", file=sys.stderr)
        except Exception as _v88_log_exc:
            print(f"[write_plan_lock] V88-SKIP: audit log failed (non-blocking): {_v88_log_exc}", file=sys.stderr)
    else:
        write_lock._skip_v88 = False  # type: ignore[attr-defined]

    write_lock(args.plan_path, last_taskcard=args.last_taskcard,
               complete=args.complete, terminal=args.terminal,
               track_type=args.track_type, binding=args.binding,
               audit_gate=getattr(args, "audit_gate", False),
               completion_candidate=getattr(args, "completion_candidate", False),
               skip_audit=getattr(args, "skip_audit", False),
               track=getattr(args, "track", None))
    return 0





if __name__ == "__main__":
    sys.exit(main())
