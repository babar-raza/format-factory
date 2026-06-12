"""
test_dogfood_fodp_text_extraction.py -- FODP text extraction dogfood pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-2
Uses installed FODP codec to create a presentation, write it, and extract text.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodp.fodp_codec import load, extract_text, get_page_count, FODP_MIME


_PRESENTATION = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
    ' xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"'
    ' xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"'
    ' xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"'
    ' xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"'
    f' office:mimetype="{FODP_MIME}">'
    '<office:body><office:presentation>'
    '<draw:page draw:name="Slide1">'
    '<draw:frame presentation:class="title">'
    '<draw:text-box><text:p>Format Factory Presentation</text:p></draw:text-box>'
    '</draw:frame>'
    '</draw:page>'
    '<draw:page draw:name="Slide2">'
    '<draw:frame>'
    '<draw:text-box><text:p>Product pipeline test</text:p></draw:text-box>'
    '</draw:frame>'
    '</draw:page>'
    '</office:presentation></office:body>'
    '</office:document>'
)


def test_fodp_text_extraction_pipeline():
    """Create FODP in memory, extract text, verify content."""
    texts = extract_text(_PRESENTATION.encode("utf-8"))
    assert "Format Factory Presentation" in texts
    assert "Product pipeline test" in texts


def test_fodp_page_count_pipeline():
    """Verify page count from in-memory FODP."""
    assert get_page_count(_PRESENTATION.encode("utf-8")) == 2


def test_fodp_write_load_roundtrip(tmp_path):
    """Write FODP to disk, reload, verify content preserved."""
    fp = tmp_path / "test.fodp"
    fp.write_text(_PRESENTATION, encoding="utf-8")
    model = load(fp)
    assert model["is_fodp"] is True
    assert model["page_count"] == 2
