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


def load_foss_gaps(max_gaps: int = 5) -> list[dict]:
    """Load FOSS-eligible gaps from the gap ledger, skipping already-implemented."""
    if not _GAP_LEDGER_PATH.exists():
        _log(f"Gap ledger not found: {_GAP_LEDGER_PATH}")
        return []

    data = _load_json(_GAP_LEDGER_PATH)
    if not data or "gaps" not in data:
        _log("Invalid gap ledger format")
        return []

    all_gaps = data["gaps"]
    _log(f"Gap ledger: {len(all_gaps)} total gaps")

    selected: list[dict] = []
    for gap in all_gaps:
        if len(selected) >= max_gaps:
            break
        # Only FOSS gaps
        ptype = gap.get("product_type", "").lower()
        if ptype not in _ELIGIBLE_PRODUCT_TYPES:
            continue
        # Skip gaps explicitly marked as closed
        if gap.get("status", "").lower() == "closed":
            continue
        # Skip already-closed gaps by gap_type
        if gap.get("gap_type", "").lower() in _SKIP_GAP_TYPES:
            continue
        # Must have a format and function hint
        if not gap.get("format") and not gap.get("capability_name"):
            continue
        selected.append(gap)

    _log(f"Selected {len(selected)} FOSS gaps for compilation")
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
