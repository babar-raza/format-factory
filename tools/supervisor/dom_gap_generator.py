"""dom_gap_generator.py — TC-PCL-001 (peppy-crafting-lark)

Creates Lane B DOM advancement gaps in gap-ledger.json.
Idempotent: running twice produces identical ledger state.
Gap IDs are deterministic: same format + dom_target + behavior = same ID.

Usage:
    python tools/supervisor/dom_gap_generator.py [--dry-run] [--ledger PATH] [--policies PATH]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_LEDGER_PATH = REPO_ROOT / "registry" / "product-deepening-ledger.yaml"
DEFAULT_GAP_LEDGER_PATH = REPO_ROOT / "reports" / "capability-layer" / "gap-ledger.json"
DEFAULT_POLICIES_PATH = REPO_ROOT / ".supervisor" / "policies.yaml"

_MATURITY_ORDER = {"D0": 0, "D1": 1, "D2": 2, "D3": 3, "D4": 4, "D5": 5}
_DOM_LEVELS = ["D0", "D1", "D2", "D3", "D4", "D5"]

_BEHAVIOR_MAP: dict[str, dict] = {
    "D2": {
        "behavior": "MUTATION-AND-ROUNDTRIP",
        "desc": "mutate element property, write to disk, re-parse, verify mutation persisted",
    },
    "D3": {
        "behavior": "NESTED-TRAVERSAL-MUTATION",
        "desc": "traverse nested elements, mutate, verify in roundtrip",
    },
    "D4": {
        "behavior": "NESTED-MUTATION-PERSISTENCE",
        "desc": "nested structure mutation persists through full write-parse cycle",
    },
    "D5": {
        "behavior": "FULL-SCHEMA-ROUNDTRIP",
        "desc": "complete schema roundtrip with all element types preserved",
    },
}

_PRIORITY_MAP = {"D2": "P1", "D3": "P1", "D4": "P2", "D5": "P3"}


def _next_target(current: str, ceiling: str) -> Optional[str]:
    try:
        ci = _MATURITY_ORDER[current]
        cei = _MATURITY_ORDER[ceiling]
    except KeyError:
        return None
    ni = ci + 1
    return _DOM_LEVELS[ni] if ni <= cei else None


def _make_gap_id(format_name: str, target: str, behavior: str) -> str:
    return f"GAP-{format_name.upper()}-DOM-{target}-{behavior}-001"


def _make_gap_entry(format_name: str, target: str, current: str) -> dict:
    bdef = _BEHAVIOR_MAP.get(target, {
        "behavior": "DOM-ADVANCEMENT",
        "desc": f"advance {format_name} DOM to {target}",
    })
    behavior = bdef["behavior"]
    gap_id = _make_gap_id(format_name, target, behavior)
    fmt_lower = format_name.lower()
    return {
        "gap_id": gap_id,
        "format": format_name.upper(),
        "lane": "B",
        "dom_target": target,
        "current_dom_maturity": current,
        "required_behavior": bdef["desc"],
        "gap_type": f"dom_maturity_{target.lower()}",
        "capability_name": f"dom_advancement_{target.lower()} for {fmt_lower}",
        "deepening_lane": "dom",
        "product_type": "foss",
        "status": "open",
        "priority": _PRIORITY_MAP.get(target, "P2"),
        "dom_impact": "HIGH",
        "blocks_poc": False,
        "blocks_readiness": False,
        "commercial_impact": "MEDIUM",
        "foss_impact": "HIGH",
        "owning_lane": 1,
        "suggested_taskcard": "",
        "suggested_verification": f".venv/Scripts/pytest tests/python/{fmt_lower}/ -v",
        "blockers": [],
        "spec_facts": [],
        "supplemental": True,
        "generated_by": "dom_gap_generator",
    }


def _load_ledger(ledger_path: Path) -> list[dict]:
    try:
        import yaml
        data = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"Cannot load ledger {ledger_path}: {exc}") from exc
    if not isinstance(data, list):
        raise RuntimeError(f"Ledger must be a list, got {type(data)}")
    return data


def _load_policies(policies_path: Optional[Path]) -> dict:
    if not policies_path or not policies_path.exists():
        return {}
    try:
        import yaml
        return yaml.safe_load(policies_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def run(
    ledger_path: Path = DEFAULT_LEDGER_PATH,
    gap_ledger_path: Path = DEFAULT_GAP_LEDGER_PATH,
    policies_path: Optional[Path] = DEFAULT_POLICIES_PATH,
    dry_run: bool = False,
    format_filter: Optional[str] = None,
) -> dict:
    """Generate Lane B DOM gaps. Returns summary dict with added/skipped counts."""
    ledger = _load_ledger(ledger_path)

    try:
        raw = json.loads(gap_ledger_path.read_text(encoding="utf-8", errors="replace"))
    except Exception as exc:
        return {"error": str(exc), "added": 0, "skipped": 0}

    gaps: list[dict] = raw.get("gaps", []) if isinstance(raw, dict) else raw
    existing_ids: set[str] = {g.get("gap_id", "") for g in gaps}

    # Eligibility: python runtime, FULL or PARTIAL applicability, below ceiling
    # Use first python entry per format (deduplicate)
    seen_formats: set[str] = set()
    eligible: list[dict] = []
    for entry in ledger:
        fmt = str(entry.get("format", "")).lower()
        runtime = str(entry.get("runtime", "python")).lower()
        if runtime not in ("python", ""):
            continue
        if fmt in seen_formats:
            continue
        applicability = str(entry.get("dom_applicability", "")).upper()
        if applicability not in ("FULL", "PARTIAL"):
            continue
        current = entry.get("lane_b_maturity", "D0")
        ceiling = entry.get("lane_b_ceiling", "D5")
        target = _next_target(current, ceiling)
        if target is None:
            continue  # at ceiling
        if format_filter and fmt != format_filter.lower():
            continue
        seen_formats.add(fmt)
        eligible.append({"format": fmt, "current": current, "target": target})

    new_entries: list[dict] = []
    skipped = 0
    for item in eligible:
        entry = _make_gap_entry(item["format"], item["target"], item["current"])
        if entry["gap_id"] in existing_ids:
            skipped += 1
        else:
            new_entries.append(entry)

    if not dry_run and new_entries:
        if isinstance(raw, dict):
            raw["gaps"] = gaps + new_entries
            out = raw
        else:
            out = {"schema_version": "1.0", "gaps": gaps + new_entries,
                   "total_gaps": len(gaps) + len(new_entries)}
        gap_ledger_path.write_text(json.dumps(out, indent=2), encoding="utf-8")

    if dry_run:
        for e in new_entries:
            print(f"  WOULD ADD: {e['gap_id']} (format={e['format']}, target={e['dom_target']})")
        for item in eligible:
            test_id = _make_gap_id(item["format"].upper(), item["target"],
                                   _BEHAVIOR_MAP.get(item["target"], {}).get("behavior", "DOM-ADVANCEMENT"))
            if test_id in existing_ids:
                print(f"  SKIP (already exists): {test_id}")

    added = len(new_entries)
    print(f"Added {added} new Lane B DOM gaps. Skipped {skipped} duplicates.")
    return {"added": added, "skipped": skipped, "eligible": len(eligible), "dry_run": dry_run}


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Lane B DOM gaps in gap-ledger.json")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be added without modifying file")
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER_PATH,
                        help="Path to product-deepening-ledger.yaml")
    parser.add_argument("--policies", type=Path, default=DEFAULT_POLICIES_PATH,
                        help="Path to policies.yaml")
    parser.add_argument("--format", dest="format_filter",
                        help="Restrict to single format (e.g. fods)")
    args = parser.parse_args()

    result = run(
        ledger_path=args.ledger,
        gap_ledger_path=DEFAULT_GAP_LEDGER_PATH,
        policies_path=args.policies,
        dry_run=args.dry_run,
        format_filter=args.format_filter,
    )
    if "error" in result:
        print(f"ERROR: {result['error']}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
