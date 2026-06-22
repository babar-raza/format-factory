"""
analytics_bucket_detector.py — Backfill scanner for analytics-bucket anti-patterns.

Walks src/python/ and classifies all analytics-related files by:
  1. Forbidden name violations (*_analytics_extra.py, *_extra.py, *_misc.py)
  2. Arithmetic function violations (functions with arithmetic-only names)

Exit codes:
  0 — CLEAN (no violations)
  1 — VIOLATIONS_FOUND (at least one violation)

Usage:
  python tools/validators/analytics_bucket_detector.py
  python tools/validators/analytics_bucket_detector.py --report-path reports/audits/analytics-backfill.json
  python tools/validators/analytics_bucket_detector.py --fail-on-violation
"""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
_SRC = _REPO / "src" / "python"

# Forbidden file name pattern (module-level prohibition)
_FORBIDDEN_NAME = re.compile(
    r"[^/\\]+_(analytics_extra|extra|misc)\.py$"
)

# Arithmetic function name pattern (extended — catches all arithmetic-bucket functions)
_ARITH_FN = re.compile(
    r"^(?:abw|csv|dif|fodg|fods|fodt|fodp|gnumeric|ndjson|ods|odt|pbm|pgm|ppm|qoi|sylk|toml|tsv|xcf|zst)"
    r"_\w+_(times|mod|plus|minus|div|squared|cubed|is_even|is_odd|"
    r"greater_than|less_than|times_\d|plus_\d|minus_\d|mod_\d)"
)

# Files that are legitimate analytics containers (NOT forbidden by name)
_ANALYTICS_TARGETS = re.compile(r"_analytics\.py$")


def _get_functions(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        return [
            n.name for n in ast.iter_child_nodes(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
    except Exception:
        return []


def scan(src_root: Path = _SRC) -> dict:
    """Scan src_root for analytics-bucket anti-patterns."""
    forbidden_name_violations: list[dict] = []
    arithmetic_function_violations: list[dict] = []
    clean_files: list[str] = []

    for fpath in sorted(src_root.rglob("*.py")):
        # Skip build artifacts and nested duplicate packages
        parts = fpath.parts
        if "build" in parts or "__pycache__" in parts:
            continue
        try:
            rel_to_src = fpath.relative_to(src_root)
        except ValueError:
            continue
        rel_parts = rel_to_src.parts
        if len(rel_parts) >= 2 and rel_parts[0] == rel_parts[1]:
            continue

        rel_str = fpath.relative_to(_REPO).as_posix()
        fname = fpath.name

        # Check 1: Forbidden file name
        if _FORBIDDEN_NAME.search(rel_str):
            forbidden_name_violations.append({
                "path": rel_str,
                "reason": f"Forbidden analytics-bucket module suffix in {fname!r}",
                "rule": "MODULE-NAME-001",
            })
            continue  # Skip arithmetic check for forbidden files (would be redundant)

        # Check 2: Arithmetic functions in any analytics file
        if _ANALYTICS_TARGETS.search(fname) or "analytics" in fname:
            fns = _get_functions(fpath)
            arith_fns = [f for f in fns if _ARITH_FN.match(f)]
            if arith_fns:
                arithmetic_function_violations.append({
                    "file": rel_str,
                    "count": len(arith_fns),
                    "total_functions": len(fns),
                    "examples": arith_fns[:5],
                    "rule": "ARITHMETIC_BUCKET",
                })
            else:
                if fns or "analytics" in fname:
                    clean_files.append(rel_str)

    total_violations = len(forbidden_name_violations) + len(arithmetic_function_violations)
    verdict = "VIOLATIONS_FOUND" if total_violations > 0 else "CLEAN"

    return {
        "verdict": verdict,
        "forbidden_name_violations": forbidden_name_violations,
        "arithmetic_function_violations": arithmetic_function_violations,
        "clean_files": clean_files,
        "summary": {
            "total_violations": total_violations,
            "forbidden_name_count": len(forbidden_name_violations),
            "arithmetic_function_files": len(arithmetic_function_violations),
            "clean_count": len(clean_files),
        },
    }


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Analytics bucket anti-pattern detector")
    parser.add_argument("--src-root", type=Path, default=_SRC)
    parser.add_argument("--report-path", type=Path, default=None,
                        help="Write JSON report to this path")
    parser.add_argument("--fail-on-violation", action="store_true",
                        help="Exit 1 if any violation found")
    parser.add_argument("--json", action="store_true", dest="json_out",
                        help="Output JSON to stdout")
    args = parser.parse_args(argv)

    result = scan(args.src_root)

    if args.json_out:
        print(json.dumps(result, indent=2))
    else:
        print(f"=== analytics_bucket_detector ===")
        print(f"Verdict: {result['verdict']}")
        s = result["summary"]
        print(f"  Forbidden name violations: {s['forbidden_name_count']}")
        print(f"  Files with arithmetic functions: {s['arithmetic_function_files']}")
        print(f"  Clean analytics files: {s['clean_count']}")
        if result["forbidden_name_violations"]:
            print("\nForbidden name violations:")
            for v in result["forbidden_name_violations"]:
                print(f"  [FAIL] {v['path']} — {v['reason']}")
        if result["arithmetic_function_violations"]:
            print("\nArithmetic function violations:")
            for v in result["arithmetic_function_violations"]:
                print(f"  [WARN] {v['file']} — {v['count']} arithmetic functions")
                print(f"         Examples: {v['examples'][:3]}")

    if args.report_path:
        args.report_path.parent.mkdir(parents=True, exist_ok=True)
        args.report_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(f"\nReport written to {args.report_path}")

    if args.fail_on_violation and result["summary"]["forbidden_name_count"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
