"""validate_migration_safe.py — Phase F2 migration safety validator (FF-FORENSIC-AUDIT-20260623)

Before any source restructuring (moving spec/ files), scans all Python files to
detect import dependencies on spec/ and Compat/ files that would break if moved.

OUTPUT: For each spec/ file, lists all callers that import from it.
Safe migration = no PRODUCTION callers (parsers/models importing from spec stubs).

Architecture stubs (spec/ and Compat/) are supposed to be imported BY facades only,
not by production parsers/models. This validator flags violations.

Usage:
    python tools/backfill/validate_migration_safe.py [--format FMT] [--verbose]
"""
from __future__ import annotations

import argparse
import ast
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parent.parent.parent

# These file patterns are SAFE callers of spec/ stubs (expected imports)
_SAFE_CALLER_PATTERNS = (
    "/Compat/",     # Compat facades import from spec/ — expected
    "/spec/",       # spec/ can import from other spec/ — expected
    "/test_",       # tests may import spec classes — expected
    "tests/",       # test files — expected
)

# These patterns in the CALLER indicate production code that should NOT import spec stubs
_PRODUCTION_PATTERNS = (
    "_parser.py",
    "_codec.py",
    "_writer.py",
    "_model.py",
    "neutral_model.py",
    "models.py",
    "__init__.py",
)

_FORMATS = [
    "abw", "csv", "dif", "fodg", "fodp", "fods", "fodt",
    "gnumeric", "ndjson", "ods", "odt", "pbm", "pgm", "ppm",
    "qoi", "sylk", "toml", "tsv", "xcf", "zst",
]


def _extract_imports(py_file: Path) -> list[str]:
    """Extract all import module strings from a Python file (AST-based)."""
    try:
        tree = ast.parse(py_file.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imports.append(module)
    return imports


def _is_safe_caller(caller_path: str) -> bool:
    """Return True if caller is expected to import from spec/ stubs."""
    return any(pat in caller_path for pat in _SAFE_CALLER_PATTERNS)


def _is_production_caller(caller_path: str) -> bool:
    """Return True if caller is production code (parser/model/writer)."""
    return any(caller_path.endswith(pat) for pat in _PRODUCTION_PATTERNS)


def scan_format(fmt: str) -> dict[str, Any]:
    """Scan one format package for unsafe imports of spec/ stubs."""
    fmt_dir = _REPO / "src/python" / fmt
    if not fmt_dir.exists():
        return {"format": fmt, "skipped": True, "reason": "format dir not found"}

    spec_dir = fmt_dir / "spec"
    compat_dir = fmt_dir / "Compat"

    # Collect all spec/ and Compat/ files as potential import targets
    spec_files: set[str] = set()
    for d in [spec_dir, compat_dir]:
        if d.exists():
            for py in d.rglob("*.py"):
                if py.name != "__init__.py":
                    spec_files.add(str(py.relative_to(_REPO)).replace("\\", "/"))

    if not spec_files:
        return {
            "format": fmt,
            "spec_files": [],
            "production_callers": [],
            "safe": True,
            "summary": f"No spec/ or Compat/ files found in {fmt}/",
        }

    # Scan all Python files in format package for imports of spec/ files
    production_callers = []
    safe_callers = []

    all_py = list(fmt_dir.rglob("*.py"))
    for py_file in all_py:
        rel = str(py_file.relative_to(_REPO)).replace("\\", "/")

        # Is this file itself a spec/ or Compat/ file? Skip it.
        if "/spec/" in rel or "/Compat/" in rel:
            continue

        # Check if this file imports from spec/ or Compat/ via relative imports
        try:
            content = py_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        # Check for relative imports referencing spec/ or Compat/
        imports_spec = (
            "from .spec" in content
            or "from ..spec" in content
            or "from .Compat" in content
            or "from ..Compat" in content
            or f"from src.python.{fmt}.spec" in content
            or f"from src.python.{fmt}.Compat" in content
        )

        if not imports_spec:
            continue

        caller_info = {
            "caller_file": rel,
            "is_production": _is_production_caller(py_file.name),
            "is_safe": _is_safe_caller(rel),
        }

        if _is_production_caller(py_file.name) and not _is_safe_caller(rel):
            # Production code importing from spec stubs — RISKY
            caller_info["risk"] = "HIGH"
            caller_info["reason"] = (
                f"Production file {py_file.name!r} imports spec/ stubs. "
                "Moving spec/ would break production imports."
            )
            production_callers.append(caller_info)
        else:
            caller_info["risk"] = "LOW"
            safe_callers.append(caller_info)

    is_safe = len(production_callers) == 0

    return {
        "format": fmt,
        "spec_files": sorted(spec_files),
        "spec_file_count": len(spec_files),
        "production_callers": production_callers,
        "safe_callers": safe_callers,
        "safe": is_safe,
        "summary": (
            f"SAFE: {len(spec_files)} spec files, no production callers"
            if is_safe
            else f"RISKY: {len(production_callers)} production caller(s) import spec stubs"
        ),
    }


def run(
    format_filter: str | None = None,
    verbose: bool = False,
    out_path: Path | None = None,
) -> dict[str, Any]:
    """Run migration safety validation across all (or one) format(s)."""
    formats = [format_filter] if format_filter else _FORMATS

    results = []
    total_risky = 0
    total_safe = 0

    for fmt in formats:
        result = scan_format(fmt)
        results.append(result)
        if result.get("safe", True):
            total_safe += 1
        else:
            total_risky += 1

    all_safe = total_risky == 0

    report = {
        "audit_type": "migration_safety_validation",
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "summary": {
            "formats_audited": len(results),
            "safe_formats": total_safe,
            "risky_formats": total_risky,
            "migration_safe_overall": all_safe,
        },
        "per_format": results,
    }

    # Print summary
    print("Migration Safety Validator")
    print("=" * 50)
    print(f"Formats scanned:  {len(results)}")
    print(f"Safe formats:     {total_safe}")
    print(f"Risky formats:    {total_risky}")
    print(f"Overall verdict:  {'SAFE' if all_safe else 'RISKY — check production_callers'}")
    print()

    for r in results:
        if r.get("skipped"):
            continue
        prod_callers = r.get("production_callers", [])
        if prod_callers or verbose:
            print(f"  {r['format']}: {r['summary']}")
            if prod_callers:
                for c in prod_callers[:3]:
                    print(f"    RISKY: {c['caller_file']}: {c['reason'][:80]}")

    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"\nReport written: {out_path}")

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate migration safety of spec/ file moves")
    parser.add_argument("--format", help="Scan only this format")
    parser.add_argument("--verbose", action="store_true", help="Show all format results")
    parser.add_argument("--out", help="Write report to JSON file")
    args = parser.parse_args()

    out_path = Path(args.out) if args.out else None
    report = run(format_filter=args.format, verbose=args.verbose, out_path=out_path)

    # Exit with 1 if risky formats found
    if not report.get("summary", {}).get("migration_safe_overall", True):
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()
