"""
FODT Python FOSS — Edit, Save Example (Installed Wheel Version)
Format Factory R83 — installed-package workflow proof

Run ONLY from installed FODT wheel. No PYTHONPATH to source repo required.

Usage:
    pip install fodt-0.1.0.dev0-py3-none-any.whl
    python edit_save_fodt_installed.py
"""
from __future__ import annotations


def _get_sample_fodt_bytes() -> bytes:
    """Return a minimal self-contained FODT file for demo."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
                 office:mimetype="application/vnd.oasis.opendocument.text">
  <office:body>
    <office:text>
      <text:h text:outline-level="1">Introduction</text:h>
      <text:p>This is the first paragraph of the document.</text:p>
      <text:p>This is the second paragraph.</text:p>
      <text:h text:outline-level="2">Section A</text:h>
      <text:p>Content under Section A.</text:p>
    </office:text>
  </office:body>
</office:document>"""
    return xml.encode("utf-8")


def main() -> None:
    import fodt

    print(f"fodt version: {fodt.__version__}")
    print(f"fodt track: {fodt.__track__}")
    print()

    data = _get_sample_fodt_bytes()

    # Step 1: Parse
    doc = fodt.parse_fodt(data)
    print("Step 1: parse_fodt -> OK")

    # Step 2: Headings
    headings = fodt.document_headings(doc)
    print(f"Step 2: document_headings -> {headings}")

    # Step 3: Paragraph count (GAP-FODT-STRUCT-001 repaired)
    count = fodt.document_paragraph_count(doc)
    print(f"Step 3: document_paragraph_count -> {count}")

    # Step 4: Body text
    body = fodt.document_body_text(doc)
    print(f"Step 4: document_body_text -> {len(body)} chars")

    # Step 5: Stats
    stats = fodt.document_stats(doc)
    print(f"Step 5: document_stats -> {stats}")

    # Step 6: Append paragraph
    doc2 = fodt.document_append_paragraph(doc, "R83 appended paragraph.")
    new_count = fodt.document_paragraph_count(doc2)
    print(f"Step 6: document_append_paragraph -> count now {new_count}")

    # Step 7: Remove paragraph (remove the last one we added)
    doc3 = fodt.document_remove_paragraph(doc2, new_count - 1)
    final_count = fodt.document_paragraph_count(doc3)
    print(f"Step 7: document_remove_paragraph -> count now {final_count}")

    # Step 8: Write FODT
    out_bytes = fodt.write_fodt(doc3)
    print(f"Step 8: write_fodt -> {len(out_bytes)} bytes")

    # Step 9: Round-trip verify
    doc4 = fodt.parse_fodt(out_bytes)
    rt_count = fodt.document_paragraph_count(doc4)
    assert rt_count == count, f"Round-trip count mismatch: {rt_count} != {count}"
    print(f"Step 9: Round-trip paragraph count preserved: {rt_count} == {count}")

    print("\nAll 9 product workflow steps: PASS")
    print("FODT_INSTALLED_REAL_SAMPLE_WORKFLOW: PASS")


if __name__ == "__main__":
    main()
