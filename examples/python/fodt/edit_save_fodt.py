"""
edit_save_fodt.py — Example: load, edit, and save a FODT document.

This example demonstrates the R76 edit-and-save workflow for FODT:

1. Parse an existing FODT file into the neutral model
2. Use document_set_block_text() to modify a paragraph
3. Check document_warnings_for_unsupported_edit() for safety disclosures
4. Write the modified document back to a new FODT file

Requirements:
    pip install format-factory-fodt

Usage:
    python examples/python/fodt/edit_save_fodt.py

License: Apache-2.0 — Format Factory Python FOSS track
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.python.fodt import (
    parse_fodt,
    write_fodt,
    document_set_block_text,
    document_warnings_for_unsupported_edit,
    document_stats,
)

SAMPLE_FODT = REPO_ROOT / "samples" / "by-format" / "fodt" / "minimal-document.fodt"


def main() -> None:
    print("=== FODT Edit-and-Save Example ===\n")

    # Step 1: Parse
    print(f"Loading: {SAMPLE_FODT.name}")
    doc = parse_fodt(SAMPLE_FODT)
    stats = document_stats(doc)
    print(f"Paragraphs: {stats.get('paragraph_count', 0)}")
    print(f"Headings: {stats.get('heading_count', 0)}")
    print(f"Total words: {stats.get('total_words', 0)}")

    if not doc.get("blocks"):
        print("No blocks found in document")
        return

    # Step 2: Check for edit warnings
    warnings = document_warnings_for_unsupported_edit(doc, 0)
    if warnings:
        print("\nEdit warnings:")
        for w in warnings:
            print(f"  WARNING: {w}")
    else:
        print("\nNo edit warnings for block 0")

    # Step 3: Edit
    print(f"\nBefore edit: {doc['blocks'][0]['text']!r}")
    ok, msg = document_set_block_text(doc, 0, "Edited by Format Factory FODT")
    if not ok:
        print(f"Edit failed: {msg}")
        sys.exit(1)
    print(f"After edit: {doc['blocks'][0]['text']!r}")
    print(f"Edit result: {msg}")

    # Step 4: Save
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False) as tf:
        out_path = Path(tf.name)

    write_fodt(doc, out_path)
    print(f"\nSaved to: {out_path}")

    # Step 5: Verify round-trip
    doc2 = parse_fodt(out_path)
    val = doc2["blocks"][0]["text"]
    assert val == "Edited by Format Factory FODT", f"Round-trip mismatch: {val!r}"
    print("Round-trip verification: PASS")

    print("\n=== Edit-and-Save Example Complete ===")


if __name__ == "__main__":
    main()
