"""Dogfood example: Export FODT to TXT, Markdown, and HTML using Format Factory exporters.

Demonstrates the new FODT export capability added in sprint ff-hardening-realignment-20260624.
Uses src/python/fodt/exporters.py: fodt_to_txt, fodt_to_markdown, fodt_to_html.

Runnable: python examples/python/fodt/dogfood_fodt_exporters.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from src.python.fodt.exporters import fodt_to_txt, fodt_to_markdown, fodt_to_html

SAMPLE_FODT = _REPO / "samples" / "by-format" / "fodt" / "headings-and-paragraphs.fodt"
OUTPUT_DIR = _REPO / ".local" / "dogfood-proofs" / "fodt-exporters"


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Source: {SAMPLE_FODT}")

    # Step 1: Export to plain text
    txt = fodt_to_txt(str(SAMPLE_FODT))
    txt_path = OUTPUT_DIR / "output.txt"
    txt_path.write_text(txt, encoding="utf-8")
    print(f"\n[TXT] {txt_path} ({len(txt)} chars)")
    print(txt[:200])

    # Step 2: Export to Markdown
    md = fodt_to_markdown(str(SAMPLE_FODT))
    md_path = OUTPUT_DIR / "output.md"
    md_path.write_text(md, encoding="utf-8")
    print(f"\n[MD] {md_path} ({len(md)} chars)")
    print(md[:200])

    # Step 3: Export to HTML
    html = fodt_to_html(str(SAMPLE_FODT))
    html_path = OUTPUT_DIR / "output.html"
    html_path.write_text(html, encoding="utf-8")
    print(f"\n[HTML] {html_path} ({len(html)} chars)")
    print(html[:200])

    # Verify outputs are non-empty and contain content
    errors = []
    if not txt.strip():
        errors.append("TXT output is empty")
    if not md.strip():
        errors.append("Markdown output is empty")
    if not any(tag in html for tag in ("<h1>", "<h2>", "<h3>", "<p>", "<ul>")):
        errors.append(f"HTML output missing HTML tags: {html[:100]}")

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 1

    print("\nDOGFOOD PASS: fodt_to_txt, fodt_to_markdown, fodt_to_html all produce non-empty output")
    return 0


if __name__ == "__main__":
    sys.exit(main())
