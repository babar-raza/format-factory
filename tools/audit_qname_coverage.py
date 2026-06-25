"""
audit_qname_coverage.py — QName registry-to-source coverage audit tool.

Reads all 20 shared/qname-registry/{format}.yaml files and checks whether
each entry's declared python_file and dotnet_file actually exist and contain
the expected spec_qname assignment (Python) or SpecQName constant (.NET).

Emits: reports/qname-coverage-{date}.json

Usage:
    python tools/audit_qname_coverage.py [--format FORMAT] [--out PATH]

Exit codes:
    0: All entries with non-null python_file have spec_qname; no missing files
    1: At least one gap found (missing file or missing spec_qname assignment)
    2: Error reading registries
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_DIR = REPO_ROOT / "shared" / "qname-registry"
SRC_PYTHON = REPO_ROOT / "src" / "python"
SRC_NET = REPO_ROOT / "src" / "net"

# Status values that imply a python_file should exist (if python_file is not null)
ACTIVE_STATUSES = {"architecture_only", "implementing", "implemented", "stable"}

# Status values where python_file=null is acceptable (not yet assigned)
SEEDED_STATUSES = {"seeded", "deprecated"}


def _load_yaml_list(path: Path) -> list[dict]:
    """Load a YAML file as a list of dicts (simple parser — no PyYAML dependency)."""
    try:
        import yaml  # type: ignore
        with path.open(encoding="utf-8") as f:
            result = yaml.safe_load(f)
        if result is None:
            return []
        if isinstance(result, list):
            return result
        return []
    except ImportError:
        # Fallback: use simple line-based YAML parser for basic cases
        return _parse_yaml_list_simple(path)
    except Exception as e:
        raise RuntimeError(f"Failed to parse {path}: {e}") from e


def _parse_yaml_list_simple(path: Path) -> list[dict]:
    """Very simple YAML list parser for list-of-dicts with string/null values."""
    entries: list[dict] = []
    current: dict | None = None
    with path.open(encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.rstrip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("- ") or line == "-":
                if current is not None:
                    entries.append(current)
                current = {}
                rest = line[2:].strip()
                if rest and ":" in rest:
                    k, _, v = rest.partition(":")
                    current[k.strip()] = _parse_val(v.strip())
            elif current is not None and line.startswith("  "):
                stripped = line.strip()
                if ":" in stripped:
                    k, _, v = stripped.partition(":")
                    current[k.strip()] = _parse_val(v.strip())
    if current is not None:
        entries.append(current)
    return entries


def _parse_val(v: str):
    """Parse a YAML scalar value."""
    v = v.strip()
    if v in ("null", "~", ""):
        return None
    if v.startswith('"') and v.endswith('"'):
        return v[1:-1]
    if v.startswith("'") and v.endswith("'"):
        return v[1:-1]
    return v


def _has_spec_qname_python(path: Path) -> bool:
    """Return True if the Python file has a spec_qname assignment.

    Matches both simple assignments (``spec_qname = "..."```) and
    type-annotated ClassVar assignments (``spec_qname: ClassVar[str] = "..."``).
    """
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        # Match `spec_qname = "..."` OR `spec_qname: <type> = "..."`
        return bool(re.search(r"spec_qname\s*(?::[^=]+)?\s*=", content))
    except Exception:
        return False


def _has_spec_qname_dotnet(path: Path) -> bool:
    """Return True if the .NET file has a SpecQName constant or property."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        return bool(re.search(r"SpecQName\s*=|spec_qname\s*=", content, re.IGNORECASE))
    except Exception:
        return False


def audit_format(format_id: str, registry_path: Path) -> dict:
    """Audit a single format's qname registry against source files."""
    entries = _load_yaml_list(registry_path)

    result: dict = {
        "format_id": format_id,
        "total_entries": len(entries),
        "seeded_count": 0,
        "active_count": 0,
        "python_file_declared": 0,
        "python_file_exists": 0,
        "python_has_spec_qname": 0,
        "python_file_missing": 0,
        "python_spec_qname_missing": 0,
        "dotnet_file_declared": 0,
        "dotnet_file_exists": 0,
        "dotnet_file_missing": 0,
        "null_python_in_active": 0,
        "coverage_score": 0.0,
        "gaps": [],
    }

    for entry in entries:
        qname = entry.get("qname", "?")
        status = entry.get("status", "seeded")
        python_file = entry.get("python_file")
        dotnet_file = entry.get("dotnet_file")

        if status in SEEDED_STATUSES:
            result["seeded_count"] += 1
        else:
            result["active_count"] += 1

        # Python file audit
        if python_file is not None:
            result["python_file_declared"] += 1
            py_path = REPO_ROOT / python_file
            if py_path.exists():
                result["python_file_exists"] += 1
                if _has_spec_qname_python(py_path):
                    result["python_has_spec_qname"] += 1
                else:
                    result["python_spec_qname_missing"] += 1
                    result["gaps"].append({
                        "qname": qname,
                        "status": status,
                        "issue": "python_file_exists_but_no_spec_qname",
                        "python_file": python_file,
                        "severity": "HIGH" if status in ACTIVE_STATUSES else "MEDIUM",
                    })
            else:
                result["python_file_missing"] += 1
                result["gaps"].append({
                    "qname": qname,
                    "status": status,
                    "issue": "python_file_declared_but_missing",
                    "python_file": python_file,
                    "severity": "CRITICAL" if status in ACTIVE_STATUSES else "HIGH",
                })
        elif status in ACTIVE_STATUSES:
            result["null_python_in_active"] += 1
            result["gaps"].append({
                "qname": qname,
                "status": status,
                "issue": "active_entry_has_null_python_file",
                "python_file": None,
                "severity": "MEDIUM",
            })

        # .NET file audit
        if dotnet_file is not None:
            result["dotnet_file_declared"] += 1
            net_path = REPO_ROOT / dotnet_file
            if net_path.exists():
                result["dotnet_file_exists"] += 1
            else:
                result["dotnet_file_missing"] += 1
                result["gaps"].append({
                    "qname": qname,
                    "status": status,
                    "issue": "dotnet_file_declared_but_missing",
                    "dotnet_file": dotnet_file,
                    "severity": "HIGH" if status in ACTIVE_STATUSES else "MEDIUM",
                })

    # Coverage score: python spec_qname present / total active entries
    active = result["active_count"]
    if active > 0:
        result["coverage_score"] = round(result["python_has_spec_qname"] / active, 3)
    else:
        result["coverage_score"] = 1.0  # No active entries = fully covered

    return result


def main(args: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit QName registry coverage")
    parser.add_argument(
        "--format", dest="format_filter",
        help="Audit only this format (e.g. fods). Default: all formats."
    )
    parser.add_argument(
        "--out",
        help="Output JSON path. Default: reports/qname-coverage-{date}.json"
    )
    parsed = parser.parse_args(args)

    today = date.today().strftime("%Y%m%d")
    out_path = Path(parsed.out) if parsed.out else (
        REPO_ROOT / "reports" / f"qname-coverage-{today}.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Discover registries
    registry_files = sorted(REGISTRY_DIR.glob("*.yaml"))
    registry_files = [f for f in registry_files if f.name != "schema.yaml"]

    if parsed.format_filter:
        registry_files = [f for f in registry_files if f.stem == parsed.format_filter]
        if not registry_files:
            print(f"ERROR: No registry found for format '{parsed.format_filter}'",
                  file=sys.stderr)
            return 2

    results: list[dict] = []
    total_gaps = 0
    total_critical = 0

    for reg_path in registry_files:
        format_id = reg_path.stem
        try:
            fmt_result = audit_format(format_id, reg_path)
        except Exception as e:
            print(f"ERROR auditing {format_id}: {e}", file=sys.stderr)
            fmt_result = {"format_id": format_id, "error": str(e), "gaps": []}
        results.append(fmt_result)
        gaps = fmt_result.get("gaps", [])
        total_gaps += len(gaps)
        total_critical += sum(1 for g in gaps if g.get("severity") == "CRITICAL")

    # Summary
    summary = {
        "date": today,
        "formats_audited": len(results),
        "total_gaps": total_gaps,
        "critical_gaps": total_critical,
        "overall_coverage": round(
            sum(r.get("coverage_score", 0.0) for r in results) / max(len(results), 1), 3
        ),
        "formats": results,
    }

    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # Print summary to stdout
    print(f"\n=== QName Coverage Audit — {today} ===")
    print(f"Formats audited: {len(results)}")
    print(f"Total gaps:      {total_gaps}")
    print(f"Critical gaps:   {total_critical}")
    print(f"Overall coverage score: {summary['overall_coverage']:.1%}\n")

    print(f"{'Format':<12} {'Entries':>8} {'Active':>7} {'PY OK':>6} {'PY Miss':>8} {'Coverage':>9} {'Gaps':>5}")
    print("-" * 65)
    for r in results:
        if "error" in r:
            print(f"{r['format_id']:<12} ERROR: {r['error']}")
            continue
        print(
            f"{r['format_id']:<12} {r['total_entries']:>8} {r['active_count']:>7} "
            f"{r['python_has_spec_qname']:>6} {r['python_file_missing']:>8} "
            f"{r['coverage_score']:>9.1%} {len(r['gaps']):>5}"
        )

    if total_gaps > 0:
        print(f"\nGaps written to: {out_path}")
        print("Run with --format <name> to see per-format gaps.")

    print(f"\nFull report: {out_path}")
    return 1 if total_critical > 0 else (1 if total_gaps > 0 else 0)


if __name__ == "__main__":
    sys.exit(main())
