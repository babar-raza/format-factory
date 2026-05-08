#!/usr/bin/env python3
"""
validate_fodt_samples.py — Validate FODT Gate 3 sample corpus.

Checks each synthetic FODT sample file for:
1. XML well-formedness (no parse errors)
2. Root element is office:document
3. Correct MIME type: application/vnd.oasis.opendocument.text-flat-xml
4. ODF version 1.3
5. office:body element present
6. office:text element present (text document body)

Usage:
    python tools/samples/validate_fodt_samples.py

Exit code:
    0 = all samples PASS
    1 = one or more samples FAIL

License: Apache-2.0 (project-owned, format-factory)
Created: 2026-05-08 (run043)
"""

from __future__ import annotations

import hashlib
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

FODT_SAMPLES_DIR = Path("samples/by-format/fodt")

EXPECTED_MIME = "application/vnd.oasis.opendocument.text-flat-xml"
EXPECTED_VERSION = "1.3"

NS_OFFICE = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
NS_TEXT = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
NS_TABLE = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"

EXPECTED_SAMPLES = [
    "minimal-document.fodt",
    "headings-and-paragraphs.fodt",
    "list-basic.fodt",
    "table-basic.fodt",
]

MAX_FILE_BYTES = 10 * 1024 * 1024  # 10 MB guard for samples


def validate_sample(path: Path) -> tuple[bool, list[str]]:
    """
    Validate a single FODT sample. Returns (pass, list_of_issues).
    """
    issues: list[str] = []

    if not path.exists():
        return False, [f"File not found: {path}"]

    size = path.stat().st_size
    if size == 0:
        issues.append("File is empty")
        return False, issues
    if size > MAX_FILE_BYTES:
        issues.append(f"File too large: {size} bytes > {MAX_FILE_BYTES}")
        return False, issues

    # Check XML well-formedness
    try:
        tree = ET.parse(str(path))
    except ET.ParseError as exc:
        return False, [f"XML parse error: {exc}"]

    root = tree.getroot()

    # Check root element
    expected_root = f"{{{NS_OFFICE}}}document"
    if root.tag != expected_root:
        issues.append(f"Root element: expected '{expected_root}', got '{root.tag}'")

    # Check MIME type
    mime = root.get(f"{{{NS_OFFICE}}}mimetype")
    if mime != EXPECTED_MIME:
        issues.append(f"MIME type: expected '{EXPECTED_MIME}', got '{mime}'")

    # Check version
    ver = root.get(f"{{{NS_OFFICE}}}version")
    if ver != EXPECTED_VERSION:
        issues.append(f"Version: expected '{EXPECTED_VERSION}', got '{ver}'")

    # Check office:body
    body = root.find(f"{{{NS_OFFICE}}}body")
    if body is None:
        issues.append("Missing office:body element")
        return False, issues

    # Check office:text
    text_el = body.find(f"{{{NS_OFFICE}}}text")
    if text_el is None:
        issues.append("Missing office:text element inside office:body")

    return len(issues) == 0, issues


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    print("=" * 60)
    print("FODT Sample Validation — Gate 3 Corpus")
    print("=" * 60)

    # Check all expected samples exist
    missing = [s for s in EXPECTED_SAMPLES if not (FODT_SAMPLES_DIR / s).exists()]
    if missing:
        print(f"ERROR: Missing samples: {missing}")
        print(f"Expected samples dir: {FODT_SAMPLES_DIR}")
        return 1

    results = []
    for sample_name in EXPECTED_SAMPLES:
        path = FODT_SAMPLES_DIR / sample_name
        passed, issues = validate_sample(path)
        sha = sha256_of(path)
        size = path.stat().st_size

        if passed:
            print(f"  PASS  {sample_name}  ({size} bytes)")
            print(f"        sha256:{sha}")
        else:
            print(f"  FAIL  {sample_name}")
            for issue in issues:
                print(f"        ERROR: {issue}")

        results.append(passed)

    print()
    pass_count = sum(results)
    total = len(results)
    print(f"Results: {pass_count}/{total} PASS")

    if pass_count == total:
        print("FODT_SAMPLE_VALIDATION: PASS")
        return 0
    else:
        print("FODT_SAMPLE_VALIDATION: FAIL")
        return 1


if __name__ == "__main__":
    sys.exit(main())
