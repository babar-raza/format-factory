"""FODT consumer roundtrip — TC-D-003 (ALLFORMAT-DEEPENING-20260625).

load → inspect blocks → export to txt/markdown/html → verify non-empty.

Usage:
    python examples/python/fodt/consumer_roundtrip.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]

try:
    from fodt import parse_fodt_strict, document_text_content
    from fodt.exporters import fodt_to_txt, fodt_to_markdown, fodt_to_html
except ImportError:
    sys.path.insert(0, str(_REPO / "src" / "python"))
    from fodt import parse_fodt_strict, document_text_content  # type: ignore
    from fodt.exporters import fodt_to_txt, fodt_to_markdown, fodt_to_html  # type: ignore

SAMPLE = _REPO / "samples" / "by-format" / "fodt" / "headings-and-paragraphs.fodt"
MINIMAL = _REPO / "samples" / "by-format" / "fodt" / "minimal-document.fodt"


def _find_sample() -> Path:
    """Return an existing sample FODT file."""
    for p in (SAMPLE, MINIMAL):
        if p.exists():
            return p
    raise FileNotFoundError(f"No FODT sample found in {SAMPLE.parent}")


def main() -> int:
    print("=== FODT Consumer Roundtrip Proof ===")
    sample = _find_sample()

    # Step 1: Load and inspect
    doc = parse_fodt_strict(str(sample))
    assert isinstance(doc, dict), "parse_fodt_strict() must return dict"
    blocks = doc.get("blocks", [])
    print(f"[LOAD] {sample.name}: {len(blocks)} block(s)")
    for i, block in enumerate(blocks[:3]):
        print(f"  block[{i}]: type={block.get('type')!r} text={block.get('text','')[:50]!r}")

    # Step 2: Full text content
    full_text = document_text_content(doc)
    assert isinstance(full_text, str), "document_text_content() must return str"
    print(f"[TEXT] {len(full_text)} chars")

    # Step 3: Export to TXT
    txt = fodt_to_txt(str(sample))
    assert isinstance(txt, str) and len(txt.strip()) > 0, "fodt_to_txt() must return non-empty string"
    print(f"[EXPORT-TXT] {len(txt)} chars")

    # Step 4: Export to Markdown
    md = fodt_to_markdown(str(sample))
    assert isinstance(md, str) and len(md.strip()) > 0, "fodt_to_markdown() must return non-empty string"
    print(f"[EXPORT-MD] {len(md)} chars")

    # Step 5: Export to HTML
    html = fodt_to_html(str(sample))
    assert isinstance(html, str) and len(html.strip()) > 0, "fodt_to_html() must return non-empty string"
    has_tags = any(tag in html for tag in ("<h1>", "<h2>", "<h3>", "<p>", "<ul>"))
    assert has_tags, f"HTML output missing block-level tags: {html[:100]!r}"
    print(f"[EXPORT-HTML] {len(html)} chars")

    print("\nCONSUMER_PROOF: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
