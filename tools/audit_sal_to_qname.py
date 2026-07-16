"""audit_sal_to_qname.py — Phase C (FF-FORENSIC-AUDIT-20260623)

Cross-references QName registry spec_fact_ref fields against sal-facts-latest.json.
For each registry entry with spec_fact_ref: FACT-*, verifies the fact exists
in the SAL output. Emits reports/sal-qname-gap-{date}.json.

Usage:
    python tools/audit_sal_to_qname.py [--out PATH] [--format FMT]
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml as _yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

_REPO = Path(__file__).parent.parent
# NOTE: reads from .local/spec-cache/sal-facts-latest.json (NOT .local/sal-output/)
# These are two different files. The spec-cache path is the canonical audit source.
# sal-output/ is populated by the SAL ingestion pipeline; spec-cache/ is the merged/resolved copy.
_SAL_PATH = _REPO / ".local/spec-cache/sal-facts-latest.json"
_REGISTRY_DIR = _REPO / "shared/qname-registry"
_OVERRIDES_PATH = _REPO / "shared/sal-fact-overrides.yaml"


_ALIASES_PATH = _REPO / "shared/sal-fact-id-aliases.json"


def _load_aliases() -> dict[str, str]:
    """Load the FACT-* → SAL-* alias map (TC-SAL-ID-006)."""
    if not _ALIASES_PATH.exists():
        return {}
    try:
        data = json.loads(_ALIASES_PATH.read_text(encoding="utf-8"))
        return data.get("aliases", {})
    except Exception:
        return {}


def load_sal_fact_id_overrides() -> dict[str, set[str]]:
    """Load committed SAL fact overrides from shared/sal-fact-overrides.yaml.

    This file commits facts that supplement the gitignored sal-facts-latest.json,
    ensuring 100% coverage survives a fresh checkout (TC-HRD-001).

    Returns:
        dict mapping format_id (lowercase) → set of fact IDs (both FACT-* and SAL-*)
    """
    if not _HAS_YAML or not _OVERRIDES_PATH.exists():
        return {}
    try:
        data = _yaml.safe_load(_OVERRIDES_PATH.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}

    overrides: dict[str, set[str]] = {}
    for entry in data.get("overrides", []):
        fmt = entry.get("format_id", "").lower()
        qname = entry.get("qname", "")
        fact_id = entry.get("fact_id", "")
        if qname.startswith("FACT-"):
            overrides.setdefault(fmt, set()).add(qname)
        if fact_id.startswith("SAL-"):
            overrides.setdefault(fmt, set()).add(fact_id)
    return overrides


_STORES_DIR = _REPO / "shared/sal-facts"


def load_committed_store_fact_ids() -> dict[str, set[str]]:
    """Load fact IDs from the committed canonical stores (shared/sal-facts/*.yaml).

    TC-GWB-H04: the committed stores are the source of truth for manually-seeded
    formats; consulting them directly makes this audit independent of the derived
    (gitignored) sal-facts-latest.json on a fresh checkout.
    """
    fact_ids: dict[str, set[str]] = {}
    if not _HAS_YAML or not _STORES_DIR.is_dir():
        return fact_ids
    for store_path in sorted(_STORES_DIR.glob("*.yaml")):
        try:
            store = _yaml.safe_load(store_path.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        fmt = str(store.get("format_id", store_path.stem)).lower()
        ids: set[str] = set()
        for fact in store.get("facts", []):
            for key in ("qname", "fact_id"):
                value = fact.get(key, "")
                if value.startswith(("FACT-", "SAL-")):
                    ids.add(value)
        if ids:
            fact_ids.setdefault(fmt, set()).update(ids)
    return fact_ids


def load_sal_fact_ids() -> dict[str, set[str]]:
    """Load SAL facts: committed stores + sal-facts-latest.json + overrides.

    Returns:
        dict mapping format_id (lowercase) → set of fact IDs (FACT-* and SAL-*)
    """
    fact_ids: dict[str, set[str]] = {}

    if _SAL_PATH.exists():
        try:
            data = json.loads(_SAL_PATH.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            data = {}
        results = data.get("results", [])
        for result in results:
            fmt = result.get("format_id", "").lower()
            facts = result.get("spec_facts", [])
            ids: set[str] = set()
            for fact in facts:
                qname = fact.get("qname", "")
                if qname.startswith("FACT-"):
                    ids.add(qname)
                fact_id = fact.get("fact_id", "")
                if fact_id.startswith("SAL-"):
                    ids.add(fact_id)
            fact_ids[fmt] = ids

    # Merge committed canonical stores (primary committed source, TC-GWB-H04)
    for fmt, ids in load_committed_store_fact_ids().items():
        fact_ids.setdefault(fmt, set()).update(ids)

    # Merge committed overrides (legacy overlay for formats without stores)
    for fmt, ids in load_sal_fact_id_overrides().items():
        fact_ids.setdefault(fmt, set()).update(ids)

    # Merge aliases so legacy FACT-* refs resolve to SAL-* IDs
    aliases = _load_aliases()
    for fmt_ids in fact_ids.values():
        extra: set[str] = set()
        for fid in fmt_ids:
            if fid in aliases:
                extra.add(aliases[fid])
        fmt_ids.update(extra)

    return fact_ids


def audit_format_sal_coverage(
    format_id: str,
    registry_path: Path,
    sal_ids_by_format: dict[str, set[str]],
) -> dict[str, Any]:
    """Audit a single format's qname registry against SAL facts.

    Returns per-format audit result with list of gaps.
    """
    if not _HAS_YAML:
        return {
            "format": format_id,
            "error": "pyyaml not installed",
            "gaps": [],
            "total_entries": 0,
            "entries_with_spec_fact_ref": 0,
            "entries_resolved": 0,
            "entries_missing_in_sal": 0,
        }

    try:
        entries = _yaml.safe_load(registry_path.read_text(encoding="utf-8")) or []
    except Exception as e:
        return {
            "format": format_id,
            "error": str(e),
            "gaps": [],
            "total_entries": 0,
            "entries_with_spec_fact_ref": 0,
            "entries_resolved": 0,
            "entries_missing_in_sal": 0,
        }

    # Build full SAL ID set for this format (may appear under format_id or variant)
    fmt_lower = format_id.lower()
    sal_ids: set[str] = sal_ids_by_format.get(fmt_lower, set())

    # Also check common variant keys (e.g. "fods" → "FACT-FODS-*")
    all_sal_ids: set[str] = set()
    for ids in sal_ids_by_format.values():
        all_sal_ids |= ids

    total = 0
    with_ref = 0
    resolved = 0
    missing = 0
    gaps = []

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        total += 1
        ref = entry.get("spec_fact_ref")
        if not ref or (not str(ref).startswith("FACT-") and not str(ref).startswith("SAL-")):
            continue
        with_ref += 1
        fact_id = str(ref)
        if fact_id in all_sal_ids:
            resolved += 1
        else:
            missing += 1
            gaps.append({
                "qname": entry.get("qname", ""),
                "spec_fact_ref": fact_id,
                "status": entry.get("status", ""),
                "issue": f"spec_fact_ref {fact_id!r} not found in sal-facts-latest.json",
                "severity": "WARN" if entry.get("status") in ("seeded", "architecture_only") else "HIGH",
            })

    return {
        "format": format_id,
        "total_entries": total,
        "entries_with_spec_fact_ref": with_ref,
        "entries_resolved": resolved,
        "entries_missing_in_sal": missing,
        "coverage_pct": round(100 * resolved / with_ref, 1) if with_ref else None,
        "gaps": gaps,
    }


def run_audit(format_filter: str | None = None, out_path: Path | None = None) -> dict:
    """Run full SAL-to-QName cross-reference audit."""
    if not _REGISTRY_DIR.exists():
        print("ERROR: shared/qname-registry/ not found")
        return {}

    sal_ids_by_format = load_sal_fact_ids()
    total_sal_facts = sum(len(v) for v in sal_ids_by_format.values())
    print(f"SAL facts loaded: {total_sal_facts} total across {len(sal_ids_by_format)} formats")

    per_format: list[dict] = []
    total_gaps = 0
    total_high = 0
    total_entries = 0
    total_with_ref = 0
    total_resolved = 0

    for yaml_path in sorted(_REGISTRY_DIR.glob("*.yaml")):
        if yaml_path.name == "schema.yaml":
            continue
        fmt = yaml_path.stem
        if format_filter and fmt != format_filter:
            continue
        result = audit_format_sal_coverage(fmt, yaml_path, sal_ids_by_format)
        per_format.append(result)
        total_gaps += result.get("entries_missing_in_sal", 0)
        total_high += sum(1 for g in result.get("gaps", []) if g.get("severity") == "HIGH")
        total_entries += result.get("total_entries", 0)
        total_with_ref += result.get("entries_with_spec_fact_ref", 0)
        total_resolved += result.get("entries_resolved", 0)

    report = {
        "audit_type": "sal_to_qname_cross_reference",
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "sal_facts_path": str(_SAL_PATH),
        "sal_total_facts": total_sal_facts,
        "summary": {
            "total_formats_audited": len(per_format),
            "total_registry_entries": total_entries,
            "entries_with_spec_fact_ref": total_with_ref,
            "entries_resolved_in_sal": total_resolved,
            "entries_missing_in_sal": total_gaps,
            "high_severity_gaps": total_high,
            "overall_coverage_pct": (
                round(100 * total_resolved / total_with_ref, 1)
                if total_with_ref else None
            ),
        },
        "per_format": per_format,
    }

    # Print summary
    print("\nSAL-to-QName Cross-Reference Report")
    print(f"{'='*50}")
    print(f"Formats audited:      {len(per_format)}")
    print(f"Total entries:        {total_entries}")
    print(f"Entries with ref:     {total_with_ref}")
    print(f"Resolved in SAL:      {total_resolved}")
    print(f"Missing from SAL:     {total_gaps}")
    print(f"High severity:        {total_high}")
    if total_with_ref:
        print(f"Overall coverage:     {round(100*total_resolved/total_with_ref, 1)}%")
    print()

    if total_gaps:
        print("Gaps (by format):")
        for fmt_result in per_format:
            gaps = fmt_result.get("gaps", [])
            if gaps:
                print(f"  {fmt_result['format']}: {len(gaps)} gap(s)")
                for g in gaps[:3]:
                    print(f"    - {g['qname']}: {g['issue'][:60]}")

    # Write report
    if out_path is None:
        date_str = datetime.now().strftime("%Y%m%d")
        out_path = _REPO / f"reports/sal-qname-gap-{date_str}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nReport written: {out_path}")

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="SAL-to-QName cross-reference audit")
    parser.add_argument("--format", help="Audit only this format (e.g. fods)")
    parser.add_argument("--out", help="Output path for report JSON")
    args = parser.parse_args()

    out_path = Path(args.out) if args.out else None
    report = run_audit(format_filter=args.format, out_path=out_path)

    # Exit with 1 if high-severity gaps found
    high = report.get("summary", {}).get("high_severity_gaps", 0)
    if high > 0:
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()
