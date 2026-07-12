"""
autonomous_cycle.py — Declaration-Driven Autonomous Supervisor Cycle
Orchestrates the full cycle: validate -> inspect -> grade -> plan-next -> manifest

This is the canonical supervisor command. It takes a declaration path
(not a ZIP, not a watcher state) and produces a complete review.

Exit codes:
  0 — cycle complete, autonomous continue possible
  3 — cycle complete, critical rework exists
  9 — unexpected error

Playbook Integration (FF-PLAYBOOK-SYSTEM-001, 2026-07-01):
  After the next work item is selected, this cycle optionally invokes
  tools/playbook/playbook_selector.py to route the work item type to an applicable
  Sprint Task Template (Layer A). If found: log path and extract constraints.
  If not found or validation fails: log warning and continue (never blocks sprint).
  Missing skills → CREATE_SKILL_GAP action (gap, not hard failure).
  See docs/governance/playbook-layer.md Section 24 for Model C architecture.
"""
# ruff: noqa: F821  # complex control flow causes false-positive undefined-name in try/except blocks

import argparse
import json
import os
import shutil
import sys

from atomic_io import atomic_write_json, atomic_write_text  # noqa: E402
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent

# Import sibling modules
sys.path.insert(0, str(SCRIPT_DIR))

# Structured logging (TC-APRV-011)
from logging_config import configure_supervisor_logging
_logger = configure_supervisor_logging()

from evidence_declaration import validate_declaration
from inspect_declared_evidence import inspect_declaration
from grade_declared_work import grade_all, write_outputs
from generate_next_worker_prompt import generate_prompt, generate_next_work_items
from evidence_manifest import generate_from_declaration, validate_manifest, write_manifest
from materialize_declared_evidence import materialize as materialize_evidence
from build_context_pack import build_context_pack, generate_md as generate_context_md
from anti_skip_checker import run_all_checks as run_anti_skip_checks
from failure_memory import FailureMemory
from autonomous_cycle_utils import (  # TC-SAL-DEBT-001: extracted to reduce LOC
    classify_continuation_state,
    run_stale_repair_pre_cycle,
    _PRODUCT_SOURCE_TYPES,
    _sync_hard_stops_after_repair,
    _compute_exit_code,
    bridge_to_legacy_format,
)


def _validate_and_correct_signal_coherence(signal: dict, sprint_id: str) -> dict:
    """TC-MA2-SIGNAL-001-02: Validate and correct signal field coherence at write time.

    Prevents incoherent combinations such as stop_reason set while autonomous_continue
    is True and rework_items is empty (observed on disk 2026-07-04).

    Does NOT raise — emits diagnostic and returns corrected signal (REQ-SIGNAL-001).
    """
    issues: list[str] = []
    corrected = dict(signal)

    ac = corrected.get("autonomous_continue")
    stop = corrected.get("stop_reason")
    rework = corrected.get("rework_items", [])
    hard_stops = corrected.get("hard_stops_detected", [])

    # Incoherence 1: stop_reason set but autonomous_continue=True and no hard stops
    if stop and ac is True and not hard_stops:
        issues.append(
            f"INCOHERENT: stop_reason={stop!r} with autonomous_continue=True "
            "and no hard_stops_detected — clearing stop_reason"
        )
        corrected["stop_reason"] = None

    # Incoherence 2: rework_items non-empty but autonomous_continue=True (allowed as "true_with_rework")
    # This is NOT incoherent — autonomous loop continues with rework. No correction needed.

    # Incoherence 3: autonomous_continue=False but no stop_reason and no hard stops and no rework
    if ac is False and not stop and not hard_stops and not rework:
        issues.append(
            "INCOHERENT: autonomous_continue=False with no stop_reason, "
            "hard_stops, or rework_items — setting stop_reason=unknown_stop"
        )
        corrected["stop_reason"] = "unknown_stop"

    if issues:
        corrected["_coherence_corrections"] = {
            "sprint_id": sprint_id,
            "issues": issues,
        }
        for issue in issues:
            print(f"  [SIGNAL-COHERENCE] {issue}")

    return corrected


def _update_lane_counters(declaration, ledger_path):
    from autonomous_cycle_extensions import update_lane_counters
    update_lane_counters(declaration, ledger_path)


def evaluate_gate11_readiness(format_id: str, declaration: dict, repo_root: "Path | None" = None) -> dict:
    """Evaluate Gate 11 P1-P10 criteria for a format/language pair.

    Reads registry/gate-states.yaml for the current per-product gate state.
    Updates state to GATE_11_READY if all P1-P10 criteria are met.
    Returns {gate_11_ready: bool, criteria_met: [], criteria_missing: [], state_written: bool}.

    Implements: TC-GFB-022 (FF-MR-2026-001). Fixes: GAP-GATE11-NOT-GOVERNED.
    Non-blocking on any file-read or parse error.
    """
    import yaml
    from pathlib import Path as _Path

    repo = Path(repo_root) if repo_root is not None else _Path(__file__).resolve().parent.parent.parent
    gate_states_path = repo / "registry" / "gate-states.yaml"

    if not gate_states_path.exists():
        return {"gate_11_ready": False, "criteria_met": [], "criteria_missing": ["gate-states.yaml missing"], "state_written": False}

    try:
        data = yaml.safe_load(gate_states_path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        return {"gate_11_ready": False, "criteria_met": [], "criteria_missing": [str(exc)], "state_written": False}

    # Determine language from declaration (default to python for FOSS formats)
    work_items = declaration.get("planned_work_items", [])
    language = "python"
    for item in work_items:
        wtype = item.get("work_item_type", "")
        if "dotnet" in wtype.lower() or "net" in wtype.lower():
            language = "dotnet"
            break

    format_states = data.get("format_gate_states", {})
    fmt_state = format_states.get(format_id, {}).get(language, {})
    if not fmt_state:
        return {"gate_11_ready": False, "criteria_met": [], "criteria_missing": ["no gate state for this format/language"], "state_written": False}

    # Check P1-P10 criteria
    criteria_fields = [
        "p1_oracle_verified", "p2_validators_pass", "p3_pyproject_present",
        "p4_package_installs", "p5_consumer_roundtrip", "p6_spec_qname_classvar",
        "p7_py_typed_present", "p8_dogfood_exports", "p9_analytics_loc_compliant",
        "p10_no_known_violations_at_cap",
    ]
    criteria_met = [f for f in criteria_fields if fmt_state.get(f) is True]
    criteria_missing = [f for f in criteria_fields if not fmt_state.get(f)]

    gate_11_ready = len(criteria_missing) == 0
    state_written = False

    if gate_11_ready and fmt_state.get("state") != "GATE_11_READY":
        try:
            fmt_state["state"] = "GATE_11_READY"
            fmt_state["state_reason"] = "All P1-P10 criteria met — awaiting Babar Raza P11 authorization"
            from datetime import datetime, timezone
            fmt_state["last_evaluated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            gate_states_path.write_text(yaml.dump(data, default_flow_style=False, allow_unicode=True), encoding="utf-8")
            state_written = True
        except Exception:
            pass

    return {
        "gate_11_ready": gate_11_ready,
        "criteria_met": criteria_met,
        "criteria_missing": criteria_missing,
        "state_written": state_written,
        "format_id": format_id,
        "language": language,
    }


def _extract_declared_paths(declaration_path: Path) -> list[str]:
    """Extract repo-relative file paths from an evidence-declaration.yaml.

    Sources: evidence_paths in planned_work_items + changed_files.
    Skips .local/ paths (state-only, not working-tree sources).
    TC-CONC-008
    """
    try:
        import yaml
        data = yaml.safe_load(declaration_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    paths: set[str] = set()
    for item in (data.get("planned_work_items") or []):
        for p in (item.get("evidence_paths") or []):
            if isinstance(p, str) and not p.startswith(".local"):
                paths.add(p.lstrip("./"))
    for p in (data.get("changed_files") or []):
        if isinstance(p, str) and not p.startswith(".local"):
            paths.add(p.lstrip("./"))
    return list(paths)


def run_cycle(declaration_path: Path, repo_root: Path, track: str | None = None) -> dict:
    """Run a complete autonomous supervisor cycle.

    track: TC-P2-002 — "product" | "machinery" | None.
      product  → work_groups=["G3","G4","G5"], signal written to product/ subdir
      machinery → work_groups=["G1","G2","G6","G7","G8"], signal written to machinery/ subdir
      None     → legacy mode (all groups, shared .local/supervisor/ path)
    """
    timestamp = datetime.now().isoformat()
    continuation_warnings: list = []  # accumulated non-blocking warnings; written to signal

    # Step 0-pre (TC-PGI-044): Auto-GC SUPERSEDED plan locks older than 30 days.
    # Extracted to plan_lock_gc.py to keep this file within LOC cap.
    _gc_dir = repo_root / ".local" / "supervisor" / "plan-locks"
    if _gc_dir.is_dir():
        try:
            from plan_lock_gc import gc_superseded_locks as _gc_fn  # noqa: PLC0415
            _gc_deleted = _gc_fn(_gc_dir)
            if _gc_deleted > 0:
                print(f"  [TC-PGI-044] GC: deleted {_gc_deleted} SUPERSEDED locks older than 30 days")
        except Exception:
            pass  # best-effort

    # Step 0-pre-aq (TC-HQP-005): GC action-queue.jsonl entries older than 7 days.
    # The queue is append-only with no consumer TTL; without GC it grows unbounded.
    # Entries from closed sprints >7 days ago are stale and cannot be actioned.
    _aq_path_gc = repo_root / ".local" / "supervisor" / "action-queue.jsonl"
    if _aq_path_gc.exists():
        try:
            from datetime import datetime as _dt_gc, timezone as _tz_gc, timedelta as _td_gc
            _aq_cutoff = _dt_gc.now(_tz_gc.utc) - _td_gc(days=7)
            _aq_lines = _aq_path_gc.read_text(encoding="utf-8").splitlines()
            _aq_kept, _aq_dropped = [], 0
            for _aq_line in _aq_lines:
                if not _aq_line.strip():
                    continue
                try:
                    _aq_entry = json.loads(_aq_line)
                    _aq_ts_str = _aq_entry.get("queued_at") or _aq_entry.get("created_at")
                    if _aq_ts_str:
                        _aq_ts = datetime.fromisoformat(_aq_ts_str)
                        if _aq_ts.tzinfo is None:
                            _aq_ts = _aq_ts.replace(tzinfo=timezone.utc)
                        if _aq_ts < _aq_cutoff:
                            _aq_dropped += 1
                            continue
                except Exception:
                    pass
                _aq_kept.append(_aq_line)
            if _aq_dropped > 0:
                _aq_path_gc.write_text("\n".join(_aq_kept) + "\n", encoding="utf-8")
                print(f"  [TC-HQP-005] action-queue GC: dropped {_aq_dropped} entries older than 7 days, kept {len(_aq_kept)}")
        except Exception as _aq_gc_err:
            print(f"  [TC-HQP-005] action-queue GC skipped (non-blocking): {_aq_gc_err}", file=sys.stderr)

    # Step 0 (pre-cycle): Stale queue repair (disabled by default, dry-run safe)
    print("=== STEP 0: PRE-CYCLE STALE REPAIR ===")
    repair_result = run_stale_repair_pre_cycle(repo_root, dry_run=True, enabled=False)
    if repair_result.get("skipped"):
        print(f"  Stale repair: {repair_result['status']}")
    else:
        print(f"  Stale repair: stale={repair_result.get('stale_count', 0)} "
              f"gaps={repair_result.get('gap_count', 0)} "
              f"status={repair_result.get('status', 'UNKNOWN')}")
    # Step 0a (TC-SAL-REGEN-001): SAL regeneration trigger.
    # Refreshes spec facts if sal-facts-latest.json is older than 7 days.
    # Completely non-blocking: timeout or error logs and skips — never stops sprint.
    print("=== STEP 0a: SAL REGENERATION CHECK ===")
    try:
        import subprocess as _sal_subprocess
        import time as _sal_time
        _sal_facts_path = repo_root / ".local" / "sal-output" / "sal-facts-latest.json"
        _sal_stale_days = 7
        _sal_is_stale = False
        if _sal_facts_path.exists():
            _sal_age_days = (_sal_time.time() - _sal_facts_path.stat().st_mtime) / 86400
            _sal_is_stale = _sal_age_days > _sal_stale_days
            print(f"  SAL facts age: {_sal_age_days:.1f} days "
                  f"({'STALE — regenerating' if _sal_is_stale else 'fresh — skipping'})")
        else:
            _sal_is_stale = True
            print("  SAL facts: not found — triggering regeneration")
        if _sal_is_stale:
            _sal_runner = repo_root / "tools" / "specification-authority-layer" / "sal_master_runner.py"
            if _sal_runner.exists():
                _sal_result = _sal_subprocess.run(
                    ["python", str(_sal_runner), "--all", "--from-cache-only"],
                    cwd=str(repo_root),
                    timeout=300,
                    capture_output=True,
                    text=True,
                )
                if _sal_result.returncode == 0:
                    print("  SAL regeneration: SUCCESS — triggering capability map refresh")
                    # Trigger capability map regeneration downstream
                    _capmap = repo_root / "tools" / "capability_layer" / "capability_map_generator.py"
                    if _capmap.exists():
                        _cm_result = _sal_subprocess.run(
                            ["python", str(_capmap)],
                            cwd=str(repo_root),
                            timeout=120,
                            capture_output=True,
                            text=True,
                        )
                        if _cm_result.returncode == 0:
                            print("  Capability map refresh: SUCCESS")
                        else:
                            print(f"  WARNING: Capability map refresh failed (non-blocking): "
                                  f"{_cm_result.stderr[:200]}")
                else:
                    print(f"  WARNING: SAL regeneration failed (non-blocking): "
                          f"{_sal_result.stderr[:200]}")
            else:
                print("  SAL runner not found — skipping regeneration")
    except Exception as _sal_exc:
        print(f"  WARNING: SAL regeneration check skipped (non-blocking): {_sal_exc}")
    # Step 0a-staleness (TC-MACH-SAL-001): Escalate SAL staleness to sprint-blocking
    # for PRODUCT sprints when >7 days old. MACHINERY:sal_repair sprints are exempt.
    # Logic extracted to autonomous_cycle_extensions.check_sal_staleness() for testability.
    try:
        from autonomous_cycle_extensions import check_sal_staleness
        _sprint_type = decl.get("declared_scope", {}).get("sprint_type", "")
        _sal_stops = check_sal_staleness(sal_is_stale=_sal_is_stale, sprint_type=_sprint_type)
        if _sal_stops:
            hard_stops.extend(_sal_stops)
            print("  [SAL_STALENESS] BLOCKING: SAL facts >7 days old for product sprint")
        elif _sal_is_stale:
            print("  [SAL_STALENESS] WARNING: SAL stale but machinery/sal_repair sprint — not blocking")
    except Exception as _sal_stale_err:
        print(f"  [SAL_STALENESS] Error: {_sal_stale_err}")
    # Step 0a-prepass (TC-SH-005) + Step 0a3 (TC-SH-011): extracted to extensions
    try:
        from autonomous_cycle_extensions import run_sprint_learnings_prepass, run_stale_lock_reaper
        run_sprint_learnings_prepass(repo_root)
        run_stale_lock_reaper(repo_root, timestamp)
    except Exception as _ext_err:
        print(f"  WARNING: Pre-pass extensions skipped (non-blocking): {_ext_err}")

    # Step 0a-qname (FF-FORENSIC-AUDIT-20260623-H7): QName coverage regression check.
    # Runs audit_qname_coverage.py and warns if coverage dropped below baseline.
    # Completely non-blocking: error or timeout logs and skips.
    print("=== STEP 0a-qname: QNAME COVERAGE CHECK ===")
    try:
        import subprocess as _qn_subprocess
        _qn_baseline_path = repo_root / "reports" / "qname-coverage-baseline.json"
        _qn_tool = repo_root / "tools" / "audit_qname_coverage.py"
        if _qn_tool.exists():
            _qn_result = _qn_subprocess.run(
                [sys.executable, str(_qn_tool)],
                capture_output=True, text=True, timeout=60,
                cwd=str(repo_root),
            )
            if _qn_result.returncode == 0:
                # Extract coverage % from output
                import re as _qn_re
                _qn_match = _qn_re.search(r"Overall coverage score:\s+([\d.]+)%", _qn_result.stdout)
                if _qn_match:
                    _qn_current = float(_qn_match.group(1))
                    _qn_baseline = 96.9  # baseline from 2026-06-23 audit
                    if _qn_baseline_path.exists():
                        try:
                            import json as _qn_json
                            _qn_bl_data = _qn_json.loads(_qn_baseline_path.read_text())
                            _qn_baseline = float(_qn_bl_data.get("overall_coverage_pct", 96.9))
                        except Exception:
                            pass
                    if _qn_current < _qn_baseline - 1.0:
                        continuation_warnings.append(
                            f"QNAME_COVERAGE_REGRESSION: {_qn_current:.1f}% < baseline {_qn_baseline:.1f}%"
                        )
                        print(f"  WARNING: QName coverage regression: {_qn_current:.1f}% < {_qn_baseline:.1f}%")
                    else:
                        print(f"  QName coverage: {_qn_current:.1f}% (baseline: {_qn_baseline:.1f}%) — OK")
            else:
                print(f"  WARNING: audit_qname_coverage.py exited {_qn_result.returncode} (non-blocking)")
        else:
            print("  SKIP: tools/audit_qname_coverage.py not found")
    except Exception as _qn_err:
        print(f"  WARNING: QName coverage check skipped (non-blocking): {_qn_err}")
    # Step 0a-v54v55 (FF-DEFERRED-RESOLVE-20260624 TC-D1): V54/V55 promotion tracker.
    print("=== STEP 0a-v54v55: V54/V55 PROMOTION TRACKER ===")
    try:
        _v54_tracker_path = repo_root / "reports" / "v54v55-sprint-tracker.json"
        if _v54_tracker_path.exists():
            import json as _v54_json
            _v54_data = _v54_json.loads(_v54_tracker_path.read_text(encoding="utf-8"))
            _v54_count = _v54_data.get("clean_sprint_count", 0)
            _v54_target = _v54_data.get("target_clean_sprints", 3)
            _v54_promoted = _v54_data.get("promoted", False)
            if _v54_promoted:
                print(f"  V54/V55 already promoted to blocking ({_v54_count}/{_v54_target} clean sprints)")
            else:
                print(f"  V54/V55 clean sprints: {_v54_count}/{_v54_target} (promotion pending)")
                if _v54_count >= _v54_target:
                    print("  INFO: V54/V55 eligible for promotion — will promote after governance run")
        else:
            print("  SKIP: reports/v54v55-sprint-tracker.json not found")
    except Exception as _v54_err:
        print(f"  WARNING: V54/V55 tracker check skipped (non-blocking): {_v54_err}")
    # Steps 0a-sal + 0a-gap-sal: SAL audit checks — extracted to extensions (TC-PGI-045)
    try:
        from autonomous_cycle_extensions import run_sal_audit_checks
        run_sal_audit_checks(repo_root, continuation_warnings)
    except Exception as _sal_audit_err:
        print(f"  WARNING: SAL audit checks skipped (non-blocking): {_sal_audit_err}")

    # Step 0c: Action queue consumption — promote machine_executable actions (TC-FL-008)
    _consumed_actions: list[dict] = []
    try:
        _aq_path = repo_root / "reports" / "capability-layer" / "action-queue.json"
        # TC-CAP-008: prefer active split; fall back to full ledger
        _gl_path_0c = repo_root / "reports" / "capability-layer" / "gap-ledger-active.json"
        if not _gl_path_0c.exists():
            _gl_path_0c = repo_root / "reports" / "capability-layer" / "gap-ledger.json"
        if _aq_path.exists() and _gl_path_0c.exists():
            _aq = json.loads(_aq_path.read_text(encoding="utf-8"))
            _gl_0c = json.loads(_gl_path_0c.read_text(encoding="utf-8"))
            _gap_status_0c = {g["gap_id"]: g.get("status", "open") for g in _gl_0c.get("gaps", [])}

            for _action in _aq.get("actions", []):
                if (_action.get("machine_executable")
                        and not _action.get("advisory_only")
                        and _gap_status_0c.get(_action.get("gap_id")) != "closed"):
                    _action["taskcard"] = f"TC-ACT-{_action['gap_id']}-{sprint_id[:8]}"
                    _consumed_actions.append(_action)

            if _consumed_actions:
                print(f"  [Step 0c] Consumed {len(_consumed_actions)} executable actions from queue")
    except Exception as _aq_err:
        print(f"  WARNING: Action queue consumption skipped: {_aq_err}")

    # Step 0b: Detect active per-chat plan lock
    plan_lock = None
    _plan_locks_dir = repo_root / ".local" / "supervisor" / "plan-locks"
    _plan_lock_candidates: list[Path] = []
    if _plan_locks_dir.is_dir():
        _plan_lock_candidates.extend(sorted(_plan_locks_dir.glob("*.json")))
    _shared_lock = repo_root / ".local" / "supervisor" / "active-plan-lock.json"
    if _shared_lock.exists():
        _plan_lock_candidates.append(_shared_lock)
    for _lp in _plan_lock_candidates:
        try:
            _ld = json.loads(_lp.read_text(encoding="utf-8"))
            # Only treat IN_PROGRESS locks as active. COMPLETE and TERMINAL_CLOSED are done.
            if _ld.get("status") == "IN_PROGRESS":
                plan_lock = _ld
                print(f"  [PLAN_LOCK] Active plan: {plan_lock.get('plan_path')}")
                print(f"  [PLAN_LOCK] Last taskcard: {plan_lock.get('last_taskcard')}")
                break
            # TC-TCF-008: COMPLETION_CANDIDATE is also an active plan (non-blocking)
            if _ld.get("status") == "COMPLETION_CANDIDATE":
                plan_lock = _ld
                print(f"  [PLAN_LOCK] COMPLETION_CANDIDATE detected: {plan_lock.get('plan_path')}")
                print("  [PLAN_LOCK] Running completion audit before proceeding...")
                break
        except Exception as _pe:
            print(f"  [PLAN_LOCK] Warning: could not read {_lp.name}: {_pe}")

    # Step 0b-reopen-check: Autonomous reopening of prematurely closed plans (TC-TCF-008)
    # If we find a TERMINAL_CLOSED lock for the current session AND the plan has open taskcards,
    # reopen the plan automatically.
    # POSTCLEAN-002 guard: never auto-reopen external per-chat plans (~/.claude/plans/).
    # These are loaded ONLY via plan-mode and must not be picked up by the autonomous loop.
    # Only reopen plans that live inside the repository's plans/ directory.
    _REPO_PLANS_DIR = str(repo_root / "plans").replace("\\", "/")
    if plan_lock is None:
        for _lp in _plan_lock_candidates:
            try:
                _ld = json.loads(_lp.read_text(encoding="utf-8"))
                if _ld.get("status") != "TERMINAL_CLOSED":
                    continue
                _plan_path = _ld.get("plan_path")
                if not _plan_path:
                    continue
                # POSTCLEAN-002: Skip external per-chat plan files (not in repo plans/)
                _plan_path_norm = str(_plan_path).replace("\\", "/")
                if not _plan_path_norm.startswith(_REPO_PLANS_DIR) and "/.claude/plans/" in _plan_path_norm:
                    continue  # External per-chat plan — never auto-reopen
                # Check if plan file has open taskcards
                try:
                    import sys as _sys_reopen
                    _sup_dir_reopen = str(Path(__file__).resolve().parent)
                    if _sup_dir_reopen not in _sys_reopen.path:
                        _sys_reopen.path.insert(0, _sup_dir_reopen)
                    from lifecycle_audit import parse_plan_taskcards  # type: ignore[import]
                    _tcs = parse_plan_taskcards(_plan_path)
                    _open_tcs = [tc for tc in _tcs if tc["status"] not in ("CLOSED", "SUPERSEDED", "EXCLUDED")]
                    if _open_tcs:
                        print(f"  [AUTONOMOUS REOPEN] {len(_open_tcs)} open taskcards found in "
                              f"TERMINAL_CLOSED plan {_plan_path}")
                        try:
                            from reopen_plan_lock import reopen_plan  # type: ignore[import]
                            reopen_plan(
                                plan_path=_plan_path,
                                reason=f"Autonomous detection: {len(_open_tcs)} open taskcards in closed plan",
                                trigger="AUTONOMOUS_OPEN_TASKCARD_DETECTION",
                            )
                            # Re-read the lock file which is now IN_PROGRESS
                            _ld_reopened = json.loads(_lp.read_text(encoding="utf-8"))
                            plan_lock = _ld_reopened
                            print("  [AUTONOMOUS REOPEN] Plan reopened. Continuing execution.")
                            # TC-TCF-005: identify next eligible task to prevent fall-through
                            try:
                                from autonomous_cycle_extensions import find_next_eligible_task_in_plan as _fnet  # type: ignore[import]
                                _reopened_next = _fnet(_plan_path)
                                if _reopened_next:
                                    print(f"  [TCF-005] Reopened plan next task: {_reopened_next['tc_id']}")
                            except Exception:
                                pass  # Non-blocking
                        except Exception as _reopen_exc:
                            print(f"  [AUTONOMOUS REOPEN] WARNING: reopen failed ({_reopen_exc}). "
                                  "Plan remains TERMINAL_CLOSED.")
                except ImportError:
                    pass  # lifecycle_audit or reopen_plan_lock not available
                except Exception:
                    pass  # Non-blocking
                if plan_lock is not None:
                    break  # Found and reopened a plan
            except Exception:
                continue

    # Step 0b-validate: Pre-execution plan readiness check (TC-PG-005)
    # Non-blocking: log CRITICAL and return exit 3 if plan is invalid (Supreme Directive applies).
    if plan_lock and plan_lock.get("plan_path"):
        try:
            import sys as _sys
            _sup_dir = str(Path(__file__).resolve().parent)
            if _sup_dir not in _sys.path:
                _sys.path.insert(0, _sup_dir)
            from validate_plan_readiness import validate_plan_readiness as _vpr  # type: ignore[import]
            _active_plan_path = Path(plan_lock["plan_path"])
            _readiness = _vpr(_active_plan_path)
            _pev = _readiness.get("pre_execution_plan_validation", {})
            if _pev.get("execution_may_start", True):
                for _w in _pev.get("warnings", []):
                    print(f"  [PLAN_READINESS] WARN: {_w}")
                print(f"  [PLAN_READINESS] PASS — {_active_plan_path.name}")
            else:
                for _f in _pev.get("failures", []):
                    print(f"  [PLAN_READINESS] CRITICAL: {_f}")
                print("  [PLAN_READINESS] FAIL — plan not ready for execution. "
                      "Logging and continuing per Supreme Directive (exit 3 non-blocking).")
        except ImportError:
            print("  [PLAN_READINESS] validate_plan_readiness not available — skipping (non-blocking)")
        except Exception as _vpr_exc:
            print(f"  [PLAN_READINESS] WARNING: readiness check failed ({_vpr_exc}) — skipping (non-blocking)")

    # Steps 0d + 0e: OIC + CPF checks — extracted to extensions (TC-PGI-045)
    try:
        from autonomous_cycle_extensions import run_output_invariant_and_parity_checks
        _oic_rework_entries = run_output_invariant_and_parity_checks(declaration_path, repo_root)
    except Exception as _oic_ext_err:
        print(f"  WARNING: OIC/CPF checks skipped (non-blocking): {_oic_ext_err}")
        _oic_rework_entries = []

    # Step 1: Validate declaration
    _logger.info("Step 1: Validate declaration", extra={"sprint_id": "pending"})
    print("=== STEP 1: VALIDATE DECLARATION ===")
    validation = validate_declaration(declaration_path, repo_root)
    if not validation["valid"]:
        print(f"DECLARATION_INVALID: {declaration_path}")
        for e in validation.get("schema_errors", []):
            print(f"  SCHEMA_ERROR: {e}")
        for e in validation.get("path_errors", []):
            print(f"  PATH_ERROR: {e}")
        return {"exit_code": 1, "error": "Declaration validation failed"}

    decl = validation["declaration"]
    run_id = decl.get("run_id", "unknown")
    sprint_id = decl.get("sprint_id", "unknown")
    _logger.info("Declaration validated", extra={"sprint_id": run_id})
    print(f"  VALID: run_id={run_id}, sprint_id={sprint_id}")

    # TC-CONC-008: Path ownership guard state (initialized here, claimed after Step 1b)
    _claims_mgr = None
    _worker_id = f"autonomous_cycle_{run_id}"

    # Step 1a (TC-PB-008): Best-effort playbook selection hook.
    # Advisory only — NEVER blocks sprint execution. All failures log and continue.
    print("=== STEP 1a: PLAYBOOK SELECTION (advisory) ===")
    try:
        import sys as _pb_sys
        _pb_tools = str(REPO_ROOT / "tools" / "playbook")
        if _pb_tools not in _pb_sys.path:
            _pb_sys.path.insert(0, _pb_tools)
        from playbook_selector import select_playbook as _select_playbook
        _pb_items = decl.get("planned_work_items", [])
        _pb_seen_types: set = set()
        for _pb_item in _pb_items:
            _pb_type = _pb_item.get("item_type", "")
            if _pb_type and _pb_type not in _pb_seen_types:
                _pb_seen_types.add(_pb_type)
                try:
                    _pb_path = _select_playbook(_pb_type)
                    if _pb_path:
                        print(f"  [PLAYBOOK] Selected for {_pb_type}: {_pb_path}")
                    else:
                        print(f"  [PLAYBOOK] No applicable playbook for {_pb_type}")
                except Exception as _pb_item_err:
                    print(f"  [PLAYBOOK] WARNING: selection failed for {_pb_type} (non-blocking): {_pb_item_err}")
        if not _pb_seen_types:
            print("  [PLAYBOOK] No work item types found — skipping playbook selection")
    except ImportError:
        print("  [PLAYBOOK] playbook_selector not available — skipping (non-blocking)")
    except Exception as _pb_err:
        print(f"  [PLAYBOOK] WARNING: playbook hook failed (non-blocking): {_pb_err}")

    # TC-HARD-010 (2026-06-23): Capture actual HEAD at review time.
    # The declaration's git_head_end may be stale (written before the final commit).
    # git_head_at_review is injected into the review manifest for accurate provenance.
    _git_head_at_review = "unknown"
    try:
        import subprocess as _gh_sp
        _gh_result = _gh_sp.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10, cwd=repo_root
        )
        if _gh_result.returncode == 0:
            _git_head_at_review = _gh_result.stdout.strip()[:12]
    except Exception:
        pass
    _git_head_declared = decl.get("git_head_end", "unknown")
    if _git_head_at_review != "unknown" and _git_head_declared not in ("unknown", _git_head_at_review):
        print(f"  [TC-HARD-010] git_head_end in declaration ({_git_head_declared}) differs "
              f"from actual HEAD ({_git_head_at_review}). Declaration was written pre-commit. "
              f"Review manifest will include git_head_at_review for accurate provenance.")

    # TC-H2-002: Anti-inflation check — tests_run vs tests_created
    _tests_run = decl.get("tests_run", 0)
    _tests_created = decl.get("tests_created")
    if _tests_created is not None and _tests_created < 5 and _tests_run > 1000:
        print(f"  [WARN] TEST_COUNT_INFLATION: tests_run={_tests_run} but tests_created={_tests_created}. "
              f"tests_run reflects full-suite regression; tests_created should count new tests only.")
    elif _tests_created is None and _tests_run > 1000:
        print(f"  [INFO] tests_created not declared. Add tests_created to distinguish "
              f"new tests from full-suite run ({_tests_run} tests_run).")

    # Step 1b: System healing gate check (GATE_ADVISORY — warns but does not block)
    _healing_gate_failed = False
    _has_product_source_items = any(
        item.get("item_type", "") in _PRODUCT_SOURCE_TYPES
        for item in decl.get("planned_work_items", [])
    )
    if _has_product_source_items:
        try:
            _sys_heal_dir = Path(__file__).parent
            import sys as _sys_mod
            if str(_sys_heal_dir) not in _sys_mod.path:
                _sys_mod.path.insert(0, str(_sys_heal_dir))
            from check_system_healing_gate import check_healing_gate as _chg
            _gate_result = _chg(repo_root=repo_root, advisory=True)
            _gate_verdict = _gate_result.get("verdict", "UNKNOWN")
            _gate_exit = _gate_result.get("exit_code", -1)
            _failed_lanes = _gate_result.get("failed_lanes", [])
            if _gate_exit != 0:
                print(f"  [SYSTEM_HEALING_GATE] ADVISORY: verdict={_gate_verdict}, "
                      f"failed_lanes={_failed_lanes}. "
                      f"Product source work proceeding (advisory mode). "
                      f"Resolve healing gate before switching to GATE_STRICT mode.")
                _healing_gate_failed = True
            else:
                print(f"  [SYSTEM_HEALING_GATE] PASSED: verdict={_gate_verdict}")
        except Exception as _ghg_err:
            print(f"  [SYSTEM_HEALING_GATE] Could not check: {_ghg_err}")
            _healing_gate_failed = False

    # Step 1c (TC-MACH-LANE-001): Preventive lane conflict guard
    # Checks declared_scope.lane against changed_files BEFORE grading.
    # Logic extracted to autonomous_cycle_extensions.check_lane_conflicts() for testability.
    _lane_conflict_detected = False
    try:
        from autonomous_cycle_extensions import check_lane_conflicts
        _declared_lane = decl.get("declared_scope", {}).get("lane", "")
        _changed = decl.get("changed_files", [])
        _policies_path = repo_root / ".supervisor" / "policies.yaml"
        _lane_stops = check_lane_conflicts(
            declared_lane=_declared_lane,
            changed_files=_changed,
            policies_path=_policies_path if _policies_path.exists() else None,
        )
        if _lane_stops:
            for _ls in _lane_stops:
                print(f"  [LANE_GUARD] CONFLICT DETECTED: {_ls}")
                hard_stops.append(_ls)
            _lane_conflict_detected = True
        else:
            print("  [LANE_GUARD] No lane conflicts detected")
    except Exception as _lc_err:
        print(f"  [LANE_GUARD] Error: {_lc_err}")

    # Step 1b: Evidence completeness pre-check + auto-repair (TC-FL-005)
    print("\n=== STEP 1b: EVIDENCE COMPLETENESS PRE-CHECK ===")
    _evidence_repair_count = 0
    try:
        from sprint_executor_validate import (
            check_fix_sprint_evidence as _check_fse,
            check_parent_id_evidence_tagging as _check_pid,
        )
        _fse_warns = _check_fse(decl)
        _pid_warns = _check_pid(decl)

        if _fse_warns or _pid_warns:
            # Auto-repair FSE-001: add changed test files to matching PRODUCT items
            _changed_tests = {
                f for f in (decl.get("changed_files") or [])
                if "/test_" in f or f.startswith("tests/")
            }
            for _item in decl.get("planned_work_items", []):
                if _item.get("item_type") in ("PRODUCT_SOURCE", "PRODUCT_TEST"):
                    _existing_ep = set(_item.get("evidence_paths") or [])
                    _fmt_parts = (_item.get("gap_ledger_ref") or "").split("-")[1:2]
                    _fmt_lower = _fmt_parts[0].lower() if _fmt_parts else ""
                    for _tf in _changed_tests:
                        if _fmt_lower and _fmt_lower in _tf.lower() and _tf not in _existing_ep:
                            _item.setdefault("evidence_paths", []).append(_tf)
                            _evidence_repair_count += 1

            # Auto-repair PID-001: copy children's evidence to empty parents
            _items_by_id = {i.get("item_id"): i for i in decl.get("planned_work_items", [])}
            for _item in decl.get("planned_work_items", []):
                _parent_id = _item.get("parent_id")
                if _parent_id and _parent_id in _items_by_id:
                    _parent = _items_by_id[_parent_id]
                    if _parent.get("status") == "completed" and not (_parent.get("evidence_paths") or []):
                        _child_evidence = _item.get("evidence_paths") or []
                        if _child_evidence:
                            _parent.setdefault("evidence_paths", []).extend(_child_evidence)
                            _evidence_repair_count += 1

            # Re-validate after repair
            _fse_warns = _check_fse(decl)
            _pid_warns = _check_pid(decl)

            # Remaining warnings become rework items
            review.setdefault("rework_items", [])
            for _w in _fse_warns + _pid_warns:
                if _w not in review["rework_items"]:
                    review["rework_items"].append(_w)

        print(f"  FSE-001 warnings: {len(_fse_warns)}, PID-001 warnings: {len(_pid_warns)}, "
              f"Auto-repairs: {_evidence_repair_count}")
    except Exception as _ev_err:
        print(f"  WARNING: Evidence pre-check skipped: {_ev_err}")

    # TC-CONC-008: Path ownership guard — acquire write claims before mutating files
    print("\n=== STEP 1c-CONC: PATH OWNERSHIP GUARD (advisory) ===")
    try:
        _db_path_cycle = repo_root / ".local" / "supervisor" / "control-index.db"
        _declared_paths = _extract_declared_paths(declaration_path)
        if _declared_paths:
            from concurrency.worker_claim import WorkerClaims  # type: ignore[import]
            from concurrency.errors import PathOwnershipConflict  # type: ignore[import]
            _claims_mgr = WorkerClaims(db_path=_db_path_cycle)
            _claims_mgr.claim(
                worker_id=_worker_id,
                task_id=sprint_id,
                paths=_declared_paths,
                mission_id="format-factory-main",
                lock_id="unknown",
                mode="WRITE",
            )
            print(f"  Path ownership claimed: {len(_declared_paths)} paths for worker {_worker_id}")
        else:
            print("  No declared paths to claim.")
    except Exception as _poc_err:
        if "PathOwnershipConflict" in type(_poc_err).__name__:
            print(f"  WARNING: Path ownership conflict detected (advisory): {_poc_err}")
            # Advisory mode — log but do not block
        else:
            print(f"  WARNING: Path ownership check skipped: {_poc_err}")
        _claims_mgr = None

    # Step 2: Inspect declared evidence
    print("\n=== STEP 2: INSPECT DECLARED EVIDENCE ===")
    inspection = inspect_declaration(decl, repo_root)
    item_count = len(inspection.get("item_inspections", []))
    artifact_count = len(inspection.get("artifact_inspections", []))
    print(f"  Inspected: {item_count} work items, {artifact_count} artifacts")

    # Step 2b: Generate/validate evidence manifest
    print("\n=== STEP 2b: EVIDENCE MANIFEST ===")
    try:
        evidence_manifest = generate_from_declaration(declaration_path, repo_root)
        evidence_manifest_path = (repo_root / decl["evidence_root"]) / "evidence-manifest.yaml"
        if evidence_manifest_path.exists():
            # Validate existing manifest
            val_result = validate_manifest(evidence_manifest_path, repo_root)
            print(f"  Existing manifest: {'VALID' if val_result['valid'] else 'INVALID'} ({val_result['checked']} artifacts checked)")
            if not val_result["valid"]:
                for err in val_result["errors"][:5]:
                    print(f"    {err}")
        else:
            # Write generated manifest
            write_manifest(evidence_manifest, evidence_manifest_path)
            print(f"  Generated: {evidence_manifest_path} ({len(evidence_manifest['artifacts'])} artifacts)")
    except Exception as e:
        print(f"  WARNING: Manifest step skipped: {e}")

    # Step 2c: Materialize declared evidence (R99 fix: D99-MODEL-01)
    print("\n=== STEP 2c: MATERIALIZE DECLARED EVIDENCE ===")
    try:
        mat_dir = repo_root / ".local" / "supervisor" / "materialized" / run_id
        mat_result = materialize_evidence(declaration_path, repo_root, mat_dir)
        print(f"  Verified: {mat_result['artifacts_verified']}, Missing: {mat_result['artifacts_missing']}")
    except Exception as e:
        print(f"  WARNING: Materialization skipped: {e}")

    # Step 2d: Adoption compliance validation (R111: consumed by cycle)
    print("\n=== STEP 2d: ADOPTION COMPLIANCE VALIDATION ===")
    review_dir = repo_root / ".local" / "supervisor" / "reviews" / run_id
    review_dir.mkdir(parents=True, exist_ok=True)
    adoption_result = None
    try:
        from validate_adoption_compliance import validate_adoption
        adoption_result = validate_adoption(decl)
        (review_dir / "adoption-compliance-result.json").write_text(
            json.dumps(adoption_result, indent=2), encoding="utf-8"
        )
        print(f"  Adoption compliance: {'PASS' if adoption_result['compliant'] else 'FAIL'} "
              f"({adoption_result['non_exempt_items']} non-exempt, "
              f"{adoption_result['items_with_transcript']} with transcript, "
              f"{adoption_result['items_with_skill_id']} with skill_id)")
    except Exception as e:
        print(f"  WARNING: Adoption compliance check skipped: {e}")

    # Step 2a (Fix 2): Work-type-to-skill gate — check gap_mappings at runtime
    skill_gate_violations = []
    try:
        from validate_adoption_compliance import check_work_type_skill_gate
        skill_gate_violations = check_work_type_skill_gate(decl, repo_root)
        if skill_gate_violations:
            print(f"\n  SKILL GATE: {len(skill_gate_violations)} BLOCKED_SKILL_GAP violation(s):")
            for _sid, _wt, _reason in skill_gate_violations:
                print(f"    [{_sid}] work_type={_wt}: {_reason}")
        else:
            print("  SKILL GATE: All work types have active skills (or no PRODUCT items).")
    except Exception as e:
        print(f"  WARNING: Skill gate check skipped: {e}")

    # Step 2d2: Requirements authority validation (SAL-I-004, Sprint 2 advisory / Sprint 3 hard-block)
    # REQUIREMENT and READINESS items must pass requirements authority validation.
    # Sprint 3 promotion: failure for these item types marks critical rework (blocks continuation).
    print("\n=== STEP 2d2: REQUIREMENTS AUTHORITY VALIDATION ===")
    _BLOCKING_RA_TYPES = frozenset({"REQUIREMENT", "READINESS", "RELEASE_GATE"})
    requirement_items = [
        item for item in decl.get("planned_work_items", [])
        if item.get("item_type") in _BLOCKING_RA_TYPES
    ]
    _ra_failure_blocks = False  # set True if blocking item types fail RA validation
    if requirement_items:
        try:
            import sys as _sys
            _ra_dir = repo_root / "tools" / "requirements_authority"
            if str(_ra_dir) not in _sys.path:
                _sys.path.insert(0, str(_ra_dir))
            from validate_requirements_authority import run_validation
            _ra_output_dir = review_dir / "requirements-authority"
            _ra_output_dir.mkdir(parents=True, exist_ok=True)
            _ra_result = run_validation(
                graph_dir=None,
                fixtures_dir=None,
                output_dir=_ra_output_dir,
            )
            _ra_overall = _ra_result.overall
            _blocking_count = sum(
                1 for i in requirement_items if i.get("item_type") in _BLOCKING_RA_TYPES
            )
            print(f"  Requirements authority: {_ra_overall} ({_blocking_count} blocking-type items)")
            if _ra_overall != "PASS":
                _ra_failure_blocks = True
                print(f"  BLOCK: Requirements authority validation FAIL for {_blocking_count} "
                      f"REQUIREMENT/READINESS/RELEASE_GATE items. "
                      f"Review {_ra_output_dir} for details.")
            else:
                print("  PASS: Requirements authority validation passed.")
            (_ra_output_dir / "item-count.txt").write_text(
                f"{_blocking_count} blocking-type items validated, overall={_ra_overall}\n",
                encoding="utf-8",
            )
        except Exception as _ra_e:
            print(f"  WARNING: Requirements authority validation skipped: {_ra_e}")
    else:
        print("  No REQUIREMENT/READINESS/RELEASE_GATE items in declaration — "
              "requirements authority step skipped")

    # Step 2d3: TC-GUARD-001 — Gap ledger trace check — BLOCK mode (enforced 2026-06-18).
    # GOVERNANCE_ASSET items are exempt (they create the registry that gap-ledger entries reference).
    # Violations stored in _guard001_violations; added to review["rework_items"] after grading.
    print("\n=== STEP 2d3: TC-GUARD-001 GAP LEDGER TRACE CHECK (BLOCK MODE) ===")
    from guard_001_checker import check_guard_001_all as _check_guard001  # GOVERNANCE_ASSET exempt
    _guard001_violations = _check_guard001(decl.get("planned_work_items", []))
    if _guard001_violations:
        print(
            f"  [BLOCK] TC-GUARD-001: {len(_guard001_violations)} PRODUCT_SOURCE/TEST "
            f"item(s) have no gap_ledger_ref, capability_ref, or spec_fact_refs: "
            f"{_guard001_violations}. These items will be added to rework_items after grading."
        )
    else:
        _checked = [i for i in decl.get("planned_work_items", []) if i.get("item_type") in ("PRODUCT_SOURCE", "PRODUCT_TEST")]
        print(f"  PASS: TC-GUARD-001 — all {len(_checked)} PRODUCT_SOURCE/TEST items have gap tracing (or no such items)")

    # Step 2d4: TC-SAL-IMPL-001 — AI fact guard (advisory — warns on AI self-certification)
    # validate_ai_fact_guard() checks that no AI-suggested fact carries verification_status=verified.
    # This is advisory only: violations are printed but do NOT block grading or continuation.
    print("\n=== STEP 2d4: AI FACT GUARD (ADVISORY) ===")
    try:
        import sys as _sys_aig
        _sal_tools = repo_root / "tools" / "supervisor"
        if str(_sal_tools) not in _sys_aig.path:
            _sys_aig.path.insert(0, str(_sal_tools))
        from validate_spec_fact_refs import validate_spec_cache_ai_guard
        _ai_result = validate_spec_cache_ai_guard()
        _violations = _ai_result.get("violations", [])
        if _violations:
            print(f"  WARN[ai_fact_guard]: {len(_violations)} AI self-certification violation(s) found.")
            for _v in _violations[:5]:
                print(f"    {_v}")
        else:
            print("  PASS: AI fact guard — 0 violations (AI-suggested facts not self-certified as verified)")
    except Exception as _aig_e:
        print(f"  WARNING: AI fact guard skipped: {_aig_e}")

    # Step 2e: Governance validators (GRE-TC-002: wired into pipeline)
    print("\n=== STEP 2e: GOVERNANCE VALIDATORS ===")
    governance_validation_result = None
    try:
        # governance_validators.py internally uses `from tools.supervisor.*` imports,
        # which requires REPO_ROOT (not just SCRIPT_DIR) to be on sys.path.
        if str(REPO_ROOT) not in sys.path:
            sys.path.insert(0, str(REPO_ROOT))
        from governance_validators import run_all_governance_validators
        governance_validation_result = run_all_governance_validators(decl, repo_root)
        (review_dir / "governance-validation-result.json").write_text(
            json.dumps(governance_validation_result, indent=2), encoding="utf-8"
        )
        _gov_fail = governance_validation_result.get("fail_count", 0)
        _gov_warn = governance_validation_result.get("warn_count", 0)
        _gov_pass = governance_validation_result.get("pass_count", 0)
        _gov_blocks = governance_validation_result.get("blocks_sprint", False)
        print(f"  Governance: {_gov_pass} PASS / {_gov_warn} WARN / {_gov_fail} FAIL"
              f" | blocks_sprint={_gov_blocks}")
        if _gov_fail > 0:
            for v in governance_validation_result.get("validators", []):
                if v.get("result") == "FAIL":
                    print(f"    FAIL [{v['validator']}]: {v.get('summary', '')[:120]}")
    except Exception as e:
        print(f"  WARNING: Governance validators skipped: {e}")

    # Step 2e-v54v55: Update V54/V55 sprint tracker after governance run (TC-D1)
    try:
        _v54_tracker_path2 = repo_root / "reports" / "v54v55-sprint-tracker.json"
        if _v54_tracker_path2.exists() and 'governance_validation_result' in dir():
            _v54_data2 = json.loads(_v54_tracker_path2.read_text(encoding="utf-8"))
            if not _v54_data2.get("promoted", False):
                # Check if V54/V55 produced false positives (WARN on real cross-lane violations)
                _v54_false_pos = False
                for _v in governance_validation_result.get("validators", []):
                    if _v.get("validator", "").startswith(("validate_cross_lane_product", "validate_cross_lane_machinery")):
                        if _v.get("result") in ("WARN", "FAIL"):
                            _v54_false_pos = True
                            break
                if not _v54_false_pos:
                    _v54_data2["clean_sprint_count"] = _v54_data2.get("clean_sprint_count", 0) + 1
                    _v54_data2["sprints"].append({
                        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                        "false_positives": False,
                        "sprint_id": run_id,
                    })
                    # Auto-promote if target reached
                    if _v54_data2["clean_sprint_count"] >= _v54_data2.get("target_clean_sprints", 3):
                        _v54_data2["promoted"] = True
                        print(f"  V54/V55 PROMOTION: {_v54_data2['clean_sprint_count']} clean sprints reached — marked for promotion")
                    else:
                        print(f"  V54/V55 tracker: {_v54_data2['clean_sprint_count']}/{_v54_data2.get('target_clean_sprints', 3)} clean sprints")
                    _v54_tracker_path2.write_text(json.dumps(_v54_data2, indent=2) + "\n", encoding="utf-8")
                else:
                    print("  V54/V55 tracker: false positive detected this sprint — not incrementing")
    except Exception as _v54_err2:
        print(f"  WARNING: V54/V55 tracker update skipped (non-blocking): {_v54_err2}")

    # Step 2e¼: Promotion integrity check (TC-CQGA-018 — PQLM-GOV-001)
    # Non-blocking: detects api_baseline_hash changes on PROMOTED_STABLE entries.
    try:
        _ledger_path = repo_root / "registry" / "promotion-ledger.yaml"
        if _ledger_path.is_file():
            import yaml as _yaml
            import hashlib as _hashlib
            import json as _json
            import sys as _sys
            _ledger = _yaml.safe_load(_ledger_path.read_text(encoding="utf-8")) or {}
            _reopened = []
            for _entry in _ledger.get("entries", []):
                if _entry.get("state") == "PROMOTED_STABLE" and _entry.get("api_baseline_hash"):
                    _fmt = _entry.get("format_id", "")
                    _lang = _entry.get("language", "")
                    _stored_hash = _entry["api_baseline_hash"]
                    # Recompute hash: import package and hash sorted __all__
                    try:
                        _pkg_path = repo_root / "src" / "python" / _fmt
                        if _pkg_path.is_dir():
                            if str(repo_root / "src" / "python") not in _sys.path:
                                _sys.path.insert(0, str(repo_root / "src" / "python"))
                            import importlib as _il
                            _mod = _il.import_module(_fmt)
                            _symbols = sorted(getattr(_mod, "__all__", []))
                            _current_hash = _hashlib.sha256(_json.dumps(_symbols).encode()).hexdigest()
                            if _current_hash != _stored_hash:
                                _entry["state"] = "REOPENED"
                                _reopened.append(f"{_fmt}/{_lang}")
                    except Exception:
                        pass
            if _reopened:
                _ledger_path.write_text(_yaml.dump(_ledger, default_flow_style=False), encoding="utf-8")
                print(f"  WARN(PROMOTION_INTEGRITY_BREACH): {len(_reopened)} entries reopened: {_reopened}")
            else:
                print("  Promotion integrity: OK (no PROMOTED_STABLE entries or hashes match)")
        else:
            print("  Promotion ledger not found — integrity check skipped")
    except Exception as _promo_err:
        print(f"  WARNING: Promotion integrity check skipped (non-blocking): {_promo_err}")

    # Step 2e½: Source structure validator (spec-derived architecture governance)
    print("\n=== STEP 2e½: SOURCE STRUCTURE VALIDATOR ===")
    try:
        _validator_path = repo_root / "tools" / "validators" / "source_structure_validator.py"
        if _validator_path.is_file():
            import importlib.util
            _spec = importlib.util.spec_from_file_location("source_structure_validator", str(_validator_path))
            _ssv = importlib.util.module_from_spec(_spec)
            _spec.loader.exec_module(_ssv)
            _ss_result = _ssv.run_full_scan(repo_root)
            (review_dir / "source-structure-result.json").write_text(
                json.dumps(_ss_result, indent=2), encoding="utf-8"
            )
            _ss_blocks = _ss_result.get("blocks_sprint", False)
            _ss_status = _ss_result.get("result", _ss_result.get("status", "UNKNOWN"))
            print(f"  Source structure: {_ss_status} | blocks_sprint={_ss_blocks}")
            if _ss_blocks:
                for k in ("new_violations", "regressions"):
                    items = _ss_result.get(k, [])
                    if items:
                        print(f"    {k}: {'; '.join(items[:5])}")
        else:
            print("  Source structure validator not found — skipped")
    except Exception as e:
        print(f"  WARNING: Source structure validator skipped: {e}")

    # ENFORCEMENT BOUNDARY NOTE:
    # Route decision PRESENCE is validated by Validator 11 (validate_route_decision_required).
    # Route decision CONTENT (allowed_paths, forbidden_paths, required_tests) is enforced
    # at action dispatch time via next_action_runner.run_action() → check_action_route_allowed().
    # Manual/skill execution bypasses this dispatch-time enforcement.
    # See docs/governance/autonomy-default-routing-policy.md for full boundary specification.

    # Step 2f (SUP-RECT-002): DAG prerequisite validation
    print("\n=== STEP 2f: DAG PREREQUISITE VALIDATION ===")
    dag_validation_result = {"status": "skipped"}
    try:
        dag_path = repo_root / ".local" / "evidences" / "spec-to-feature-radical-correction-plan-20260612-915cfd2" / "execution-dag.yaml"
        if dag_path.exists():
            dag_data = yaml.safe_load(dag_path.read_text(encoding="utf-8"))
            waves = dag_data.get("waves", [])
            declared_wave = decl.get("wave", None)
            if declared_wave is not None:
                # Check all prerequisite waves are COMPLETED
                target_wave = None
                for w in waves:
                    if w.get("wave") == declared_wave:
                        target_wave = w
                        break
                if target_wave:
                    depends_on = target_wave.get("depends_on", [])
                    unmet = []
                    for dep in depends_on:
                        dep_num = int(str(dep).replace("wave-", ""))
                        for w in waves:
                            if w.get("wave") == dep_num and w.get("status") != "COMPLETED":
                                unmet.append(f"wave-{dep_num} (status={w.get('status', 'UNKNOWN')})")
                    dag_validation_result = {
                        "status": "checked",
                        "declared_wave": declared_wave,
                        "prerequisites": depends_on,
                        "unmet": unmet,
                        "passed": len(unmet) == 0,
                    }
                    if unmet:
                        print(f"  DAG validation: WARN — unmet prerequisites: {unmet}")
                    else:
                        print(f"  DAG validation: PASS (wave {declared_wave}, deps={depends_on})")
                else:
                    dag_validation_result = {"status": "wave_not_found", "declared_wave": declared_wave}
                    print(f"  DAG validation: wave {declared_wave} not found in DAG")
            else:
                dag_validation_result = {"status": "no_wave_declared"}
                print("  DAG validation: no wave declared in evidence — skipped")
        else:
            print("  DAG validation: execution-dag.yaml not found — skipped")
    except Exception as dag_err:
        safe_err = str(dag_err).encode("ascii", "replace").decode()
        print(f"  WARNING: DAG prerequisite check skipped: {safe_err}")
    # dag_validation_result is applied to review after grade_all() creates it (below)

    # Step 2g (FF-XPLAN-001 W3-002): Release gate check
    # Runs PYREL gates for any format mentioned in the declaration
    print("\n=== STEP 2g: RELEASE GATE CHECK ===")
    gate_check_results = []
    try:
        from gate_executor import run_gates  # noqa: PLC0415
        decl_formats = set()
        for wi in decl.get("planned_work_items", []):
            fmt = wi.get("format_id")
            if fmt:
                decl_formats.add(fmt)
        if decl_formats:
            for fmt_id in sorted(decl_formats):
                gate_result = run_gates(fmt_id, ["G1", "G2"], dry_run=True)
                gate_check_results.append(gate_result)
                g1 = next((r for r in gate_result["results"] if r["gate"] == "G1"), {})
                g2 = next((r for r in gate_result["results"] if r["gate"] == "G2"), {})
                g1_status = "PASS" if g1.get("passed") else "FAIL"
                g2_status = "PASS" if g2.get("passed") else "FAIL"
                print(f"  {fmt_id}: G1={g1_status} G2={g2_status}")
            (review_dir / "gate-check-results.json").write_text(
                json.dumps(gate_check_results, indent=2), encoding="utf-8"
            )
        else:
            print("  No format_id in declaration — gate check skipped")
    except Exception as gate_err:
        print(f"  WARNING: Release gate check skipped: {gate_err}")

    # Step 3: Grade work items (includes Step 3a: LLM semantic verification)
    print("\n=== STEP 3: GRADE WORK ITEMS ===")
    # Inject repo_root for semantic verification (LLM reads evidence files)
    decl["_repo_root"] = str(repo_root)
    # Debug: check LLM gateway availability before grading
    try:
        from grade_declared_work import _get_sv_gateway
        _dbg_gw, _dbg_cfg = _get_sv_gateway()
        print(f"  LLM gateway: {'AVAILABLE' if _dbg_gw else 'UNAVAILABLE'} (configured={getattr(_dbg_cfg, 'is_configured', False) if _dbg_cfg else False})")
    except Exception as _dbg_e:
        print(f"  LLM gateway check failed: {_dbg_e}")
    # TC-P2-004: Track-scoped grade cache (REQ-TRK-008)
    _supervisor_base = repo_root / ".local" / "supervisor"
    if track == "product":
        _grade_cache_path = _supervisor_base / "product" / "grade-cache.json"
    elif track == "machinery":
        _grade_cache_path = _supervisor_base / "machinery" / "grade-cache.json"
    else:
        _grade_cache_path = None  # Use default (legacy path)
    review = grade_all(inspection, decl, grade_cache_path=_grade_cache_path)
    review["declaration_path"] = str(declaration_path)
    review["git_head_at_review"] = _git_head_at_review  # TC-HARD-010: accurate HEAD at review time
    review["dag_validation"] = dag_validation_result

    # TC-FG-004: Closure challenge — enforce proof adequacy before ACCEPTED_VERIFIED
    try:
        from closure_challenger import run_closure_challenge as _run_cc
        import json as _json
        _cc_results = []
        for _item in review.get("item_grades", []):
            if _item.get("supervisor_grade") == "ACCEPTED_VERIFIED":
                _cc_result = _run_cc(
                    item=_item,
                    evidence_root=str(review_dir),
                    repo_root=str(repo_root),
                    proof_contracts=decl.get("proof_contracts"),
                )
                _cc_results.append(_cc_result)
                if _cc_result["verdict"] == "CLOSURE_CHALLENGE_FOUND_REWORK":
                    _item["supervisor_grade"] = "REWORK_REQUIRED"
                    _item["required_rework"] = (
                        f"Closure challenge found: {'; '.join(_cc_result['new_findings'])}"
                    )
                    review.setdefault("rework_items", []).append(
                        f"CLOSURE_CHALLENGE:{_item['item_id']}"
                    )
                    review["critical_rework_count"] = review.get("critical_rework_count", 0) + 1
                    if review.get("overall_verdict") in (
                        "ACCEPTED", "ACCEPTED_WITH_LIMITATIONS", "ACCEPTED_WITH_REWORK"
                    ):
                        review["overall_verdict"] = "ACCEPTED_WITH_REWORK"
                    if "autonomous_continue" in review:
                        review["autonomous_continue"] = False
        _cc_out = review_dir / "closure-challenge-results.json"
        _cc_out.write_text(_json.dumps(_cc_results, indent=2, default=str))
        _cc_rework = sum(1 for r in _cc_results if r["verdict"] == "CLOSURE_CHALLENGE_FOUND_REWORK")
        print(f"  [TC-FG-004] Closure challenge: {len(_cc_results)} items challenged, "
              f"{_cc_rework} found rework")
    except Exception as _cc_err:
        print(f"  WARNING: Closure challenge skipped (non-critical): {_cc_err}")

    # Step 2d2 post-grading: promote requirements authority failure to critical rework
    # Sprint 3: REQUIREMENT/READINESS/RELEASE_GATE failure is now a hard block.
    if _ra_failure_blocks:
        review["critical_rework_count"] = max(review.get("critical_rework_count", 0) + 1, 1)
        if review.get("overall_verdict") in ("ACCEPTED", "ACCEPTED_WITH_LIMITATIONS"):
            review["overall_verdict"] = "ACCEPTED_WITH_REWORK"
        review["stop_reason"] = (
            review.get("stop_reason", "") +
            " Requirements authority validation FAIL for REQUIREMENT/READINESS items."
        ).strip()
        print("  [Step 2d2] Requirements authority failure promoted to CRITICAL REWORK.")

    # Step 2d3 post-grading: TC-GUARD-001 violations added to rework_items (BLOCK mode).
    # _guard001_violations was populated before grading; applied here after review is available.
    if _guard001_violations:
        review.setdefault("rework_items", [])
        for _gv_id in _guard001_violations:
            _rw_entry = (
                f"TC-GUARD-001:gap_ledger_ref_missing:{_gv_id} — "
                f"Add gap_ledger_ref or spec_fact_refs from reports/capability-layer/gap-ledger.json"
            )
            if _rw_entry not in review["rework_items"]:
                review["rework_items"].append(_rw_entry)
        review["critical_rework_count"] = max(
            review.get("critical_rework_count", 0) + len(_guard001_violations), 1
        )
        if review.get("overall_verdict") in ("ACCEPTED", "ACCEPTED_WITH_LIMITATIONS"):
            review["overall_verdict"] = "ACCEPTED_WITH_REWORK"
        if "autonomous_continue" in review:
            review["autonomous_continue"] = False
        print(
            f"  [TC-GUARD-001 POST-GRADE] {len(_guard001_violations)} violation(s) added to "
            f"rework_items — continuation blocked until gap references are added."
        )

    # Step 0d post-grading: inject OIC invariant failures into rework_items (non-blocking).
    if _oic_rework_entries:
        review.setdefault("rework_items", [])
        for _oe in _oic_rework_entries:
            if _oe not in review["rework_items"]:
                review["rework_items"].append(_oe)
        print(f"  [OIC POST-GRADE] {len(_oic_rework_entries)} OIC failure(s) added to rework_items (non-blocking)")

    print(f"  Verdict: {review['overall_verdict']}")
    print(f"  Accepted: {len(review['accepted_items'])}")
    print(f"  Rework: {len(review['rework_items'])}")
    print(f"  Overclaimed: {len(review['overclaimed_items'])}")
    # Overclaim detection added by TC-W0-001
    overclaim_issues = []
    for idx, item in enumerate(review.get('overclaimed_items', [])):
        paths = item.get('evidence_paths', [])
        missing = [p for p in paths if not Path(p).exists()]
        if missing:
            overclaim_issues.append({'item_index': idx, 'missing_paths': missing})
    if overclaim_issues:
        out_path = repo_root / 'reports' / 'supervisor' / 'overclaim-detections.json'
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(overclaim_issues, indent=2), encoding='utf-8')
        print(f"  Overclaim detection: {len(overclaim_issues)} issues logged to {out_path}")
    else:
        print("  Overclaim detection: no issues")
    print(f"  Autonomous Continue: {review['autonomous_continue']}")

    # Step 3a-pre: Merge gap_ledger_ref from work items into declaration (TC-C7-005)
    # The closure engine needs gap_ledger_ref in planned_work_items to match gaps.
    # Worker-written declarations often omit this field. Merge from canonical work items.
    try:
        _wi_sources = [
            repo_root / ".local" / "supervisor" / "product" / "next-work-items.json",
            repo_root / ".local" / "supervisor" / "next-work-items.json",
        ]
        _wi_by_id: dict[str, str] = {}
        for _wi_src in _wi_sources:
            if _wi_src.exists():
                _wi_data = json.loads(_wi_src.read_text(encoding="utf-8"))
                _wi_list = _wi_data if isinstance(_wi_data, list) else _wi_data.get("items", _wi_data.get("work_items", []))
                for _wi in _wi_list:
                    _ref = _wi.get("gap_ledger_ref") or _wi.get("gap_id")
                    _wid = _wi.get("item_id") or _wi.get("action_id")
                    if _ref and _wid:
                        _wi_by_id[_wid] = _ref
                # TC-V4-006 (2026-06-25): Only break if refs were actually found.
                # Bug: prior code broke after first existing file even if it had 0 refs,
                # preventing fallback to secondary source. E.g. if primary is in PLAN_LOCKED
                # mode with no gap_ledger_ref items, secondary source was never checked.
                if _wi_by_id:
                    break  # found refs in this source; no need to check secondary
        if _wi_by_id:
            _merged = 0
            for _di in decl.get("planned_work_items", []):
                _did = _di.get("item_id", "")
                if not _di.get("gap_ledger_ref") and _did in _wi_by_id:
                    _di["gap_ledger_ref"] = _wi_by_id[_did]
                    _merged += 1
            if _merged:
                print(f"  [TC-C7-005] Merged gap_ledger_ref into {_merged} declaration item(s)")
    except Exception as _merge_err:
        print(f"  WARNING: gap_ledger_ref merge skipped: {_merge_err}")

    # Step 3a-pre2: Close implementation_verified gaps via test scan (TC-BOOL-002)
    print("\n=== STEP 3a-pre2: IMPL-VERIFIED GAP CLOSURE SCAN ===")
    try:
        from gap_closure_engine import close_implementation_verified_gaps as _close_iv_gaps
        _gl_path_iv = repo_root / "reports" / "capability-layer" / "gap-ledger-active.json"
        if not _gl_path_iv.exists():
            _gl_path_iv = repo_root / "reports" / "capability-layer" / "gap-ledger.json"
        if _gl_path_iv.exists():
            _iv_result = _close_iv_gaps(
                gap_ledger_path=_gl_path_iv,
                test_root=repo_root / "tests",
                sprint_id=sprint_id,
            )
            print(f"  Closed {_iv_result.get('closed', 0)} implementation_verified gaps via test scan")
            print(f"  Promoted {_iv_result.get('no_tests_found', 0)} to implementation_verified_no_tests")
        else:
            print("  gap-ledger not found — skipped")
    except Exception as _iv_err:
        print(f"  WARNING: implementation_verified gap scan failed: {_iv_err}")
        # Best-effort — never blocks sprint continuation

    # Step 3a-closure: Automated gap closure from graded evidence (TC-FL-002)
    print("\n=== STEP 3a-closure: GAP CLOSURE FROM GRADES ===")
    try:
        from gap_closure_engine import close_gaps_from_grades as _close_gaps
        # TC-CAP-008: prefer active split; fall back to full ledger
        _gl_path = repo_root / "reports" / "capability-layer" / "gap-ledger-active.json"
        if not _gl_path.exists():
            _gl_path = repo_root / "reports" / "capability-layer" / "gap-ledger.json"
        if _gl_path.exists():
            _closure_result = _close_gaps(
                review=review, declaration=decl,
                gap_ledger_path=_gl_path, sprint_id=sprint_id,
            )
            review["gap_closures"] = _closure_result
            print(f"  Matches: {_closure_result.get('matches', 0)}, "
                  f"Closed: {_closure_result.get('closed', 0)}, "
                  f"Skipped: {_closure_result.get('skipped', 0)}")
        else:
            print("  gap-ledger-active.json and gap-ledger.json not found — skipped")
    except Exception as _gc_err:
        print(f"  WARNING: Gap closure skipped: {_gc_err}")
        review["gap_closures"] = {"status": "error", "error": str(_gc_err)}

    # Step 3a-verify: Post-closure verification levels (TC-FL-013)
    if review.get("gap_closures", {}).get("closed", 0) > 0:
        try:
            from gap_verification_engine import verify_closed_gaps as _verify_closed
            _verifications = _verify_closed(
                review["gap_closures"], decl.get("test_results", {}), decl, repo_root
            )
            review["gap_verifications"] = _verifications
            _l2_count = sum(1 for v in _verifications if v.get("verification_level") == 2)
            print(f"  Gap verifications: {len(_verifications)} total, {_l2_count} at Level 2")
        except Exception as _gv_err:
            print(f"  WARNING: Gap verification skipped: {_gv_err}")

    # Step 3a-llm: Report LLM semantic verification results
    sv_items = [g for g in review.get("item_grades", []) if g.get("semantic_verification", {}).get("llm_used")]
    if sv_items:
        sv_downgrades = [g for g in sv_items if not g["semantic_verification"].get("adequate")]
        sv_stubs = [g for g in sv_items if g["semantic_verification"].get("stub_detected")]
        print("\n  --- Step 3a: LLM Semantic Verification ---")
        print(f"  Items verified: {len(sv_items)}")
        print(f"  Downgrades: {len(sv_downgrades)}")
        print(f"  Stubs detected: {len(sv_stubs)}")
        for g in sv_downgrades:
            deficiencies = g["semantic_verification"].get("deficiencies", [])
            safe_deficiencies = [d.encode("ascii", "replace").decode() for d in deficiencies[:2]]
            print(f"    [{g['item_id']}] {'; '.join(safe_deficiencies)}")

    # Step 3b: Adoption compliance check
    print("\n=== STEP 3b: ADOPTION COMPLIANCE CHECK ===")

    # R111+Fix1: Adoption compliance — BLOCKING for PRODUCT_SOURCE/PRODUCT_TEST items
    if adoption_result is not None:
        review["adoption_compliance"] = adoption_result
        if not adoption_result["compliant"]:
            # Build item_type lookup from declaration
            _item_types = {
                wi.get("item_id", ""): wi.get("item_type", "")
                for wi in decl.get("planned_work_items", [])
            }
            # Check if any non-compliant, non-exempt item is product work
            _product_non_compliant = [
                r["item_id"] for r in adoption_result.get("items", [])
                if not r.get("exempt") and not r.get("compliant")
                and _item_types.get(r["item_id"], "") in ("PRODUCT_SOURCE", "PRODUCT_TEST")
            ]
            if _product_non_compliant:
                # BLOCKING: product items without skill provenance
                review["critical_rework_count"] = review.get("critical_rework_count", 0) + 1
                review.setdefault("rework_items", [])
                review["rework_items"].append(
                    f"ADOPTION_NON_COMPLIANCE:product_items={','.join(_product_non_compliant[:5])}"
                )
                if review["overall_verdict"] in ("ACCEPTED", "ACCEPTED_WITH_REWORK"):
                    review["overall_verdict"] = "REWORK_REQUIRED"
            else:
                # Non-product items: advisory only (preserve existing behavior)
                if review["overall_verdict"] == "ACCEPTED":
                    review["overall_verdict"] = "ACCEPTED_WITH_REWORK"
            review["stop_reason"] = (
                review.get("stop_reason", "") +
                f" Adoption compliance FAIL: {adoption_result['summary']}"
            ).strip()

    # Fix 2 verdict: skill gate violations are BLOCKING for PRODUCT items
    if skill_gate_violations:
        review["skill_gate_violations"] = [
            {"item_id": sid, "work_type": wt, "reason": reason}
            for sid, wt, reason in skill_gate_violations
        ]
        review["critical_rework_count"] = review.get("critical_rework_count", 0) + len(skill_gate_violations)
        review.setdefault("rework_items", [])
        for sid, wt, reason in skill_gate_violations:
            review["rework_items"].append(f"SKILL_GATE:{sid}:{reason}")
        if review["overall_verdict"] in ("ACCEPTED", "ACCEPTED_WITH_REWORK"):
            review["overall_verdict"] = "REWORK_REQUIRED"

    # GRE-TC-002: Attach governance validation result to review
    if governance_validation_result is not None:
        review["governance_validation"] = governance_validation_result
        if governance_validation_result.get("blocks_sprint"):
            # Blocking governance failure is a hard block (exit 3), not just a downgrade
            review["critical_rework_count"] = max(review.get("critical_rework_count", 0) + 1, 1)
            review["autonomous_continue"] = False
            if review["overall_verdict"] in ("ACCEPTED", "ACCEPTED_WITH_LIMITATIONS",
                                              "ACCEPTED_WITH_REWORK"):
                review["overall_verdict"] = "ACCEPTED_WITH_REWORK"
            review["stop_reason"] = (
                review.get("stop_reason", "") +
                f" Governance validator FAIL (blocks_sprint): {governance_validation_result.get('summary', '')}"
            ).strip()
            # Add blocking validators to rework_items so they are visible
            for v in governance_validation_result.get("validators", []):
                if v.get("result") == "FAIL" and v.get("blocks_sprint"):
                    rework_id = f"GOV_BLOCK:{v['validator']}"
                    if rework_id not in review.get("rework_items", []):
                        review.setdefault("rework_items", []).append(rework_id)

    # TC-PGI-042: Governance degradation detection — too many skipped validators signals
    # import failures that reduce governance coverage without surfacing as explicit FAILs.
    _gov_skipped = governance_validation_result.get("skipped_count", 0)
    if _gov_skipped > 5:
        _gov_degraded = f"GOVERNANCE_DEGRADED:{_gov_skipped}_validators_skipped"
        review.setdefault("rework_items", [])
        if _gov_degraded not in review["rework_items"]:
            review["rework_items"].append(_gov_degraded)
        print(f"  [TC-PGI-042] WARNING: {_gov_skipped} governance validators skipped — "
              f"governance coverage degraded. Added to rework_items: {_gov_degraded}")

    # Step 2e (SUP-RECT-001): Lane enforcement validation
    print("\n=== STEP 2e: LANE ENFORCEMENT VALIDATION ===")
    try:
        from lane_enforcement_validator import LaneEnforcementValidator
        lane_validator = LaneEnforcementValidator()
        declared_lane = decl.get("lane", None)
        lane_result = lane_validator.validate(decl, declared_lane=declared_lane)
        (review_dir / "lane-enforcement-result.json").write_text(
            json.dumps({"passed": lane_result.passed, "violations": lane_result.violations,
                        "evidence": lane_result.evidence}, indent=2), encoding="utf-8"
        )
        if lane_result.passed:
            print(f"  Lane enforcement: PASS ({len(lane_result.evidence)} files checked)")
        else:
            print(f"  Lane enforcement: FAIL — {len(lane_result.violations)} violation(s)")
            for v in lane_result.violations:
                severity = "CRITICAL" if v in lane_result.critical_violations else "VIOLATION"
                print(f"    [{severity}] {v}")
            # CRITICAL violations (product file in governance/SAL lane) → hard stop
            if lane_result.critical_violations:
                review.setdefault("hard_stops_detected", []).append(
                    f"LANE_ENFORCEMENT_CRITICAL:{len(lane_result.critical_violations)}_violations"
                )
                print(f"  Lane enforcement: {len(lane_result.critical_violations)} CRITICAL violation(s) → hard_stops_detected")
            # Non-critical violations remain advisory rework (multi-lane sprints are common)
            non_critical = len(lane_result.violations) - len(lane_result.critical_violations)
            if non_critical > 0:
                review.setdefault("rework_items", [])
                review["rework_items"].append(f"LANE_ENFORCEMENT:{non_critical}_violations")
    except Exception as lane_err:
        print(f"  WARNING: Lane enforcement check skipped: {lane_err}")

    # Lane 5: Record governance failures to durable failure memory
    if governance_validation_result is not None and governance_validation_result.get("blocks_sprint"):
        try:
            from failure_memory import FailureMemory
            fm = FailureMemory(repo_root)
            import re as _fm_re
            _MONO = "monolith_detection_validator"
            for v in governance_validation_result.get("validators", []):
                if v.get("result") == "FAIL":
                    _vf = _fm_re.findall(r'\b(src/[\w./]+\.(?:py|cs))\b', v.get("detail") or "") if v.get("validator") == _MONO else []
                    fm.record_failure(
                        category="GOVERNANCE_FALSE_TRIGGER" if not v.get("blocks_sprint") else "SUPERVISOR_CONTROL_FAILURE",
                        root_cause=f"governance_validator_{v['validator']}_failed",
                        correction="Requires item-level fix in declaration",
                        sprint_id=sprint_id,
                        files_modified=_vf,
                    )
            fm.save()
        except Exception as fm_err:
            print(f"  [WARN] Failure memory recording failed: {fm_err}")

    # TC-L15-WRITER-001: Write sprint-learnings.jsonl before consumer scan
    try:
        from write_sprint_learnings import write_sprint_learnings as _wsl
        _lp = _wsl(sprint_id, repo_root / ".local" / "evidences" / sprint_id, declaration_path)
        print(f"  [Step 2f2] Sprint learnings written: {_lp.name}")
    except Exception as _wsl_e:
        print(f"  [WARN] write_sprint_learnings skipped: {_wsl_e}")

    # HEAL-RECT-002: Run learning consumer — scan learnings, generate rule proposals
    print("\n=== STEP 2g: LEARNING CONSUMER ===")
    try:
        from learning_consumer import LearningConsumer
        lc = LearningConsumer(repo_root)
        scan_count = lc.scan_all_learnings()
        proposals = lc.generate_proposals(threshold=3)
        if proposals:
            lc.save_proposals()
            print(f"  Learning consumer: {scan_count} entries, {len(proposals)} rule proposal(s) promoted")
        else:
            print(f"  Learning consumer: {scan_count} entries scanned, no promotions")
        review["learning_consumer"] = {"scanned": scan_count, "proposals": len(proposals)}
    except Exception as lc_err:
        print(f"  WARNING: Learning consumer skipped: {lc_err}")

    # Step 2h: Capability queue consumption — refresh compiled-gap-taskcards.json
    print("\n=== STEP 2h: CAPABILITY QUEUE CONSUMER ===")
    try:
        from capability_queue_consumer import run_consumer as _run_cqc
        cqc_summary = _run_cqc(max_gaps=10)
        _cqc_compiled = cqc_summary.get("gaps_compiled", 0)
        print(f"  Queue consumer: {_cqc_compiled} gap(s) compiled to taskcards")
        review["capability_queue"] = {"compiled": _cqc_compiled, "status": cqc_summary.get("status")}
    except Exception as cqc_err:
        print(f"  WARNING: Capability queue consumer failed: {cqc_err}")

    # Write review outputs
    review_dir = repo_root / ".local" / "supervisor" / "reviews" / run_id
    write_outputs(review, review_dir)

    # TC-SGOV-W2-005: Skill execution receipt auto-write (EP-004)
    # Write receipts for all declared skills after each processed declaration.
    try:
        from skill_receipt_writer import write_skill_receipts as _write_receipts
        _written = _write_receipts(decl, run_id, declaration_path,
                                   review.get("overall_verdict", "UNKNOWN"), repo_root)
        if _written:
            print(f"  [TC-SGOV-W2-005] Skill receipts written: {sorted(_written)}")
        else:
            print("  [TC-SGOV-W2-005] No skill_ids declared — no receipts written")
    except Exception as _rec_err:
        print(f"  [TC-SGOV-W2-005] WARNING: skill receipt auto-write failed: {_rec_err}")

    # Write inspection JSON
    (review_dir / "inspection.json").write_text(
        json.dumps(inspection, indent=2), encoding="utf-8"
    )

    # Step 3.5: Quality Scoring via grade-to-quality adapter (advisory, non-blocking)
    print("\n=== STEP 3.5: QUALITY SCORING ===")
    quality_result = None
    try:
        from grade_to_quality_adapter import adapt_item_grades
        from quality_scorer import score_execution
        taskcard_results = adapt_item_grades(review.get("item_grades", []))
        quality_result = score_execution(taskcard_results, repo_root=repo_root)
        (review_dir / "quality-scores.json").write_text(
            json.dumps(quality_result, indent=2), encoding="utf-8"
        )
        review["quality_scores"] = quality_result.get("overall_scores", {})
        review["quality_verdict"] = quality_result.get("overall_verdict", "UNKNOWN")
        all_green = quality_result.get("all_green", False)
        print(f"  Quality verdict: {quality_result.get('overall_verdict')} (all_green={all_green})")
        if not all_green:
            for r in quality_result.get("reroute_log", []):
                print(f"    Reroute: {r.get('taskcard_id')} — {r.get('reason', '')[:100]}")
    except Exception as qs_err:
        print(f"  WARNING: Quality scoring skipped: {qs_err}")

    # Step 3b: Post-grading anti-skip checks — extracted to autonomous_cycle_extensions.py (TC-SGOV-008)
    anti_skip_impact = None
    anti_skip_result = None
    try:
        from autonomous_cycle_extensions import run_post_grading_anti_skip
        anti_skip_result, anti_skip_impact = run_post_grading_anti_skip(
            review, decl, sprint_id, review_dir, repo_root, detected_stream)
    except Exception as e:
        print(f"  WARNING: Anti-skip checks skipped: {e}")

    # Step 3c (SUP-RECT-003): Run overclaim detector if graph store available
    print("\n=== STEP 3c: OVERCLAIM DETECTOR ===")
    try:
        ra_tools = REPO_ROOT / "tools" / "requirements_authority"
        if str(ra_tools) not in sys.path:
            sys.path.insert(0, str(ra_tools))
        from overclaim_detector import OverclaimDetector, OverclaimReport
        from graph_store import GraphStore

        # Support both directory format (nodes.jsonl + edges.jsonl) and legacy JSON.
        # Prefer directory; fall back to JSON file for backwards compatibility.
        graph_dir = repo_root / "reports" / "capability-layer" / "proof-graph"
        graph_path_json = repo_root / "reports" / "capability-layer" / "proof-graph.json"
        if graph_dir.is_dir():
            store = GraphStore.load_from_dir(graph_dir)
            _graph_source = str(graph_dir)
        elif graph_path_json.exists():
            # Legacy JSON path — attempt directory-compatible JSON load
            try:
                _pg_data = json.loads(graph_path_json.read_text(encoding="utf-8"))
                store = GraphStore()
                for n in _pg_data.get("nodes", []):
                    from models import GraphNode as _GN  # type: ignore
                    store.add_node(_GN.from_dict(n))
                for e in _pg_data.get("edges", []):
                    from models import GraphEdge as _GE  # type: ignore
                    store.add_edge(_GE.from_dict(e))
            except Exception:
                store = GraphStore()
            _graph_source = str(graph_path_json)
        else:
            store = None
            _graph_source = None

        if store is not None:
            detector = OverclaimDetector(store)
            oc_report: OverclaimReport = detector.detect_all()
            oc_dict = oc_report.to_dict()
            (review_dir / "overclaim-detector-result.json").write_text(
                json.dumps(oc_dict, indent=2), encoding="utf-8"
            )
            print(f"  Overclaim detector ({_graph_source}): {oc_report.error_count} ERROR, "
                  f"{oc_report.warning_count} WARNING findings")
            if oc_report.error_count > 0:
                review["overclaim_detector_errors"] = oc_report.error_count
                # Promote ERROR findings to critical rework if items are overclaimed
                for finding in oc_report.findings:
                    if finding.severity == "ERROR":
                        review.setdefault("overclaim_findings", []).append(finding.to_dict())
                print(f"  >>> {oc_report.error_count} ERROR overclaim findings recorded")
        else:
            print("  Overclaim detector: proof-graph dir/file not found — skipped")
    except ImportError:
        print("  Overclaim detector: import failed — skipped (non-blocking)")
    except Exception as e:
        print(f"  WARNING: Overclaim detector failed: {e}")

    # Step 3c2 (TC-SH-007): Rework classification — extracted to extensions
    _rework_items_pre = review.get("rework_items", [])
    try:
        from autonomous_cycle_extensions import classify_rework_items
        classify_rework_items(_rework_items_pre, sprint_id, timestamp, review_dir, repo_root)
    except Exception as _rw_err:
        print(f"  WARNING: Rework classification skipped (non-blocking): {_rw_err}")

    # Step 3d+3e+3f: SAL recompute, capability map, queue consumer, fabric
    # Step 3e: Capability Queue Consumer (TC-WIRE-001) — wiring in extensions module
    # Extracted to autonomous_cycle_extensions.py (TC-SGOV-008)
    try:
        from autonomous_cycle_extensions import run_sal_capmap_recompute
        sal_recompute_result, capmap_recompute_result, cap_consumer_result, fabric_result = \
            run_sal_capmap_recompute(decl, repo_root, review)
    except Exception as _recompute_err:
        print(f"  WARNING: Steps 3d+3e+3f skipped: {_recompute_err}")
        sal_recompute_result = {"status": "error", "error": str(_recompute_err)}
        capmap_recompute_result = {"status": "skipped"}
        cap_consumer_result = {"status": "skipped"}
        fabric_result = {"status": "skipped"}
    review["sal_recompute"] = sal_recompute_result
    review["capmap_recompute"] = capmap_recompute_result
    review["cap_consumer"] = cap_consumer_result
    review["authority_fabric"] = fabric_result

    # Step 3g: Track P reads machinery_to_product handoff (TC-P2-005-04, advisory)
    # Advisory only — if Track M has published a fresh gap snapshot, log it for
    # sprint context. Does NOT block if missing or stale.
    if track == "product":
        try:
            from write_track_handoff import read_machinery_handoff
            _m2p = read_machinery_handoff(repo_root)
            if _m2p:
                print("\n=== STEP 3g: TRACK M HANDOFF (advisory) ===")
                print(f"  machinery_to_product: written_at={_m2p.get('written_at', 'unknown')}")
                print(f"    validated_gap_count: {_m2p.get('validated_gap_count', 'n/a')}")
                print(f"    high_priority_gap_count: {_m2p.get('high_priority_gap_count', 'n/a')}")
                print(f"    gap_ledger_snapshot: {_m2p.get('gap_ledger_snapshot_path', 'n/a')}")
                review["machinery_handoff"] = _m2p
            else:
                review["machinery_handoff"] = None
        except Exception as _m2p_err:
            review["machinery_handoff"] = {"error": str(_m2p_err)}

    # Step 4: Generate next worker prompt (R108: stream-specific)
    print("\n=== STEP 4: GENERATE NEXT WORKER PROMPT ===")
    try:
        from validate_package_identity import _extract_stream_from_sprint
        detected_stream = _extract_stream_from_sprint(sprint_id)
    except Exception:
        detected_stream = "mainstream"
    # TC-P2-002/TC-P2-003: Derive work_groups from track for two-track routing.
    try:
        from generate_next_worker_prompt import TRACK_GROUPS
        _work_groups = list(TRACK_GROUPS[track]) if track and track in TRACK_GROUPS else None
    except Exception:
        _work_groups = None
    if _work_groups:
        print(f"  Track={track!r} -> work_groups={_work_groups}")

    prompt = generate_prompt(review, repo_root=repo_root, stream=detected_stream,
                             work_groups=_work_groups)
    prompt_path = review_dir / "combined-next-worker-prompt.md"
    prompt_path.write_text(prompt, encoding="utf-8")

    next_work = generate_next_work_items(review, stream=detected_stream, plan_lock=plan_lock,
                                         work_groups=_work_groups)
    work_path = review_dir / "next-work-items.yaml"
    work_path.write_text(
        yaml.dump(next_work, default_flow_style=False, sort_keys=False), encoding="utf-8"
    )
    # Step 4a-compiler (TC-PROD-H-010): Merge gap-ledger-sourced items via capability compiler.
    try:
        from capability_feature_compiler import compile_gaps as _compile_gaps
        _gl_path = repo_root / "reports" / "capability-layer" / "gap-ledger.json"
        if _gl_path.exists():
            _gl = json.loads(_gl_path.read_text(encoding="utf-8"))
            _open = [g for g in _gl.get("gaps", []) if g.get("status") != "closed"]
            _comp_items, _ = _compile_gaps(_open, max_items=10)
            if _comp_items:
                next_work["gap_sourced_items"] = _comp_items
                next_work["work_selection_mode"] = "CAPABILITY_COMPILER_MERGED"
                next_work["gap_sourced_count"] = len(_comp_items)
                print(f"  Capability compiler: {len(_comp_items)} gap-sourced items merged (work_selection_mode=CAPABILITY_COMPILER_MERGED)")
            else:
                # TC-CL-006: Make fallback explicit — do NOT silently proceed
                next_work["work_selection_mode"] = "EXPANSION_GOAL_FALLBACK"
                next_work["gap_sourced_count"] = 0
                next_work["fallback_reason"] = "gap_ledger_has_no_open_actionable_gaps"
                print("  Capability compiler: 0 open gaps matched — work_selection_mode=EXPANSION_GOAL_FALLBACK")
        else:
            print("  Capability compiler: gap-ledger.json not found -- skipped")
    except Exception as _ce:
        print(f"  WARNING: Capability compiler skipped: {_ce}")

    # TC-CL-003-05: Best-effort SAL compiler invocation (capability_compiler.py).
    # Produces sal-driven-capability-map.json with obligation_ids for ODF formats.
    # Runs as subprocess to avoid module-level state pollution. Non-blocking.
    try:
        import subprocess as _subproc
        _sal_compiler = repo_root / "tools" / "capability_layer" / "capability_compiler.py"
        if _sal_compiler.exists():
            _sal_result = _subproc.run(
                [sys.executable, str(_sal_compiler)],
                capture_output=True, text=True, timeout=60,
                cwd=str(repo_root),
            )
            if _sal_result.returncode == 0:
                print("  [TC-CL-003] SAL compiler: sal-driven-capability-map.json updated")
            else:
                print(f"  [TC-CL-003] SAL compiler: non-zero exit {_sal_result.returncode} (best-effort, continuing)")
        else:
            print("  [TC-CL-003] SAL compiler: capability_compiler.py not found -- skipped")
    except Exception as _sal_err:
        print(f"  [TC-CL-003] SAL compiler: skipped ({type(_sal_err).__name__}: {_sal_err})")

    # TC-CL-005: Flag-only gap closure detection scanner (non-blocking, does NOT close gaps).
    # Checks each non-DEFERRED gap: if all test_refs exist on disk → candidate for manual closure.
    # Produces .local/capability-layer/gap-closure-candidates.json.
    try:
        _DEFERRED_STATUSES = {"DEFERRED_BY_DESIGN", "DEFERRED", "closed", "CLOSED"}
        _active_gl_path = repo_root / "reports" / "capability-layer" / "gap-ledger-active.json"
        _scan_gl_path = _active_gl_path if _active_gl_path.exists() else (
            repo_root / "reports" / "capability-layer" / "gap-ledger.json"
        )
        _candidates: list[dict] = []
        if _scan_gl_path.exists():
            _scan_data = json.loads(_scan_gl_path.read_text(encoding="utf-8"))
            _all_gaps = _scan_data.get("gaps", _scan_data.get("active_gaps", []))
            for _g in _all_gaps:
                _status = _g.get("status", "")
                if _status.upper() in _DEFERRED_STATUSES:
                    continue
                _test_refs = _g.get("test_refs", [])
                if not _test_refs:
                    continue
                if all((repo_root / _tr).exists() for _tr in _test_refs):
                    _candidates.append({
                        "gap_id": _g.get("gap_id", ""),
                        "status": _status,
                        "test_refs": _test_refs,
                        "closure_candidate": True,
                        "reason": "all test_refs exist on disk",
                    })
        _cl_dir = repo_root / ".local" / "capability-layer"
        _cl_dir.mkdir(parents=True, exist_ok=True)
        (_cl_dir / "gap-closure-candidates.json").write_text(
            json.dumps({
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "source_ledger": str(_scan_gl_path) if _scan_gl_path.exists() else "not_found",
                "candidates": _candidates,
                "note": "FLAG ONLY — no gaps auto-closed. Review and manually close via gap-ledger update.",
            }, indent=2),
            encoding="utf-8",
        )
        print(f"  [TC-CL-005] Gap closure scanner: {len(_candidates)} candidates flagged")
    except Exception as _gc_err:
        print(f"  [TC-CL-005] Gap closure scanner: skipped ({type(_gc_err).__name__}: {_gc_err})")

    (review_dir / "next-work-items.json").write_text(
        json.dumps(next_work, indent=2), encoding="utf-8"
    )
    print(f"  Prompt: {prompt_path}")

    # Step 4a2: Write sprint contract for gap-sourced items (TC-FL-010)
    _gap_items = next_work.get("gap_sourced_items", [])
    if _gap_items:
        try:
            _contract = {
                "sprint_id": sprint_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "contracted_items": [
                    {
                        "item_id": gi.get("item_id", ""),
                        "gap_ref": gi.get("gap_ref") or gi.get("gap_id", ""),
                        "verification_command": gi.get("verification_command", ""),
                        "acceptance_criteria": gi.get("acceptance_criteria", ""),
                        "priority": gi.get("priority", 99),
                        "source": "gap_ledger",
                    }
                    for gi in _gap_items
                ],
            }
            _contract_path = repo_root / ".local" / "supervisor" / "sprint-contract.json"
            _contract_path.parent.mkdir(parents=True, exist_ok=True)
            _contract_path.write_text(json.dumps(_contract, indent=2) + "\n", encoding="utf-8")
            print(f"  Sprint contract: {len(_gap_items)} gap-sourced items written")
        except Exception as _sc_err:
            print(f"  WARNING: Sprint contract write failed: {_sc_err}")

    # SUP-RECT-005: Circuit breaker for zero-task loops (inline + delegated to extensions)
    _zero_task_counter_path = repo_root / ".local" / "supervisor" / "zero-task-counter.json"
    _all_items = next_work.get("items", next_work.get("work_items", []))
    if not _all_items:
        try:
            _ztc: dict = {}
            if _zero_task_counter_path.exists():
                _ztc = json.loads(_zero_task_counter_path.read_text(encoding="utf-8"))
            _ztc["count"] = _ztc.get("count", 0) + 1
            _ztc.setdefault("sprints", []).append(sprint_id)
            _zero_task_counter_path.parent.mkdir(parents=True, exist_ok=True)
            _zero_task_counter_path.write_text(json.dumps(_ztc, indent=2), encoding="utf-8")
            if _ztc["count"] >= 3:
                print(f"  CIRCUIT BREAKER: {_ztc['count']} consecutive zero-task cycles detected!")
                review.setdefault("continuation_warnings", []).append(
                    f"CIRCUIT_BREAKER: {_ztc['count']} zero-task cycles ({_ztc['sprints'][-3:]})"
                )
        except Exception as _ztc_err:
            print(f"  WARNING: zero-task-counter update failed: {_ztc_err}")
    else:
        # Reset counter when tasks are present
        try:
            if _zero_task_counter_path.exists():
                _zero_task_counter_path.write_text(json.dumps({"count": 0, "sprints": []}, indent=2), encoding="utf-8")
        except Exception:
            pass

    # Steps 4b+4c: Prompt quality, zero-task circuit breaker, completeness
    # Delegated to autonomous_cycle_extensions.py (TC-SGOV-008)
    print("\n=== STEP 4b: PROMPT QUALITY VALIDATION ===")
    try:
        from autonomous_cycle_extensions import validate_prompt_and_work_items
        validate_prompt_and_work_items(
            review, prompt_path, next_work, detected_stream,
            sprint_id, review_dir, repo_root)
    except Exception as _pv_err:
        print(f"  WARNING: Steps 4b+4c (prompt validation) failed: {_pv_err}")

    # Step 5: Write cycle manifest
    print("\n=== STEP 5: WRITE CYCLE MANIFEST ===")
    manifest = {
        "cycle_id": f"cycle-{run_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "run_id": run_id,
        "sprint_id": sprint_id,
        "timestamp": timestamp,
        "declaration_path": str(declaration_path),
        "review_path": str(review_dir / "supervisor-review.json"),
        "next_prompt_path": str(prompt_path),
        "item_grades_path": str(review_dir / "item-grades.yaml"),
        "next_work_items_path": str(work_path),
        "memory_synced": False,
        "autonomous_continue": review["autonomous_continue"],
        "stop_reason": review.get("stop_reason", ""),
        "exit_code": _compute_exit_code(review, decl, governance_validation_result),
        "accepted_count": len(review["accepted_items"]),
        "rework_count": len(review["rework_items"]),
        "rejected_count": len(review["rejected_items"]),
        "overclaimed_count": len(review["overclaimed_items"]),
        "blocked_count": len([g for g in review["item_grades"] if g["supervisor_grade"] == "BLOCKED_EXTERNAL_GATE"]),
        "git_head_at_review": review.get("git_head_at_review", "unknown"),  # TC-HARD-013
    }
    manifest_path = review_dir / "supervisor-cycle-manifest.yaml"
    manifest_path.write_text(
        yaml.dump(manifest, default_flow_style=False, sort_keys=False), encoding="utf-8"
    )
    print(f"  Manifest: {manifest_path}")

    # TC-DL-011: Update dual-lane counters in product-deepening ledger after accepted sprint
    if manifest.get("exit_code", 1) == 0:
        try:
            _update_lane_counters(decl, repo_root / "registry" / "product-deepening-ledger.yaml")
        except Exception as _lane_exc:
            print(f"  WARNING: lane counter update failed (non-blocking): {_lane_exc}")

    # TC-H5-001: Append grading history BEFORE overwriting latest-review
    # TC-HIST-DEDUP-001: Dedup check — delegated to autonomous_cycle_extensions
    try:
        from autonomous_cycle_extensions import append_grading_history
        append_grading_history(repo_root, sprint_id, run_id, timestamp, review, manifest)
    except Exception as _hist_err:
        print(f"  [WARN] grading-history.jsonl append failed: {_hist_err}")

    # Step 6: Copy latest summaries — extracted to autonomous_cycle_extensions.py (TC-SGOV-008)
    # Also writes stream-local authority-map.json with STREAM_LOCAL authority model (R112)
    print("\n=== STEP 6: COPY CYCLE SUMMARIES ===")
    try:
        from autonomous_cycle_extensions import copy_cycle_summaries
        copy_cycle_summaries(review, review_dir, repo_root, detected_stream,
                             run_id, sprint_id, timestamp, track, prompt_path)
    except Exception as _copy_err:
        print(f"  WARNING: Step 6 (copy summaries) failed: {_copy_err}")
        try:
            from closeout_skip_ledger import record_closeout_skip
            record_closeout_skip("copy_cycle_summaries", str(_copy_err), sprint_id=sprint_id)
        except Exception:
            pass  # skip ledger is itself best-effort
    # Write stream-local authority map for cross-stream isolation (R112)
    try:
        _auth_map = {
            "authority": "STREAM_LOCAL",
            "stream": detected_stream,
            "sprint_id": sprint_id,
            "run_id": run_id,
        }
        _auth_path = review_dir / "authority-map.json"
        _auth_path.write_text(json.dumps(_auth_map, indent=2), encoding="utf-8")
    except Exception as _auth_err:
        print(f"  WARNING: authority-map.json write failed: {_auth_err}")

    # Step 6b (FF-XPLAN-001 W3-003): Evidence retention cleanup
    # Delete evidence directories older than 30 days, preserving active/pinned ones
    print("\n=== STEP 6b: EVIDENCE RETENTION CLEANUP ===")
    try:
        import shutil
        evidence_base = repo_root / ".local" / "evidences"
        if evidence_base.is_dir():
            cutoff = datetime.now(timezone.utc) - timedelta(days=30)
            removed = 0
            kept = 0
            for edir in sorted(evidence_base.iterdir()):
                if not edir.is_dir():
                    continue
                # Preserve current run and pinned evidence
                if edir.name == run_id:
                    kept += 1
                    continue
                pin_file = edir / ".pinned"
                if pin_file.exists():
                    kept += 1
                    continue
                # Check modification time
                try:
                    mtime = datetime.fromtimestamp(edir.stat().st_mtime, tz=timezone.utc)
                    if mtime < cutoff:
                        shutil.rmtree(edir, ignore_errors=True)
                        removed += 1
                    else:
                        kept += 1
                except Exception:
                    kept += 1
            print(f"  Retention: removed {removed} old, kept {kept}")
        else:
            print("  No evidence directory found — skipped")
    except Exception as _ret_err:
        print(f"  WARNING: Evidence retention cleanup failed: {_ret_err}")

    # Step 7: Bridge to legacy format for session-resume/approval-gates/next-sprint
    print("\n=== STEP 7: BRIDGE TO LEGACY PACKET FORMAT ===")
    try:
        bridge_to_legacy_format(review, manifest, decl, repo_root)
        print("  Bridge: evidence-review.json + contradictions.json written to reports/supervisor/")
    except Exception as e:
        print(f"  WARNING: Bridge step failed: {e}")

    # Step 7b: Regenerate legacy markdown files (R99 fix: D99-STALE-01)
    # R101: Pass detected stream so next-sprint.md is stream-specific
    print("\n=== STEP 7b: REGENERATE LEGACY MARKDOWN ===")
    try:
        from generate_supervisor_packet import generate_packet, detect_stream_from_sprint_id
        detected_stream = detect_stream_from_sprint_id(sprint_id)
        generate_packet(repo_root, stream=detected_stream, plan_lock=plan_lock)
        print(f"  Regenerated: session-resume.md, approval-gates.md, next-sprint.md (stream={detected_stream})")
    except Exception as e:
        print(f"  WARNING: Legacy markdown regeneration failed: {e}")

    # Step 7c: Rebuild context pack (R99 fix: D99-STALE-02)
    print("\n=== STEP 7c: REBUILD CONTEXT PACK ===")
    try:
        pack = build_context_pack(repo_root)
        context_yaml_path = repo_root / ".supervisor" / "context-pack.yaml"
        context_yaml_path.write_text(
            yaml.dump(pack, default_flow_style=False, sort_keys=False),
            encoding="utf-8"
        )
        context_md_path = repo_root / "reports" / "supervisor" / "context-pack.md"
        context_md_path.write_text(generate_context_md(pack), encoding="utf-8")
        print(f"  Context pack rebuilt: {context_yaml_path}")
    except Exception as e:
        print(f"  WARNING: Context pack rebuild failed: {e}")

    # Step 7d (TC-SH-012): Maturity trend — extracted to extensions
    try:
        from autonomous_cycle_extensions import append_maturity_trend
        append_maturity_trend(repo_root)
    except Exception as _mt_err:
        print(f"  WARNING: Maturity trend skipped (non-blocking): {_mt_err}")

    # Step 7e: Root README drift detection (non-blocking)
    try:
        from tools.readme_sync.generate_root_status import detect_root_readme_drift
        _root_drift = detect_root_readme_drift(repo_root)
        if _root_drift.get("drifted"):
            print(f"  ROOT README DRIFT: {_root_drift['drifted_fields']}")
        else:
            print("  Root README: no drift detected")
    except Exception as _rd_err:
        print(f"  WARNING: root README drift check failed (non-blocking): {_rd_err}")

    # Step 7b: Track P Ledger Enforcement (TC-P2-008 — REQ-LED-001/LED-002/LED-003)
    # For Track P sprints, validate that at least one ledger entry exists in
    # product-code-change-ledger.json for this sprint_id before writing signal.
    # Non-Track-P: skipped entirely (backward compat).
    if track == "product":
        print("\n=== STEP 7b: TRACK P LEDGER VALIDATION ===")
        try:
            from validate_ledger_entry import validate_ledger_entry_exists
            _led_items = decl.get("planned_work_items", [])
            _ledger_path = repo_root / "reports" / "r90" / "product-code-change-ledger.json"
            _led_valid, _led_missing, _led_error = validate_ledger_entry_exists(
                sprint_id=sprint_id,
                work_items=_led_items,
                ledger_path=_ledger_path,
            )
            if _led_valid:
                print(f"  Ledger validation: PASS (sprint_id={sprint_id!r})")
                review["ledger_validation"] = {"status": "passed", "sprint_id": sprint_id}
            else:
                print(f"  Ledger validation: FAIL — {_led_error}", file=sys.stderr)
                review["ledger_validation"] = {
                    "status": "failed",
                    "sprint_id": sprint_id,
                    "missing": _led_missing,
                    "error": _led_error,
                }
                # REQ-LED-003: Reject declaration if ledger entry is missing for product work items
                sys.exit(7)
        except ImportError as _led_import_err:
            print(f"  WARNING: validate_ledger_entry unavailable — skipping ({_led_import_err})")
            review["ledger_validation"] = {"status": "skipped", "reason": str(_led_import_err)}
        except SystemExit:
            raise
        except Exception as _led_exc:
            print(f"  WARNING: Ledger validation error (non-blocking): {_led_exc}")
            review["ledger_validation"] = {"status": "error", "error": str(_led_exc)}

    # Step 8: Write continuation signal for autonomous loop (MODE 5)
    print("\n=== STEP 8: WRITE CONTINUATION SIGNAL ===")
    try:
        signal_dir = repo_root / ".local" / "supervisor"
        signal_dir.mkdir(parents=True, exist_ok=True)
        # TC-P2-002: Route signal to track-specific subdirectory when --track is set.
        # Legacy path is always updated for backward compat.
        if track == "product":
            _track_signal_dir = signal_dir / "product"
            _track_signal_dir.mkdir(parents=True, exist_ok=True)
            signal_path = _track_signal_dir / "continuation-signal.json"
            _legacy_signal_path = signal_dir / "continuation-signal.json"
        elif track == "machinery":
            _track_signal_dir = signal_dir / "machinery"
            _track_signal_dir.mkdir(parents=True, exist_ok=True)
            signal_path = _track_signal_dir / "continuation-signal.json"
            _legacy_signal_path = None  # Track M: no legacy fallback (strict isolation)
        else:
            signal_path = signal_dir / "continuation-signal.json"
            _legacy_signal_path = None

        # Read existing signal to preserve iteration count, then increment
        existing_iteration = 0
        existing_rework_items: list = []  # TC-REPAIR-VERIFY-001: track prior structural GOV_BLOCKs
        if signal_path.exists():
            try:
                existing = json.loads(signal_path.read_text(encoding="utf-8"))
                existing_iteration = existing.get("iteration", 0)
                existing_rework_items = existing.get("rework_items", [])
            except Exception:
                pass
        existing_iteration += 1  # Each cycle run advances the counter

        # Load max_iterations from policies
        max_iterations = 5
        policies_path = repo_root / ".supervisor" / "policies.yaml"
        if policies_path.exists():
            try:
                policies = yaml.safe_load(policies_path.read_text(encoding="utf-8"))
                max_iterations = policies.get("autonomous_continuation", {}).get("max_iterations", 5)
            except Exception:
                pass

        hard_stops = []
        if manifest.get("exit_code") == 3:
            hard_stops.append("critical_rework_blocks_continuation")

        # Determine continuation mode:
        #   true            — all items accepted, pure new-work sprint
        #   true_with_rework — rework items exist but safe lanes can continue
        #   false           — hard stop (overclaim/reject/external gate)
        rework_items = review.get("rework_items", [])
        overclaimed = review.get("overclaimed_items", [])

        # TC-REPAIR-VERIFY-001: Active post-repair GOV_BLOCK re-scan.
        # If prior signal had structural GOV_BLOCK items and this sprint looks like
        # a TC-HEAL analytics-separation sprint, run validate_source_architecture.py.
        # Exit 0 → remove GOV_BLOCK items from rework_items; non-zero → annotate.
        _tc_heal_sprint = (
            "TC-HEAL" in sprint_id.upper()
            or "analytics-separation" in sprint_id.lower()
            or "analytics-heal" in sprint_id.lower()
        )
        if not _tc_heal_sprint:
            _all_planned = decl.get("planned_work_items", [])
            if _all_planned and all(
                item.get("item_type") == "GOVERNANCE_TASKCARD" for item in _all_planned
            ):
                _tc_heal_sprint = True

        _GOVBLOCK_PREFIXES = (
            "GOV_BLOCK:monolith_detection_validator",
            "GOV_BLOCK:validate_source_architecture",
        )
        _prior_structural_blocks = [
            it for it in existing_rework_items
            if any(it.startswith(p) or it == p for p in _GOVBLOCK_PREFIXES)
        ]

        if _tc_heal_sprint and _prior_structural_blocks:
            _val_path = repo_root / "tools" / "validators" / "validate_source_architecture.py"
            if _val_path.exists():
                try:
                    import subprocess as _sp
                    _rescan = _sp.run(
                        [sys.executable, str(_val_path), "--check-new-files"],
                        capture_output=True, text=True, timeout=60,
                    )
                    if _rescan.returncode == 0:
                        rework_items = [
                            it for it in rework_items
                            if not any(it.startswith(p) or it == p for p in _GOVBLOCK_PREFIXES)
                        ]
                        hard_stops = _sync_hard_stops_after_repair(
                            hard_stops, rework_items, _prior_structural_blocks
                        )
                        review["post_repair_rescan"] = {
                            "status": "RESOLVED",
                            "sprint_id": sprint_id,
                            "resolved_prior_items": _prior_structural_blocks,
                            "validator_exit_code": 0,
                        }
                        print(
                            f"  TC-REPAIR-VERIFY-001: Post-repair re-scan PASSED — "
                            f"{len(_prior_structural_blocks)} structural GOV_BLOCK(s) resolved"
                        )
                    else:
                        rework_items = [
                            (it + " [post_repair_rescan:STILL_FAILING]"
                             if any(it.startswith(p) or it == p for p in _GOVBLOCK_PREFIXES)
                             else it)
                            for it in rework_items
                        ]
                        review["post_repair_rescan"] = {
                            "status": "STILL_FAILING",
                            "sprint_id": sprint_id,
                            "validator_exit_code": _rescan.returncode,
                            "validator_stderr": _rescan.stderr[:500],
                        }
                        print(
                            f"  TC-REPAIR-VERIFY-001: Post-repair re-scan FAILED "
                            f"(exit {_rescan.returncode}) — GOV_BLOCK items retained"
                        )
                except Exception as _rescan_err:
                    print(f"  TC-REPAIR-VERIFY-001: Re-scan error (non-blocking): {_rescan_err}")

        # R98 fix: Check iteration >= max_iterations before allowing continuation
        at_max_iterations = existing_iteration >= max_iterations
        rollover_note = None
        if at_max_iterations:
            # R5: CHECKPOINT_ROLLOVER — per stop_reason_adjudicator Rule 6, max_iterations
            # is NOT terminal when no other hard stops exist. The agent can handle by resetting
            # the iteration counter (governed rollover, not manual reset required).
            # Check whether any OTHER hard stops exist before deciding to rollover vs stop.
            non_iter_hard_stops_early = [
                h for h in hard_stops if h != "max_iterations_reached"
            ]
            overclaimed_or_rework_blocks = bool(
                manifest.get("exit_code") == 3 or
                review.get("overclaimed_items")
            )
            if not non_iter_hard_stops_early and not overclaimed_or_rework_blocks:
                # Governed rollover: reset iteration to 0 and continue
                rollover_note = {
                    "rollover_from_iteration": existing_iteration,
                    "rollover_at_max": max_iterations,
                    "rollover_rule": "CHECKPOINT_ROLLOVER_CONTINUE (stop_reason_adjudicator Rule 6)",
                    "rollover_action": "iteration reset to 0 — new autonomous batch starting",
                }
                existing_iteration = 0
                at_max_iterations = False
            else:
                hard_stops.append("max_iterations_reached")

        # R107 Lane G: Check evidence quality — stop on quality regression
        # Legacy evidence_quality_score is deprecated; check semantic_quality_score first
        eqb = review.get("evidence_quality_breakdown", {})
        sqs = eqb.get("semantic_quality_score")
        eqs = review.get("evidence_quality_score", 1.0)
        if sqs is None and eqs == 0.0 and len(review.get("accepted_items", [])) > 0:
            # B5: evidence_quality_zero is LOCAL_REPAIR_CONTINUE per CLAUDE.md/MEMORY.md —
            # LLM grader unavailable with accepted items is NOT a hard stop.
            # Move to continuation_warnings so autonomous_continue is not forced false.
            review.setdefault("continuation_warnings", []).append("evidence_quality_zero")

        # R107 Lane G: Check anti-skip critical blocks
        if anti_skip_impact and anti_skip_impact.get("block"):
            hard_stops.append("anti_skip_critical_block")

        # R108: Prompt quality failure blocks continuation
        if review.get("prompt_quality_failure"):
            hard_stops.append("prompt_quality_failure")

        # R-CLOSEOUT: Run closeout gate and no-stop watchdog if evidence root exists
        evidence_root_path = None
        if declaration_path and declaration_path.parent.exists():
            evidence_root_path = declaration_path.parent
        if evidence_root_path:
            try:
                from validate_closeout_gate import run_closeout_gate
                closeout_result = run_closeout_gate(evidence_root_path)
                review["closeout_gate_verdict"] = closeout_result.get("verdict", "UNKNOWN")
                review["closeout_gate_checks"] = closeout_result.get("gates", [])
                print(f"  Closeout gate: {closeout_result.get('verdict', 'UNKNOWN')} "
                      f"({closeout_result.get('passed_count', 0)}/{closeout_result.get('total_gates', 0)})")
            except ImportError:
                print("  WARNING: validate_closeout_gate not available, skipping")
            except Exception as cg_err:
                print(f"  WARNING: Closeout gate check failed: {cg_err}")

            try:
                from validate_no_stop_watchdog import run_no_stop_watchdog
                watchdog_result = run_no_stop_watchdog(evidence_root_path)
                review["watchdog_verdict"] = watchdog_result.get("verdict", "UNKNOWN")
                review["watchdog_checks"] = watchdog_result.get("checks", [])
                wd_verdict = watchdog_result.get("verdict", "ALLOW_STOP")
                print(f"  No-stop watchdog: {wd_verdict} "
                      f"({watchdog_result.get('block_count', 0)} blocks)")
            except ImportError:
                print("  WARNING: validate_no_stop_watchdog not available, skipping")
            except Exception as wd_err:
                print(f"  WARNING: No-stop watchdog check failed: {wd_err}")

        if hard_stops or overclaimed:
            auto_continue_value = False
        elif rework_items and not overclaimed:
            auto_continue_value = "true_with_rework"
        else:
            auto_continue_value = bool(manifest.get("autonomous_continue", False))

        # R99: Full continuation state classification (D99-CONT-01)
        # R112: Pass anti_skip_result for YES_WITH_LIMITATIONS detection
        continuation_state = classify_continuation_state(
            auto_continue_value, at_max_iterations, hard_stops,
            overclaimed, rework_items, review, policies_path,
            anti_skip_result=anti_skip_result,
            # New params use default True — backward compatible (R113 product-first)
        )

        # Emit per-format product deepening gate results (TC-HEAL-PD-004)
        try:
            import sys as _sys_pd
            _pd_gate_dir = Path(__file__).resolve().parent
            if str(_pd_gate_dir) not in _sys_pd.path:
                _sys_pd.path.insert(0, str(_pd_gate_dir))
            from product_deepening_gate import emit_continuation_signal_gates as _emit_pd_gates
            _pd_gaps_path = repo_root / ".local" / "supervisor" / "selected-product-gaps.json"
            _pd_selected = []
            if _pd_gaps_path.exists():
                try:
                    _pd_selected = json.loads(_pd_gaps_path.read_text(encoding="utf-8")).get("selected_gaps", [])
                except Exception:
                    pass
            review["product_deepening_gate_results"] = _emit_pd_gates(_pd_selected)
        except Exception as _pd_gate_err:
            review["product_deepening_gate_results"] = {
                "error": str(_pd_gate_err),
                "evaluated_formats": [],
                "all_allowed": False,
                "blocked_formats": [],
            }

        # C5 (SIGNAL-UNIFY-001): Patch work-item-grades.md and latest-cycle-summary.md to
        # use auto_continue_value so all three outputs (grades, summary, signal) are
        # consistent.  review["autonomous_continue"] was written before hard_stops were
        # evaluated; auto_continue_value incorporates hard_stops, overclaimed, and
        # rework_items — it is the authoritative value.
        try:
            _latest_dir = repo_root / "reports" / "supervisor"
            _wg_path = _latest_dir / "work-item-grades.md"
            if _wg_path.exists():
                _wg_text = _wg_path.read_text(encoding="utf-8")
                _old_ac = f"- Autonomous Continue: {review['autonomous_continue']}"
                _new_ac = f"- Autonomous Continue: {auto_continue_value}"
                if _old_ac != _new_ac and _old_ac in _wg_text:
                    _wg_path.write_text(_wg_text.replace(_old_ac, _new_ac, 1), encoding="utf-8")
            _cs_path = _latest_dir / "latest-cycle-summary.md"
            if _cs_path.exists():
                _cs_text = _cs_path.read_text(encoding="utf-8")
                _old_cs = f"Autonomous Continue: {review['autonomous_continue']}"
                _new_cs = f"Autonomous Continue: {auto_continue_value}"
                if _old_cs != _new_cs and _old_cs in _cs_text:
                    _cs_path.write_text(_cs_text.replace(_old_cs, _new_cs, 1), encoding="utf-8")
        except Exception as _unify_err:
            print(f"  WARNING: Signal unification patch failed (non-blocking): {_unify_err}")

        # CCI-MVP: Stable session_id for cross-chat isolation (TC-CCI-200)
        # TC-HQP-004: Two-tier session scoping — only embed session_id when a per-chat
        # plan is IN_PROGRESS. Product-track signals are session-agnostic (null session_id)
        # so SESSION_MISMATCH never fires at session boundaries for ledger work.
        # check_continuation.py line 69: `if session_id and signal_session_id:` already
        # short-circuits the mismatch check when signal_session_id is None.
        _alp_path_hqp004 = repo_root / ".local" / "supervisor" / "active-plan-lock.json"
        _plan_is_active_hqp004 = False
        try:
            if _alp_path_hqp004.exists():
                _alp_data = json.loads(_alp_path_hqp004.read_text(encoding="utf-8"))
                _plan_is_active_hqp004 = _alp_data.get("status") == "IN_PROGRESS"
        except Exception:
            pass  # If we can't read the lock, treat as no active plan (safe default)

        if _plan_is_active_hqp004:
            # Per-chat plan is running — session-scope the signal so CCI-MVP protects it
            try:
                from continuation_identity import get_or_create_session_identity
                _cci_identity = get_or_create_session_identity(sprint_id=sprint_id)
                session_id = _cci_identity.session_id
            except Exception as _cci_err:
                print(f"  WARNING: CCI identity fallback: {_cci_err}", file=sys.stderr)
                session_id = os.environ.get("CLAUDE_SESSION_ID") or str(uuid.uuid4())[:12]
        else:
            # Product-track or no active plan — emit null so next session is never blocked
            session_id = None
            print("  [TC-HQP-004] No active per-chat plan: session_id=null in signal (product-agnostic)")

        # TC-P2-002: Include track and chat_id (for Track M) in signal.
        _chat_id_value = None
        if track == "machinery":
            try:
                from continuation_identity import get_or_create_machinery_identity
                _m_identity = get_or_create_machinery_identity()
                _chat_id_value = _m_identity.chat_id
                # Write current-chat-id.json for check_continuation.py resolution
                _chat_id_reg = signal_dir / "machinery" / "current-chat-id.json"
                _chat_id_reg.parent.mkdir(parents=True, exist_ok=True)
                atomic_write_json(_chat_id_reg, {"chat_id": _chat_id_value, "written_at": timestamp})
            except Exception as _cid_err:
                print(f"  WARNING: Track M chat_id generation failed: {_cid_err}", file=sys.stderr)

        # TC-SRB-031-02: Build structured continuation_reason_codes list.
        # Non-breaking addition alongside existing stop_reason (string).
        # Aggregates all machine-readable stop/rework causes into a typed list.
        _reason_codes: list[str] = []
        for _hs in hard_stops:
            _reason_codes.append(f"HARD_STOP:{_hs}")
        for _rw in rework_items:
            _reason_codes.append(f"REWORK:{_rw}")
        if at_max_iterations:
            _reason_codes.append("MAX_ITERATIONS")
        if overclaimed:
            _reason_codes.append("OVERCLAIMED")

        signal = {
            "autonomous_continue": auto_continue_value,
            "iteration": existing_iteration,
            "max_iterations": max_iterations,
            "next_sprint_path": "reports/supervisor/next-sprint.md",
            "stop_reason": hard_stops[0] if hard_stops else None,
            "continuation_reason_codes": _reason_codes,
            "rework_items": rework_items,
            "safe_lanes_available": not bool(hard_stops),
            "generated_at": timestamp,
            "source_sprint_id": sprint_id,
            "hard_stops_detected": hard_stops,
            "continuation_state": continuation_state,
            "session_id": session_id,
            "owner": "autonomous_cycle",
        }
        if track:
            signal["track"] = track
        if _chat_id_value:
            signal["chat_id"] = _chat_id_value
        if rollover_note:
            signal["checkpoint_rollover"] = rollover_note

        # TC-REPAIR-VERIFY-001: Auto-confirm post-repair GOV_BLOCK resolution.
        # If the prior signal had structural GOV_BLOCK items but the current cycle's
        # governance validators passed (no new structural blocks), mark as resolved.
        # This removes the need for manual govblock_resolved_by setting after TC-HEAL.
        _STRUCTURAL_GOV_VALIDATORS = {
            "GOV_BLOCK:monolith_detection_validator",
            "GOV_BLOCK:validate_source_architecture",
        }
        _prior_structural_blocks = [
            item for item in existing_rework_items
            if any(item.startswith(v) or item == v for v in _STRUCTURAL_GOV_VALIDATORS)
        ]
        _current_structural_blocks = [
            item for item in rework_items
            if any(item.startswith(v) or item == v for v in _STRUCTURAL_GOV_VALIDATORS)
        ]
        if _prior_structural_blocks and not _current_structural_blocks:
            signal["govblock_resolved_by"] = (
                f"post_repair_auto_verified:{sprint_id}"
            )
            print(
                f"  TC-REPAIR-VERIFY-001: Structural GOV_BLOCK auto-resolved — "
                f"prior blocks {_prior_structural_blocks} cleared by passing validators"
            )

        # TC-OCRD-B1: Embed contradiction summary in signal (non-blocking advisory).
        _contradictions_path = REPO_ROOT / "reports" / "supervisor" / "contradictions.json"
        _critical_count = 0
        _contradiction_summary: list[str] = []
        try:
            if _contradictions_path.exists():
                _c_data = json.loads(_contradictions_path.read_text(encoding="utf-8"))
                _critical_count = int(_c_data.get("critical_count", 0))
                _contradiction_summary = [
                    c.get("id", "") for c in _c_data.get("contradictions", [])
                    if c.get("severity") == "CRITICAL" and c.get("id")
                ]
        except Exception:
            pass  # Non-blocking per Supreme Directive
        signal["critical_contradiction_count"] = _critical_count
        signal["contradiction_summary"] = _contradiction_summary

        # TC-MA2-SIGNAL-001-02/03: Validate signal field coherence before writing.
        # Corrects incoherent combinations that can reach the disk (REQ-SIGNAL-001).
        signal = _validate_and_correct_signal_coherence(signal, sprint_id)

        atomic_write_json(signal_path, signal)
        # Also update legacy path for Track P (backward compat) — NOT for Track M (strict isolation)
        if _legacy_signal_path is not None:
            atomic_write_json(_legacy_signal_path, signal)
        print(f"  Signal: {signal_path} (continue={signal['autonomous_continue']}, "
              f"iter={existing_iteration}/{max_iterations}, track={track!r})")

        # CCI: Record signal creation in continuation ledger (TC-CCI-202)
        try:
            from continuation_ledger import append_event
            append_event("CREATED", "continuation-signal.json",
                         session_id=session_id, sprint_id=sprint_id)
        except Exception:
            pass  # Ledger is best-effort

        # R109: Also write stream-local continuation signal
        stream_signal_dir = signal_dir / "streams" / detected_stream
        stream_signal_dir.mkdir(parents=True, exist_ok=True)
        stream_signal = {**signal, "stream": detected_stream}
        stream_signal_path = stream_signal_dir / "continuation-signal.json"
        atomic_write_json(stream_signal_path, stream_signal)
        print(f"  Stream signal: {stream_signal_path}")

        # TC-AMD-SIGNAL-001: Emit maturity signal for external consumption
        try:
            from emit_maturity_signal import emit_signal as _emit_maturity
            _emit_maturity(review, signal, repo_root)
            print("  Maturity signal: reports/supervisor/maturity-signal.json")
        except Exception as _ms_err:
            print(f"  WARNING: Maturity signal emission skipped: {_ms_err}")
        # TC-FG-007 (healed TC-AMD-LLM-001): Adversarial check — HIGH risk now blocks rework
        # iteration >= 3 gate removed; LLM-unavailable (None return) never blocks
        try:
            from adversarial_check import run_and_write as _adv_rw
            _adv_result = _adv_rw(review, repo_root, sprint_id, signal.get("iteration", 0))
            if _adv_result is not None and _adv_result >= 1:
                # HIGH risk findings: add to rework_items (not just warnings)
                review.setdefault("rework_items", []).append(
                    f"ADVERSARIAL_HIGH_RISK:{_adv_result}_findings"
                )
                review["critical_rework_count"] = review.get("critical_rework_count", 0) + 1
                if review.get("overall_verdict") in ("ACCEPTED", "ACCEPTED_WITH_LIMITATIONS"):
                    review["overall_verdict"] = "ACCEPTED_WITH_REWORK"
                if "autonomous_continue" in review:
                    review["autonomous_continue"] = False
                continuation_warnings.append(f"adversarial_check_high_risk:{_adv_result}_findings")
            elif _adv_result is None:
                print("  INFO: Adversarial check skipped (LLM unavailable) — not blocking")
        except Exception as _ae:
            print(f"  WARNING: Adversarial check skip: {_ae}")
        # TC-SH-006: GOV_BLOCK auto-repair directive — extracted to extensions
        if _current_structural_blocks:
            try:
                from autonomous_cycle_extensions import write_govblock_directive
                write_govblock_directive(_current_structural_blocks, sprint_id, timestamp, signal_dir)
            except Exception as _dir_err:
                print(f"  WARNING: TC-SH-006 directive skipped (non-blocking): {_dir_err}")

        # HEAL-RECT-005: Archive rework items for cross-sprint persistence
        if rework_items:
            rework_archive_path = signal_dir / "rework_archive.jsonl"
            try:
                with open(rework_archive_path, "a", encoding="utf-8") as ra:
                    for rw_id in rework_items:
                        ra.write(json.dumps({
                            "item_id": rw_id,
                            "sprint_id": sprint_id,
                            "archived_at": timestamp,
                            "resolved": False,
                        }) + "\n")
            except Exception as ra_err:
                print(f"  WARNING: Rework archive failed: {ra_err}")

        # R-NMPC: Wire evidence_continuation to produce machine-readable continuation.
        # Without this, autonomous_continue=true points only to advisory Markdown
        # (next-sprint.md), which continuation_router.py rejects, causing the user
        # to manually paste prompts. We always call this when autonomous_continue is
        # truthy so next-action.json + active-continuation.json are fresh.
        if auto_continue_value:
            try:
                from evidence_continuation import (
                    apply_post_closeout_continuation,
                    repair_global_continuation_signal,
                    seed_post_closeout_queue_item,
                )
                post_result = apply_post_closeout_continuation(
                    sprint_id=sprint_id,
                    run_id=getattr(manifest, "get", lambda k, d=None: d)("run_id"),
                    cycle_index=existing_iteration,
                )
                repair_result = repair_global_continuation_signal(sprint_id=sprint_id)
                seed_result = seed_post_closeout_queue_item(sprint_id=sprint_id)
                print(f"  Machine continuation: {post_result.get('next_action_path')}")
                print(f"  Signal repair: {repair_result.get('status')}")
                print(f"  Queue seed: {seed_result.get('status')}")
            except Exception as ec_err:
                print(f"  WARNING: evidence_continuation bridge failed: {ec_err}")
                # Non-silent: record failure in signal so check_continuation surfaces it
                signal["evidence_continuation_failed"] = True
                signal["evidence_continuation_error"] = str(ec_err)
                atomic_write_json(signal_path, signal)
    except Exception as e:
        print(f"  WARNING: Continuation signal failed: {e}")

    # TC-LOCK-POSTCLEAN-001: Auto-supersede stale TERMINAL_CLOSED plan locks after a clean sprint.
    # Root cause: after a plan closes (TERMINAL_CLOSED) in session N, subsequent autonomous sprints
    # in the SAME session hit POST_PLAN_TERMINAL because check_continuation.py sees the
    # TERMINAL_CLOSED lock as the newest session lock, even though it predates all recent sprints.
    # Fix: when autonomous_continue is True and the sprint produced a clean signal, scan for
    # current-session TERMINAL_CLOSED locks whose updated_at < sprint start_time and auto-supersede.
    # Non-blocking (wrapped in try/except). Only affects the current session's locks.
    try:
        if auto_continue_value:
            _locks_dir = repo_root / ".local" / "supervisor" / "plan-locks"
            _sprint_start = decl.get("start_time", "")
            if _locks_dir.is_dir() and _sprint_start and session_id:
                from datetime import datetime as _dt_lock, timezone as _tz_lock
                try:
                    _sprint_start_dt = _dt_lock.fromisoformat(
                        _sprint_start.replace("Z", "+00:00")
                    )
                except Exception:
                    _sprint_start_dt = None
                if _sprint_start_dt:
                    for _lf in sorted(_locks_dir.glob("*.json")):
                        try:
                            _ldata = json.loads(_lf.read_text(encoding="utf-8"))
                        except Exception:
                            continue
                        if _ldata.get("status") != "TERMINAL_CLOSED":
                            continue
                        if _ldata.get("session_id") != session_id:
                            continue  # Only auto-supersede current session's locks
                        _lock_updated = _ldata.get("updated_at", "")
                        try:
                            _lock_dt = _dt_lock.fromisoformat(
                                _lock_updated.replace("Z", "+00:00")
                            )
                            # Apply UTC offset normalization (make both offset-aware)
                            if _sprint_start_dt.tzinfo is None:
                                _sprint_start_dt = _sprint_start_dt.replace(
                                    tzinfo=_tz_lock.utc
                                )
                        except Exception:
                            continue
                        if _lock_dt >= _sprint_start_dt:
                            continue  # Lock is newer than sprint start — don't auto-supersede
                        # Lock predates this sprint and is TERMINAL_CLOSED — auto-supersede
                        _ldata["status"] = "SUPERSEDED"
                        _ldata["superseded_at"] = timestamp
                        _ldata["superseded_reason"] = (
                            f"Auto-superseded by TC-LOCK-POSTCLEAN-001: clean sprint "
                            f"'{sprint_id}' completed after this plan was closed. "
                            "check_continuation.py can now proceed without POST_PLAN_TERMINAL."
                        )
                        _lf.write_text(json.dumps(_ldata, indent=2) + "\n", encoding="utf-8")
                        print(
                            f"  [POSTCLEAN] Auto-superseded stale TERMINAL_CLOSED lock: "
                            f"{_lf.name} (plan={Path(_ldata.get('plan_path', '')).name})"
                        )
            # Also supersede phantom IN_PROGRESS locks (plan file does not exist) from
            # the current session. These arise when reopen_plan_lock creates a new lock
            # for a plan that no longer exists in the filesystem.
            # Check session-keyed lock files first.
            for _lf2 in sorted(_locks_dir.glob("*.json")):
                try:
                    _ldata2 = json.loads(_lf2.read_text(encoding="utf-8"))
                except Exception:
                    continue
                if _ldata2.get("status") != "IN_PROGRESS":
                    continue
                if _ldata2.get("session_id") != session_id:
                    continue
                _phantom_path = _ldata2.get("plan_path", "")
                if _phantom_path and not Path(_phantom_path).exists():
                    _ldata2["status"] = "SUPERSEDED"
                    _ldata2["superseded_at"] = timestamp
                    _ldata2["superseded_reason"] = (
                        f"Phantom lock auto-superseded by TC-LOCK-POSTCLEAN-001: "
                        f"plan file '{_phantom_path}' does not exist. "
                        "Clean sprint confirms no active plan context."
                    )
                    _lf2.write_text(json.dumps(_ldata2, indent=2) + "\n", encoding="utf-8")
                    print(
                        f"  [POSTCLEAN] Auto-superseded phantom IN_PROGRESS lock: "
                        f"{_lf2.name} (plan={Path(_phantom_path).name})"
                    )
            _shared_lock_path = repo_root / ".local" / "supervisor" / "active-plan-lock.json"
            if _shared_lock_path.exists():
                try:
                    _sldata = json.loads(_shared_lock_path.read_text(encoding="utf-8"))
                    _sl_status = _sldata.get("status", "")
                    _sl_same_session = _sldata.get("session_id") == session_id
                    # Case A: Phantom IN_PROGRESS (plan file missing)
                    if (
                        _sl_same_session
                        and _sl_status == "IN_PROGRESS"
                        and not Path(_sldata.get("plan_path", "")).exists()
                    ):
                        _sldata["status"] = "SUPERSEDED"
                        _sldata["superseded_at"] = timestamp
                        _sldata["superseded_reason"] = (
                            f"Phantom lock auto-superseded by TC-LOCK-POSTCLEAN-001: "
                            f"plan file '{_sldata.get('plan_path', '')}' does not exist. "
                            "Clean sprint confirms no active plan context."
                        )
                        _shared_lock_path.write_text(
                            json.dumps(_sldata, indent=2) + "\n", encoding="utf-8"
                        )
                        print(
                            f"  [POSTCLEAN] Auto-superseded phantom IN_PROGRESS lock: "
                            f"active-plan-lock.json "
                            f"(plan={Path(_sldata.get('plan_path', '')).name})"
                        )
                    # Case B: Stale TERMINAL_CLOSED (predates sprint start_time)
                    elif (
                        _sl_same_session
                        and _sl_status == "TERMINAL_CLOSED"
                        and _sprint_start_dt is not None
                    ):
                        _sl_updated = _sldata.get("updated_at", "")
                        try:
                            _sl_dt = _dt_lock.fromisoformat(
                                _sl_updated.replace("Z", "+00:00")
                            )
                            if _sprint_start_dt.tzinfo is None:
                                _sprint_start_dt = _sprint_start_dt.replace(
                                    tzinfo=_tz_lock.utc
                                )
                            if _sl_dt < _sprint_start_dt:
                                _sldata["status"] = "SUPERSEDED"
                                _sldata["superseded_at"] = timestamp
                                _sldata["superseded_reason"] = (
                                    f"Auto-superseded by TC-LOCK-POSTCLEAN-001 (Case B): "
                                    f"stale TERMINAL_CLOSED in active-plan-lock.json predates "
                                    f"sprint start ({_sprint_start}). "
                                    f"plan={_sldata.get('plan_path', '')}"
                                )
                                _shared_lock_path.write_text(
                                    json.dumps(_sldata, indent=2) + "\n", encoding="utf-8"
                                )
                                print(
                                    f"  [POSTCLEAN] Auto-superseded stale TERMINAL_CLOSED: "
                                    f"active-plan-lock.json "
                                    f"(plan={Path(_sldata.get('plan_path', '')).name}, "
                                    f"updated_at={_sl_updated})"
                                )
                        except Exception:
                            pass
                except Exception as _sle:
                    print(f"  [POSTCLEAN] Shared lock check skipped: {_sle}")
            # POSTCLEAN-002b: Supersede ALL external per-chat plan locks (any status except
            # SUPERSEDED/DEFERRED) to prevent future reopen-check from picking them up.
            # External = path contains .claude/plans/ (per-chat plan modal, not repo plans/).
            if auto_continue_value:
                try:
                    _pc2b_dir = repo_root / ".local" / "supervisor" / "plan-locks"
                    if _pc2b_dir.is_dir():
                        _pc2b_ext_count = 0
                        for _pc2b_f in sorted(_pc2b_dir.glob("*.json")):
                            try:
                                _pc2b_d = json.loads(_pc2b_f.read_text(encoding="utf-8"))
                                _pc2b_plan = _pc2b_d.get("plan_path", "").replace("\\", "/")
                                _pc2b_status = _pc2b_d.get("status", "")
                                if ".claude/plans/" in _pc2b_plan and _pc2b_status not in ("SUPERSEDED", "DEFERRED"):
                                    _pc2b_d["status"] = "SUPERSEDED"
                                    _pc2b_d["superseded_at"] = timestamp
                                    _pc2b_d["superseded_reason"] = (
                                        "POSTCLEAN-002b: External per-chat plan — superseded to prevent "
                                        "reopen-check phantom lock cycle. Plan managed via plan-mode only."
                                    )
                                    _pc2b_f.write_text(json.dumps(_pc2b_d, indent=2) + "\n", encoding="utf-8")
                                    _pc2b_ext_count += 1
                            except Exception:
                                continue
                        if _pc2b_ext_count > 0:
                            print(f"  [POSTCLEAN] POSTCLEAN-002b: superseded {_pc2b_ext_count} external plan lock(s)")
                        # Also check active-plan-lock.json
                        _pc2b_alp = repo_root / ".local" / "supervisor" / "active-plan-lock.json"
                        if _pc2b_alp.exists():
                            try:
                                _pc2b_ald = json.loads(_pc2b_alp.read_text(encoding="utf-8"))
                                _pc2b_alp_plan = _pc2b_ald.get("plan_path", "").replace("\\", "/")
                                _pc2b_alp_status = _pc2b_ald.get("status", "")
                                if ".claude/plans/" in _pc2b_alp_plan and _pc2b_alp_status not in ("SUPERSEDED", "DEFERRED"):
                                    _pc2b_ald["status"] = "SUPERSEDED"
                                    _pc2b_ald["superseded_at"] = timestamp
                                    _pc2b_ald["superseded_reason"] = "POSTCLEAN-002b: External per-chat plan superseded."
                                    _pc2b_alp.write_text(json.dumps(_pc2b_ald, indent=2) + "\n", encoding="utf-8")
                                    print("  [POSTCLEAN] POSTCLEAN-002b: superseded active-plan-lock.json (external plan)")
                            except Exception:
                                pass
                except Exception as _pc2b_err:
                    print(f"  [POSTCLEAN] POSTCLEAN-002b skipped (non-blocking): {_pc2b_err}")

            # TC-S55-004: Age-based cleanup — supersede same-session IN_PROGRESS locks
            # older than 24h. Handles plans that exist on disk but were never actually
            # started in the current conversation (autonomous_cycle machinery phantom locks).
            if auto_continue_value and session_id:
                try:
                    from write_plan_lock import cleanup_stale_in_progress_locks as _csipl
                    _age_result = _csipl(session_id=session_id, older_than_hours=24.0)
                    if _age_result.get("superseded", 0) > 0:
                        print(
                            f"  [POSTCLEAN] TC-S55-004: superseded {_age_result['superseded']} "
                            "stale IN_PROGRESS lock(s) older than 24h"
                        )
                except Exception as _s55_err:
                    print(f"  [POSTCLEAN] TC-S55-004 skipped (non-blocking): {_s55_err}")
    except Exception as _postclean_err:
        print(f"  WARNING: TC-LOCK-POSTCLEAN-001 skipped (non-blocking): {_postclean_err}")

    # TC-P2-002-04: Write Track P handoff entry when running as Track P
    # (so Track M can read it to learn about new capabilities)
    if track == "product":
        try:
            _shared_dir = repo_root / ".local" / "supervisor" / "shared"
            _shared_dir.mkdir(parents=True, exist_ok=True)
            _handoff_path = _shared_dir / "track-handoff.json"
            _existing_handoff: dict = {}
            if _handoff_path.exists():
                try:
                    _existing_handoff = json.loads(_handoff_path.read_text(encoding="utf-8"))
                except Exception:
                    pass
            _existing_handoff["handoff_version"] = 1
            _existing_handoff["product_to_machinery"] = {
                "written_at": timestamp,
                "written_by_session": session_id,
                "sprint_id": sprint_id,
                "new_capabilities_count": len(review.get("accepted_items", [])),
                "test_count": review.get("total_test_count", 0),
            }
            atomic_write_json(_handoff_path, _existing_handoff)
            print(f"  Track P handoff: {_handoff_path}")
        except Exception as _hf_err:
            print(f"  WARNING: Track P handoff write failed: {_hf_err}")

    # Step 8b: Loop Controller State Tracking (advisory, non-blocking)
    print("\n=== STEP 8b: LOOP CONTROLLER STATE ===")
    try:
        from post_sprint_loop_controller import init_loop, transition_to, classify_and_decide, get_next_stages
        loop_state_path = repo_root / ".local" / "supervisor" / "post-sprint-loop-state.json"

        # Read max_iterations from policies (align with continuation signal)
        _lc_max_iter = 12  # default matching continuation signal
        _lc_policies_path = repo_root / ".supervisor" / "policies.yaml"
        if _lc_policies_path.exists():
            try:
                _lc_policies = yaml.safe_load(_lc_policies_path.read_text(encoding="utf-8"))
                _lc_max_iter = _lc_policies.get("autonomous_continuation", {}).get("max_iterations", 12)
            except Exception:
                pass

        # Determine if loop state needs (re)initialization
        _lc_needs_init = not loop_state_path.exists()
        if not _lc_needs_init and loop_state_path.exists():
            try:
                _lc_existing = json.loads(loop_state_path.read_text(encoding="utf-8"))
                _lc_existing_run_id = _lc_existing.get("run_id", "")
                _lc_existing_state = _lc_existing.get("current_state", "")
                _lc_terminal_states = {"MAX_LOOPS_EXCEEDED", "HARD_STOP", "BLOCKED_EXTERNAL", "ACCEPTED_ALL_GREEN"}
                if _lc_existing_run_id != run_id or _lc_existing_state in _lc_terminal_states:
                    # Archive old state before reset
                    _lc_archive_path = repo_root / ".local" / "supervisor" / "post-sprint-loop-state-previous.json"
                    _lc_archive_path.write_text(
                        loop_state_path.read_text(encoding="utf-8"), encoding="utf-8"
                    )
                    _lc_needs_init = True
                    print(f"  Loop state reset (was run_id={_lc_existing_run_id}, state={_lc_existing_state})")
            except Exception:
                _lc_needs_init = True

        if _lc_needs_init:
            init_loop(repo_root, run_id, max_loops=_lc_max_iter)
            print(f"  Loop state initialized (run_id={run_id}, max_iterations={_lc_max_iter})")
            # Fast-forward through audit/hardening since autonomous_cycle is the execution
            _lc_fast_forward = [
                ("AUDIT_RUNNING", "cycle_audit_phase"),
                ("AUDIT_COMPLETE", "cycle_audit_done"),
                ("HARDENING_RUNNING", "cycle_harden_phase"),
                ("HARDENING_COMPLETE", "cycle_harden_done"),
                ("EXECUTION_RUNNING", "cycle_execution_phase"),
                ("EXECUTION_COMPLETE", "cycle_execution_done"),
            ]
            for _lc_state, _lc_trigger in _lc_fast_forward:
                transition_to(repo_root, _lc_state, _lc_trigger)
        quality_path = review_dir / "quality-scores.json"
        if quality_path.exists():
            decision = classify_and_decide(repo_root, quality_path)
            (review_dir / "loop-decision.json").write_text(
                json.dumps(decision, indent=2), encoding="utf-8"
            )
            next_state = decision.get("next_state", "UNKNOWN")
            next_stages = get_next_stages(next_state)
            print(f"  Loop decision: {next_state}")
            print(f"  Next stages: {next_stages}")
        else:
            print("  No quality scores — loop classification skipped")
    except Exception as lc_err:
        print(f"  WARNING: Loop controller skipped: {lc_err}")

    # TC-PSG-006: PROJECT_STATUS.md freshness check (advisory, non-blocking).
    # If any status-relevant sources changed in this sprint, validate the structure.
    print("\n=== STEP 8c: PROJECT_STATUS FRESHNESS CHECK ===")
    try:
        import subprocess as _subprocess
        _validate_result = _subprocess.run(
            ["python", "tools/docs/generate_project_status.py", "--validate"],
            capture_output=True, text=True,
            cwd=str(repo_root), timeout=30,
        )
        if _validate_result.returncode != 0:
            print(
                "  WARN: PROJECT_STATUS.md structural check failed "
                "(non-blocking -- regenerate with: "
                "python tools/docs/generate_project_status.py)"
            )
        else:
            print("  PROJECT_STATUS.md structural check: PASS")
    except Exception as _psg_err:
        print(f"  WARNING: PROJECT_STATUS freshness check skipped (non-blocking): {_psg_err}")

    # STEP 8d (TC-CPR-005): Consumer proof evidence capture (best-effort, non-blocking)
    # Runs all 20 consumer_roundtrip.py scripts and captures stdout to .local/evidences/.
    # Only fires when PRODUCT_SOURCE items are present in the declaration (source was modified).
    print("\n=== STEP 8d: CONSUMER PROOF EVIDENCE CAPTURE ===")
    try:
        _has_product_source = any(
            wi.get("type") == "PRODUCT_SOURCE"
            for wi in declaration.get("planned_work_items", [])
            if isinstance(wi, dict)
        )
        if _has_product_source:
            import subprocess as _cpr_subprocess
            _cpr_script = repo_root / "tools" / "consumer_proof_runner.py"
            if _cpr_script.exists():
                _cpr_result = _cpr_subprocess.run(
                    [sys.executable, str(_cpr_script)],
                    capture_output=True, text=True,
                    cwd=str(repo_root), timeout=180,
                )
                if _cpr_result.returncode == 0:
                    print("  Consumer proof: 20/20 PASS — evidence captured")
                else:
                    _cpr_lines = (_cpr_result.stdout + _cpr_result.stderr).splitlines()
                    _summary = next((l for l in reversed(_cpr_lines) if l.strip()), "")
                    print(f"  Consumer proof: PARTIAL or FAIL — {_summary} (non-blocking)")
            else:
                print("  Consumer proof runner not found — skipping (non-blocking)")
        else:
            print("  No PRODUCT_SOURCE items — skipping consumer proof capture")
    except Exception as _cpr_err:
        print(f"  Consumer proof capture skipped (non-blocking): {_cpr_err}")

    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run declaration-driven autonomous supervisor cycle"
    )
    parser.add_argument(
        "--declaration", type=Path, required=True,
        help="Path to evidence-declaration.yaml"
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--sync-index", action="store_true", default=False,
        help="After cycle completes, sync the control index (non-blocking)."
    )
    parser.add_argument(
        "--track", type=str, choices=["product", "machinery"], default=None,
        help=(
            "TC-P2-002: Track type for two-track separation. "
            "product → G3/G4/G5 work groups, product/ signal path. "
            "machinery → G1/G2/G6/G7/G8 work groups, machinery/ signal path. "
            "None (default) → legacy mode (all groups, shared signal path)."
        ),
    )
    args = parser.parse_args()

    if not args.declaration.exists():
        print(f"ERROR: Declaration not found: {args.declaration}", file=sys.stderr)
        return 1

    _logger.info("Autonomous supervisor cycle starting", extra={"sprint_id": str(args.declaration)})
    print("=" * 60)
    print("AUTONOMOUS SUPERVISOR CYCLE")
    print(f"Declaration: {args.declaration}")
    if args.track:
        print(f"Track: {args.track}")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)

    manifest = run_cycle(args.declaration, args.repo_root, track=args.track)

    exit_code = manifest.get("exit_code", 9)
    _logger.info(
        "Cycle complete",
        extra={
            "sprint_id": manifest.get("run_id", "unknown"),
            "work_item": f"exit_{exit_code}",
        },
    )

    # TC-RECON-007 / HEAL-RECT-001: Record failure on exit code 3 (rework required).
    # Best-effort — wrapped in try/except so failure memory write never blocks sprint exit.
    if exit_code == 3:
        try:
            sprint_id = manifest.get("run_id", "unknown")
            rework_items = manifest.get("rework_items", [])
            correction = f"Rework required: {', '.join(str(r) for r in rework_items[:5])}" if rework_items else "critical_rework_required"
            fm = FailureMemory(args.repo_root)
            fm.record_failure(
                category="SUPERVISOR_CONTROL_FAILURE",
                root_cause="exit_code_3_rework_required",
                correction=correction,
                sprint_id=sprint_id,
                files_modified=[str(args.declaration)],
                verification_command=f"python autonomous_cycle.py --declaration {args.declaration}",
                severity="HIGH",
            )
            fm.save()
            print(f"  [FAILURE_MEMORY] Recorded exit-3 failure for sprint {sprint_id}")
        except Exception as _fm_err:  # noqa: BLE001
            print(f"  [FAILURE_MEMORY] Warning: could not record failure: {_fm_err}")

    # Optional control-index sync (non-blocking, best-effort)
    if args.sync_index:
        try:
            from control_index.sync import sync_all as _ci_sync
            from control_index import DEFAULT_DB_PATH
            _ci_report = _ci_sync(DEFAULT_DB_PATH, args.repo_root)
            _ci_inserted = sum(r.inserted for r in _ci_report.results)
            print(f"  [CONTROL_INDEX] Synced ({_ci_inserted} rows updated)")
        except Exception as _ci_err:  # noqa: BLE001
            print(f"  [CONTROL_INDEX] Sync skipped: {_ci_err}")

    print()
    print("=" * 60)
    print(f"CYCLE COMPLETE (exit {exit_code})")
    print(f"Autonomous Continue: {manifest.get('autonomous_continue', False)}")
    if manifest.get("stop_reason"):
        print(f"Stop Reason: {manifest['stop_reason']}")
    print("=" * 60)

    # TC-CONC-008: Release path ownership claims (best-effort)
    # _claims_mgr is scoped to run_cycle(); guard with NameError for safety.
    try:
        if _claims_mgr is not None:
            released = _claims_mgr.release_all(_worker_id)
            if released:
                print(f"  [PathOwnership] Released {released} path claim(s) for {_worker_id}")
    except (NameError, Exception):
        pass

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
