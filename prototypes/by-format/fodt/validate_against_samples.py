#!/usr/bin/env python3
"""
validate_against_samples.py — Validate FODT parser prototype against Gate 3 samples.

Gate 4 validation for format-factory FODT acquisition.

Runs 4 test cases (PT-001 through PT-004) against the 4 FODT samples from
samples/by-format/fodt/ and verifies the expected output from parser-test-plan.md.

Expected output:
    PT-001: minimal-document.fodt — PASS
    PT-002: headings-and-paragraphs.fodt — PASS
    PT-003: list-basic.fodt — PASS
    PT-004: table-basic.fodt — PASS

    Results: 4/4 PASS
    FODT_PROTOTYPE_VALIDATION: PASS

Exit code:
    0 on PASS, 1 on FAIL

License: Apache-2.0 (project-owned, format-factory)
Created: 2026-05-08 (run045)
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Load parser
# ---------------------------------------------------------------------------

def load_parser():
    """Load fodt_parser from the same directory as this script."""
    parser_path = Path(__file__).parent / "fodt_parser.py"
    spec = importlib.util.spec_from_file_location("fodt_parser", str(parser_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load fodt_parser from {parser_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.parse_fodt


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

def check(label: str, condition: bool, detail: str = "") -> bool:
    if condition:
        return True
    else:
        msg = f"  FAIL: {label}"
        if detail:
            msg += f" — {detail}"
        print(msg)
        return False


def run_test(name: str, filepath: Path, test_fn) -> bool:
    """Run a single test case. Returns True on PASS, False on FAIL."""
    if not filepath.exists():
        print(f"  FAIL: File not found: {filepath}")
        return False
    result = None
    try:
        parse_fodt = test_fn["parse_fodt"]
        result = parse_fodt(str(filepath))
    except Exception as e:
        print(f"  FAIL: Unhandled exception: {type(e).__name__}: {e}")
        return False

    failures = []

    def assert_check(label: str, condition: bool, detail: str = "") -> None:
        if not condition:
            msg = label
            if detail:
                msg += f" — {detail}"
            failures.append(msg)

    test_fn["assertions"](result, assert_check)

    if failures:
        for f in failures:
            print(f"  FAIL: {f}")
        return False
    return True


# ---------------------------------------------------------------------------
# PT-001: minimal-document.fodt
# ---------------------------------------------------------------------------

def test_pt001(result: dict, assert_check) -> None:
    """PT-001: minimal-document.fodt — FR-001, FR-002."""
    assert_check(
        "result must not have 'error' key (fatal error)",
        "error" not in result,
        str(result.get("error", "")),
    )
    assert_check(
        "result['mime_type'] == 'application/vnd.oasis.opendocument.text-flat-xml'",
        result.get("mime_type") == "application/vnd.oasis.opendocument.text-flat-xml",
        f"got: {result.get('mime_type')!r}",
    )
    assert_check(
        "result['version'] == '1.3'",
        result.get("version") == "1.3",
        f"got: {result.get('version')!r}",
    )
    assert_check(
        "len(result['paragraphs']) >= 1",
        len(result.get("paragraphs", [])) >= 1,
        f"got: {len(result.get('paragraphs', []))}",
    )
    paras = result.get("paragraphs", [])
    if paras:
        assert_check(
            "result['paragraphs'][0]['element'] == 'paragraph'",
            paras[0].get("element") == "paragraph",
            f"got: {paras[0].get('element')!r}",
        )
        assert_check(
            "result['paragraphs'][0]['text'] is non-empty string",
            isinstance(paras[0].get("text"), str) and len(paras[0].get("text", "")) > 0,
            f"got: {paras[0].get('text')!r}",
        )
    assert_check(
        "result['errors'] == []",
        result.get("errors", []) == [],
        f"got: {result.get('errors')}",
    )


# ---------------------------------------------------------------------------
# PT-002: headings-and-paragraphs.fodt
# ---------------------------------------------------------------------------

def test_pt002(result: dict, assert_check) -> None:
    """PT-002: headings-and-paragraphs.fodt — FR-001, FR-002, FR-003."""
    assert_check(
        "result must not have 'error' key (fatal error)",
        "error" not in result,
        str(result.get("error", "")),
    )
    assert_check(
        "result['mime_type'] == 'application/vnd.oasis.opendocument.text-flat-xml'",
        result.get("mime_type") == "application/vnd.oasis.opendocument.text-flat-xml",
        f"got: {result.get('mime_type')!r}",
    )
    assert_check(
        "result['errors'] == []",
        result.get("errors", []) == [],
        f"got: {result.get('errors')}",
    )
    paras = result.get("paragraphs", [])
    headings_1 = [p for p in paras if p.get("element") == "heading" and p.get("outline_level") == 1]
    headings_2 = [p for p in paras if p.get("element") == "heading" and p.get("outline_level") == 2]
    paragraphs_only = [p for p in paras if p.get("element") == "paragraph"]
    assert_check(
        "at least 1 element with element='heading' and outline_level=1",
        len(headings_1) >= 1,
        f"found {len(headings_1)} level-1 headings",
    )
    assert_check(
        "at least 1 element with element='heading' and outline_level=2",
        len(headings_2) >= 1,
        f"found {len(headings_2)} level-2 headings",
    )
    assert_check(
        "at least 1 element with element='paragraph'",
        len(paragraphs_only) >= 1,
        f"found {len(paragraphs_only)} paragraphs",
    )
    # All heading text fields must be non-empty strings
    bad_headings = [p for p in paras if p.get("element") == "heading" and not p.get("text")]
    assert_check(
        "all heading 'text' fields are non-empty strings",
        len(bad_headings) == 0,
        f"{len(bad_headings)} headings have empty text",
    )


# ---------------------------------------------------------------------------
# PT-003: list-basic.fodt
# ---------------------------------------------------------------------------

def test_pt003(result: dict, assert_check) -> None:
    """PT-003: list-basic.fodt — FR-001, FR-004."""
    assert_check(
        "result must not have 'error' key (fatal error)",
        "error" not in result,
        str(result.get("error", "")),
    )
    assert_check(
        "result['errors'] == []",
        result.get("errors", []) == [],
        f"got: {result.get('errors')}",
    )
    lists = result.get("lists", [])
    assert_check(
        "len(result['lists']) >= 2 (at least 1 bullet + 1 numbered list)",
        len(lists) >= 2,
        f"found {len(lists)} lists",
    )
    bullet_lists   = [lst for lst in lists if lst.get("list_style") == "bullet"]
    numbered_lists = [lst for lst in lists if lst.get("list_style") == "numbered"]
    assert_check(
        "at least one list with list_style='bullet'",
        len(bullet_lists) >= 1,
        f"found {len(bullet_lists)} bullet lists",
    )
    assert_check(
        "at least one list with list_style='numbered'",
        len(numbered_lists) >= 1,
        f"found {len(numbered_lists)} numbered lists",
    )
    for i, lst in enumerate(lists):
        items = lst.get("items", [])
        assert_check(
            f"list[{i}] has at least 1 item",
            len(items) >= 1,
            f"found {len(items)} items",
        )
        for j, item in enumerate(items):
            assert_check(
                f"list[{i}].items[{j}] has non-empty 'text'",
                isinstance(item.get("text"), str) and len(item.get("text", "")) > 0,
                f"got: {item.get('text')!r}",
            )
            assert_check(
                f"list[{i}].items[{j}] has 'level' >= 1",
                isinstance(item.get("level"), int) and item.get("level", 0) >= 1,
                f"got level: {item.get('level')}",
            )


# ---------------------------------------------------------------------------
# PT-004: table-basic.fodt
# ---------------------------------------------------------------------------

def test_pt004(result: dict, assert_check) -> None:
    """PT-004: table-basic.fodt — FR-001, FR-005."""
    assert_check(
        "result must not have 'error' key (fatal error)",
        "error" not in result,
        str(result.get("error", "")),
    )
    assert_check(
        "result['errors'] == []",
        result.get("errors", []) == [],
        f"got: {result.get('errors')}",
    )
    tables = result.get("tables", [])
    assert_check(
        "len(result['tables']) >= 1",
        len(tables) >= 1,
        f"found {len(tables)} tables",
    )
    if tables:
        rows = tables[0].get("rows", [])
        assert_check(
            "result['tables'][0]['rows'] has at least 2 rows",
            len(rows) >= 2,
            f"found {len(rows)} rows",
        )
        for i, row in enumerate(rows):
            assert_check(
                f"table row[{i}] has at least 1 cell",
                len(row) >= 1,
                f"found {len(row)} cells",
            )
            for j, cell in enumerate(row):
                assert_check(
                    f"table row[{i}] cell[{j}] value is a string",
                    isinstance(cell, str),
                    f"got type: {type(cell).__name__}",
                )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    samples_dir = repo_root / "samples" / "by-format" / "fodt"

    print("=" * 60)
    print("FODT Gate 4 Parser Prototype Validation")
    print(f"Samples dir: {samples_dir}")
    print("=" * 60)

    try:
        parse_fodt = load_parser()
    except Exception as e:
        print(f"FAIL: Cannot load fodt_parser: {e}", file=sys.stderr)
        return 1

    tests = [
        ("PT-001", "minimal-document.fodt",         test_pt001),
        ("PT-002", "headings-and-paragraphs.fodt",  test_pt002),
        ("PT-003", "list-basic.fodt",                test_pt003),
        ("PT-004", "table-basic.fodt",               test_pt004),
    ]

    pass_count = 0
    fail_count = 0

    for pt_id, filename, assertions_fn in tests:
        filepath = samples_dir / filename
        ctx = {"parse_fodt": parse_fodt, "assertions": assertions_fn}
        passed = run_test(pt_id, filepath, ctx)
        status = "PASS" if passed else "FAIL"
        print(f"{pt_id}: {filename} — {status}")
        if passed:
            pass_count += 1
        else:
            fail_count += 1

    print()
    print(f"Results: {pass_count}/{len(tests)} PASS")

    if pass_count == len(tests):
        print("FODT_PROTOTYPE_VALIDATION: PASS")
        return 0
    else:
        print(f"FODT_PROTOTYPE_VALIDATION: FAIL ({fail_count} test(s) failed)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
