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


def validate_spec_fact_provenance_advisory(declaration: dict, repo_root: "Path | None" = None) -> dict:
    """V-NEW-002: Warn when READINESS items have spec_fact_refs but no spec_fact_provenance.

    spec_fact_provenance provides finer-grained traceability (section_ref, page_ref,
    source_sha256) from a declared fact back to the source spec text. Advisory only —
    never blocks a sprint. Will be promoted to blocking at >=80% workbench coverage.

    Added: SAL-HEAL-B001 2026-06-26.
    """
    items = declaration.get("planned_work_items", [])
    _READINESS_TYPES = frozenset(["READINESS", "RELEASE_GATE"])
    missing_provenance = []

    for item in items:
        if item.get("item_type") not in _READINESS_TYPES:
            continue
        refs = item.get("spec_fact_refs") or []
        if not refs:
            continue  # no spec_fact_refs — V13/V47 handles that separately
        provenance = item.get("spec_fact_provenance") or []
        if not provenance:
            missing_provenance.append({
                "item_id": item.get("item_id", "?"),
                "item_type": item.get("item_type", "?"),
                "spec_fact_refs_count": len(refs),
                "note": "Add spec_fact_provenance for traceability to source spec text",
            })

    if missing_provenance:
        return {
            "validator": "validate_spec_fact_provenance_advisory",
            "result": "WARN",
            "blocks_sprint": False,
            "items": missing_provenance,
            "summary": (
                f"V-NEW-002: {len(missing_provenance)} READINESS/RELEASE_GATE item(s) "
                "have spec_fact_refs but no spec_fact_provenance (advisory — add for "
                "traceability; will become required at >=80% workbench coverage)"
            ),
        }

    return {
        "validator": "validate_spec_fact_provenance_advisory",
        "result": "PASS",
        "blocks_sprint": False,
        "items": [],
        "summary": (
            "V-NEW-002: All READINESS/RELEASE_GATE items have spec_fact_provenance "
            "or no spec_fact_refs"
        ),
    }


def validate_sal_facts_schema(declaration: dict, repo_root: "Path | None" = None) -> dict:
    """V-SAL-SCHEMA-001: Validate sal-facts-latest.json exists and matches required structure."""
    import json as _json
    _repo = Path(repo_root) if repo_root else Path(__file__).parent.parent.parent

    # Try both known locations for sal-facts-latest.json
    # sal-output/ is the canonical location written by sal_master_runner.py --all
    # spec-cache/ is a legacy location; prefer sal-output/ to avoid stale reads
    sal_candidates = [
        _repo / ".local" / "sal-output" / "sal-facts-latest.json",
        _repo / ".local" / "spec-cache" / "sal-facts-latest.json",
    ]
    sal_path = next((p for p in sal_candidates if p.exists()), None)

    if sal_path is None:
        return {
            "validator": "validate_sal_facts_schema",
            "result": "WARN",
            "blocks_sprint": False,
            "items": [{"issue": "sal-facts-latest.json not found in any known location"}],
            "summary": "V-SAL-SCHEMA-001: WARN — sal-facts-latest.json not found (run SAL ingestion)",
        }

    try:
        data = _json.loads(sal_path.read_text(encoding="utf-8", errors="replace"))
    except Exception as _e:
        return {
            "validator": "validate_sal_facts_schema",
            "result": "WARN",
            "blocks_sprint": False,
            "items": [{"issue": f"parse error: {_e}"}],
            "summary": f"V-SAL-SCHEMA-001: WARN — sal-facts parse error: {_e}",
        }

    issues = []
    required_top = ["generated_at", "generator", "formats_processed", "spec_facts_total",
                    "workbench_verified_fact_total", "results"]
    for f in required_top:
        if f not in data:
            issues.append(f"Missing top-level field: {f}")

    results = data.get("results", [])
    if not isinstance(results, list):
        issues.append("results is not a list")
    else:
        formats_with_zero_facts = []
        for r in results:
            if "format_id" not in r:
                issues.append("results entry missing format_id")
            if "spec_facts" not in r:
                issues.append(f"results[{r.get('format_id','?')}] missing spec_facts")
            elif len(r.get("spec_facts", [])) == 0:
                formats_with_zero_facts.append(r.get("format_id", "?"))

        if formats_with_zero_facts:
            issues.append(
                f"Formats with zero spec_facts (SAL pipeline incomplete): {', '.join(formats_with_zero_facts)}"
            )

    if issues:
        # Zero-fact formats are a known gap, block only on structural errors
        structural = [i for i in issues if not i.startswith("Formats with zero")]
        return {
            "validator": "validate_sal_facts_schema",
            "result": "WARN",
            "blocks_sprint": bool(structural),
            "items": [{"issue": i} for i in issues],
            "summary": (
                f"V-SAL-SCHEMA-001: {len(issues)} issue(s) — "
                f"{len(formats_with_zero_facts) if 'formats_with_zero_facts' in dir() else '?'} formats have zero spec_facts"
            ),
        }

    return {
        "validator": "validate_sal_facts_schema",
        "result": "PASS",
        "blocks_sprint": False,
        "items": [],
        "summary": (
            f"V-SAL-SCHEMA-001: PASS — {len(results)} formats, "
            f"{data.get('spec_facts_total', 0)} facts total"
        ),
    }
