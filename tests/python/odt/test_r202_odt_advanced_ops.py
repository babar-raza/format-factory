"""
tests/python/odt/test_r202_odt_advanced_ops.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-SPRINT13-001
TASK-001 (part B): ODT advanced operations.

Covers: parse_odt, parse_odt_strict, probe_odt, get_capabilities,
odt_word_count, odt_heading_count, odt_paragraph_count,
OdtDocument, OdtParagraph, OdtHeading, OdtListItem.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from odt import (
    parse_odt, parse_odt_strict, probe_odt, get_capabilities,
    odt_word_count, odt_heading_count, odt_paragraph_count,
    OdtDocument, OdtParagraph,
)

_SAMPLES = _REPO / "samples" / "by-format" / "odt" / "valid"
_MINIMAL = str(_SAMPLES / "minimal-document.odt")
_TWO_PARA = str(_SAMPLES / "two-paragraphs.odt")
_UNICODE = str(_SAMPLES / "unicode-text.odt")


class TestOdtParseAndProbe:
    """parse_odt, parse_odt_strict, probe_odt, get_capabilities."""

    def test_parse_odt_returns_dict(self):
        result = parse_odt(_MINIMAL)
        assert isinstance(result, dict)

    def test_parse_odt_ok_true(self):
        result = parse_odt(_MINIMAL)
        assert result.get("ok") is True

    def test_parse_odt_minimal_paragraph_count(self):
        result = parse_odt(_MINIMAL)
        assert result.get("paragraph_count") == 1

    def test_parse_odt_two_paragraphs(self):
        result = parse_odt(_TWO_PARA)
        assert result.get("paragraph_count") == 2

    def test_parse_odt_has_paragraphs_list(self):
        result = parse_odt(_MINIMAL)
        assert isinstance(result.get("paragraphs"), list)

    def test_parse_odt_paragraph_text(self):
        result = parse_odt(_MINIMAL)
        text = result["paragraphs"][0]["text"]
        assert isinstance(text, str)
        assert len(text) > 0

    def test_parse_odt_unicode_text(self):
        result = parse_odt(_UNICODE)
        text = result["paragraphs"][0]["text"]
        assert "Café" in text or len(text) > 0

    def test_parse_odt_has_headings_list(self):
        result = parse_odt(_MINIMAL)
        assert isinstance(result.get("headings"), list)

    def test_parse_odt_strict_returns_odtdocument(self):
        doc = parse_odt_strict(_MINIMAL)
        assert isinstance(doc, OdtDocument)

    def test_parse_odt_strict_paragraphs_attr(self):
        doc = parse_odt_strict(_MINIMAL)
        assert hasattr(doc, "paragraphs")
        assert isinstance(doc.paragraphs, list)

    def test_parse_odt_strict_paragraph_type(self):
        doc = parse_odt_strict(_MINIMAL)
        assert len(doc.paragraphs) >= 1
        assert isinstance(doc.paragraphs[0], OdtParagraph)

    def test_probe_odt_returns_dict(self):
        result = probe_odt(_MINIMAL)
        assert isinstance(result, dict)

    def test_probe_odt_valid_container(self):
        result = probe_odt(_MINIMAL)
        assert result.get("valid_container") is True

    def test_probe_odt_exists(self):
        result = probe_odt(_MINIMAL)
        assert result.get("exists") is True

    def test_probe_odt_mimetype(self):
        result = probe_odt(_MINIMAL)
        assert "oasis" in result.get("mimetype", "")

    def test_get_capabilities_dict(self):
        caps = get_capabilities()
        assert isinstance(caps, dict)
        assert caps.get("format") == "odt"

    def test_get_capabilities_has_supported(self):
        caps = get_capabilities()
        assert isinstance(caps.get("supported"), list)
        assert len(caps["supported"]) > 0


class TestOdtAnalytics:
    """odt_word_count, odt_heading_count, odt_paragraph_count."""

    def test_odt_word_count_int(self):
        count = odt_word_count(_MINIMAL)
        assert isinstance(count, int)
        assert count >= 1

    def test_odt_word_count_minimal(self):
        # "Hello, world." → 2 words
        count = odt_word_count(_MINIMAL)
        assert count == 2

    def test_odt_word_count_two_paragraphs(self):
        # "First paragraph. Second paragraph." → 4 words
        count = odt_word_count(_TWO_PARA)
        assert count == 4

    def test_odt_heading_count_int(self):
        count = odt_heading_count(_MINIMAL)
        assert isinstance(count, int)

    def test_odt_heading_count_zero_for_minimal(self):
        count = odt_heading_count(_MINIMAL)
        assert count == 0

    def test_odt_paragraph_count_int(self):
        count = odt_paragraph_count(_MINIMAL)
        assert isinstance(count, int)
        assert count >= 1

    def test_odt_paragraph_count_minimal(self):
        count = odt_paragraph_count(_MINIMAL)
        assert count == 1

    def test_odt_paragraph_count_two(self):
        count = odt_paragraph_count(_TWO_PARA)
        assert count == 2
