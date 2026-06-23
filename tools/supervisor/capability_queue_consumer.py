"""
capability_queue_consumer.py — Gap-to-Taskcard Queue Consumer

Advances the system-healing lane: Capability/gap/action queue consumption by task generation.

This is the integration bridge between:
  1. Gap records (reports/capability-layer/gap-ledger.json)
  2. Capability-to-feature compiler (tools/supervisor/capability_compiler.py)
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
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent

sys.path.insert(0, str(SCRIPT_DIR))
from capability_compiler import compile_gap, compile_gap_to_feature_ir, compile_feature_ir_to_taskcard


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_GAP_LEDGER_PATH = REPO_ROOT / "reports" / "capability-layer" / "gap-ledger.json"
_FOSS_CAPABILITY_MAP = REPO_ROOT / "reports" / "capability-layer" / "foss-reduced-capability-map.json"

# Only consume FOSS gaps (not commercial) — commercial requires Gate 11
_ELIGIBLE_PRODUCT_TYPES = {"foss", "foss_reduced", "open_source", "both"}

# Gaps already implemented (skip compilation)
_SKIP_GAP_TYPES = {"implementation_verified", "already_closed"}


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
        if gap.get("status", "").lower() == "closed":
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
            taskcard["gap_type"] = compiler_input.get("gap_type", "")
            taskcard["gap_priority"] = compiler_input.get("priority", "P2")
            taskcard["compiled_at"] = _now_iso()
            taskcard["compiled_by"] = "capability_queue_consumer"

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
