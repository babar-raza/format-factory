"""
governance_validators_sal.py — SAL-specific governance validators (SAL-VHIP-001).
Extracted to keep governance_validators_ext.py within its baseline_loc_cap.
"""
from __future__ import annotations
from pathlib import Path


def validate_capability_fact_ratio(declaration: dict, repo_root: "Path | None" = None) -> dict:
    """V-NEW-001: Warn when capabilities/verified_facts ratio > 10 for a format (inflation check)."""
    import json as _json
    _repo = Path(repo_root) if repo_root else Path(__file__).parent.parent.parent

    sal_path = _repo / ".local" / "sal-output" / "sal-facts-latest.json"
    cap_path = _repo / "reports" / "capability-layer" / "unified-capability-map.json"

    if not sal_path.exists() or not cap_path.exists():
        return {
            "validator": "validate_capability_fact_ratio",
            "result": "SKIP",
            "blocks_sprint": False,
            "items": [],
            "summary": "V-NEW-001: Skipped — sal-facts or capability-map not found",
        }

    try:
        sal = _json.loads(sal_path.read_text(encoding="utf-8", errors="replace"))
        cap_data = _json.loads(cap_path.read_text(encoding="utf-8", errors="replace"))
    except Exception as _e:
        return {
            "validator": "validate_capability_fact_ratio",
            "result": "SKIP",
            "blocks_sprint": False,
            "items": [],
            "summary": f"V-NEW-001: Skipped — parse error: {_e}",
        }

    # Build format -> verified fact count from SAL
    sal_verified: dict = {}
    for r in sal.get("results", []):
        fmt = r.get("format_id", "").lower()
        facts = r.get("spec_facts", [])
        cnt = sum(1 for f in facts if f.get("fact_status") == "verified")
        if fmt and cnt > 0:
            sal_verified[fmt] = cnt

    # Build format -> capability count from unified capability map
    cap_count: dict = {}
    capabilities = cap_data if isinstance(cap_data, list) else cap_data.get("capabilities", [])
    for cap in capabilities:
        fmt = (cap.get("format_id") or cap.get("format") or "").lower()
        if fmt:
            cap_count[fmt] = cap_count.get(fmt, 0) + 1

    # Compute inflation ratios
    INFLATION_THRESHOLD = 10
    inflation_items = []
    for fmt, n_caps in sorted(cap_count.items()):
        n_facts = sal_verified.get(fmt, 0)
        if n_facts == 0:
            continue  # no facts at all — different validator handles this
        ratio = n_caps / n_facts
        if ratio > INFLATION_THRESHOLD:
            inflation_items.append({
                "format": fmt,
                "capabilities": n_caps,
                "verified_facts": n_facts,
                "ratio": round(ratio, 1),
            })

    if inflation_items:
        return {
            "validator": "validate_capability_fact_ratio",
            "result": "WARN",
            "blocks_sprint": False,
            "items": inflation_items,
            "summary": (
                f"V-NEW-001: {len(inflation_items)} format(s) have capabilities/facts ratio > {INFLATION_THRESHOLD} "
                f"(advisory only — existing capabilities not blocked)"
            ),
        }

    return {
        "validator": "validate_capability_fact_ratio",
        "result": "PASS",
        "blocks_sprint": False,
        "items": [],
        "summary": "V-NEW-001: All formats have acceptable capabilities/facts ratios",
    }
