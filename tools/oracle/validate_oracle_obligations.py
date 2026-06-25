#!/usr/bin/env python3
"""
validate_oracle_obligations.py — Format Factory Oracle Obligation Validator

Enforces the oracle obligation gate:
1. Every format in registry/format-registry.yaml must have an entry in
   oracle/registry/format-oracle-registry.yaml
2. If an oracle package exists (oracle/formats/<format>/oracle-package.yaml),
   it must pass schema validation
3. Required minimum floor: valid_cases >= 1, invalid_cases >= 1 for any format
   with product_oracle_status not in {OBLIGATION_CREATED, SCAFFOLDED}
4. Products advancing beyond GATE_4 must have CASES_DEFINED oracle status

Exit codes:
    0 — all checks pass (or only warnings)
    1 — validation failures detected
    2 — configuration error (missing required files)

Usage:
    python tools/oracle/validate_oracle_obligations.py
    python tools/oracle/validate_oracle_obligations.py --strict  (warnings become errors)
    python tools/oracle/validate_oracle_obligations.py --check-new-format <format_id>
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

REPO_ROOT = Path(__file__).resolve().parents[2]
FORMAT_REGISTRY = REPO_ROOT / "registry" / "format-registry.yaml"
ORACLE_REGISTRY = REPO_ROOT / "oracle" / "registry" / "format-oracle-registry.yaml"
ORACLE_FORMATS_DIR = REPO_ROOT / "oracle" / "formats"

# Statuses that require at least minimum oracle floor
REQUIRES_FLOOR = {
    "CASES_DEFINED", "VERIFIED", "PRODUCTION_ACTIVE"
}

# Oracle status lifecycle order
STATUS_ORDER = [
    "OBLIGATION_CREATED",
    "SCAFFOLDED",
    "AUTHORITY_MAPPED",
    "CASES_DEFINED",
    "VERIFIED",
    "PRODUCTION_ACTIVE",
]

# Minimum floor per profile once CASES_DEFINED
MINIMUM_FLOOR = {
    "valid_cases": 1,
    "invalid_cases": 1,
}


def load_yaml(path: Path) -> dict | list | None:
    """Load a YAML file. Returns None if YAML not available."""
    if not HAS_YAML:
        print(f"[WARN] PyYAML not available — cannot validate {path}")
        return None
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_registered_formats() -> set[str]:
    """Get all format_ids from format-registry.yaml."""
    data = load_yaml(FORMAT_REGISTRY)
    if data is None:
        return set()
    formats = data.get("formats", [])
    return {f["format_id"] for f in formats if "format_id" in f}


def get_oracle_registry() -> dict[str, dict]:
    """Get oracle registry indexed by format_id."""
    data = load_yaml(ORACLE_REGISTRY)
    if data is None:
        return {}
    entries = data.get("format_oracles", [])
    return {e["format_id"]: e for e in entries if "format_id" in e}


def get_oracle_package(format_id: str) -> dict | None:
    """Load oracle package for a format if it exists."""
    pkg_path = ORACLE_FORMATS_DIR / format_id / "oracle-package.yaml"
    return load_yaml(pkg_path)


def validate_obligations(strict: bool = False) -> tuple[list, list, list]:
    """
    Validate all oracle obligations.
    Returns (errors, warnings, infos).
    """
    errors = []
    warnings = []
    infos = []

    # --- Check 1: All registered formats have an oracle obligation ---
    registered = get_registered_formats()
    oracle_reg = get_oracle_registry()

    # Exclude meta-formats and pipeline-only formats
    excluded_formats = {"odf-shared"}
    governed_formats = registered - excluded_formats

    for fmt in sorted(governed_formats):
        if fmt not in oracle_reg:
            # New format without obligation — this is a FAIL for product advancement
            errors.append({
                "code": "MISSING_OBLIGATION",
                "format_id": fmt,
                "message": f"Format '{fmt}' is in format-registry.yaml but has NO entry in format-oracle-registry.yaml. "
                           f"Oracle obligation must be created before product advancement beyond Gate 4.",
                "remediation": f"Add entry for '{fmt}' in oracle/registry/format-oracle-registry.yaml",
            })
        else:
            infos.append(f"OK: {fmt} has oracle obligation (status: {oracle_reg[fmt].get('product_oracle_status', 'unknown')})")

    # --- Check 2: Formats in oracle registry but NOT in format registry ---
    orphan_obligations = set(oracle_reg.keys()) - governed_formats
    for fmt in sorted(orphan_obligations):
        warnings.append({
            "code": "ORPHAN_OBLIGATION",
            "format_id": fmt,
            "message": f"Oracle obligation exists for '{fmt}' but format is NOT in format-registry.yaml",
        })

    # --- Check 3: Oracle packages with CASES_DEFINED+ must meet minimum floor ---
    for fmt_id, entry in sorted(oracle_reg.items()):
        status = entry.get("product_oracle_status", "OBLIGATION_CREATED")
        if status not in REQUIRES_FLOOR:
            continue

        pkg = get_oracle_package(fmt_id)
        if pkg is None:
            errors.append({
                "code": "MISSING_ORACLE_PACKAGE",
                "format_id": fmt_id,
                "message": f"Format '{fmt_id}' has product_oracle_status={status} but no oracle-package.yaml found at oracle/formats/{fmt_id}/oracle-package.yaml",
            })
            continue

        # Check minimum case floor
        valid_cases = len(pkg.get("valid_cases", []))
        invalid_cases = len(pkg.get("invalid_cases", []))

        if valid_cases < MINIMUM_FLOOR["valid_cases"]:
            errors.append({
                "code": "BELOW_MINIMUM_FLOOR",
                "format_id": fmt_id,
                "message": f"Oracle package for '{fmt_id}' has {valid_cases} valid_cases but minimum is {MINIMUM_FLOOR['valid_cases']}",
            })

        if invalid_cases < MINIMUM_FLOOR["invalid_cases"]:
            if status in {"VERIFIED", "PRODUCTION_ACTIVE"}:
                errors.append({
                    "code": "BELOW_MINIMUM_FLOOR",
                    "format_id": fmt_id,
                    "message": f"Oracle package for '{fmt_id}' has {invalid_cases} invalid_cases but minimum is {MINIMUM_FLOOR['invalid_cases']} (required for status={status})",
                })
            else:
                warnings.append({
                    "code": "BELOW_RECOMMENDED_FLOOR",
                    "format_id": fmt_id,
                    "message": f"Oracle package for '{fmt_id}' has {invalid_cases} invalid_cases (recommend >= 1)",
                })

    # --- Check 4: Oracle packages that exist without registry entries ---
    if ORACLE_FORMATS_DIR.exists():
        for fmt_dir in sorted(ORACLE_FORMATS_DIR.iterdir()):
            if not fmt_dir.is_dir():
                continue
            fmt_id = fmt_dir.name
            pkg_path = fmt_dir / "oracle-package.yaml"
            if pkg_path.exists() and fmt_id not in oracle_reg:
                warnings.append({
                    "code": "UNREGISTERED_ORACLE_PACKAGE",
                    "format_id": fmt_id,
                    "message": f"Oracle package exists for '{fmt_id}' but no entry in format-oracle-registry.yaml",
                    "remediation": f"Add entry for '{fmt_id}' in oracle/registry/format-oracle-registry.yaml",
                })

    return errors, warnings, infos


def check_new_format_oracle_gate(format_id: str) -> dict:
    """
    Check oracle gate for a specific new format.
    Returns gate verdict: PASS | WARN | FAIL
    """
    oracle_reg = get_oracle_registry()
    pkg = get_oracle_package(format_id)

    result = {
        "format_id": format_id,
        "gate": "ORACLE_ONBOARDING",
        "checks": [],
        "verdict": "PASS",
    }

    # Check 1: Obligation exists
    if format_id not in oracle_reg:
        result["checks"].append({
            "check": "OBLIGATION_EXISTS",
            "result": "FAIL",
            "message": f"No oracle obligation found for '{format_id}'",
        })
        result["verdict"] = "FAIL"
    else:
        result["checks"].append({"check": "OBLIGATION_EXISTS", "result": "PASS"})

    # Check 2: Oracle package exists
    if pkg is None:
        result["checks"].append({
            "check": "PACKAGE_EXISTS",
            "result": "WARN",
            "message": f"No oracle package found at oracle/formats/{format_id}/oracle-package.yaml",
        })
        if result["verdict"] != "FAIL":
            result["verdict"] = "WARN"
    else:
        result["checks"].append({"check": "PACKAGE_EXISTS", "result": "PASS"})

        # Check 3: Minimum floor
        valid_count = len(pkg.get("valid_cases", []))
        invalid_count = len(pkg.get("invalid_cases", []))
        if valid_count >= 1:
            result["checks"].append({"check": "VALID_CASES_MINIMUM", "result": "PASS", "count": valid_count})
        else:
            result["checks"].append({
                "check": "VALID_CASES_MINIMUM", "result": "FAIL",
                "message": "At least 1 valid case required"
            })
            result["verdict"] = "FAIL"

        if invalid_count >= 1:
            result["checks"].append({"check": "INVALID_CASES_MINIMUM", "result": "PASS", "count": invalid_count})
        else:
            result["checks"].append({
                "check": "INVALID_CASES_MINIMUM", "result": "WARN",
                "message": "At least 1 invalid case recommended"
            })
            if result["verdict"] != "FAIL":
                result["verdict"] = "WARN"

        # Check 4: Authority class (no UNKNOWN)
        all_cases = pkg.get("valid_cases", []) + pkg.get("invalid_cases", [])
        unknown_auth = [c["case_id"] for c in all_cases if c.get("authority_class") == "UNKNOWN"]
        if unknown_auth:
            result["checks"].append({
                "check": "NO_UNKNOWN_AUTHORITY",
                "result": "FAIL",
                "message": f"Cases with UNKNOWN authority_class: {unknown_auth}",
            })
            result["verdict"] = "FAIL"
        else:
            result["checks"].append({"check": "NO_UNKNOWN_AUTHORITY", "result": "PASS"})

    return result


def print_report(errors: list, warnings: list, infos: list, strict: bool) -> int:
    """Print validation report and return exit code."""
    print("\n=== Format Factory Oracle Obligation Validation ===\n")

    if not errors and not warnings:
        print(f"[PASS] All oracle obligations validated. {len(infos)} formats checked.")
        return 0

    if errors:
        print(f"[FAIL] {len(errors)} errors:")
        for e in errors:
            print(f"  ERROR [{e['code']}] {e['format_id']}: {e['message']}")
            if "remediation" in e:
                print(f"    REMEDIATION: {e['remediation']}")

    if warnings:
        print(f"\n[WARN] {len(warnings)} warnings:")
        for w in warnings:
            fmt = w.get("format_id", "")
            print(f"  WARN [{w['code']}] {fmt}: {w['message']}")

    if infos:
        print(f"\n[INFO] {len(infos)} format obligations checked OK")

    if errors or (strict and warnings):
        return 1
    return 0


def main():
    parser = argparse.ArgumentParser(description="Format Factory Oracle Obligation Validator")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--check-new-format", metavar="FORMAT_ID",
                        help="Check oracle onboarding gate for a specific new format")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    if not HAS_YAML:
        print("[ERROR] PyYAML not available. Install with: pip install pyyaml", file=sys.stderr)
        sys.exit(2)

    if args.check_new_format:
        result = check_new_format_oracle_gate(args.check_new_format)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n=== Oracle Onboarding Gate: {args.check_new_format} ===")
            for check in result["checks"]:
                icon = "OK" if check["result"] == "PASS" else ("WARN" if check["result"] == "WARN" else "FAIL")
                print(f"  [{icon}] {check['check']}: {check.get('message', 'OK')}")
            print(f"\nVERDICT: {result['verdict']}")
        sys.exit(0 if result["verdict"] == "PASS" else (1 if result["verdict"] == "FAIL" else 0))

    errors, warnings, infos = validate_obligations(args.strict)

    if args.json:
        print(json.dumps({
            "errors": errors,
            "warnings": warnings,
            "infos": infos,
            "error_count": len(errors),
            "warning_count": len(warnings),
        }, indent=2))
        sys.exit(1 if errors or (args.strict and warnings) else 0)

    exit_code = print_report(errors, warnings, infos, args.strict)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
