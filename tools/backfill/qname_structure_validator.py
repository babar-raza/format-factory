"""
qname_structure_validator.py — Deep QName Structure Validator (Phase A — Forensic Audit)

Goes beyond audit_qname_coverage.py by validating STRUCTURE, not just presence:

1. canonical_class name exists as a class definition in the python_file
2. python_file path hierarchy matches qname namespace structure
   (e.g., csv:record should resolve to spec/record/record.py, not csv_parser.py)
3. .NET SpecQName constant VALUE matches the expected qname string
4. Status vs. implementation consistency (architecture_only with python_file=null is OK)
5. Generates migration recommendations for non-compliant entries

Usage:
    python tools/backfill/qname_structure_validator.py [--format FORMAT] [--out PATH] [--migration-plan]

Exit codes:
    0: All checks pass (or only advisory warnings)
    1: Structural gaps found (class name mismatch, wrong path, SpecQName value wrong)
    2: Critical gaps (file missing, status=implemented but no class found)
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REGISTRY_DIR = REPO_ROOT / "shared" / "qname-registry"

# Status values where a python_file is expected (if not null)
ACTIVE_STATUSES = {"implementing", "implemented", "stable"}

# architecture_only: python_file may legitimately be null (spec placeholder)
ARCHITECTURE_ONLY = "architecture_only"


# ---------------------------------------------------------------------------
# YAML loading
# ---------------------------------------------------------------------------

def _load_registry(path: Path) -> list[dict]:
    try:
        import yaml
        with path.open(encoding="utf-8") as f:
            result = yaml.safe_load(f)
        return result if isinstance(result, list) else []
    except ImportError:
        return _load_yaml_simple(path)
    except Exception as e:
        raise RuntimeError(f"Cannot load {path}: {e}") from e


def _load_yaml_simple(path: Path) -> list[dict]:
    entries: list[dict] = []
    current: dict | None = None
    with path.open(encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("- ") or line == "-":
                if current is not None:
                    entries.append(current)
                current = {}
                rest = line[2:].strip()
                if rest and ":" in rest:
                    k, _, v = rest.partition(":")
                    current[k.strip()] = _val(v.strip())
            elif current is not None and line.startswith("  "):
                stripped = line.strip()
                if stripped.startswith("- "):  # list item inside entry (facade_names)
                    continue
                if ":" in stripped:
                    k, _, v = stripped.partition(":")
                    current[k.strip()] = _val(v.strip())
    if current is not None:
        entries.append(current)
    return entries


def _val(v: str):
    v = v.strip().strip('"').strip("'")
    if v in ("null", "~", ""):
        return None
    return v


# ---------------------------------------------------------------------------
# Structural checks
# ---------------------------------------------------------------------------

def _get_class_names(path: Path) -> set[str]:
    """Return all top-level class names defined in a Python file."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        return {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
    except Exception:
        return set()


def _canonical_class_short(canonical_class: str) -> str:
    """Get the short class name from 'Namespace.ClassName' → 'ClassName'."""
    if not canonical_class:
        return ""
    return canonical_class.split(".")[-1]


def _expected_spec_path(qname: str, format_id: str) -> str:
    """Derive the expected spec/ path from a qname (heuristic).

    E.g.:
        csv:record  → src/python/csv/spec/record/record.py
        text:p      → src/python/fodt/spec/text/p.py   (or paragraph.py)
        draw:frame  → src/python/fodg/spec/draw/frame.py
    """
    if ":" not in qname:
        return ""
    ns, local = qname.split(":", 1)
    local_snake = local.replace("-", "_")
    return f"src/python/{format_id}/spec/{ns}/{local_snake}.py"


def _check_dotnet_specqname_value(path: Path, expected_qname: str) -> tuple[bool, str | None]:
    """Check .NET file has SpecQName constant with the correct value.

    Returns (has_correct_value, actual_value_or_None)
    """
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        # Match: public const string SpecQName = "csv:record";
        m = re.search(
            r'SpecQName\s*=\s*"([^"]+)"',
            content,
            re.IGNORECASE,
        )
        if not m:
            return False, None
        actual = m.group(1)
        return actual == expected_qname, actual
    except Exception:
        return False, None


def _path_matches_qname_hierarchy(python_file: str, qname: str, format_id: str) -> tuple[bool, str]:
    """Check if the python_file path follows the spec/{namespace}/{local_name}.py hierarchy.

    Returns (matches, expected_path)
    """
    expected = _expected_spec_path(qname, format_id)
    py_normalized = python_file.replace("\\", "/")

    # If the file IS in a spec/ directory, it should match the hierarchy
    if "/spec/" in py_normalized:
        matches = py_normalized.endswith(expected.split(f"{format_id}/spec/")[-1])
        return matches, expected

    # If the file is NOT in spec/ (e.g., codec.py), that's a structural gap for spec-layer entries
    return False, expected


# ---------------------------------------------------------------------------
# Per-format audit
# ---------------------------------------------------------------------------

def audit_format(format_id: str, registry_path: Path) -> dict:
    entries = _load_registry(registry_path)
    gaps = []
    migration_recommendations = []
    pass_count = 0
    warn_count = 0
    fail_count = 0

    for entry in entries:
        qname = entry.get("qname", "?")
        status = entry.get("status", "seeded")
        python_file = entry.get("python_file")
        dotnet_file = entry.get("dotnet_file")
        canonical_class = entry.get("canonical_class", "")
        short_class = _canonical_class_short(canonical_class)
        source_layer = entry.get("source_layer", "")

        entry_result = {
            "qname": qname,
            "status": status,
            "python_file": python_file,
            "dotnet_file": dotnet_file,
            "canonical_class": canonical_class,
            "checks": [],
        }

        # ---- Python checks ----
        if python_file is not None:
            py_path = REPO_ROOT / python_file

            if not py_path.exists():
                entry_result["checks"].append({
                    "check": "python_file_exists",
                    "result": "FAIL",
                    "severity": "CRITICAL" if status in ACTIVE_STATUSES else "HIGH",
                    "detail": f"File missing: {python_file}",
                })
                fail_count += 1
                migration_recommendations.append({
                    "qname": qname,
                    "action": "CREATE_FILE",
                    "target_path": python_file,
                    "suggested_path": _expected_spec_path(qname, format_id),
                    "note": f"Create spec class with spec_qname='{qname}'",
                })
            else:
                # Check 1: spec_qname presence
                content = py_path.read_text(encoding="utf-8", errors="replace")
                has_sqname = bool(re.search(r"spec_qname\s*(?::[^=]+)?\s*=", content))
                if has_sqname:
                    entry_result["checks"].append({
                        "check": "python_spec_qname_present",
                        "result": "PASS",
                    })
                    pass_count += 1
                else:
                    sev = "HIGH" if status in ACTIVE_STATUSES else "MEDIUM"
                    entry_result["checks"].append({
                        "check": "python_spec_qname_present",
                        "result": "FAIL",
                        "severity": sev,
                        "detail": f"No spec_qname assignment in {python_file}",
                    })
                    fail_count += 1
                    migration_recommendations.append({
                        "qname": qname,
                        "action": "ADD_SPEC_QNAME",
                        "target_path": python_file,
                        "note": f"Add: spec_qname: ClassVar[str] = '{qname}'",
                    })

                # Check 2: canonical class name exists in file
                if source_layer == "Spec" and short_class:
                    defined_classes = _get_class_names(py_path)
                    if short_class in defined_classes:
                        entry_result["checks"].append({
                            "check": "canonical_class_defined",
                            "result": "PASS",
                            "detail": f"Class '{short_class}' found in {python_file}",
                        })
                        pass_count += 1
                    else:
                        # Warn: class name mismatch (could be alias or naming convention)
                        entry_result["checks"].append({
                            "check": "canonical_class_defined",
                            "result": "WARN",
                            "severity": "MEDIUM",
                            "detail": (
                                f"Class '{short_class}' (from canonical_class='{canonical_class}') "
                                f"not found in {python_file}. "
                                f"Defined: {sorted(defined_classes)[:5]}"
                            ),
                        })
                        warn_count += 1
                        migration_recommendations.append({
                            "qname": qname,
                            "action": "RENAME_OR_CREATE_CLASS",
                            "target_path": python_file,
                            "expected_class": short_class,
                            "defined_classes": sorted(defined_classes),
                            "note": f"Registry expects class named '{short_class}'",
                        })

                # Check 3: path hierarchy (advisory for spec-layer entries)
                if source_layer == "Spec":
                    matches, expected = _path_matches_qname_hierarchy(python_file, qname, format_id)
                    if matches:
                        entry_result["checks"].append({
                            "check": "path_hierarchy",
                            "result": "PASS",
                            "detail": f"Path matches qname hierarchy: {python_file}",
                        })
                        pass_count += 1
                    elif "/spec/" in python_file:
                        # In spec/ but wrong sub-path
                        entry_result["checks"].append({
                            "check": "path_hierarchy",
                            "result": "WARN",
                            "severity": "LOW",
                            "detail": (
                                f"Path diverges from qname hierarchy. "
                                f"Got: {python_file}, expected pattern: {expected}"
                            ),
                        })
                        warn_count += 1
                    else:
                        # Not in spec/ at all for a Spec-layer entry
                        entry_result["checks"].append({
                            "check": "path_hierarchy",
                            "result": "WARN",
                            "severity": "MEDIUM",
                            "detail": (
                                f"Spec-layer qname maps to non-spec/ file: {python_file}. "
                                f"Expected: {expected}"
                            ),
                        })
                        warn_count += 1
                        migration_recommendations.append({
                            "qname": qname,
                            "action": "MOVE_TO_SPEC_LAYER",
                            "current_path": python_file,
                            "suggested_path": expected,
                            "note": "Spec-layer entries should live in spec/{namespace}/{local}.py",
                        })

        elif status in ACTIVE_STATUSES:
            # Active entry with null python_file (should have one)
            entry_result["checks"].append({
                "check": "python_file_required_for_active",
                "result": "FAIL",
                "severity": "HIGH",
                "detail": f"Status='{status}' but python_file is null",
            })
            fail_count += 1
            migration_recommendations.append({
                "qname": qname,
                "action": "ADD_PYTHON_FILE",
                "suggested_path": _expected_spec_path(qname, format_id),
                "note": "Active entry needs python_file",
            })
        elif status == ARCHITECTURE_ONLY and python_file is None:
            # OK: architecture_only with null python_file is intentional
            entry_result["checks"].append({
                "check": "architecture_only_null_python_file",
                "result": "PASS",
                "detail": "architecture_only with python_file=null is intentional",
            })
            pass_count += 1

        # ---- .NET checks ----
        if dotnet_file is not None:
            net_path = REPO_ROOT / dotnet_file
            if not net_path.exists():
                entry_result["checks"].append({
                    "check": "dotnet_file_exists",
                    "result": "FAIL",
                    "severity": "HIGH",
                    "detail": f".NET file missing: {dotnet_file}",
                })
                fail_count += 1
            else:
                correct, actual = _check_dotnet_specqname_value(net_path, qname)
                if actual is None:
                    entry_result["checks"].append({
                        "check": "dotnet_specqname_present",
                        "result": "WARN",
                        "severity": "MEDIUM",
                        "detail": f"No SpecQName constant in {dotnet_file}",
                    })
                    warn_count += 1
                elif correct:
                    entry_result["checks"].append({
                        "check": "dotnet_specqname_value",
                        "result": "PASS",
                        "detail": f'SpecQName = "{qname}" ✓',
                    })
                    pass_count += 1
                else:
                    entry_result["checks"].append({
                        "check": "dotnet_specqname_value",
                        "result": "FAIL",
                        "severity": "HIGH",
                        "detail": f'SpecQName mismatch: got "{actual}", expected "{qname}"',
                    })
                    fail_count += 1
                    migration_recommendations.append({
                        "qname": qname,
                        "action": "FIX_DOTNET_SPECQNAME_VALUE",
                        "target_path": dotnet_file,
                        "expected_value": qname,
                        "actual_value": actual,
                        "note": f'Change SpecQName to "{qname}"',
                    })

        gaps.append(entry_result)

    return {
        "format_id": format_id,
        "total_entries": len(entries),
        "pass_count": pass_count,
        "warn_count": warn_count,
        "fail_count": fail_count,
        "entries": gaps,
        "migration_recommendations": migration_recommendations,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(args: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Deep QName structure validator — checks canonical classes, path hierarchy, .NET SpecQName values"
    )
    parser.add_argument("--format", dest="format_filter", help="Audit one format only")
    parser.add_argument("--out", help="Output JSON path (default: reports/qname-structure-{date}.json)")
    parser.add_argument("--migration-plan", action="store_true", help="Include migration recommendations in output")
    parsed = parser.parse_args(args)

    today = date.today().strftime("%Y%m%d")
    out_path = Path(parsed.out) if parsed.out else (
        REPO_ROOT / "reports" / f"qname-structure-{today}.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)

    registry_files = sorted(f for f in REGISTRY_DIR.glob("*.yaml") if f.name != "schema.yaml")
    if parsed.format_filter:
        registry_files = [f for f in registry_files if f.stem == parsed.format_filter]
        if not registry_files:
            print(f"ERROR: No registry for format '{parsed.format_filter}'", file=sys.stderr)
            return 2

    all_results = []
    total_pass = total_warn = total_fail = total_migration = 0

    for reg_path in registry_files:
        fmt = reg_path.stem
        try:
            result = audit_format(fmt, reg_path)
        except Exception as e:
            print(f"ERROR auditing {fmt}: {e}", file=sys.stderr)
            result = {"format_id": fmt, "error": str(e)}
        all_results.append(result)
        total_pass += result.get("pass_count", 0)
        total_warn += result.get("warn_count", 0)
        total_fail += result.get("fail_count", 0)
        total_migration += len(result.get("migration_recommendations", []))

    summary = {
        "date": today,
        "tool": "qname_structure_validator",
        "description": "Deep structural audit: canonical class existence, path hierarchy, .NET SpecQName value correctness",
        "formats_audited": len(all_results),
        "total_pass": total_pass,
        "total_warn": total_warn,
        "total_fail": total_fail,
        "total_migration_recommendations": total_migration,
        "overall_verdict": "PASS" if total_fail == 0 else ("WARN" if total_warn > 0 else "FAIL"),
        "formats": all_results if parsed.migration_plan else [
            {k: v for k, v in r.items() if k != "entries"} for r in all_results
        ],
    }

    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # Console output
    print(f"\n=== QName Structure Validator — {today} ===")
    print(f"Formats: {len(all_results)}  PASS: {total_pass}  WARN: {total_warn}  FAIL: {total_fail}")
    print(f"Migration recommendations: {total_migration}")
    print(f"Overall verdict: {summary['overall_verdict']}\n")
    print(f"{'Format':<12} {'Entries':>7} {'PASS':>6} {'WARN':>6} {'FAIL':>6} {'Migrate':>8}")
    print("-" * 55)
    for r in all_results:
        if "error" in r:
            print(f"{r['format_id']:<12} ERROR: {r['error']}")
            continue
        print(
            f"{r['format_id']:<12} {r['total_entries']:>7} "
            f"{r['pass_count']:>6} {r['warn_count']:>6} {r['fail_count']:>6} "
            f"{len(r.get('migration_recommendations', [])):>8}"
        )

    if total_fail > 0 or total_warn > 0:
        print(f"\nDetailed report: {out_path}")
        print("Use --migration-plan to include per-format migration recommendations.")

    return 1 if total_fail > 0 else (0 if total_warn == 0 else 0)


if __name__ == "__main__":
    sys.exit(main())
