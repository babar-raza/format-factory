"""Tests for R1229: AbwDocument content analysis properties.

Properties under test:
    total_text_length     — sum of len(p) for p in paragraphs
    avg_paragraph_length  — total_text_length / paragraph_count (0.0 if empty)
    has_long_paragraphs   — any paragraph > 200 characters

spec_fact_ref: FACT-ABW-001
"""

import pytest
from abw.models import AbwDocument


def _make_doc(paragraphs: list) -> AbwDocument:
    """Build an AbwDocument stub with the given paragraph list."""
    data = {
        "is_abw": True,
        "section_count": 1,
        "paragraph_count": len(paragraphs),
        "paragraphs": paragraphs,
    }
    return AbwDocument(data)


# ── total_text_length ─────────────────────────────────────────────────────────

class TestTotalTextLength:
    def test_empty_doc_is_zero(self):
        doc = _make_doc([])
        assert doc.total_text_length == 0

    def test_single_paragraph(self):
        doc = _make_doc(["hello"])
        assert doc.total_text_length == 5

    def test_multiple_paragraphs(self):
        doc = _make_doc(["ab", "cde", "f"])
        assert doc.total_text_length == 6

    def test_empty_strings(self):
        doc = _make_doc(["", ""])
        assert doc.total_text_length == 0

    def test_mixed_empty_and_nonempty(self):
        doc = _make_doc(["", "hello", ""])
        assert doc.total_text_length == 5

    def test_long_paragraph(self):
        text = "x" * 300
        doc = _make_doc([text])
        assert doc.total_text_length == 300

    def test_unicode_characters_counted(self):
        doc = _make_doc(["αβγδ"])
        assert doc.total_text_length == 4


# ── avg_paragraph_length ──────────────────────────────────────────────────────

class TestAvgParagraphLength:
    def test_empty_doc_returns_zero(self):
        doc = _make_doc([])
        assert doc.avg_paragraph_length == 0.0

    def test_single_paragraph(self):
        doc = _make_doc(["hello"])
        assert doc.avg_paragraph_length == 5.0

    def test_two_equal_paragraphs(self):
        doc = _make_doc(["abc", "abc"])
        assert doc.avg_paragraph_length == 3.0

    def test_unequal_paragraphs(self):
        doc = _make_doc(["ab", "abcd"])  # (2+4)/2 = 3.0
        assert doc.avg_paragraph_length == 3.0

    def test_empty_paragraphs(self):
        doc = _make_doc(["", ""])
        assert doc.avg_paragraph_length == 0.0

    def test_returns_float(self):
        doc = _make_doc(["a", "bb", "ccc"])  # (1+2+3)/3 = 2.0
        assert isinstance(doc.avg_paragraph_length, float)

    def test_fractional_average(self):
        doc = _make_doc(["a", "bb"])  # (1+2)/2 = 1.5
        assert doc.avg_paragraph_length == 1.5


# ── has_long_paragraphs ───────────────────────────────────────────────────────

class TestHasLongParagraphs:
    def test_empty_doc_no_long_paragraphs(self):
        doc = _make_doc([])
        assert doc.has_long_paragraphs is False

    def test_short_paragraphs_only(self):
        doc = _make_doc(["short", "also short"])
        assert doc.has_long_paragraphs is False

    def test_exactly_200_chars_not_long(self):
        doc = _make_doc(["x" * 200])
        assert doc.has_long_paragraphs is False

    def test_201_chars_is_long(self):
        doc = _make_doc(["x" * 201])
        assert doc.has_long_paragraphs is True

    def test_mixed_short_and_long(self):
        doc = _make_doc(["short", "x" * 250, "also short"])
        assert doc.has_long_paragraphs is True

    def test_all_long(self):
        doc = _make_doc(["x" * 300, "y" * 400])
        assert doc.has_long_paragraphs is True

    def test_empty_string_not_long(self):
        doc = _make_doc([""])
        assert doc.has_long_paragraphs is False


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_zero_total_implies_zero_avg(self):
        doc = _make_doc([])
        assert doc.total_text_length == 0
        assert doc.avg_paragraph_length == 0.0

    def test_long_paragraph_has_large_total(self):
        text = "x" * 250
        doc = _make_doc([text])
        assert doc.has_long_paragraphs is True
        assert doc.total_text_length == 250
        assert doc.avg_paragraph_length == 250.0

    def test_many_short_no_long(self):
        doc = _make_doc(["short"] * 10)
        assert doc.has_long_paragraphs is False
        assert doc.total_text_length == 50
        assert doc.avg_paragraph_length == 5.0
