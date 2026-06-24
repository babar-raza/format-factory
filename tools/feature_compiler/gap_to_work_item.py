"""gap_to_work_item.py — Phase 1 gap-ledger-driven work item generator (TC-FEATURE-COMPILER-001).

Reads gap-ledger.json, filters by format maturity >= P3 and severity >= MEDIUM,
then emits the top 10 work items to reports/feature-pipeline/derived-work-items.yaml.

CLI:
    python tools/feature_compiler/gap_to_work_item.py \\
        [--gap-ledger reports/capability-layer/gap-ledger.json] \\
        [--output reports/feature-pipeline/derived-work-items.yaml] \\
        [--max-items 10]

Exit codes:
    0 — success
    1 — gap-ledger not found or invalid
    2 — output write failure
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml as _yaml_lib
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

# ── Maturity ordering ──────────────────────────────────────────────────────────
_MATURITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "P4": 4, "P5": 5, "P6": 6, "P7": 7, "P8": 8}
_MIN_MATURITY_LEVEL = 3  # P3

# ── Severity weights (for scoring) ────────────────────────────────────────────
_SEVERITY_WEIGHT = {"CRITICAL": 5, "HIGH": 4, "MEDIUM": 3, "LOW": 2, "NONE": 1}
_MIN_SEVERITY = "MEDIUM"
_MIN_SEVERITY_WEIGHT = _SEVERITY_WEIGHT[_MIN_SEVERITY]

# ── Format maturity hints (fallback when gap lacks maturity info) ─────────────
# FODS and FODT are known P7/P8; others default to P3 for pilot filtering
_FORMAT_MATURITY_HINT: dict[str, str] = {
    "FODS": "P7",
    "FODT": "P8",
    "NDJSON": "P3",
    "CSV": "P4",
    "XCF": "P3",
    "ZST": "P4",
}
_DEFAULT_MATURITY = "P3"


def _format_maturity(gap: dict) -> int:
    """Return numeric maturity level for the gap's format."""
    fmt = gap.get("format", "").upper()
    hint = _FORMAT_MATURITY_HINT.get(fmt, _DEFAULT_MATURITY)
    return _MATURITY_ORDER.get(hint, 3)


def _severity_weight(gap: dict) -> int:
    """Return numeric severity weight."""
    # gap_type maps loosely to severity; use commercial/foss impact as proxy
    ci = gap.get("commercial_impact", "NONE")
    fi = gap.get("foss_impact", "NONE")
    # Use max of both impacts
    ci_w = _SEVERITY_WEIGHT.get(ci, 1)
    fi_w = _SEVERITY_WEIGHT.get(fi, 1)
    return max(ci_w, fi_w, _SEVERITY_WEIGHT.get("MEDIUM", 3) if gap.get("blocks_poc") else 1)


def _item_score(gap: dict) -> float:
    """Score = severity_weight * format_maturity_weight (higher = higher priority)."""
    return _severity_weight(gap) * _format_maturity(gap)


def _is_implementation_verified(gap: dict) -> bool:
    state = gap.get("current_state", "")
    return state in ("implementation_verified",)


def filter_gaps(gaps: list[dict]) -> list[dict]:
    """Apply Phase 1 filter: format maturity >= P3, severity >= MEDIUM, not verified."""
    result = []
    for gap in gaps:
        if gap.get("status") == "closed":
            continue
        if _format_maturity(gap) < _MIN_MATURITY_LEVEL:
            continue
        if _severity_weight(gap) < _MIN_SEVERITY_WEIGHT:
            continue
        if _is_implementation_verified(gap):
            continue
        result.append(gap)
    return result


def _gap_to_work_item(gap: dict, score: float) -> dict:
    gap_id = gap.get("gap_id", "")
    fmt = gap.get("format", "")
    cap = gap.get("capability_name", "")
    return {
        "item_id": f"WI-{gap_id}",
        "title": f"{cap} for {fmt}",
        "gap_ledger_ref": gap_id,
        "lane": "product",
        "priority": int(score),
        "format": fmt,
        "capability": cap,
        "gap_type": gap.get("gap_type", ""),
        "description": gap.get("suggested_taskcard", "") or f"Implement {cap} for {fmt}.",
        "verification": gap.get("suggested_verification", ""),
        "commercial_impact": gap.get("commercial_impact", "NONE"),
        "foss_impact": gap.get("foss_impact", "NONE"),
        "blocks_poc": bool(gap.get("blocks_poc")),
        "spec_facts": gap.get("spec_facts") or [],
    }


def compile(
    gaps: list[dict],
    max_items: int = 10,
) -> list[dict]:
    """Filter, score, sort, and return top N work items."""
    filtered = filter_gaps(gaps)
    scored = [(gap, _item_score(gap)) for gap in filtered]
    scored.sort(key=lambda x: (-x[1], x[0].get("gap_id", "")))
    items = [_gap_to_work_item(gap, score) for gap, score in scored[:max_items]]
    return items


def run(
    gap_ledger_path: Path,
    output_path: Path,
    max_items: int = 10,
) -> int:
    if not gap_ledger_path.exists():
        print(f"ERROR: gap-ledger not found: {gap_ledger_path}", file=sys.stderr)
        return 1

    try:
        ledger = json.loads(gap_ledger_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: cannot parse gap-ledger: {exc}", file=sys.stderr)
        return 1

    if not isinstance(ledger.get("gaps"), list):
        print("ERROR: gap-ledger missing 'gaps' list", file=sys.stderr)
        return 1

    gaps: list[dict] = ledger["gaps"]
    items = compile(gaps, max_items=max_items)

    output_data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": str(gap_ledger_path),
        "total_input_gaps": len(gaps),
        "filtered_count": len(items),
        "max_items": max_items,
        "items": items,
    }

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if _HAS_YAML:
            output_path.write_text(
                _yaml_lib.dump(output_data, default_flow_style=False, allow_unicode=True),
                encoding="utf-8",
            )
        else:
            # Fallback to JSON with .yaml extension
            output_path.write_text(
                json.dumps(output_data, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        print(f"Wrote {len(items)} work items to {output_path}", file=sys.stderr)
    except OSError as exc:
        print(f"ERROR: cannot write output: {exc}", file=sys.stderr)
        return 2

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate gap-ledger-driven work items (Phase 1)")
    parser.add_argument(
        "--gap-ledger",
        type=Path,
        default=Path("reports/capability-layer/gap-ledger.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/feature-pipeline/derived-work-items.yaml"),
    )
    parser.add_argument("--max-items", type=int, default=10)
    args = parser.parse_args()
    sys.exit(run(args.gap_ledger, args.output, args.max_items))


if __name__ == "__main__":
    main()
