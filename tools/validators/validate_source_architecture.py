"""
validate_source_architecture.py — Anti-monolith architecture validator for Format Factory.

Proactively scans src/python/ for architectural violations defined in the
production-readiness-standard.md. Does NOT rely solely on declared-changed files.

Rules enforced:
  RULE-AM-001: Analytics functions must not exist in parser/codec/model files
  RULE-AM-002: __init__.py must not exceed 100 LOC (new files)
  RULE-AM-003: No new file may exceed 800 LOC
  RULE-AM-004: No new file may have > 60 functions

Severity:
  - New file violation (not in baseline known_violations): FAIL (blocks sprint)
  - Existing violation (in baseline known_violations): WARN (advisory, must shrink)

Exit codes:
  0 — PASS or WARN only (no blocking failures)
  1 — FAIL (at least one blocking violation)

Usage:
  python tools/validators/validate_source_architecture.py [src_root] [--json] [--self-test] [--check-new-files]
  python tools/validators/validate_source_architecture.py --self-test
"""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_default_repo = _here.parent.parent
_default_src = _default_repo / "src" / "python"
_default_baseline = _default_repo / "registry" / "source-structure-baseline.json"

# Pattern for analytics function names:
# {format}_{property}_{formula} where formula contains mod_N, times_N, plus_, minus_, div_
_ANALYTICS_PATTERN = re.compile(
    r"^(?:abw|csv|dif|fodg|fods|fodt|fodp|gnumeric|ndjson|ods|odt|pbm|pgm|ppm|qoi|sylk|toml|tsv|xcf|zst)"
    r"_.+_(?:mod_\d+|times_\d+|plus_|minus_|div_)"
)

_MAX_LOC_NEW = 800
_MAX_FUNCTIONS_NEW = 60
_MAX_INIT_LOC_NEW = 100

# Files that are exempt from analytics-in-non-analytics check
_ANALYTICS_OK_NAMES = {"analytics.py", "__init__.py"}

# Recognized purposes for files (orphan check uses separate validator)
_RECOGNIZED_SUFFIXES = {
    "_parser.py", "_codec.py", "_writer.py", "_analytics.py",
    "_model.py", "_exceptions.py", "_constants.py", "_exporter.py",
    "_converter.py", "_encoder.py",
}


def _count_loc(path: Path) -> int:
    try:
        return sum(1 for _ in path.open(encoding="utf-8", errors="replace"))
    except Exception:
        return 0


def _parse_functions(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        return [
            n.name for n in ast.iter_child_nodes(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
    except Exception:
        return []


def _load_baseline(baseline_path: Path) -> dict:
    try:
        return json.loads(baseline_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _is_known_violation(rel_posix: str, baseline: dict) -> bool:
    known = baseline.get("known_violations", {})
    return rel_posix in known


def scan(src_root: Path, baseline: dict, repo_root: Path) -> dict:
    """
    Proactively scan src_root for architectural violations.

    Returns a validator-format dict:
      {validator, result, items, summary, blocks_sprint}
    """
    items: list[dict] = []
    known = baseline.get("known_violations", {})
    fail_count = 0
    warn_count = 0

    py_files = [
        p for p in src_root.rglob("*.py")
        if "build" not in p.parts
        and "__pycache__" not in p.parts
    ]

    for fpath in sorted(py_files):
        # Skip nested duplicate packages (e.g. src/python/fods/fods/)
        try:
            rel_to_src = fpath.relative_to(src_root)
        except ValueError:
            continue
        parts = rel_to_src.parts
        if len(parts) >= 2 and parts[0] == parts[1]:
            continue

        try:
            rel_posix = fpath.relative_to(repo_root).as_posix()
        except ValueError:
            rel_posix = fpath.as_posix()

        is_known = rel_posix in known
        fname = fpath.name

        # --- RULE-AM-001: Analytics functions outside analytics.py ---
        # Exempt: files named analytics.py OR ending with _analytics.py OR __init__.py
        _is_analytics_file = (
            fname == "analytics.py"
            or fname.endswith("_analytics.py")
            or fname == "__init__.py"
        )
        if not _is_analytics_file:
            functions = _parse_functions(fpath)
            analytics_fns = [f for f in functions if _ANALYTICS_PATTERN.match(f)]
            if analytics_fns:
                status = "WARN" if is_known else "FAIL"
                if status == "FAIL":
                    fail_count += 1
                else:
                    warn_count += 1
                items.append({
                    "file": rel_posix,
                    "rule": "RULE-AM-001",
                    "description": f"{len(analytics_fns)} analytics function(s) in non-analytics file",
                    "examples": analytics_fns[:3],
                    "current": len(analytics_fns),
                    "cap": 0,
                    "status": status,
                    "is_known_violation": is_known,
                })

        # --- RULE-AM-002: __init__.py size ---
        if fname == "__init__.py":
            loc = _count_loc(fpath)
            if loc > _MAX_INIT_LOC_NEW:
                status = "WARN" if is_known else "FAIL"
                if status == "FAIL":
                    fail_count += 1
                else:
                    warn_count += 1
                items.append({
                    "file": rel_posix,
                    "rule": "RULE-AM-002",
                    "description": f"__init__.py exceeds {_MAX_INIT_LOC_NEW} LOC",
                    "current": loc,
                    "cap": _MAX_INIT_LOC_NEW,
                    "status": status,
                    "is_known_violation": is_known,
                })
            continue  # Skip RULE-AM-003/004 for __init__.py (checked via AM-002)

        # --- RULE-AM-003: New file LOC limit ---
        if not is_known:
            loc = _count_loc(fpath)
            if loc > _MAX_LOC_NEW:
                fail_count += 1
                items.append({
                    "file": rel_posix,
                    "rule": "RULE-AM-003",
                    "description": f"New file exceeds {_MAX_LOC_NEW} LOC",
                    "current": loc,
                    "cap": _MAX_LOC_NEW,
                    "status": "FAIL",
                    "is_known_violation": False,
                })

            # --- RULE-AM-004: New file function count ---
            functions = _parse_functions(fpath)
            if len(functions) > _MAX_FUNCTIONS_NEW:
                fail_count += 1
                items.append({
                    "file": rel_posix,
                    "rule": "RULE-AM-004",
                    "description": f"New file exceeds {_MAX_FUNCTIONS_NEW} functions",
                    "current": len(functions),
                    "cap": _MAX_FUNCTIONS_NEW,
                    "status": "FAIL",
                    "is_known_violation": False,
                })
        else:
            # For known violations: check against baseline_loc_cap
            cap = known[rel_posix].get("baseline_loc_cap", known[rel_posix].get("loc", 0))
            if cap > 0:
                loc = _count_loc(fpath)
                if loc > cap:
                    warn_count += 1
                    items.append({
                        "file": rel_posix,
                        "rule": "RULE-AM-003-WORSENED",
                        "description": f"Known violation grew beyond baseline_loc_cap",
                        "current": loc,
                        "cap": cap,
                        "status": "WARN",
                        "is_known_violation": True,
                    })

    result = "PASS"
    if fail_count > 0:
        result = "FAIL"
    elif warn_count > 0:
        result = "WARN"

    summary_parts = []
    if fail_count:
        summary_parts.append(f"{fail_count} FAIL")
    if warn_count:
        summary_parts.append(f"{warn_count} WARN")
    summary = ", ".join(summary_parts) if summary_parts else "all files pass"

    return {
        "validator": "validate_source_architecture",
        "result": result,
        "items": items,
        "summary": f"validate_source_architecture: {summary}",
        "blocks_sprint": fail_count > 0,
    }


def _run_self_test() -> bool:
    """Run self-test against synthetic in-memory fixture. Returns True on pass."""
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        tmproot = Path(tmpdir)
        src = tmproot / "src" / "python"
        src.mkdir(parents=True)

        # Clean file — should PASS
        clean = src / "clean_module.py"
        clean.write_text("def clean_func():\n    return 1\n")

        # Analytics-in-codec violation — should FAIL (not in known_violations)
        bad = src / "bad_codec.py"
        bad.write_text(
            "def bad_codec_load():\n    pass\n"
            "def csv_row_count_mod_7_times_3_plus_col_count_times_5():\n    return 42\n"
        )

        # Analytics file — should be exempt from RULE-AM-001
        analytics = src / "csv_analytics.py"
        analytics.write_text(
            "def csv_row_count_mod_7_times_3_plus_col_count_times_5():\n    return 42\n"
        )

        # __init__ over 100 lines — should FAIL (not in known_violations)
        init = src / "__init__.py"
        init.write_text("\n".join(f"# line {i}" for i in range(150)) + "\n")

        baseline = {"known_violations": {}}
        result = scan(src, baseline, tmproot)

        fails = [i for i in result["items"] if i["status"] == "FAIL"]
        # Expect: bad_codec.py RULE-AM-001 FAIL, __init__.py RULE-AM-002 FAIL
        # clean_module.py should not appear
        # csv_analytics.py should not appear (exempt)
        bad_codec_fail = any(
            i["file"].endswith("bad_codec.py") and i["rule"] == "RULE-AM-001"
            for i in fails
        )
        init_fail = any(
            i["file"].endswith("__init__.py") and i["rule"] == "RULE-AM-002"
            for i in fails
        )
        clean_absent = not any(
            i["file"].endswith("clean_module.py") for i in result["items"]
        )
        analytics_absent = not any(
            i["file"].endswith("csv_analytics.py") and i["rule"] == "RULE-AM-001"
            for i in result["items"]
        )

        if bad_codec_fail and init_fail and clean_absent and analytics_absent:
            print("SELF-TEST PASS", file=sys.stderr)
            return True
        else:
            print(f"SELF-TEST FAIL: bad_codec={bad_codec_fail} init={init_fail} "
                  f"clean_absent={clean_absent} analytics_absent={analytics_absent}",
                  file=sys.stderr)
            print(json.dumps(result["items"], indent=2), file=sys.stderr)
            return False


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Anti-monolith architecture validator")
    parser.add_argument("src_root", nargs="?", type=Path, default=None,
                        help="Source root to scan (default: src/python/)")
    parser.add_argument("--repo-root", type=Path, default=_default_repo)
    parser.add_argument("--baseline", type=Path, default=_default_baseline)
    parser.add_argument("--json", action="store_true", dest="json_out",
                        help="Output machine-readable JSON")
    parser.add_argument("--self-test", action="store_true",
                        help="Run self-test against synthetic fixture")
    parser.add_argument("--check-new-files", action="store_true",
                        help="Exit 1 if any new-file violation found (for pre-commit)")
    args = parser.parse_args(argv)

    if args.self_test:
        ok = _run_self_test()
        return 0 if ok else 1

    src_root = args.src_root or (args.repo_root / "src" / "python")
    baseline = _load_baseline(args.baseline)
    result = scan(src_root, baseline, args.repo_root)

    if args.json_out:
        print(json.dumps(result, indent=2))
    else:
        print(f"=== validate_source_architecture ===")
        print(f"Result: {result['result']}  |  {result['summary']}")
        print(f"Blocks sprint: {result['blocks_sprint']}")
        if result["items"]:
            for item in sorted(result["items"], key=lambda x: (x["status"], x["file"])):
                print(f"  [{item['status']}] {item['rule']} — {item['file']}")
                print(f"         {item['description']} (current={item['current']}, cap={item['cap']})")
        else:
            print("  No violations found.")

    return 0 if not result["blocks_sprint"] else 1


if __name__ == "__main__":
    sys.exit(main())
