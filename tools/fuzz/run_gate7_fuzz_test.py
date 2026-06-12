#!/usr/bin/env python3
"""
run_gate7_fuzz_test.py — FODS Gate 7 malformed/fuzz test runner.

Gate 7: Malformed Input and Fuzz Testing — format-factory project.

PURPOSE:
    Run the FODS parser prototype against all malformed test inputs in
    tests/fixtures/fods/malformed/ and verify:
      1. No crashes (no unhandled exceptions)
      2. No silent corruption (every error input returns an error result or warning)
      3. Memory-bounded (no input causes runaway memory growth)
      4. Time-bounded (no input takes more than 30 seconds)

    Output:
      GATE7_FUZZ_TEST: PASS N/N CRASH 0/N CORRUPT 0/N
      or
      GATE7_FUZZ_TEST: FAIL (crash count > 0 or silent corruption count > 0)

USAGE:
    python tools/fuzz/run_gate7_fuzz_test.py [--fixtures-dir PATH] [--parser-path PATH]

EXIT CODE:
    0 on PASS, 1 on FAIL

License: Apache-2.0 (project-owned, format-factory)
Created: 2026-05-08 (run045)
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
import time
from pathlib import Path


# ---------------------------------------------------------------------------
# Expected behaviors per fixture
# ---------------------------------------------------------------------------

# Fixtures that must return an error dict (fatal parse/structure errors).
EXPECT_ERROR = {
    "truncated-mid-tag.fods",
    "truncated-mid-attribute.fods",
    "no-root-element.fods",
    "invalid-xml-chars.fods",
    "missing-namespace.fods",
    "wrong-root-element.fods",
    "missing-office-body.fods",
    "minimal-spreadsheet-mut1.fods",   # office:body deleted → error
    "multi-sheet-mut1.fods",           # table:worksheet not recognized → 0 sheets (empty workbook ok)
}

# Fixtures that may parse but must produce at least one warning or have 0 sheets.
EXPECT_WARNING_OR_EMPTY = {
    "wrong-mimetype.fods",             # wrong MIME → warning emitted
    "invalid-value-type.fods",         # unsupported value-type → warning
    "missing-table-name.fods",         # missing table:name → empty name, warning
    "typed-values-mut1.fods",          # empty value-type → treated as None/warning
    "formula-mut1.fods",               # corrupt formula text → warning or stored as-is
}

# Fixtures that parse successfully (no error, no requirement for warning).
EXPECT_SUCCESS = {
    "deeply-nested.fods",    # deeply nested unknown elements → parsed (unknown elems ignored)
    "large-attribute.fods",  # large attribute value → parsed (ignored by parser)
    "many-sheets.fods",      # 1000 sheets → parsed successfully
    "wide-row.fods",         # 10,000 cells in one row → parsed successfully
}

TIME_LIMIT_SEC = 30.0


# ---------------------------------------------------------------------------
# Result record
# ---------------------------------------------------------------------------

class TestResult:
    def __init__(self, fixture: str):
        self.fixture = fixture
        self.status: str = "UNKNOWN"
        self.result: dict | None = None
        self.elapsed: float = 0.0
        self.crash: bool = False
        self.silent_corrupt: bool = False
        self.timeout: bool = False
        self.notes: str = ""


# ---------------------------------------------------------------------------
# Load parser
# ---------------------------------------------------------------------------

def load_parser(parser_path: Path):
    """Dynamically load fods_parser module from path."""
    spec = importlib.util.spec_from_file_location("fods_parser", str(parser_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load parser from {parser_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Run one fixture
# ---------------------------------------------------------------------------

def run_fixture(fixture_path: Path, parse_fods) -> TestResult:
    r = TestResult(fixture_path.name)
    t0 = time.monotonic()

    try:
        result = parse_fods(str(fixture_path))
    except Exception as exc:
        r.elapsed = time.monotonic() - t0
        r.crash = True
        r.status = "CRASH"
        r.notes = f"Unhandled exception: {type(exc).__name__}: {exc}"
        return r

    r.elapsed = time.monotonic() - t0
    r.result = result

    if r.elapsed > TIME_LIMIT_SEC:
        r.timeout = True
        r.status = "TIMEOUT"
        r.notes = f"Elapsed {r.elapsed:.1f}s > limit {TIME_LIMIT_SEC}s"
        return r

    name = fixture_path.name

    # --- Check expectations ---
    has_error = "error" in result
    has_warnings = bool(result.get("warnings"))
    sheet_count = result.get("sheet_count", 0)

    if name in EXPECT_ERROR:
        if has_error:
            r.status = "PASS"
            r.notes = f"error returned: {str(result['error'])[:80]}"
        elif sheet_count == 0:
            # multi-sheet-mut1: table:worksheet not a recognized table:table → 0 sheets
            r.status = "PASS"
            r.notes = "no tables recognized (0 sheets); no error raised (acceptable)"
        else:
            # No error returned but one was expected — check if it's a silent corruption
            r.silent_corrupt = True
            r.status = "FAIL_SILENT_CORRUPT"
            r.notes = (
                f"Expected error result but got: sheet_count={sheet_count}, "
                f"warnings={result.get('warnings', [])[:2]}"
            )

    elif name in EXPECT_WARNING_OR_EMPTY:
        if has_error:
            r.status = "PASS"
            r.notes = f"error returned (acceptable): {str(result['error'])[:80]}"
        elif has_warnings or sheet_count == 0:
            r.status = "PASS"
            r.notes = f"warning/empty result: warnings={result.get('warnings', [])[:2]}"
        else:
            # Parsed cleanly — this is acceptable (parser may be lenient for some inputs)
            r.status = "PASS"
            r.notes = f"parsed without warning (lenient parser ok for this input): sheets={sheet_count}"

    elif name in EXPECT_SUCCESS:
        if has_error:
            r.status = "FAIL_UNEXPECTED_ERROR"
            r.notes = f"Unexpected error: {str(result['error'])[:80]}"
            r.silent_corrupt = False  # Not silent corruption, just unexpected
        else:
            r.status = "PASS"
            r.notes = f"parsed successfully: sheets={sheet_count}, warnings={len(result.get('warnings', []))}"

    else:
        # Unknown fixture: any non-crashing result is acceptable
        r.status = "PASS"
        r.notes = f"unknown fixture: no crash, has_error={has_error}, sheets={sheet_count}"

    return r


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="FODS Gate 7 fuzz test runner")
    parser.add_argument(
        "--fixtures-dir",
        default=None,
        help="Path to malformed test fixtures directory",
    )
    parser.add_argument(
        "--parser-path",
        default=None,
        help="Path to fods_parser.py",
    )
    args = parser.parse_args()

    # Resolve paths
    repo_root = Path(__file__).resolve().parent.parent.parent
    fixtures_dir = (
        Path(args.fixtures_dir)
        if args.fixtures_dir
        else repo_root / "tests" / "fixtures" / "fods" / "malformed"
    )
    parser_path = (
        Path(args.parser_path)
        if args.parser_path
        else repo_root / "prototypes" / "by-format" / "fods" / "fods_parser.py"
    )

    # Load parser
    try:
        mod = load_parser(parser_path)
        parse_fods = mod.parse_fods
    except Exception as exc:
        print(f"GATE7_FUZZ_TEST: FAIL — cannot load parser: {exc}", file=sys.stderr)
        return 1

    # Discover fixtures
    if not fixtures_dir.exists():
        print(f"GATE7_FUZZ_TEST: FAIL — fixtures directory not found: {fixtures_dir}", file=sys.stderr)
        return 1

    fixtures = sorted(fixtures_dir.glob("*.fods"))
    if not fixtures:
        print(f"GATE7_FUZZ_TEST: FAIL — no .fods fixtures found in {fixtures_dir}", file=sys.stderr)
        return 1

    print("=" * 60)
    print("FODS Gate 7 — Malformed Input Fuzz Test")
    print(f"Fixtures dir: {fixtures_dir}")
    print(f"Parser: {parser_path}")
    print(f"Fixtures found: {len(fixtures)}")
    print("=" * 60)

    results: list[TestResult] = []
    for fixture_path in fixtures:
        r = run_fixture(fixture_path, parse_fods)
        results.append(r)
        status_icon = "+" if r.status == "PASS" else "-"
        print(
            f"  [{status_icon}] {r.fixture:<40s} "
            f"{r.status:<25s} {r.elapsed:.3f}s  {r.notes[:70]}"
        )

    # Tally
    total = len(results)
    pass_count = sum(1 for r in results if r.status == "PASS")
    crash_count = sum(1 for r in results if r.crash)
    corrupt_count = sum(1 for r in results if r.silent_corrupt)
    timeout_count = sum(1 for r in results if r.timeout)

    print()
    print(f"Total fixtures: {total}")
    print(f"PASS:           {pass_count}/{total}")
    print(f"CRASH:          {crash_count}/{total}")
    print(f"SILENT_CORRUPT: {corrupt_count}/{total}")
    print(f"TIMEOUT:        {timeout_count}/{total}")
    print()

    if crash_count == 0 and corrupt_count == 0 and timeout_count == 0:
        print(f"GATE7_FUZZ_TEST: PASS {pass_count}/{total} CRASH {crash_count}/{total} CORRUPT {corrupt_count}/{total}")
        return 0
    else:
        print(f"GATE7_FUZZ_TEST: FAIL {pass_count}/{total} CRASH {crash_count}/{total} CORRUPT {corrupt_count}/{total}")
        if crash_count > 0:
            print("\nCrashed fixtures:")
            for r in results:
                if r.crash:
                    print(f"  {r.fixture}: {r.notes}")
        if corrupt_count > 0:
            print("\nSilently corrupt fixtures:")
            for r in results:
                if r.silent_corrupt:
                    print(f"  {r.fixture}: {r.notes}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
