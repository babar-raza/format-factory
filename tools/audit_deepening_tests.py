#!/usr/bin/env python3
"""Audit deepening tests for spec backing and arithmetic patterns.

Classifies every file in tests/python/deepening/ (and optionally dogfood/) into:
  spec_backed     - file references a GAP-* ledger ID or FACT-* spec fact
  arithmetic_only - file tests arithmetic-formula functions (*_mod_N*, *_times_N*)
  dogfood_pipeline- file tests a load->transform->export pipeline across formats
  mixed           - file contains both arithmetic and legitimate analytics tests
  unknown         - cannot classify automatically

Outputs:
  registry/deepening-test-audit.yaml        -- full classification report
  registry/arithmetic-deepening-tests.txt   -- one file path per line (for --skip-arithmetic)

Usage:
  python tools/audit_deepening_tests.py
  python tools/audit_deepening_tests.py --dry-run    # print summary, don't write files
  python tools/audit_deepening_tests.py --include-dogfood
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path
from typing import NamedTuple

REPO_ROOT = Path(__file__).resolve().parent.parent
DEEPENING_DIR = REPO_ROOT / "tests" / "python" / "deepening"
DOGFOOD_DIR = REPO_ROOT / "tests" / "python" / "dogfood"
AUDIT_OUTPUT = REPO_ROOT / "registry" / "deepening-test-audit.yaml"
MANIFEST_OUTPUT = REPO_ROOT / "registry" / "arithmetic-deepening-tests.txt"

# All known format names
KNOWN_FORMATS = {
    "abw", "csv", "dif", "fodg", "fodp", "fods", "fodt",
    "gnumeric", "ndjson", "ods", "odt", "pbm", "pgm", "ppm",
    "qoi", "sylk", "toml", "tsv", "xcf", "zst",
}

# Patterns that indicate arithmetic formula functions (suspended)
_ARITH_PATTERNS = [
    re.compile(r'\b\w+_mod_\d+\b'),              # fods_x_mod_479
    re.compile(r'\b\w+_times_\d+\b'),             # abw_x_times_4950
    re.compile(r'\b\w+_times_[a-z]+_[a-z]+\b'),   # abw_x_times_eighty_nine
    re.compile(r'\b\w+_plus_\d+\b'),              # zst_x_plus_197
    re.compile(r'\b\w+_minus_\d+\b'),             # csv_x_minus_100
    # Long compound arithmetic names (>55 chars for a single identifier segment)
    # e.g. zst_compressed_mod_479_times_4950_plus_decompressed_times_197_plus_file_size_times_204
]

# Patterns that indicate spec backing
_SPEC_PATTERNS = [
    re.compile(r'GAP-[A-Z]+-\w+'),               # GAP-FODS-COMM-LOAD-001
    re.compile(r'FACT-[A-Z]+-\w+'),               # FACT-FODS-003
    re.compile(r'spec_fact'),                      # spec_fact reference
    re.compile(r'gap_ledger_ref'),                 # explicit gap_ledger_ref
    re.compile(r'capability_ref'),                 # capability reference
]


class FileResult(NamedTuple):
    rel_path: str
    classification: str
    arith_functions: list[str]
    test_count: int
    formats_covered: list[str]
    reason: str


def _extract_formats_from_filename(filename: str) -> list[str]:
    """Extract format names from a test filename like test_r273_dif_sylk_abw_fods_deepening."""
    stem = Path(filename).stem  # e.g. test_r273_dif_sylk_abw_fods_deepening
    parts = stem.split("_")
    return [p for p in parts if p in KNOWN_FORMATS]


def _extract_identifiers(content: str) -> set[str]:
    """Extract all identifiers from Python source (names + attributes)."""
    try:
        tree = ast.parse(content)
        names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
        attrs = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
        return names | attrs
    except SyntaxError:
        # Fallback: regex-based extraction
        return set(re.findall(r'\b[a-z][a-z0-9_]{10,}\b', content))


def _count_tests(content: str) -> int:
    """Count test functions in file."""
    try:
        tree = ast.parse(content)
        return sum(
            1 for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
        )
    except SyntaxError:
        return content.count("\ndef test_") + content.count("\n    def test_")


def _find_arithmetic_functions(identifiers: set[str]) -> list[str]:
    """Return list of identifiers that match arithmetic patterns."""
    results = []
    for ident in identifiers:
        # Skip short identifiers (not function names)
        if len(ident) < 15:
            continue
        for pat in _ARITH_PATTERNS:
            if pat.search(ident):
                results.append(ident)
                break
        # Also catch very long compound names (>60 chars) that are format-prefixed
        if len(ident) > 60 and ident[:3] in {fmt[:3] for fmt in KNOWN_FORMATS}:
            if ident not in results:
                results.append(ident)
    return sorted(set(results))


def _has_spec_backing(content: str) -> bool:
    """Return True if file references a spec fact or GAP-ledger ID."""
    return any(pat.search(content) for pat in _SPEC_PATTERNS)


def _is_dogfood_pipeline(content: str, identifiers: set[str]) -> bool:
    """Return True if file tests a multi-format load->transform->export pipeline."""
    # Dogfood files typically import from 2+ formats AND use export/write functions
    format_imports = 0
    for fmt in KNOWN_FORMATS:
        if f"from src.python.{fmt}" in content or f"import {fmt}" in content:
            format_imports += 1
    write_present = any(w in content for w in ("export", "write", "save", "to_ndjson", "dump"))
    return format_imports >= 2 and write_present


def classify_file(filepath: Path) -> FileResult:
    """Classify a single deepening/dogfood test file."""
    rel_path = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return FileResult(
            rel_path=rel_path, classification="error",
            arith_functions=[], test_count=0, formats_covered=[],
            reason=f"read error: {e}",
        )

    identifiers = _extract_identifiers(content)
    test_count = _count_tests(content)
    formats = _extract_formats_from_filename(filepath.name)

    # 1. Spec-backed check (highest priority — even if arithmetic patterns present)
    if _has_spec_backing(content):
        return FileResult(
            rel_path=rel_path, classification="spec_backed",
            arith_functions=[], test_count=test_count, formats_covered=formats,
            reason="contains GAP-* or FACT-* or spec_fact reference",
        )

    # 2. Arithmetic check
    arith = _find_arithmetic_functions(identifiers)
    has_arith = bool(arith)

    # 3. Dogfood pipeline check
    is_dogfood = _is_dogfood_pipeline(content, identifiers)

    # 4. Classify
    if has_arith and is_dogfood:
        classification = "mixed"
        reason = f"arithmetic functions AND dogfood pipeline; arith count={len(arith)}"
    elif has_arith:
        # Check if ALL tests are arithmetic (vs. just some)
        # If more than half the test functions test arithmetic functions → arithmetic_only
        arith_set = set(arith)
        test_call_count = sum(1 for ident in identifiers if ident in arith_set)
        if test_call_count > 0:
            classification = "arithmetic_only"
            reason = f"{len(arith)} arithmetic formula function(s) tested; examples: {arith[:2]}"
        else:
            classification = "unknown"
            reason = "arithmetic patterns in identifiers but not called in test functions"
    elif is_dogfood:
        classification = "dogfood_pipeline"
        reason = "multi-format load->transform->export pipeline"
    elif test_count > 0:
        classification = "unknown"
        reason = "no arithmetic patterns and no spec backing detected"
    else:
        classification = "unknown"
        reason = "no test functions found"

    return FileResult(
        rel_path=rel_path, classification=classification,
        arith_functions=arith[:5],  # store up to 5 examples
        test_count=test_count, formats_covered=formats,
        reason=reason,
    )


def run_audit(
    include_dogfood: bool = False,
    dry_run: bool = False,
) -> dict:
    """Audit all deepening tests. Return summary dict."""
    directories = [DEEPENING_DIR]
    if include_dogfood:
        directories.append(DOGFOOD_DIR)

    files: list[FileResult] = []
    for d in directories:
        if not d.is_dir():
            print(f"WARNING: directory not found: {d}", file=sys.stderr)
            continue
        for fp in sorted(d.glob("test_*.py")):
            result = classify_file(fp)
            files.append(result)

    # Tally
    counts: dict[str, int] = {}
    for r in files:
        counts[r.classification] = counts.get(r.classification, 0) + 1

    arithmetic_files = [r.rel_path for r in files if r.classification == "arithmetic_only"]
    mixed_files = [r.rel_path for r in files if r.classification == "mixed"]
    # Treat mixed as arithmetic for skip purposes (conservative)
    skip_candidates = arithmetic_files + mixed_files

    total = len(files)
    print(f"\nDeepening Test Audit Summary")
    print(f"  Total files scanned: {total}")
    for cls, n in sorted(counts.items()):
        pct = 100 * n / total if total else 0
        print(f"  {cls:20s}: {n:5d} ({pct:.1f}%)")
    print(f"\n  Skip candidates (arithmetic_only + mixed): {len(skip_candidates)}")

    if dry_run:
        print("\n[dry-run] Not writing output files.")
        return {"counts": counts, "total": total, "skip_candidates": len(skip_candidates)}

    # Write audit YAML
    lines = ["# Deepening Test Audit — Format Factory", "# Generated by tools/audit_deepening_tests.py", ""]
    lines.append(f"audit_date: \"2026-06-18\"")
    lines.append(f"total_files_scanned: {total}")
    lines.append("counts:")
    for cls, n in sorted(counts.items()):
        lines.append(f"  {cls}: {n}")
    lines.append("")
    lines.append("files:")
    for r in files:
        lines.append(f"  - rel_path: \"{r.rel_path}\"")
        lines.append(f"    classification: \"{r.classification}\"")
        lines.append(f"    test_count: {r.test_count}")
        lines.append(f"    formats_covered: {r.formats_covered!r}")
        lines.append(f"    reason: \"{r.reason}\"")
        if r.arith_functions:
            lines.append(f"    arith_functions_sample: {r.arith_functions!r}")

    audit_text = "\n".join(lines) + "\n"
    AUDIT_OUTPUT.write_text(audit_text, encoding="utf-8")
    print(f"\nWrote audit: {AUDIT_OUTPUT}")

    # Write arithmetic manifest (one path per line)
    manifest_text = "\n".join(skip_candidates) + ("\n" if skip_candidates else "")
    MANIFEST_OUTPUT.write_text(manifest_text, encoding="utf-8")
    print(f"Wrote arithmetic manifest: {MANIFEST_OUTPUT} ({len(skip_candidates)} files)")

    return {
        "counts": counts,
        "total": total,
        "skip_candidates": len(skip_candidates),
        "audit_path": str(AUDIT_OUTPUT),
        "manifest_path": str(MANIFEST_OUTPUT),
    }


def main():
    parser = argparse.ArgumentParser(description="Audit deepening tests for arithmetic patterns")
    parser.add_argument("--dry-run", action="store_true", help="Print summary only, don't write files")
    parser.add_argument("--include-dogfood", action="store_true", help="Also scan tests/python/dogfood/")
    args = parser.parse_args()

    result = run_audit(include_dogfood=args.include_dogfood, dry_run=args.dry_run)
    skip_count = result.get("skip_candidates", 0)
    total = result.get("total", 0)
    if skip_count > 0:
        pct = 100 * skip_count / total if total else 0
        print(f"\n{skip_count}/{total} files ({pct:.1f}%) are skip candidates.")
        if not args.dry_run:
            print(f"Use --skip-arithmetic flag in pytest to exclude these from runs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
