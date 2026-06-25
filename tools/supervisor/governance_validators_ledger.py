"""governance_validators_ledger.py — V74: Ledger continuation gate validator.

Extracted from governance_validators_ext.py to keep that file within its baseline_loc_cap.

V74 (TC-PDL-005): Block PRODUCT_SOURCE/PRODUCT_TEST items for formats with
continuation_allowed=false in product-deepening-ledger.yaml.

Created: 2026-06-25
Task: TC-PDL-005 (sunny-crunching-galaxy)
"""
from __future__ import annotations

import re as _re
from pathlib import Path


def validate_ledger_continuation_gate(
    declaration: dict,
    repo_root: "Path | None" = None,
) -> dict:
    """V74 (TC-PDL-005): Block PRODUCT_SOURCE/PRODUCT_TEST items for formats with
    continuation_allowed=false in product-deepening-ledger.yaml.

    Formats with src_layout_status=mixed_model have continuation_allowed=false.
    Product deepening sprints for those formats must not proceed until LOC violations are healed.
    """
    if repo_root is None:
        repo_root = Path(__file__).parent.parent.parent
    repo_root = Path(repo_root)

    BLOCKED_ITEM_TYPES = {"PRODUCT_SOURCE", "PRODUCT_TEST"}

    items = declaration.get("work_items", [])
    if not items:
        items = declaration.get("planned_work_items", [])

    # Load ledger
    ledger_path = repo_root / "registry" / "product-deepening-ledger.yaml"
    if not ledger_path.exists():
        return {
            "validator": "validate_ledger_continuation_gate",
            "result": "SKIP",
            "blocks_sprint": False,
            "items": [],
            "summary": "V74: product-deepening-ledger.yaml not found — skipping",
        }

    try:
        import yaml as _yaml
        ledger_entries = _yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "validator": "validate_ledger_continuation_gate",
            "result": "WARN",
            "blocks_sprint": False,
            "items": [],
            "summary": f"V74: could not load ledger — {exc}",
        }

    # Build set of formats with continuation_allowed=false
    blocked_formats: set[str] = set()
    for entry in (ledger_entries or []):
        if not entry.get("continuation_allowed", True):
            blocked_formats.add(entry.get("format", "").lower())

    if not blocked_formats:
        return {
            "validator": "validate_ledger_continuation_gate",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V74: All formats have continuation_allowed=true",
        }

    _FORMAT_FROM_PATH_RE = _re.compile(
        r"src[/\\]python[/\\]([a-z][a-z0-9_]+)[/\\]",
        _re.IGNORECASE,
    )

    violations = []
    for item in items:
        item_type = item.get("item_type", "")
        if item_type not in BLOCKED_ITEM_TYPES:
            continue
        # Detect format from evidence_paths or changed_files
        paths = item.get("evidence_paths", []) + item.get("changed_files", [])
        for p in paths:
            m = _FORMAT_FROM_PATH_RE.search(str(p))
            if m:
                fmt = m.group(1).lower()
                if fmt in blocked_formats:
                    violations.append({
                        "item_id": item.get("item_id", "unknown"),
                        "item_type": item_type,
                        "format": fmt,
                        "path": str(p),
                        "reason": (
                            f"Format '{fmt}' has continuation_allowed=false "
                            "(src_layout=mixed_model, LOC violations unhealed). "
                            "Heal LOC violations before product deepening."
                        ),
                    })
                    break

    if violations:
        return {
            "validator": "validate_ledger_continuation_gate",
            "result": "FAIL",
            "blocks_sprint": True,
            "items": violations,
            "summary": (
                f"V74: {len(violations)} PRODUCT item(s) target format(s) with "
                f"continuation_allowed=false: "
                f"{sorted({v['format'] for v in violations})}"
            ),
        }
    return {
        "validator": "validate_ledger_continuation_gate",
        "result": "PASS",
        "blocks_sprint": False,
        "items": [],
        "summary": (
            f"V74: No PRODUCT items violate ledger continuation gate "
            f"({len(blocked_formats)} formats blocked, none targeted)"
        ),
    }
