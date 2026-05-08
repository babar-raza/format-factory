#!/usr/bin/env python3
"""
Validator for FODT Neutral Model v1.
Gate 5 artifact — validates fodt_parser.py output against the neutral model.
Created: run046 (2026-05-08)

Usage:
    python tools/model/validate_fodt_neutral_model.py [samples_dir]

If samples_dir is not given, defaults to samples/by-format/fodt/.
Exit code 0 on PASS, 1 on FAIL.
"""
import sys
import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
PARSER_DIR = REPO_ROOT / "prototypes" / "by-format" / "fodt"
DEFAULT_SAMPLES = REPO_ROOT / "samples" / "by-format" / "fodt"

if str(PARSER_DIR) not in sys.path:
    sys.path.insert(0, str(PARSER_DIR))

import fodt_parser

FODT_MIME = "application/vnd.oasis.opendocument.text-flat-xml"

SAMPLES = [
    "minimal-document.fodt",
    "headings-and-paragraphs.fodt",
    "list-basic.fodt",
    "table-basic.fodt",
]


def validate_sample(name, path):
    checks = []
    errors = []

    def ck(label, cond):
        if cond:
            checks.append(f"    PASS: {label}")
        else:
            checks.append(f"    FAIL: {label}")
            errors.append(label)

    result = fodt_parser.parse_fodt(str(path))

    # VR-F001: parse succeeds
    ck("VR-F001: parse_fodt returns dict", isinstance(result, dict))
    ck("VR-F001b: no fatal error key", "error" not in result)
    if "error" in result:
        return False, checks, errors

    # VR-F002: required top-level keys present
    required = {"mime_type", "version", "paragraphs", "lists", "tables", "word_count", "errors"}
    ck("VR-F002: required keys present", required.issubset(set(result.keys())))

    # VR-F003: mime_type
    ck("VR-F003: mime_type is string", isinstance(result.get("mime_type"), str))
    ck("VR-F004: mime_type == FODT MIME type", result.get("mime_type") == FODT_MIME)

    # VR-F005: version
    ver = result.get("version")
    ck("VR-F005: version is non-empty string", isinstance(ver, str) and len(ver) > 0)

    # VR-F006: word_count
    wc = result.get("word_count")
    ck("VR-F006: word_count is int >= 0", isinstance(wc, int) and wc >= 0)

    # Container checks
    paras = result.get("paragraphs", [])
    lists = result.get("lists", [])
    tables = result.get("tables", [])
    errs = result.get("errors", [])

    ck("VR-F007: paragraphs is list", isinstance(paras, list))
    ck("VR-F008: lists is list", isinstance(lists, list))
    ck("VR-F009: tables is list", isinstance(tables, list))
    ck("VR-F010: errors is empty list", errs == [])

    # Block validation
    for i, block in enumerate(paras):
        elem = block.get("element")
        ck(f"VR-F009b: block[{i}] has element field", "element" in block)
        ck(f"VR-F009c: block[{i}] element is paragraph or heading",
           elem in ("paragraph", "heading"))
        if elem == "heading":
            ol = block.get("outline_level")
            ck(f"VR-F011: heading[{i}] outline_level is int", isinstance(ol, int))
            ck(f"VR-F011b: heading[{i}] outline_level 1-10",
               isinstance(ol, int) and 1 <= ol <= 10)
        if elem == "paragraph":
            ol = block.get("outline_level")
            ck(f"VR-F012: paragraph[{i}] outline_level is null", ol is None)

    # List validation
    for i, lst in enumerate(lists):
        ls = lst.get("list_style")
        items = lst.get("items", [])
        ck(f"VR-F013: list[{i}] list_style is valid", ls in ("bullet", "numbered", None))
        ck(f"VR-F014: list[{i}] items is list", isinstance(items, list))
        for j, item in enumerate(items):
            ck(f"VR-F015: list[{i}].item[{j}] text is string",
               isinstance(item.get("text"), str))
            lvl = item.get("level")
            ck(f"VR-F016: list[{i}].item[{j}] level >= 1",
               isinstance(lvl, int) and lvl >= 1)

    # Table validation
    for i, tbl in enumerate(tables):
        rows = tbl.get("rows", [])
        ck(f"VR-F017: table[{i}] rows is list", isinstance(rows, list))
        for j, row in enumerate(rows):
            ck(f"VR-F017b: table[{i}].row[{j}] is list", isinstance(row, list))
            for k, cell in enumerate(row):
                ck(f"VR-F019: table[{i}].row[{j}].cell[{k}] is string",
                   isinstance(cell, str))

    return len(errors) == 0, checks, errors


def main():
    samples_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SAMPLES

    print("=" * 60)
    print("FODT Neutral Model v1 Validator")
    print(f"Samples: {samples_dir}")
    print("=" * 60)

    total_checks = 0
    total_errors = 0
    passed = 0
    failed = 0

    for i, name in enumerate(SAMPLES, 1):
        sample_path = samples_dir / name
        print(f"\nPT-{i:03d}: {name}")

        if not sample_path.exists():
            print(f"  ERROR: Sample not found: {sample_path}")
            failed += 1
            continue

        ok, checks, errs = validate_sample(name, sample_path)
        for line in checks:
            print(line)
        total_checks += len(checks)
        total_errors += len(errs)

        if ok:
            print(f"  RESULT: PASS ({len(checks)} checks, 0 errors)")
            passed += 1
        else:
            print(f"  RESULT: FAIL ({len(checks)} checks, {len(errs)} errors)")
            for e in errs:
                print(f"    ERROR: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Total checks: {total_checks}")
    print(f"Errors: {total_errors}")
    print(f"Samples: {passed}/{len(SAMPLES)} PASS")
    if failed == 0:
        print(f"FODT_NEUTRAL_MODEL_VALIDATION: PASS {passed}/{len(SAMPLES)}")
        sys.exit(0)
    else:
        print(f"FODT_NEUTRAL_MODEL_VALIDATION: FAIL {passed}/{len(SAMPLES)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
