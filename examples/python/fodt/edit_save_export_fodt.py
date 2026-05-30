"""
edit_save_export_fodt.py — Example: load, edit, save, and export a FODT document.

This example demonstrates the complete R78 FODT product workflow:

1. Parse an existing FODT file into the neutral model
2. Inspect the document using analysis APIs
3. Edit paragraphs using document_set_block_text()
4. Append a new paragraph using document_append_paragraph()
5. Write the modified document back to FODT
6. Export plain text using document_text_content()

Requirements:
    pip install format-factory-fodt

Usage:
    python examples/python/fodt/edit_save_export_fodt.py

License: Apache-2.0 — Format Factory Python FOSS track
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.python.fodt import (
    parse_fodt,
    write_fodt,
    document_stats,
    document_text_content,
    document_heading_outline,
    document_word_count,
    document_set_block_text,
    document_warnings_for_unsupported_edit,
    document_append_paragraph,
    document_paragraph_count,
)

SAMPLE_FODT = REPO_ROOT / "samples" / "by-format" / "fodt" / "minimal-document.fodt"


def main() -> None:
    print("=== FODT Edit-Save-Export Example ===\n")

    # Step 1: Parse
    print(f"Loading: {SAMPLE_FODT.name}")
    doc = parse_fodt(SAMPLE_FODT)
    stats = document_stats(doc)
    print(f"Paragraphs: {stats.get('paragraph_count', 0)}")
    print(f"Headings: {stats.get('heading_count', 0)}")
    print(f"Total words: {stats.get('total_words', 0)}")
    print(f"Paragraph count (API): {document_paragraph_count(doc)}")

    # Step 2: Inspect headings
    outline = document_heading_outline(doc)
    if outline:
        print(f"\nHeadings ({len(outline)}):")
        for h in outline[:5]:
            print(f"  Level {h.get('level', '?')}: {h.get('text', '')!r}")
    else:
        print("\nNo headings found")

    # Step 3: Inspect word count
    wc = document_word_count(doc)
    print(f"\nWord count breakdown: {wc}")

    # Step 4: Get blocks
    blocks = doc.get("blocks") or doc.get("body", {}).get("blocks", [])
    if not blocks:
        print("\nNo blocks found in document")
    else:
        print(f"\nTotal blocks: {len(blocks)}")

        # Step 5: Check for edit warnings
        warnings = document_warnings_for_unsupported_edit(doc, 0)
        if warnings:
            print("Edit warnings for block 0:")
            for w in warnings:
                print(f"  WARNING: {w}")
        else:
            print("No edit warnings for block 0")

        # Step 6: Edit block 0
        original_text = blocks[0].get("text") or (blocks[0].get("runs") or [{}])[0].get("text", "(no text)")
        print(f"\nBefore edit: {original_text!r}")
        ok, msg = document_set_block_text(doc, 0, "Edited by Format Factory FODT")
        print(f"Edit result: {msg}")
        new_blocks = doc.get("blocks") or doc.get("body", {}).get("blocks", [])
        new_text = new_blocks[0].get("text") or (new_blocks[0].get("runs") or [{}])[0].get("text", "")
        print(f"After edit: {new_text!r}")

    # Step 7: Append a new paragraph
    ok, msg = document_append_paragraph(doc, "Appended by Format Factory R78 example.")
    if ok:
        print(f"\nAppended paragraph: {msg}")
        print(f"New paragraph count: {document_paragraph_count(doc)}")
    else:
        print(f"\nAppend note: {msg}")

    # Step 8: Save modified document
    with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False) as tf:
        fodt_out = Path(tf.name)

    write_fodt(doc, fodt_out)
    print(f"\nSaved FODT to: {fodt_out}")

    # Step 9: Export plain text
    doc_for_export = parse_fodt(fodt_out)
    plain_text = document_text_content(doc_for_export)
    word_count_chars = len(plain_text)

    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w", encoding="utf-8") as tf:
        tf.write(plain_text)
        txt_out = Path(tf.name)

    print(f"Exported plain text to: {txt_out.name} ({word_count_chars} chars)")

    # Step 10: Verify round-trip
    doc2 = parse_fodt(fodt_out)
    text2 = document_text_content(doc2)
    assert "Appended by Format Factory R78 example." in text2, "Appended text survived round-trip"
    print("\nRound-trip verification: PASS")

    print("\n=== Edit-Save-Export Example Complete ===")


if __name__ == "__main__":
    main()
