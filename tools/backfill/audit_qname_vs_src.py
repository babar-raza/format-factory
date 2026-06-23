"""audit_qname_vs_src.py — Phase F dry-run backfill inventory (FF-FORENSIC-AUDIT-20260623)

Reads shared/qname-registry/{format}.yaml for each format.
For each entry with python_file, checks actual vs expected spec class location.
Emits migration-maps/{format}/dry-run-map.json per format.

This is a READ-ONLY dry-run — it NEVER modifies source files.
It creates the migration map that a future backfill tool would use.

Expected spec hierarchy layout:
    QName: office:document  → namespace:local_name
    Expected class path:    src/python/{fmt}/spec/{namespace}/{local_name}.py
    Expected class name:    {local_name.replace('-','_').title()}  (e.g. Document)
    Actual path (if exists): python_file field from registry

Usage:
    python tools/backfill/audit_qname_vs_src.py [--format FMT] [--out-dir DIR]
    python tools/backfill/audit_qname_vs_src.py --all
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

_REPO = Path(__file__).resolve().parent.parent.parent
_REGISTRY_DIR = _REPO / "shared/qname-registry"
_MIGRATION_MAPS_DIR = _REPO / "migration-maps"

_FORMATS = [
    "abw", "csv", "dif", "fodg", "fodp", "fods", "fodt",
    "gnumeric", "ndjson", "ods", "odt", "pbm", "pgm", "ppm",
    "qoi", "sylk", "toml", "tsv", "xcf", "zst",
]


def _expected_spec_path(fmt: str, qname: str, canonical_class: str | None) -> str | None:
    """Compute the expected spec class file path from QName.

    QName format: "namespace:local_name" → spec/{namespace}/{local_name}.py
    Or: "ns:parent:local" → spec/{ns}/{parent}/{local}.py
    """
    parts = qname.split(":")
    if len(parts) < 2:
        return None
    # Join all parts into nested path
    path_parts = [p.replace("-", "_") for p in parts]
    rel_path = "/".join(path_parts)
    return f"src/python/{fmt}/spec/{rel_path}.py"


def _entry_status(
    actual_path: str | None,
    expected_path: str | None,
    repo: Path,
) -> str:
    """Classify the relationship between actual and expected paths."""
    if actual_path is None and expected_path is None:
        return "NO_PATH"
    if actual_path is None:
        return "MISSING"  # registry says no python_file; expected path exists in theory

    actual_full = repo / actual_path
    if not actual_full.exists():
        return "DECLARED_MISSING"  # python_file declared but file doesn't exist on disk

    if expected_path and actual_path == expected_path:
        return "CORRECT_LOCATION"  # file exists at expected canonical path

    if expected_path:
        expected_full = repo / expected_path
        if expected_full.exists():
            return "DUPLICATE"  # both actual and expected exist (potential conflict)
        return "WRONG_LOCATION"  # file exists but not at canonical spec path
    return "PRESENT_NO_EXPECTED"


def audit_format(fmt: str, registry_path: Path, out_dir: Path | None = None) -> dict[str, Any]:
    """Dry-run backfill inventory for a single format."""
    if not _HAS_YAML:
        return {"format": fmt, "error": "pyyaml not installed", "entries": []}

    try:
        entries = _yaml.safe_load(registry_path.read_text(encoding="utf-8")) or []
    except Exception as e:
        return {"format": fmt, "error": str(e), "entries": []}

    src_root = _REPO / f"src/python/{fmt}"
    entry_maps = []

    for entry in entries:
        if not isinstance(entry, dict):
            continue

        qname = entry.get("qname", "")
        actual = entry.get("python_file")  # may be null
        canonical = entry.get("canonical_class")
        status_val = entry.get("status", "seeded")

        expected = _expected_spec_path(fmt, qname, canonical)
        entry_status = _entry_status(actual, expected, _REPO)

        # Check if actual path has correct spec_qname assignment
        spec_qname_verified = False
        if actual and ((_REPO / actual).exists()):
            try:
                content = (_REPO / actual).read_text(encoding="utf-8", errors="replace")
                spec_qname_verified = f'spec_qname = "{qname}"' in content or f"spec_qname = '{qname}'" in content
            except Exception:
                pass

        entry_maps.append({
            "qname": qname,
            "registry_status": status_val,
            "canonical_class": canonical,
            "actual_python_file": actual,
            "expected_python_file": expected,
            "file_status": entry_status,
            "spec_qname_verified": spec_qname_verified,
            "action_needed": _recommend_action(entry_status, status_val, spec_qname_verified),
        })

    # Aggregate
    statuses = {}
    for e in entry_maps:
        s = e["file_status"]
        statuses[s] = statuses.get(s, 0) + 1

    correct = statuses.get("CORRECT_LOCATION", 0)
    total = len(entry_maps)

    result = {
        "format": fmt,
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "total_entries": total,
        "status_summary": statuses,
        "correct_pct": round(100 * correct / total, 1) if total else None,
        "entries": entry_maps,
    }

    if out_dir is not None:
        out_path = out_dir / fmt / "dry-run-map.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    return result


def _recommend_action(
    file_status: str,
    registry_status: str,
    spec_qname_verified: bool,
) -> str:
    """Recommend migration action based on file status."""
    if file_status == "CORRECT_LOCATION" and spec_qname_verified:
        return "NONE"
    if file_status == "CORRECT_LOCATION" and not spec_qname_verified:
        return "ADD_SPEC_QNAME"
    if file_status == "WRONG_LOCATION":
        return "MOVE_TO_CANONICAL_PATH"
    if file_status == "DECLARED_MISSING":
        return "CREATE_AT_ACTUAL_PATH"
    if file_status == "MISSING":
        if registry_status in ("seeded", "architecture_only"):
            return "CREATE_SPEC_STUB"
        return "CREATE_SPEC_CLASS"
    if file_status == "DUPLICATE":
        return "RESOLVE_DUPLICATE"
    return "INVESTIGATE"


def run_all(
    format_filter: str | None = None,
    out_dir: Path | None = None,
) -> dict[str, Any]:
    """Run dry-run backfill inventory for all (or one) format(s)."""
    if not _REGISTRY_DIR.exists():
        print("ERROR: shared/qname-registry/ not found")
        return {}

    maps_dir = out_dir or (_MIGRATION_MAPS_DIR)

    per_format = []
    total_entries = 0
    total_correct = 0
    total_wrong_location = 0
    total_missing = 0
    total_needs_action = 0

    formats_to_audit = [format_filter] if format_filter else _FORMATS

    for fmt in formats_to_audit:
        registry_path = _REGISTRY_DIR / f"{fmt}.yaml"
        if not registry_path.exists():
            continue
        result = audit_format(fmt, registry_path, out_dir=maps_dir)
        per_format.append(result)

        entries = result.get("entries", [])
        total_entries += len(entries)
        for e in entries:
            if e["file_status"] == "CORRECT_LOCATION" and e["spec_qname_verified"]:
                total_correct += 1
            elif e["file_status"] == "WRONG_LOCATION":
                total_wrong_location += 1
            elif "MISSING" in e["file_status"]:
                total_missing += 1
            if e["action_needed"] != "NONE":
                total_needs_action += 1

    report = {
        "audit_type": "qname_vs_src_dry_run_backfill",
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "formats_audited": len(per_format),
        "migration_maps_dir": str(maps_dir),
        "summary": {
            "total_entries": total_entries,
            "correct_location_with_qname": total_correct,
            "wrong_location": total_wrong_location,
            "missing": total_missing,
            "needs_action": total_needs_action,
            "correct_pct": (
                round(100 * total_correct / total_entries, 1)
                if total_entries else None
            ),
        },
        "per_format": [
            {
                "format": f["format"],
                "total": f["total_entries"],
                "status_summary": f["status_summary"],
                "correct_pct": f["correct_pct"],
            }
            for f in per_format
        ],
    }

    # Print summary
    print("QName vs Src Dry-Run Backfill Inventory")
    print("=" * 50)
    print(f"Formats audited:    {len(per_format)}")
    print(f"Total entries:      {total_entries}")
    print(f"Correct + verified: {total_correct}")
    print(f"Wrong location:     {total_wrong_location}")
    print(f"Missing:            {total_missing}")
    print(f"Needs action:       {total_needs_action}")
    if total_entries:
        print(f"Correct pct:        {round(100*total_correct/total_entries,1)}%")
    print()
    print("Action breakdown by format:")
    for f in per_format:
        entries = [e for e in audit_format(f["format"], _REGISTRY_DIR / f"{f['format']}.yaml").get("entries", []) if e["action_needed"] != "NONE"]
        if entries:
            actions = {}
            for e in entries:
                a = e["action_needed"]
                actions[a] = actions.get(a, 0) + 1
            actions_str = ", ".join(f"{a}={c}" for a, c in sorted(actions.items()))
            print(f"  {f['format']}: {actions_str}")

    # Write summary report
    summary_path = maps_dir / "backfill-inventory-summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nSummary report: {summary_path}")
    print(f"Per-format maps: {maps_dir}/{{format}}/dry-run-map.json")

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Dry-run backfill inventory: QName registry vs src/")
    parser.add_argument("--format", help="Audit single format (e.g. csv)")
    parser.add_argument("--all", action="store_true", help="Audit all 20 formats")
    parser.add_argument("--out-dir", help="Output directory for migration maps")
    args = parser.parse_args()

    out_dir = Path(args.out_dir) if args.out_dir else None
    run_all(format_filter=args.format, out_dir=out_dir)


if __name__ == "__main__":
    main()
