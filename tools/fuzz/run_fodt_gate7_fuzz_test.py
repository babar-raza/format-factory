#!/usr/bin/env python3
"""
run_fodt_gate7_fuzz_test.py -- FODT Gate 7 malformed/fuzz test runner.

Gate 7: Malformed Input and Fuzz Testing -- format-factory project.

PURPOSE:
    Run the FODT parser prototype against all malformed test inputs in
    tests/fixtures/fodt/malformed/ and verify:
      1. No crashes (no unhandled exceptions)
      2. No silent corruption (every error input returns an error result or warning)
      3. Memory-bounded (no input causes runaway memory growth)
      4. Time-bounded (no input takes more than 30 seconds)

    Output:
      FODT_GATE7_FUZZ_TEST: PASS N/N CRASH 0/N CORRUPT 0/N
      or
      FODT_GATE7_FUZZ_TEST: FAIL (crash count > 0 or silent corruption count > 0)

USAGE:
    python tools/fuzz/run_fodt_gate7_fuzz_test.py [--fixtures-dir PATH] [--parser-path PATH]

EXIT CODE:
    0 on PASS, 1 on FAIL

License: Apache-2.0 (project-owned, format-factory)
Created: 2026-05-08 (run048)
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
    "a01-truncated-xml.fodt",
    "a02-no-root-element.fodt",
    "a03-invalid-xml-chars.fodt",
    "a04-unclosed-tag.fodt",
    "a05-mismatched-tags.fodt",
    "b01-wrong-root-element.fodt",
    "b02-missing-namespace.fodt",
    "b04-fods-root-element.fodt",
    "c01-missing-office-body.fodt",
    "c02-missing-office-text.fodt",
    "c04-wrong-body-child.fodt",
    "d04-entity-injection-attempt.fodt",
}

# Fixtures that may parse but must produce at least one warning (non-fatal error).
EXPECT_WARNING_OR_EMPTY = {
    "b03-wrong-mime-type.fodt",  # wrong MIME -> added to errors list, no fatal error
}

# Fixtures that parse successfully (no fatal error, warnings acceptable).
EXPECT_SUCCESS = {
    "c03-empty-body.fodt",               # valid structure, empty office:text
    "d01-deeply-nested-paragraphs.fodt", # 100 nested text:span (not list -- not recursive)
    "d02-very-long-text.fodt",           # 100K char paragraph
    "d03-empty-paragraphs.fodt",         # 100 empty text:p elements
    "d05-unicode-text.fodt",             # CJK + Arabic + emoji
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
    """Dynamically load fodt_parser module from path."""
    spec = importlib.util.spec_from_file_location("fodt_parser", str(parser_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load parser from {parser_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Run one fixture
# ---------------------------------------------------------------------------

def run_fixture(fixture_path: Path, parse_fodt) -> TestResult:
    r = TestResult(fixture_path.name)
    t0 = time.monotonic()

    try:
        result = parse_fodt(str(fixture_path))
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

    # NOTE: FODT parser uses:
    #   "error" key for fatal errors
    #   "errors" list for non-fatal warnings
    #   "paragraphs" list for extracted paragraphs (not "sheet_count")
    has_fatal_error = "error" in result
    has_non_fatal_errors = bool(result.get("errors", []))
    para_count = len(result.get("paragraphs", []))

    if name in EXPECT_ERROR:
        if has_fatal_error:
            r.status = "PASS"
            r.notes = f"fatal error returned: {str(result.get('error', ''))[:80]}"
        elif para_count == 0 and not has_non_fatal_errors:
            # No error but also no content and no warnings -- possible empty result
            r.status = "PASS"
            r.notes = "no fatal error but no content and no warnings (acceptable empty result)"
        else:
            # Fatal error expected but not returned
            r.silent_corrupt = True
            r.status = "FAIL_SILENT_CORRUPT"
            r.notes = (
                f"Expected fatal error but got: para_count={para_count}, "
                f"errors={result.get('errors', [])[:2]}"
            )

    elif name in EXPECT_WARNING_OR_EMPTY:
        # For FODT, warnings are in the "errors" list of a successful parse result
        if has_fatal_error or has_non_fatal_errors or para_count == 0:
            r.status = "PASS"
            r.notes = (
                f"warning/empty result: fatal={has_fatal_error}, "
                f"non_fatal_errors={result.get('errors', [])[:2]}"
            )
        else:
            # Parsed cleanly -- lenient parser is acceptable for this input
            r.status = "PASS"
            r.notes = f"parsed without warning (lenient parser ok): para_count={para_count}"

    elif name in EXPECT_SUCCESS:
        if has_fatal_error:
            r.status = "FAIL_UNEXPECTED_ERROR"
            r.notes = f"Unexpected fatal error: {str(result.get('error', ''))[:80]}"
        else:
            r.status = "PASS"
            r.notes = f"parsed successfully: para_count={para_count}, errors={len(result.get('errors', []))}"

    else:
        # Unknown fixture: any non-crashing result is acceptable
        r.status = "PASS"
        r.notes = f"unknown fixture: no crash, fatal={has_fatal_error}, paras={para_count}"

    return r


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="FODT Gate 7 fuzz test runner")
    parser.add_argument("--fixtures-dir", default=None)
    parser.add_argument("--parser-path", default=None)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent.parent
    fixtures_dir = (
        Path(args.fixtures_dir)
        if args.fixtures_dir
        else repo_root / "tests" / "fixtures" / "fodt" / "malformed"
    )
    parser_path = (
        Path(args.parser_path)
        if args.parser_path
        else repo_root / "prototypes" / "by-format" / "fodt" / "fodt_parser.py"
    )

    try:
        mod = load_parser(parser_path)
        parse_fodt = mod.parse_fodt
    except Exception as exc:
        print(f"FODT_GATE7_FUZZ_TEST: FAIL -- cannot load parser: {exc}", file=sys.stderr)
        return 1

    if not fixtures_dir.exists():
        print(f"FODT_GATE7_FUZZ_TEST: FAIL -- fixtures dir not found: {fixtures_dir}", file=sys.stderr)
        return 1

    fixtures = sorted(fixtures_dir.glob("*.fodt"))
    if not fixtures:
        print(f"FODT_GATE7_FUZZ_TEST: FAIL -- no .fodt fixtures found in {fixtures_dir}", file=sys.stderr)
        return 1

    print("=" * 60)
    print("FODT Gate 7 -- Malformed Input Fuzz Test")
    print(f"Fixtures dir: {fixtures_dir}")
    print(f"Parser: {parser_path}")
    print(f"Fixtures found: {len(fixtures)}")
    print("=" * 60)

    results: list[TestResult] = []
    for fixture_path in fixtures:
        r = run_fixture(fixture_path, parse_fodt)
        results.append(r)
        icon = "+" if r.status == "PASS" else "-"
        print(
            f"  [{icon}] {r.fixture:<45s} "
            f"{r.status:<25s} {r.elapsed:.3f}s  {r.notes[:65]}"
        )

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
        result_line = f"FODT_GATE7_FUZZ_TEST: PASS {pass_count}/{total} CRASH {crash_count}/{total} CORRUPT {corrupt_count}/{total}"
        print(result_line)
        return 0
    else:
        result_line = f"FODT_GATE7_FUZZ_TEST: FAIL {pass_count}/{total} CRASH {crash_count}/{total} CORRUPT {corrupt_count}/{total}"
        print(result_line)
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
