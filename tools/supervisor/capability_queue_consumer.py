"""
capability_queue_consumer.py — Gap-to-Taskcard Queue Consumer

Advances the system-healing lane: Capability/gap/action queue consumption by task generation.

This is the integration bridge between:
  1. Gap records (reports/capability-layer/gap-ledger.json)
  2. The backward-compatible compile_gap/compile_gap_to_feature_ir/compile_feature_ir_to_taskcard
     API in tools/capability_layer/capability_compiler.py (NOT tools/supervisor/capability_compiler.py
     — see TC-EXT-002 remediation note below; the two files share function names for unrelated
     purposes and this consumer needs the capability_layer (L03) implementation specifically)
  3. Autonomous loop runner (tools/supervisor/autonomous_loop_runner.py)

It selects FOSS gaps from the gap ledger that are uncompiled, compiles them
to taskcards via capability_compiler, and writes them to the output directory.
This proves the gap -> taskcard -> execution pipeline is live.

Usage:
    python tools/supervisor/capability_queue_consumer.py \\
        --max-gaps 3 \\
        --output-dir .local/evidences/<run_id>/taskcards/compiled/
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent

# TC-OCRD-B2: Optional control index integration — non-blocking if DB absent
try:
    sys.path.insert(0, str(SCRIPT_DIR))
    from control_index import get_connection, DEFAULT_DB_PATH
    from control_index.gap_selection import get_exhausted_gaps, write_exhausted_gaps_json
    _CONTROL_INDEX_AVAILABLE = True
except ImportError:
    _CONTROL_INDEX_AVAILABLE = False

# TC-EXT-002 remediation (2026-07-15): tools/supervisor/capability_compiler.py (L14, feature
# compilation) and tools/capability_layer/capability_compiler.py (L03, SAL-driven derivation)
# both define same-named compile_gap/compile_gap_to_feature_ir/compile_feature_ir_to_taskcard
# functions for genuinely different purposes. This consumer needs L03's file specifically — it
# carries an explicit "Backward-compatible API (TC-CAP-011/TC-C8)" section built for exactly
# this consumer (see tools/capability_layer/capability_compiler.py, and
# tests/capability_layer/test_end_to_end_pipeline.py, which asserts this same resolution).
# Previously this relied on sys.path insertion order (a later sys.path.insert(0, ...) here
# happening to outrank an earlier one) to win a same-basename collision — correct today, but
# silently reroutable to the wrong (L14) module by an unrelated future reordering, with no
# import error, since both files' functions share signatures. Loaded explicitly by file path
# instead, so the target is pinned regardless of sys.path state.
_CAPABILITY_LAYER_COMPILER_PATH = REPO_ROOT / "tools" / "capability_layer" / "capability_compiler.py"
_spec = importlib.util.spec_from_file_location(
    "capability_layer_compiler", str(_CAPABILITY_LAYER_COMPILER_PATH)
)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Unable to load capability_layer compiler from {_CAPABILITY_LAYER_COMPILER_PATH}")
_capability_layer_compiler = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_capability_layer_compiler)
compile_gap = _capability_layer_compiler.compile_gap
compile_gap_to_feature_ir = _capability_layer_compiler.compile_gap_to_feature_ir
compile_feature_ir_to_taskcard = _capability_layer_compiler.compile_feature_ir_to_taskcard


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# TC-CAP-008/TC-CAP-011: Prefer active split; fall back to full ledger if not yet created
_GAP_LEDGER_ACTIVE = REPO_ROOT / "reports" / "capability-layer" / "gap-ledger-active.json"
_GAP_LEDGER_FULL = REPO_ROOT / "reports" / "capability-layer" / "gap-ledger.json"
_GAP_LEDGER_PATH = _GAP_LEDGER_ACTIVE if _GAP_LEDGER_ACTIVE.exists() else _GAP_LEDGER_FULL
# TC-CAP-011: Removed dead _FOSS_CAPABILITY_MAP load — map was loaded but never used

# Only consume FOSS gaps (not commercial) — commercial requires Gate 11
_ELIGIBLE_PRODUCT_TYPES = {"foss", "foss_reduced", "open_source", "both"}

# Gaps already implemented (skip compilation)
_SKIP_GAP_TYPES = {"implementation_verified_no_tests", "already_closed"}

# Statuses that exclude a gap from work selection (mirrors capability_feature_compiler.py).
# TC-DEFERRED-FILTER-001: extended to cover all non-actionable statuses.
# TC-BOOL-003 (2026-07-12): replaced "implementation_verified" with
#   "implementation_verified_no_tests" — see capability_feature_compiler.py for rationale.
_SKIP_STATUSES = {
    "closed", "CLOSED",
    "DEFERRED_BY_DESIGN", "DEFERRED",
    "test_verified", "implementation_verified_no_tests",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path) -> dict | list | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def _log(msg: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


_PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "P4": 4, "P5": 5}
_ASSIGNED_GAPS_PATH = REPO_ROOT / ".local" / "supervisor" / "assigned-gaps.json"


def _priority_sort_key(gap: dict) -> tuple:
    """Sort key: priority (P0 first), then gap_id alphabetically for determinism."""
    p = _PRIORITY_ORDER.get(gap.get("priority", "P4"), 4)
    return (p, gap.get("gap_id", ""))


def _load_assigned_gaps() -> dict:
    """Load previously assigned gaps from tracking file."""
    if _ASSIGNED_GAPS_PATH.exists():
        try:
            return json.loads(_ASSIGNED_GAPS_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _record_assigned_gaps(gaps: list[dict], sprint_id: str = "") -> None:
    """Record which gaps were assigned in this sprint."""
    assigned = _load_assigned_gaps()
    for g in gaps:
        gid = g.get("gap_id", "")
        if gid:
            assigned[gid] = {"sprint_id": sprint_id, "assigned_at": _now_iso()}
    _ASSIGNED_GAPS_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(_ASSIGNED_GAPS_PATH, assigned)


def load_foss_gaps(max_gaps: int = 5) -> list[dict]:
    """Load FOSS-eligible gaps from the gap ledger, sorted by priority.

    Deterministic selection: gaps are sorted by priority (P0 first), then
    alphabetically by gap_id. Previously-assigned gaps that haven't been
    completed are skipped to avoid re-assigning the same work.
    """
    if not _GAP_LEDGER_PATH.exists():
        _log(f"Gap ledger not found: {_GAP_LEDGER_PATH}")
        return []

    data = _load_json(_GAP_LEDGER_PATH)
    if not data or "gaps" not in data:
        _log("Invalid gap ledger format")
        return []

    all_gaps = data["gaps"]
    _log(f"Gap ledger: {len(all_gaps)} total gaps")

    # Filter eligible gaps
    eligible: list[dict] = []
    for gap in all_gaps:
        ptype = gap.get("product_type", "").lower()
        if ptype not in _ELIGIBLE_PRODUCT_TYPES:
            continue
        if gap.get("status") in _SKIP_STATUSES:
            continue
        if gap.get("gap_type", "").lower() in _SKIP_GAP_TYPES:
            continue
        if not gap.get("format") and not gap.get("capability_name"):
            continue
        eligible.append(gap)

    # Sort deterministically by priority then gap_id
    eligible.sort(key=_priority_sort_key)

    # Skip previously-assigned gaps (unless they were marked complete)
    assigned = _load_assigned_gaps()
    unassigned = [g for g in eligible if g.get("gap_id", "") not in assigned]

    # If all eligible gaps have been assigned, reset and select from full list
    if not unassigned and eligible:
        _log("All eligible gaps previously assigned — resetting assignment tracking")
        unassigned = eligible

    # TC-OCRD-B2: Filter exhausted gaps (non-blocking — DB may not be available)
    if _CONTROL_INDEX_AVAILABLE and DEFAULT_DB_PATH.exists():
        try:
            _db_conn = get_connection(DEFAULT_DB_PATH)
            _exhausted = get_exhausted_gaps(_db_conn, max_failed_attempts=3)
            _db_conn.close()
            if _exhausted:
                _before = len(unassigned)
                unassigned = [g for g in unassigned if g.get("gap_id", "") not in _exhausted]
                _removed = _before - len(unassigned)
                if _removed > 0:
                    print(
                        f"[gap-filter] Excluded {_removed} exhausted gap(s) "
                        f"from {_before} candidates (max_failed_attempts=3).",
                        file=sys.stderr,
                    )
            # Write exhausted gaps report for human inspection (best-effort)
            try:
                _report_path = REPO_ROOT / "reports" / "control-layer" / "exhausted-gaps.json"
                _db_conn2 = get_connection(DEFAULT_DB_PATH)
                write_exhausted_gaps_json(_db_conn2, _report_path, max_failed_attempts=3)
                _db_conn2.close()
            except Exception:
                pass
        except Exception as _e:
            print(f"[gap-filter] DB unavailable, skipping exhaustion filter: {_e}", file=sys.stderr)

    selected = unassigned[:max_gaps]
    _log(f"Selected {len(selected)} FOSS gaps for compilation (priority-ordered, deterministic)")
    return selected


def gap_to_compiler_input(gap: dict) -> dict:
    """Convert a gap ledger record to capability_compiler input format."""
    fmt = gap.get("format", "UNKNOWN")
    cap_name = gap.get("capability_name", "unknown_capability")

    # Normalize capability name to snake_case function name
    func_name = cap_name.lower().replace(" ", "_").replace("-", "_")
    # Remove generic suffixes
    for suffix in ("_function", "_api", "_capability"):
        if func_name.endswith(suffix):
            func_name = func_name[:-len(suffix)]

    return {
        "format_id": fmt,
        "function_name": func_name,
        "expected_signature": f"{func_name}(source) -> Any",
        "gap_id": gap.get("gap_id", ""),
        "gap_type": gap.get("gap_type", ""),
        "priority": gap.get("priority", "P2"),
        "commercial_impact": gap.get("commercial_impact", "NONE"),
    }


def compile_gaps_to_taskcards(
    gaps: list[dict],
    output_dir: Path,
) -> list[dict]:
    """Compile gap records to taskcards using capability_compiler."""
    output_dir.mkdir(parents=True, exist_ok=True)
    compiled: list[dict] = []

    for gap in gaps:
        compiler_input = gap_to_compiler_input(gap)
        fmt = compiler_input["format_id"]
        func = compiler_input["function_name"]
        _log(f"  Compiling gap: {gap.get('gap_id')} -> {fmt}.{func}")

        try:
            feature_ir = compile_gap_to_feature_ir(compiler_input)
            taskcard = compile_feature_ir_to_taskcard(feature_ir)

            # Enrich taskcard with gap metadata
            taskcard["source_gap_id"] = compiler_input.get("gap_id", "")
            taskcard["gap_ledger_ref"] = compiler_input.get("gap_id", "")  # TC-GUARD-001 requires this
            taskcard["gap_type"] = compiler_input.get("gap_type", "")
            taskcard["gap_priority"] = compiler_input.get("priority", "P2")
            taskcard["compiled_at"] = _now_iso()
            taskcard["compiled_by"] = "capability_queue_consumer"
            taskcard["status"] = "READY_TO_EXECUTE"
            taskcard["test_obligations"] = {
                "min_test_count": 5,
                "required_test_types": ["unit", "integration"],
                "test_dir": f"tests/python/{compiler_input.get('format_id', '').lower()}/",
            }

            # TC-SH-004: Set advisory_only based on priority + spec_facts.
            # FOSS P0-P1 with spec_facts -> advisory_only=false (executable).
            # Everything else -> advisory_only=true (advisory only).
            gap_priority = compiler_input.get("priority", "P2")
            has_spec_facts = bool(gap.get("spec_facts"))
            is_foss = gap.get("product_type", "").lower() in _ELIGIBLE_PRODUCT_TYPES
            is_commercial = gap.get("product_type", "").lower() == "commercial"
            if is_foss and gap_priority in ("P0", "P1") and has_spec_facts and not is_commercial:
                taskcard["advisory_only"] = False
            else:
                taskcard["advisory_only"] = True

            # Write taskcard to disk
            tc_path = output_dir / f"{taskcard['taskcard_id']}.json"
            _write_json(tc_path, taskcard)

            compiled.append({
                "gap_id": compiler_input.get("gap_id"),
                "gap_ledger_ref": compiler_input.get("gap_id"),  # TC-GUARD-001 requires this
                "format_id": fmt,
                "function_name": func,
                "taskcard_id": taskcard["taskcard_id"],
                "taskcard_path": str(tc_path),
                "status": "compiled",
            })
            _log(f"    -> Taskcard: {taskcard['taskcard_id']} -> {tc_path.name}")

        except Exception as exc:
            _log(f"    ERROR compiling {gap.get('gap_id')}: {exc}")
            compiled.append({
                "gap_id": compiler_input.get("gap_id"),
                "format_id": fmt,
                "function_name": func,
                "taskcard_id": None,
                "status": "failed",
                "error": str(exc),
            })

    return compiled


def run_consumer(
    max_gaps: int = 5,
    output_dir: Path | None = None,
) -> dict:
    """Execute the gap queue consumer.

    Returns:
        Summary dict with gaps_loaded, gaps_compiled, taskcards_written, output_dir.
    """
    if output_dir is None:
        output_dir = REPO_ROOT / ".local" / "capability-consumer" / "taskcards"
    output_dir = Path(output_dir)

    _log(f"Capability Queue Consumer — {_now_iso()}")
    _log(f"Max gaps: {max_gaps}")
    _log(f"Output dir: {output_dir}")

    gaps = load_foss_gaps(max_gaps)
    if not gaps:
        return {
            "status": "no_gaps_found",
            "gaps_loaded": 0,
            "gaps_compiled": 0,
            "taskcards_written": 0,
            "output_dir": str(output_dir),
        }

    # Record assigned gaps for deterministic tracking (Lane D)
    _record_assigned_gaps(gaps, sprint_id=_now_iso())

    results = compile_gaps_to_taskcards(gaps, output_dir)

    compiled = [r for r in results if r["status"] == "compiled"]
    failed = [r for r in results if r["status"] == "failed"]

    # Write summary
    summary = {
        "run_at": _now_iso(),
        "gaps_loaded": len(gaps),
        "gaps_compiled": len(compiled),
        "gaps_failed": len(failed),
        "taskcards_written": len(compiled),
        "output_dir": str(output_dir),
        "compiled_taskcards": compiled,
        "failed_compilations": failed,
        "status": "success" if compiled else "no_compilations",
    }
    summary_path = output_dir / "consumer-summary.json"
    _write_json(summary_path, summary)

    # TC-SH-003: Write compiled gap taskcards to persistent path for
    # autonomous_task_generator.py to read and incorporate into next-work-items.
    persistent_path = REPO_ROOT / ".local" / "supervisor" / "compiled-gap-taskcards.json"
    try:
        existing = _load_json(persistent_path)
        if not isinstance(existing, dict):
            existing = {"compiled": [], "last_updated": None}
        existing_ids = {c.get("gap_id") for c in existing.get("compiled", [])}
        new_entries = [c for c in compiled if c.get("gap_id") not in existing_ids]
        existing["compiled"] = existing.get("compiled", []) + new_entries
        existing["last_updated"] = _now_iso()
        existing["total_compiled"] = len(existing["compiled"])
        _write_json(persistent_path, existing)
        if new_entries:
            _log(f"Persisted {len(new_entries)} new compiled taskcards -> {persistent_path}")
    except Exception as exc:
        _log(f"WARNING: failed to persist compiled taskcards: {exc}")

    _log(f"Summary: {len(compiled)} compiled, {len(failed)} failed -> {summary_path}")
    return summary


def main() -> int:
    p = argparse.ArgumentParser(
        prog="capability_queue_consumer.py",
        description=(
            "Gap-to-Taskcard queue consumer.\n"
            "Selects FOSS gaps from the capability gap ledger and compiles\n"
            "them to executable taskcards via the capability_compiler.\n"
            "Advances the system-healing lane: gap queue consumption by task generation."
        ),
    )
    p.add_argument("--max-gaps", type=int, default=5,
                   help="Maximum gaps to compile in one run (default: 5)")
    p.add_argument("--output-dir",
                   default=str(REPO_ROOT / ".local" / "capability-consumer" / "taskcards"),
                   help="Output directory for compiled taskcards")
    args = p.parse_args()

    summary = run_consumer(
        max_gaps=args.max_gaps,
        output_dir=Path(args.output_dir),
    )

    print(f"\nCompiled: {summary['gaps_compiled']} taskcards")
    print(f"Output: {summary['output_dir']}")
    return 0 if summary["gaps_compiled"] >= 0 else 1


if __name__ == "__main__":
    sys.exit(main())
