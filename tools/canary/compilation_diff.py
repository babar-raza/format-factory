"""compilation_diff.py — Compare stable vs candidate gap compiler output.

CLI:
  python tools/canary/compilation_diff.py \
    --ledger reports/capability-layer/gap-ledger.json \
    [--candidate-module tools.supervisor.capability_feature_compiler_candidate] \
    --output reports/canary/compilation-diff-YYYYMMDD.yaml

Default (no --candidate-module): stable vs stable (idempotency check, expects empty diff).
With --candidate-module: stable vs candidate.

Output YAML fields:
  comparison_date, stable_module, candidate_module,
  total_stable_items, total_candidate_items, priority_changes (list),
  format_coverage_changes (list), new_items_surfaced (list), items_dropped (list),
  recommendation (str: SAFE_TO_DEPLOY | REVIEW_REQUIRED | HOLD)
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from datetime import date
from pathlib import Path

import yaml

_STABLE_MODULE = "tools.supervisor.capability_feature_compiler"
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _ensure_sys_path() -> None:
    tools_path = str(_REPO_ROOT / "tools")
    if tools_path not in sys.path:
        sys.path.insert(0, tools_path)
    supervisor_path = str(_REPO_ROOT / "tools" / "supervisor")
    if supervisor_path not in sys.path:
        sys.path.insert(0, supervisor_path)


def load_compiler(module_path: str):
    """Import and return compiler module by dotted path."""
    _ensure_sys_path()
    # Support both fully qualified (tools.supervisor.X) and bare (X) module paths
    try:
        return importlib.import_module(module_path)
    except ModuleNotFoundError:
        # Try relative to tools/supervisor/
        bare = module_path.split(".")[-1]
        return importlib.import_module(bare)


def run_compiler(compiler_module, ledger_path: Path) -> list[dict]:
    """Run compile_gaps on ledger and return the items list."""
    raw = json.loads(ledger_path.read_text(encoding="utf-8"))
    gaps = raw if isinstance(raw, list) else raw.get("gaps", raw.get("items", []))
    items, _ = compiler_module.compile_gaps(gaps)
    return items


def diff_outputs(stable: list[dict], candidate: list[dict]) -> dict:
    """Compute diff between stable and candidate compiler outputs."""
    stable_ids = {(i.get("format", ""), i.get("capability_name", "")): i for i in stable}
    cand_ids = {(i.get("format", ""), i.get("capability_name", "")): i for i in candidate}

    priority_changes = []
    for key in stable_ids:
        if key in cand_ids:
            s_pri = stable_ids[key].get("priority")
            c_pri = cand_ids[key].get("priority")
            if s_pri != c_pri:
                priority_changes.append({
                    "format": key[0],
                    "capability": key[1],
                    "stable_priority": s_pri,
                    "candidate_priority": c_pri,
                })

    stable_formats = {i.get("format", "") for i in stable}
    cand_formats = {i.get("format", "") for i in candidate}
    format_coverage_changes = []
    for fmt in stable_formats - cand_formats:
        format_coverage_changes.append({"format": fmt, "change": "dropped"})
    for fmt in cand_formats - stable_formats:
        format_coverage_changes.append({"format": fmt, "change": "added"})

    new_items = [
        {"format": k[0], "capability": k[1]}
        for k in cand_ids if k not in stable_ids
    ]
    dropped_items = [
        {"format": k[0], "capability": k[1]}
        for k in stable_ids if k not in cand_ids
    ]

    if dropped_items:
        recommendation = "HOLD"
    elif priority_changes or format_coverage_changes:
        recommendation = "REVIEW_REQUIRED"
    else:
        recommendation = "SAFE_TO_DEPLOY"

    return {
        "priority_changes": priority_changes,
        "format_coverage_changes": format_coverage_changes,
        "new_items_surfaced": new_items,
        "items_dropped": dropped_items,
        "recommendation": recommendation,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare stable vs candidate gap compiler output")
    parser.add_argument("--ledger", type=Path, required=True, help="Path to gap-ledger.json")
    parser.add_argument(
        "--candidate-module", type=str, default="",
        help="Dotted module path for candidate compiler (default: stable vs stable)"
    )
    parser.add_argument("--output", type=Path, required=True, help="Output YAML path")
    args = parser.parse_args()

    if not args.ledger.exists():
        print(f"ERROR: ledger not found: {args.ledger}", file=sys.stderr)
        return 1

    stable_mod = load_compiler(_STABLE_MODULE)
    candidate_mod = load_compiler(args.candidate_module) if args.candidate_module else stable_mod
    candidate_name = args.candidate_module or _STABLE_MODULE

    stable_items = run_compiler(stable_mod, args.ledger)
    candidate_items = run_compiler(candidate_mod, args.ledger)

    diff = diff_outputs(stable_items, candidate_items)
    output = {
        "comparison_date": date.today().isoformat(),
        "stable_module": _STABLE_MODULE,
        "candidate_module": candidate_name,
        "total_stable_items": len(stable_items),
        "total_candidate_items": len(candidate_items),
        **diff,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(yaml.dump(output, default_flow_style=False), encoding="utf-8")
    print(f"OK: diff written to {args.output}")
    print(f"  Recommendation: {output['recommendation']}")
    print(f"  Stable: {output['total_stable_items']} items | Candidate: {output['total_candidate_items']} items")
    return 0


if __name__ == "__main__":
    sys.exit(main())
