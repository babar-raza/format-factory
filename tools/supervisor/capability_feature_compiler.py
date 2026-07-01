"""capability_feature_compiler.py — Translate gap-ledger.json gaps into next-work-items.json.

Implements the design spec in docs/code-quality/capability-feature-compiler-spec.md (TC-CAPABILITY-REPAIR-001).
TC-CAPABILITY-REPAIR-002 (cheerful-floating-glade): Phase 2 implementation.

CLI:
    python tools/supervisor/capability_feature_compiler.py \\
        --gap-ledger reports/capability-layer/gap-ledger.json \\
        --output reports/supervisor/next-work-items.json \\
        [--max-items 20] \\
        [--dry-run]

Exit codes:
    0 — success
    1 — gap-ledger not found or invalid schema
    2 — output write failure
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Priority scoring constants ────────────────────────────────────────────────

_BASE_PRIORITY: dict[str, int] = {
    "P0": 0, "P1": 10, "P2": 20, "P3": 30, "P4": 40,
    "P5": 50, "P6": 60, "P7": 70, "P8": 80,
}

_EVIDENCE_MAP: dict[str, str] = {
    "missing_test_coverage": "Tests added and passing",
    "missing_implementation": "Implementation committed, tests pass",
    "spec_parity_gap": "spec_qname on class, spec fact referenced",
    "architecture_only": "Behavioral implementation replacing stub",
    "missing_qname_registration": "QName registry entry with python_file",
    "missing_capability_annotation": "capability_ref in declaration",
}
_EVIDENCE_DEFAULT = "Work item accepted by supervisor pipeline"

# Lanes 14-15 are machinery-owned; skip them
_MAX_PRODUCT_LANE = 13

# Statuses that exclude a gap from work selection.
# CLOSED/closed: already implemented; DEFERRED_BY_DESIGN/DEFERRED: intentionally deferred;
# test_verified/implementation_verified: state beyond gap-level (capability is done).
# TC-DEFERRED-FILTER-001 (2026-06-25): extended to handle all non-actionable statuses.
_SKIP_STATUSES = {
    "closed", "CLOSED",
    "DEFERRED_BY_DESIGN", "DEFERRED",
    "test_verified", "implementation_verified",
}

# Statuses that mean "not yet an open gap"
_FAIL_STATUSES = {"implementation_verified"}


def _base_priority(gap: dict) -> int:
    prio = gap.get("priority", "P8")
    return _BASE_PRIORITY.get(prio, 80)


def _impact_penalty(gap: dict) -> int:
    ci = gap.get("commercial_impact", "NONE")
    fi = gap.get("foss_impact", "NONE")
    if ci == "HIGH" and fi == "HIGH":
        return -10
    if ci == "HIGH":
        return -5
    if fi == "HIGH":
        return -3
    return 0


def _blocker_bonus(gap: dict) -> int:
    bonus = 0
    if gap.get("blocks_poc"):
        bonus -= 8
    if gap.get("blocks_readiness"):
        bonus -= 5
    return bonus


def _score(gap: dict) -> int:
    base = _base_priority(gap) + _impact_penalty(gap) + _blocker_bonus(gap)
    fmt = gap.get("format", gap.get("product_id", "")).split("-")[0].lower()
    dl = _classify_deepening_lane(gap)
    base += _lane_balance_penalty(dl, fmt)
    return base


def _lane(gap: dict) -> str:
    owning_lane = gap.get("owning_lane", 1)
    try:
        lane_int = int(owning_lane)
    except (TypeError, ValueError):
        lane_int = 1
    return "product" if lane_int <= _MAX_PRODUCT_LANE else "machinery"


def _classify_deepening_lane(gap: dict) -> str:
    """Classify gap as feature or dom deepening work."""
    gap_type = gap.get("gap_type", "")
    cap = gap.get("capability_name", "").lower()
    if gap_type in ("spec_parity_gap", "architecture_only", "missing_qname_registration"):
        return "dom"
    if any(kw in cap for kw in ("object_model", "dom_", "navigation", "mutation", "spec_class")):
        return "dom"
    return "feature"


def _lane_balance_penalty(lane: str, format_name: str) -> int:
    """Soft penalty for overrepresented lane (starvation prevention)."""
    import yaml
    ledger_path = Path("registry/product-deepening-ledger.yaml")
    if not ledger_path.exists():
        return 0
    try:
        ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8")) or []
    except Exception:
        return 0
    entry = next((e for e in ledger if e.get("format") == format_name.lower()), {})
    mode = entry.get("execution_mode", "AUTO")
    if mode == "FEATURE_ONLY" and lane == "dom":
        return 999
    if mode == "DOM_ONLY" and lane == "feature":
        return 999
    a = entry.get("lane_a_consecutive", 0)
    b = entry.get("lane_b_consecutive", 0)
    threshold = entry.get("lane_starvation_threshold", 3)
    if lane == "feature" and a - b >= threshold:
        return 15
    if lane == "dom" and b - a >= threshold:
        return 15
    return 0


def _evidence_expected(gap: dict) -> str:
    return _EVIDENCE_MAP.get(gap.get("gap_type", ""), _EVIDENCE_DEFAULT)


def _is_external_gate(gap: dict) -> bool:
    return bool(gap.get("blocks_readiness") and gap.get("product_type") == "commercial")


def _description(gap: dict) -> str:
    suggested = gap.get("suggested_taskcard", "")
    if suggested:
        return suggested
    parts = []
    cap = gap.get("capability_name", "")
    fmt = gap.get("format", "")
    gtype = gap.get("gap_type", "")
    state = gap.get("current_state", "")
    if cap and fmt:
        parts.append(f"Implement {cap} for {fmt}.")
    if gtype:
        parts.append(f"Gap type: {gtype}.")
    if state:
        parts.append(f"Current state: {state}.")
    return " ".join(parts) or f"Close gap {gap.get('gap_id', '')}."


def _human_required(gap: dict) -> bool:
    blockers = gap.get("blockers") or []
    return any("TRUE_EXTERNAL_GATE" in str(b) for b in blockers)


def _gap_to_work_item(gap: dict, score: int) -> dict:
    gap_id = gap.get("gap_id", "")
    blockers = gap.get("blockers") or []
    verification = gap.get("suggested_verification", "")
    return {
        "item_id": f"WI-{gap_id}",
        "title": f"{gap.get('capability_name', 'Unknown')} for {gap.get('format', 'Unknown')}",
        "lane": _lane(gap),
        "priority": score,
        "description": _description(gap),
        "acceptance_criteria": verification or "Verification passes",
        "verification_command": verification,
        "evidence_expected": _evidence_expected(gap),
        "source": "gap_ledger",
        "stop_reason_adjudication": "agent-owned",
        "human_required": _human_required(gap),
        "blocked_by": blockers if blockers else None,
        "external_gate": _is_external_gate(gap),
        "gap_id": gap_id,
        "gap_ref": gap_id,
        "gap_ledger_ref": gap_id,
        "spec_facts": gap.get("spec_facts") or [],
        "deepening_lane": _classify_deepening_lane(gap),
    }


def _sort_key(item: dict) -> tuple:
    """Tie-breaking: score ASC, blocks_poc DESC, blocks_readiness DESC, gap_id ASC."""
    gap_ref = item.get("gap_id", "")
    return (item["priority"], gap_ref)


def compile_gaps(
    gaps: list[dict],
    max_items: int = 20,
) -> tuple[list[dict], list[dict]]:
    """Filter, score, deduplicate, and sort gaps.

    Returns (items, deduplicated_items).
    """
    # Step 1: filter
    filtered = []
    for gap in gaps:
        if gap.get("status") in _SKIP_STATUSES:
            continue
        try:
            lane_int = int(gap.get("owning_lane", 1))
        except (TypeError, ValueError):
            lane_int = 1
        if lane_int >= 14:
            continue
        filtered.append(gap)

    # Step 2: score
    scored = [(gap, _score(gap)) for gap in filtered]

    # Step 3: deduplicate by format+capability (keep lowest score)
    best: dict[tuple, tuple] = {}
    for gap, score in scored:
        key = (gap.get("format", ""), gap.get("capability_name", ""))
        if key not in best or score < best[key][1]:
            best[key] = (gap, score)

    deduped_gaps = {id(g) for g, _ in best.values()}
    dedup_items = [
        _gap_to_work_item(gap, sc)
        for gap, sc in scored
        if id(gap) not in deduped_gaps
    ]

    # Step 4: build work items from deduped set, sort, truncate
    items = [_gap_to_work_item(gap, sc) for gap, sc in best.values()]
    items.sort(key=_sort_key)
    return items[:max_items], dedup_items


def run(
    gap_ledger_path: Path,
    output_path: Path | None,
    max_items: int = 20,
    dry_run: bool = False,
) -> int:
    """Main compile + emit. Returns exit code."""
    if not gap_ledger_path.exists():
        print(f"ERROR: gap-ledger not found: {gap_ledger_path}", file=sys.stderr)
        return 1

    try:
        ledger = json.loads(gap_ledger_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: cannot parse gap-ledger: {exc}", file=sys.stderr)
        return 1

    schema_version = ledger.get("schema_version", "1.0")
    if not isinstance(ledger.get("gaps"), list):
        print("ERROR: gap-ledger missing 'gaps' list", file=sys.stderr)
        return 1

    gaps: list[dict] = ledger["gaps"]
    open_gaps = [g for g in gaps if g.get("status") not in _SKIP_STATUSES]

    items, dedup_items = compile_gaps(open_gaps, max_items=max_items)

    output = {
        "items": items,
        "work_selection_mode": "CAPABILITY_COMPILER",
        "stream": "mainstream",
        "compiler_run_id": datetime.now(timezone.utc).isoformat(),
        "gap_ledger_version": schema_version,
        "total_input_gaps": len(gaps),
        "open_gaps_processed": len(open_gaps),
        "deduplicated_items": dedup_items,
    }

    output_json = json.dumps(output, indent=2, ensure_ascii=False)

    if dry_run:
        print(output_json)
        return 0

    if output_path is None:
        print("ERROR: --output required unless --dry-run", file=sys.stderr)
        return 2

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output_json + "\n", encoding="utf-8")
        print(f"Wrote {len(items)} work items to {output_path}", file=sys.stderr)
    except OSError as exc:
        print(f"ERROR: cannot write output: {exc}", file=sys.stderr)
        return 2

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compile gap-ledger.json into next-work-items.json"
    )
    parser.add_argument(
        "--gap-ledger",
        type=Path,
        default=Path("reports/capability-layer/gap-ledger.json"),
        help="Path to gap-ledger.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path for next-work-items.json",
    )
    parser.add_argument("--max-items", type=int, default=20, help="Max work items to emit")
    parser.add_argument("--dry-run", action="store_true", help="Print to stdout, no file write")
    args = parser.parse_args()

    sys.exit(run(args.gap_ledger, args.output, args.max_items, args.dry_run))


if __name__ == "__main__":
    main()
