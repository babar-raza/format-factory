"""calculate_oracle_coverage.py — Oracle coverage model generator (TC-W1A-002).

Produces:
  oracle/reports/oracle-coverage-report.json  — per-format metrics
  oracle/reports/oracle-gap-register.yaml     — gap classification per format
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ORACLE_ROOT = REPO_ROOT / "oracle" / "formats"
REPORTS_DIR = REPO_ROOT / "oracle" / "reports"
ORACLE_REGISTRY = REPO_ROOT / "oracle" / "registry" / "format-oracle-registry.yaml"

BLOCKING_AUTHORITY_CLASSES = {
    "AI_DRAFT_UNVERIFIED",
    "IMPLEMENTATION_OBSERVED",
    "REJECTED",
    "UNKNOWN",
}


def load_registry_status(registry_path: Path = ORACLE_REGISTRY) -> dict[str, str]:
    """Read the authoritative oracle status per format from the oracle registry.

    `oracle/registry/format-oracle-registry.yaml` is the single source of truth for
    oracle status (TC-PA-031/TC-PA-041). Its `product_oracle_status` is what the
    blocking oracle validators read; the package `status:` mirror was a duplicate with
    no producer and was removed. Coverage now derives status FROM the registry so a
    reverted/re-onboarded package can no longer publish a false-green `verified_formats`.

    Returns {format_id: product_oracle_status}.
    """
    if not registry_path.exists():
        return {}
    try:
        registry = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
    except Exception as e:  # pragma: no cover - defensive
        print(f"WARNING: could not load oracle registry {registry_path}: {e}", file=sys.stderr)
        return {}
    status: dict[str, str] = {}
    for entry in (registry.get("format_oracles") or []):
        fid = entry.get("format_id")
        if fid:
            status[fid] = entry.get("product_oracle_status", "UNKNOWN")
    return status


def load_all_oracle_packages(oracle_root: Path) -> dict[str, dict]:
    """Read all format oracle packages. Returns {format_id: package_dict}."""
    packages: dict[str, dict] = {}
    for fmt_dir in sorted(oracle_root.iterdir()):
        if not fmt_dir.is_dir():
            continue
        pkg_path = fmt_dir / "oracle-package.yaml"
        if not pkg_path.exists():
            continue
        try:
            pkg = yaml.safe_load(pkg_path.read_text(encoding="utf-8"))
            fmt_id = pkg.get("format_id", fmt_dir.name)
            packages[fmt_id] = pkg
        except Exception as e:
            print(f"WARNING: could not load {pkg_path}: {e}", file=sys.stderr)
    return packages


def _highest_authority_class(cases: list[dict]) -> str:
    """Return the highest (most authoritative) authority_class seen in a case list."""
    priority = [
        "SPEC_NORMATIVE",
        "AUTHORITATIVE_REFERENCE_VECTOR",
        "SPEC_INFORMATIVE",
        "ACCEPTED_EMPIRICAL",
        "GENERATED_FROM_NEUTRAL_MODEL",
        "UNKNOWN",
    ]
    seen = {c.get("authority_class", "UNKNOWN") for c in cases}
    for cls in priority:
        if cls in seen:
            return cls
    return "UNKNOWN"


def _authority_gap_count(cases: list[dict]) -> int:
    """Count cases with UNKNOWN or missing authority_class."""
    return sum(
        1 for c in cases
        if c.get("authority_class", "UNKNOWN") in BLOCKING_AUTHORITY_CLASSES
    )


def _load_run_summary(fmt_id: str) -> dict:
    """Load oracle-run-summary.json for a format if it exists."""
    path = REPO_ROOT / "oracle" / "formats" / fmt_id / "reports" / "oracle-run-summary.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def compute_format_coverage(fmt_id: str, pkg: dict, registry_status: dict[str, str] | None = None) -> dict:
    """Return per-format metrics dict.

    `status` is sourced from the authoritative registry (`registry_status`), never from
    the oracle-package.yaml mirror. If the format is absent from the registry the status
    is reported as UNKNOWN rather than trusting a package-authored value.
    """
    registry_status = registry_status or {}
    valid_cases: list[dict] = pkg.get("valid_cases", [])
    invalid_cases: list[dict] = pkg.get("invalid_cases", [])
    roundtrip_cases: list[dict] = pkg.get("roundtrip_cases", [])
    error_cases: list[dict] = pkg.get("error_cases", [])
    all_cases = valid_cases + invalid_cases + roundtrip_cases + error_cases

    summary = _load_run_summary(fmt_id)

    profiles_declared = pkg.get("profiles", [])
    depth_achieved = summary.get("format_depth_score", "D0") if summary else "D0"

    return {
        "format_id": fmt_id,
        "status": registry_status.get(fmt_id, "UNKNOWN"),
        "total_valid_cases": len(valid_cases),
        "total_invalid_cases": len(invalid_cases),
        "total_roundtrip_cases": len(roundtrip_cases),
        "total_error_cases": len(error_cases),
        "total_cases": len(all_cases),
        "profiles_declared": len(profiles_declared),
        "profiles_list": profiles_declared,
        "depth_achieved": depth_achieved,
        "highest_authority_class": _highest_authority_class(all_cases) if all_cases else "NONE",
        "authority_gap_count": _authority_gap_count(all_cases),
        "pass_rate": summary.get("pass_rate", "?") if summary else "not_run",
        "depth_histogram": summary.get("depth_histogram", {}) if summary else {},
    }


def identify_gaps(coverage: dict[str, dict]) -> list[dict]:
    """Return list of gap records — one per format with at least one gap."""
    gaps = []
    for fmt_id, metrics in coverage.items():
        gap_record: dict[str, Any] = {
            "format_id": fmt_id,
            "status": metrics["status"],
            "invalid_case_gap": metrics["total_invalid_cases"] == 0,
            "roundtrip_gap": metrics["total_roundtrip_cases"] == 0,
            "depth_gap": metrics["depth_achieved"] == "D0",
            "authority_gap": metrics["authority_gap_count"] > 0,
            "authority_gap_count": metrics["authority_gap_count"],
        }
        gap_record["has_any_gap"] = any([
            gap_record["invalid_case_gap"],
            gap_record["roundtrip_gap"],
            gap_record["depth_gap"],
            gap_record["authority_gap"],
        ])
        gaps.append(gap_record)
    return sorted(gaps, key=lambda g: g["format_id"])


def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    packages = load_all_oracle_packages(ORACLE_ROOT)
    print(f"Loaded {len(packages)} oracle packages.", file=sys.stderr)

    registry_status = load_registry_status()
    print(f"Loaded {len(registry_status)} registry status entries (authoritative).", file=sys.stderr)

    coverage: dict[str, dict] = {}
    for fmt_id, pkg in packages.items():
        coverage[fmt_id] = compute_format_coverage(fmt_id, pkg, registry_status)

    total_formats = len(coverage)
    total_cases = sum(m["total_cases"] for m in coverage.values())
    total_invalid = sum(m["total_invalid_cases"] for m in coverage.values())
    total_roundtrip = sum(m["total_roundtrip_cases"] for m in coverage.values())

    report = {
        "report_id": "oracle-coverage-report",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mission_id": "FF-ORC-HARDENING-002",
        "total_formats": total_formats,
        "total_cases": total_cases,
        "total_invalid_cases": total_invalid,
        "total_roundtrip_cases": total_roundtrip,
        "format_coverage": list(coverage.values()),
        "summary": {
            "verified_formats": sum(1 for m in coverage.values() if m["status"] == "VERIFIED"),
            "formats_with_invalid_cases": sum(1 for m in coverage.values() if m["total_invalid_cases"] > 0),
            "formats_with_roundtrip_cases": sum(1 for m in coverage.values() if m["total_roundtrip_cases"] > 0),
            "formats_at_d1_plus": sum(1 for m in coverage.values() if m["depth_achieved"] != "D0"),
            "formats_with_authority_gaps": sum(1 for m in coverage.values() if m["authority_gap_count"] > 0),
        },
    }

    out_path = REPORTS_DIR / "oracle-coverage-report.json"
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Written: {out_path}", file=sys.stderr)

    gaps = identify_gaps(coverage)
    formats_with_gaps = [g for g in gaps if g["has_any_gap"]]

    gap_register = {
        "gap_register_id": "oracle-gap-register",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mission_id": "FF-ORC-HARDENING-002",
        "total_formats_checked": total_formats,
        "formats_with_gaps": len(formats_with_gaps),
        "gaps": gaps,
        "gap_summary": {
            "invalid_case_gap": [g["format_id"] for g in gaps if g["invalid_case_gap"]],
            "roundtrip_gap": [g["format_id"] for g in gaps if g["roundtrip_gap"]],
            "depth_gap": [g["format_id"] for g in gaps if g["depth_gap"]],
            "authority_gap": [g["format_id"] for g in gaps if g["authority_gap"]],
        },
    }

    gap_path = REPORTS_DIR / "oracle-gap-register.yaml"
    gap_path.write_text(yaml.dump(gap_register, default_flow_style=False, sort_keys=False), encoding="utf-8")
    print(f"Written: {gap_path}", file=sys.stderr)

    # Print summary
    print(f"\nOracle Coverage Report:")
    print(f"  Formats: {total_formats}")
    print(f"  Total cases: {total_cases}")
    print(f"  Formats with invalid cases: {report['summary']['formats_with_invalid_cases']}/{total_formats}")
    print(f"  Formats with roundtrip cases: {report['summary']['formats_with_roundtrip_cases']}/{total_formats}")
    print(f"  Formats at D1+: {report['summary']['formats_at_d1_plus']}/{total_formats}")
    print(f"\nGap Register:")
    print(f"  Formats with any gap: {len(formats_with_gaps)}/{total_formats}")
    print(f"  Invalid case gaps: {gap_register['gap_summary']['invalid_case_gap']}")
    print(f"  Roundtrip gaps (all): {len(gap_register['gap_summary']['roundtrip_gap'])} formats")
    print(f"  Depth gaps (D0): {gap_register['gap_summary']['depth_gap']}")


if __name__ == "__main__":
    main()
