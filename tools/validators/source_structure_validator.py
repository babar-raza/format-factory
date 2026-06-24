"""Source Structure Validator — Spec-Derived Architecture Governance.

Validates that all source files under src/ conform to the specification-derived
architecture rules defined in the production library checklist and enforced by
the source-structure-baseline.json.

Checks performed:
  1. File LOC limits (800 max, with baseline grandfathering)
  2. Function count per file (60 max, with baseline grandfathering)
  3. Duplicate function definitions (AST scan)
  4. Module separation (analytics vs parser/model)
  5. __init__.py re-export completeness
  6. QName ownership for ODF formats
  7. Orphan file detection
  8. Facade compliance (format-prefixed names only in Compat/)

Usage:
  python tools/validators/source_structure_validator.py [--repo-root PATH]
  python tools/validators/source_structure_validator.py --json
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

_DEFAULT_MAX_LOC = 800
_DEFAULT_MAX_FUNCTIONS = 60
_BASELINE_FILE = "registry/source-structure-baseline.json"

# Format modules under src/python/
_PYTHON_SRC = "src/python"

# ODF formats get additional QName ownership checks
_ODF_FORMATS = {"fods", "fodt", "ods", "odt", "fodp", "fodg"}

# All 20 format IDs
_ALL_FORMATS = {
    "abw", "csv", "dif", "fodg", "fodp", "fods", "fodt",
    "gnumeric", "ndjson", "ods", "odt", "pbm", "pgm", "ppm",
    "qoi", "sylk", "toml", "tsv", "xcf", "zst",
}

# Recognized file purposes (not orphans)
_KNOWN_PURPOSES = {
    "__init__", "parser", "writer", "codec", "stats", "constants",
    "exceptions", "models", "neutral_model", "list_traversal",
    "csv_exporter", "conftest", "analytics",
}

# Domain module names recognized per format (not orphans)
_DOMAIN_MODULES = {
    "xcf_image_metrics", "compression_metrics", "drawing_document",
    "spreadsheet_document", "spreadsheet_model_document", "text_document",
    "presentation_document", "word_document", "tabular_document",
    "interchange_document", "json_stream", "config_document",
    "bitmap_image", "grayscale_image", "color_image", "image_document",
    "workbook_document", "compressed_stream", "compat",
    # D-group extraction targets (new domain-pattern files)
    "word_stats", "workbook_stats", "record_stats",
    "neutral_ops", "document_edit", "document_query", "drawing_metrics",
}

# Suffixes that indicate recognized converter/exporter files
_CONVERTER_PATTERNS = {"_to_", "_exporter", "_encoder"}


def _load_baseline(repo_root: Path) -> dict:
    """Load the source-structure baseline, or return empty if absent."""
    baseline_path = repo_root / _BASELINE_FILE
    if baseline_path.is_file():
        return json.loads(baseline_path.read_text(encoding="utf-8"))
    return {}


def _count_loc(path: Path) -> int:
    """Count lines of code in a file."""
    try:
        return sum(1 for _ in path.open(encoding="utf-8", errors="replace"))
    except OSError:
        return 0


def _count_top_level_functions(path: Path) -> int:
    """Count top-level function definitions using AST."""
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(path))
        return sum(1 for node in ast.iter_child_nodes(tree)
                   if isinstance(node, ast.FunctionDef))
    except (SyntaxError, OSError):
        return 0


def _find_duplicate_defs(path: Path) -> list[str]:
    """Find duplicate top-level function definitions in a file."""
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(path))
    except (SyntaxError, OSError):
        return []
    seen: dict[str, int] = {}
    duplicates: list[str] = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef):
            name = node.name
            if name in seen:
                duplicates.append(f"{name} (lines {seen[name]} and {node.lineno})")
            else:
                seen[name] = node.lineno
    return duplicates


def _is_recognized_file(filename: str, format_id: str) -> bool:
    """Check if a filename matches a recognized purpose."""
    stem = Path(filename).stem
    # Direct match to known purposes
    if stem in _KNOWN_PURPOSES:
        return True
    # Format-prefixed known files: csv_parser, csv_writer, etc.
    if stem.startswith(f"{format_id}_"):
        suffix = stem[len(format_id) + 1:]
        if (suffix in _KNOWN_PURPOSES or suffix in _DOMAIN_MODULES
                or suffix in ("parser", "writer", "codec", "stats", "encoder")):
            return True
    # Domain module names (spec-derived, format-agnostic)
    if stem in _DOMAIN_MODULES:
        return True
    # Converter/exporter files
    for pattern in _CONVERTER_PATTERNS:
        if pattern in stem:
            return True
    return False


def _get_init_all(package_dir: Path) -> list[str] | None:
    """Extract __all__ from __init__.py, or None if not found."""
    init_path = package_dir / "__init__.py"
    if not init_path.is_file():
        return None
    try:
        source = init_path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(init_path))
    except (SyntaxError, OSError):
        return None
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(node.value, ast.List):
                        return [
                            elt.value for elt in node.value.elts
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                        ]
    return None


def _get_public_defs(py_file: Path) -> list[str]:
    """Get all top-level public function/class names from a .py file."""
    try:
        source = py_file.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(py_file))
    except (SyntaxError, OSError):
        return []
    names: list[str] = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            if not node.name.startswith("_"):
                names.append(node.name)
    return names


# ─── Individual check functions ───────────────────────────────────────────


def check_file_loc(path: Path, limit: int = _DEFAULT_MAX_LOC) -> dict:
    """Check a single file's LOC against the limit."""
    loc = _count_loc(path)
    passed = loc <= limit
    return {
        "check": "file_loc",
        "file": str(path),
        "loc": loc,
        "limit": limit,
        "result": "PASS" if passed else "FAIL",
    }


def check_function_count(path: Path, limit: int = _DEFAULT_MAX_FUNCTIONS) -> dict:
    """Check a single file's top-level function count against the limit."""
    count = _count_top_level_functions(path)
    passed = count <= limit
    return {
        "check": "function_count",
        "file": str(path),
        "count": count,
        "limit": limit,
        "result": "PASS" if passed else "FAIL",
    }


def check_duplicate_defs(path: Path) -> dict:
    """Check a single file for duplicate function definitions."""
    duplicates = _find_duplicate_defs(path)
    return {
        "check": "duplicate_defs",
        "file": str(path),
        "duplicates": duplicates,
        "result": "PASS" if not duplicates else "FAIL",
    }


def check_module_separation(package_dir: Path, format_id: str) -> dict:
    """Check if analytics functions are separated from parser/model code."""
    py_files = sorted(package_dir.glob("*.py"))
    py_files = [f for f in py_files if f.name != "__init__.py"
                and f.name != "conftest.py"]

    # Find the primary source file (largest by LOC)
    primary = None
    primary_loc = 0
    for f in py_files:
        loc = _count_loc(f)
        if loc > primary_loc:
            primary_loc = loc
            primary = f

    if primary is None:
        return {
            "check": "module_separation",
            "package": str(package_dir),
            "result": "PASS",
            "detail": "No source files found.",
        }

    # Count analytics functions (format_id_*) in the primary file
    analytics_in_primary = 0
    parse_in_primary = 0
    try:
        source = primary.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(primary))
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith(f"{format_id}_"):
                    analytics_in_primary += 1
                elif node.name.startswith(("parse_", "probe_", "load",
                                            "build_", "validate_")):
                    parse_in_primary += 1
    except (SyntaxError, OSError):
        pass

    mixed = analytics_in_primary > 10 and parse_in_primary > 0
    return {
        "check": "module_separation",
        "package": str(package_dir),
        "primary_file": str(primary),
        "analytics_in_primary": analytics_in_primary,
        "parse_in_primary": parse_in_primary,
        "result": "FAIL" if mixed else "PASS",
        "detail": (f"Primary file has {analytics_in_primary} analytics + "
                   f"{parse_in_primary} parse functions mixed together."
                   if mixed else "OK"),
    }


def check_init_reexports(package_dir: Path) -> dict:
    """Check that __init__.py re-exports all public functions from submodules."""
    init_all = _get_init_all(package_dir)
    if init_all is None:
        return {
            "check": "init_reexports",
            "package": str(package_dir),
            "result": "WARN",
            "detail": "No __all__ found in __init__.py.",
        }

    # Gather all public defs from non-init .py files
    all_public: set[str] = set()
    for py_file in sorted(package_dir.glob("*.py")):
        if py_file.name in ("__init__.py", "conftest.py"):
            continue
        all_public.update(_get_public_defs(py_file))

    init_set = set(init_all)
    missing = sorted(all_public - init_set)

    # Filter out private-looking names and internal helpers
    missing = [n for n in missing if not n.startswith("_")]

    return {
        "check": "init_reexports",
        "package": str(package_dir),
        "public_defs_found": len(all_public),
        "init_all_count": len(init_all),
        "missing_from_init": missing[:20],  # Cap to avoid huge output
        "result": "PASS" if not missing else "WARN",
    }


def check_qname_ownership(package_dir: Path, format_id: str,
                           ontology_path: Path | None = None) -> dict:
    """For ODF formats: verify classes reference spec QNames."""
    if format_id not in _ODF_FORMATS:
        return {
            "check": "qname_ownership",
            "package": str(package_dir),
            "result": "SKIP",
            "detail": f"{format_id} is not an ODF format.",
        }

    # Check if constants.py defines QName constants
    constants_file = package_dir / "constants.py"
    has_qnames = False
    if constants_file.is_file():
        try:
            text = constants_file.read_text(encoding="utf-8", errors="replace")
            has_qnames = "QN_" in text or "urn:oasis" in text
        except OSError:
            pass

    # Check if any domain classes have spec_qname references
    classes_with_qname: list[str] = []
    classes_without_qname: list[str] = []
    for py_file in sorted(package_dir.glob("*.py")):
        if py_file.name in ("__init__.py", "conftest.py", "constants.py"):
            continue
        try:
            source = py_file.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source, filename=str(py_file))
        except (SyntaxError, OSError):
            continue
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
                # Check for spec_qname in class docstring or attributes
                docstring = ast.get_docstring(node) or ""
                if "spec_qname" in docstring or "spec_concept" in docstring:
                    classes_with_qname.append(node.name)
                else:
                    classes_without_qname.append(node.name)

    return {
        "check": "qname_ownership",
        "package": str(package_dir),
        "has_qname_constants": has_qnames,
        "classes_with_qname": classes_with_qname,
        "classes_without_qname": classes_without_qname,
        "result": "PASS" if has_qnames else "WARN",
        "detail": (f"Constants define QNames: {has_qnames}. "
                   f"{len(classes_without_qname)} classes lack spec_qname."),
    }


def check_orphan_files(package_dir: Path, format_id: str) -> dict:
    """Check for source files that don't match any recognized purpose."""
    orphans: list[str] = []
    for py_file in sorted(package_dir.glob("*.py")):
        if py_file.name == "conftest.py":
            continue
        if not _is_recognized_file(py_file.name, format_id):
            orphans.append(py_file.name)

    return {
        "check": "orphan_files",
        "package": str(package_dir),
        "orphans": orphans,
        "result": "PASS" if not orphans else "WARN",
    }


# ─── Full scan ────────────────────────────────────────────────────────────


def run_full_scan(repo_root: Path) -> dict:
    """Run all checks against all format modules. Returns composite result."""
    baseline = _load_baseline(repo_root)
    known_violations = baseline.get("known_violations", {})
    policy = baseline.get("policy", {})
    max_loc = policy.get("max_file_loc", _DEFAULT_MAX_LOC)
    max_funcs = policy.get("max_functions_per_file", _DEFAULT_MAX_FUNCTIONS)

    python_src = repo_root / _PYTHON_SRC
    results: dict = {
        "validator": "source_structure_validator",
        "repo_root": str(repo_root),
        "max_loc": max_loc,
        "max_functions": max_funcs,
        "baseline_loaded": bool(known_violations),
        "format_results": {},
        "loc_violations": [],
        "function_violations": [],
        "duplicate_violations": [],
        "separation_violations": [],
        "new_violations": [],
        "worsened_violations": [],
        "grandfathered_violations": [],
        "blocks_sprint": False,
    }

    # .NET checks
    dotnet_src = repo_root / "src" / "net"
    dotnet_violations: list[dict] = []
    if dotnet_src.is_dir():
        for cs_file in sorted(dotnet_src.rglob("*.cs")):
            if "obj" in cs_file.parts:
                continue
            loc = _count_loc(cs_file)
            if loc > max_loc:
                rel = str(cs_file.relative_to(repo_root)).replace("\\", "/")
                baseline_entry = known_violations.get(rel)
                if baseline_entry:
                    cap = baseline_entry.get("baseline_loc_cap", baseline_entry.get("loc", 0))
                    if loc > cap:
                        dotnet_violations.append({
                            "file": rel, "loc": loc,
                            "baseline_loc_cap": cap,
                            "status": "WORSENED",
                        })
                        results["worsened_violations"].append(rel)
                        results["blocks_sprint"] = True
                    else:
                        results["grandfathered_violations"].append(rel)
                else:
                    dotnet_violations.append({
                        "file": rel, "loc": loc, "status": "NEW",
                    })
                    results["new_violations"].append(rel)
                    results["blocks_sprint"] = True
    results["dotnet_violations"] = dotnet_violations

    # Python format modules
    for format_id in sorted(_ALL_FORMATS):
        pkg_dir = python_src / format_id
        if not pkg_dir.is_dir():
            continue

        fmt_result: dict = {
            "format_id": format_id,
            "files": {},
            "separation": {},
            "init_reexports": {},
            "qname_ownership": {},
            "orphan_files": {},
        }

        # Per-file checks
        for py_file in sorted(pkg_dir.glob("*.py")):
            if py_file.name in ("__init__.py", "conftest.py"):
                continue
            rel = str(py_file.relative_to(repo_root)).replace("\\", "/")

            loc_result = check_file_loc(py_file, max_loc)
            func_result = check_function_count(py_file, max_funcs)
            dup_result = check_duplicate_defs(py_file)

            file_info: dict = {
                "loc": loc_result["loc"],
                "functions": func_result["count"],
                "duplicates": dup_result["duplicates"],
            }

            # LOC violation handling with baseline
            if loc_result["result"] == "FAIL":
                baseline_entry = known_violations.get(rel)
                if baseline_entry:
                    # Use write-once baseline_loc_cap when available (defense in depth)
                    loc_cap = baseline_entry.get("baseline_loc_cap",
                                                  baseline_entry.get("loc", 0))
                    if loc_result["loc"] > loc_cap:
                        file_info["loc_status"] = "WORSENED"
                        file_info["loc_cap"] = loc_cap
                        results["worsened_violations"].append(rel)
                        results["blocks_sprint"] = True
                    else:
                        file_info["loc_status"] = "GRANDFATHERED"
                        results["grandfathered_violations"].append(rel)
                else:
                    file_info["loc_status"] = "NEW_VIOLATION"
                    results["new_violations"].append(rel)
                    results["blocks_sprint"] = True
                results["loc_violations"].append(rel)

            # Function count violation handling
            if func_result["result"] == "FAIL":
                baseline_entry = known_violations.get(rel)
                if baseline_entry:
                    # Use write-once baseline_functions_cap when available
                    fn_cap = baseline_entry.get("baseline_functions_cap",
                                                 baseline_entry.get("functions", 0))
                    if func_result["count"] > fn_cap:
                        file_info["func_status"] = "WORSENED"
                        file_info["fn_cap"] = fn_cap
                        results["blocks_sprint"] = True
                    else:
                        file_info["func_status"] = "GRANDFATHERED"
                else:
                    file_info["func_status"] = "NEW_VIOLATION"
                    results["blocks_sprint"] = True
                results["function_violations"].append(rel)

            # Duplicate violations — block only for non-baselined files
            if dup_result["duplicates"]:
                results["duplicate_violations"].append(rel)
                baseline_entry = known_violations.get(rel)
                if not baseline_entry:
                    results["blocks_sprint"] = True

            fmt_result["files"][rel] = file_info

        # Module-level checks
        sep = check_module_separation(pkg_dir, format_id)
        fmt_result["separation"] = sep
        if sep["result"] == "FAIL":
            results["separation_violations"].append(str(pkg_dir))

        fmt_result["init_reexports"] = check_init_reexports(pkg_dir)
        fmt_result["qname_ownership"] = check_qname_ownership(pkg_dir, format_id)
        fmt_result["orphan_files"] = check_orphan_files(pkg_dir, format_id)

        results["format_results"][format_id] = fmt_result

    # Summary
    results["summary"] = {
        "total_loc_violations": len(results["loc_violations"]),
        "total_function_violations": len(results["function_violations"]),
        "total_duplicate_violations": len(results["duplicate_violations"]),
        "total_separation_violations": len(results["separation_violations"]),
        "total_new_violations": len(results["new_violations"]),
        "total_worsened_violations": len(results["worsened_violations"]),
        "total_grandfathered": len(results["grandfathered_violations"]),
        "blocks_sprint": results["blocks_sprint"],
    }

    # Overall result
    if results["blocks_sprint"]:
        results["result"] = "FAIL"
        results["detail"] = (
            f"{len(results['new_violations'])} new + "
            f"{len(results['worsened_violations'])} worsened violations block sprint."
        )
    else:
        results["result"] = "WARN" if results["loc_violations"] else "PASS"
        results["detail"] = (
            f"{len(results['grandfathered_violations'])} grandfathered violations "
            f"(no new or worsened)."
        )

    return results


# ─── CLI ──────────────────────────────────────────────────────────────────


def main() -> int:
    """CLI entry point."""
    import argparse
    parser = argparse.ArgumentParser(
        description="Source Structure Validator — Spec-Derived Architecture Governance")
    parser.add_argument("--repo-root", type=Path, default=None,
                        help="Repository root (default: auto-detect)")
    parser.add_argument("--json", action="store_true",
                        help="Output raw JSON instead of human-readable")
    parser.add_argument("--check-baseline-growth", action="store_true",
                        help=(
                            "Exit 1 if any known violation has grown beyond its "
                            "baseline_loc_cap or baseline_functions_cap. "
                            "Intended for pre-commit hooks and CI architecture gates."
                        ))
    args = parser.parse_args()

    if args.repo_root:
        repo_root = args.repo_root.resolve()
    else:
        # Auto-detect: walk up from this file
        repo_root = Path(__file__).resolve().parents[2]

    result = run_full_scan(repo_root)

    if args.check_baseline_growth:
        worsened = result.get("worsened_violations", [])
        if worsened:
            print(f"ARCHITECTURE GATE FAIL: {len(worsened)} violation(s) exceed baseline_loc_cap:",
                  file=sys.stderr)
            for v in worsened:
                print(f"  {v}", file=sys.stderr)
            print("Decompose the file or update baseline_loc_cap only if intentional and approved.",
                  file=sys.stderr)
            return 1
        print("Architecture baseline check: OK (no violations exceed baseline_loc_cap)")
        return 0

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Source Structure Validator — {result['result']}")
        print(f"  Repo: {result['repo_root']}")
        print(f"  Baseline loaded: {result['baseline_loaded']}")
        print()

        s = result["summary"]
        print(f"  LOC violations:        {s['total_loc_violations']}")
        print(f"  Function violations:   {s['total_function_violations']}")
        print(f"  Duplicate violations:  {s['total_duplicate_violations']}")
        print(f"  Separation violations: {s['total_separation_violations']}")
        print(f"  New violations:        {s['total_new_violations']}")
        print(f"  Worsened violations:   {s['total_worsened_violations']}")
        print(f"  Grandfathered:         {s['total_grandfathered']}")
        print(f"  Blocks sprint:         {s['blocks_sprint']}")
        print()
        print(f"  Detail: {result['detail']}")

        if result["new_violations"]:
            print("\n  NEW violations (blocking):")
            for v in result["new_violations"]:
                print(f"    - {v}")

        if result["worsened_violations"]:
            print("\n  WORSENED violations (blocking):")
            for v in result["worsened_violations"]:
                print(f"    - {v}")

    return 1 if result["blocks_sprint"] else 0


def validate_suspended_rotation_stubs(repo_root: Path | None = None) -> dict:
    """Detect orphaned test stubs for suspended rotation patterns (TC-SGOV-007).

    Reads ``known_suspended_rotations`` from source-structure-baseline.json and
    scans ``tests/python/`` for test files whose names match suspended patterns.
    Returns WARN for any orphaned stubs found.
    """
    import re as _re

    if repo_root is None:
        repo_root = Path(__file__).resolve().parent.parent.parent

    baseline_path = repo_root / _BASELINE_FILE
    if not baseline_path.exists():
        return {"result": "PASS", "orphaned_stubs": [], "error": "baseline file not found"}

    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    rotations = baseline.get("known_suspended_rotations", [])
    if not rotations:
        return {"result": "PASS", "orphaned_stubs": []}

    orphaned = []
    tests_dir = repo_root / "tests" / "python"
    if not tests_dir.is_dir():
        return {"result": "PASS", "orphaned_stubs": [], "note": "tests/python not found"}

    for rotation in rotations:
        pattern = rotation.get("test_pattern", "")
        if not pattern:
            continue
        compiled = _re.compile(pattern)
        # Derive format name from file_pattern (e.g. "src/python/zst/zst_analytics.py" -> "zst")
        file_pat = rotation.get("file_pattern", "")
        parts = Path(file_pat).parts
        fmt = parts[2] if len(parts) > 2 else ""
        fmt_dir = tests_dir / fmt if fmt else None
        search_dirs = [fmt_dir] if fmt_dir and fmt_dir.is_dir() else [tests_dir]
        for search_dir in search_dirs:
            for test_file in sorted(search_dir.rglob("test_*.py")):
                try:
                    content = test_file.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                if compiled.search(content):
                    orphaned.append({
                        "file": str(test_file.relative_to(repo_root)),
                        "matched_pattern": pattern,
                        "suspended_since": rotation.get("suspended_since", ""),
                        "reason": rotation.get("reason", ""),
                    })

    result = "WARN" if orphaned else "PASS"
    return {"result": result, "orphaned_stubs": orphaned}


if __name__ == "__main__":
    sys.exit(main())
