"""Tests for R1287: AbwDocument document length and structure richness properties.

Properties under test:
    is_moderate_text  — 50 <= avg_paragraph_length <= 200
    has_rich_sections — paragraphs_per_section > 5
    is_long_document  — total_text_length > 10,000 characters

spec_fact_ref: SAL-ABW-00001
"""

import pytest
from abw.models import AbwDocument


def _make_doc(paragraphs: list[str], section_count: int = 1) -> AbwDocument:
    return AbwDocument({
        "is_abw": True,
        "section_count": section_count,
        "paragraph_count": len(paragraphs),
        "paragraphs": paragraphs,
    })


def _para(length: int) -> str:
    """Make a paragraph of given character length."""
    return "x" * length


# ── is_moderate_text ──────────────────────────────────────────────────────────

class TestIsModerateText:
    def test_no_paragraphs_not_moderate(self):
        doc = _make_doc([])
        assert doc.is_moderate_text is False

    def test_avg_exactly_50_is_moderate(self):
        # avg = 50 → 50 <= 50 <= 200 → True
        doc = _make_doc([_para(50)])
        assert doc.is_moderate_text is True

    def test_avg_exactly_200_is_moderate(self):
        # avg = 200 → 50 <= 200 <= 200 → True
        doc = _make_doc([_para(200)])
        assert doc.is_moderate_text is True

    def test_avg_below_50_not_moderate(self):
        # avg = 30 < 50
        doc = _make_doc([_para(30)])
        assert doc.is_moderate_text is False

    def test_avg_above_200_not_moderate(self):
        # avg = 250 > 200
        doc = _make_doc([_para(250)])
        assert doc.is_moderate_text is False

    def test_typical_moderate_document(self):
        # avg = 100 → moderate
        doc = _make_doc([_para(100), _para(100)])
        assert doc.is_moderate_text is True


# ── has_rich_sections ─────────────────────────────────────────────────────────

class TestHasRichSections:
    def test_no_sections_false(self):
        doc = _make_doc([], section_count=0)
        assert doc.has_rich_sections is False

    def test_few_paragraphs_per_section_false(self):
        # 5 paragraphs in 1 section → 5.0, NOT > 5
        doc = _make_doc([_para(50)] * 5, section_count=1)
        assert doc.has_rich_sections is False

    def test_exactly_6_is_rich(self):
        # 6 paragraphs in 1 section → 6.0 > 5 → True
        doc = _make_doc([_para(50)] * 6, section_count=1)
        assert doc.has_rich_sections is True

    def test_many_paragraphs_multiple_sections(self):
        # 12 paragraphs in 2 sections → avg = 6.0 > 5 → True
        doc = _make_doc([_para(50)] * 12, section_count=2)
        assert doc.has_rich_sections is True

    def test_many_sections_low_avg_false(self):
        # 10 paragraphs in 5 sections → avg = 2.0 < 5
        doc = _make_doc([_para(50)] * 10, section_count=5)
        assert doc.has_rich_sections is False


# ── is_long_document ──────────────────────────────────────────────────────────

class TestIsLongDocument:
    def test_empty_not_long(self):
        doc = _make_doc([])
        assert doc.is_long_document is False

    def test_short_doc_not_long(self):
        doc = _make_doc([_para(100)])
        assert doc.is_long_document is False

    def test_exactly_10000_not_long(self):
        # total = 10000, NOT > 10000
        doc = _make_doc([_para(1000)] * 10)
        assert doc.is_long_document is False

    def test_10001_is_long(self):
        # total = 10001 > 10000
        doc = _make_doc([_para(1000)] * 10 + [_para(1)])
        assert doc.is_long_document is True

    def test_large_document_is_long(self):
        doc = _make_doc([_para(500)] * 30)  # 15000 chars
        assert doc.is_long_document is True


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_moderate_not_dense_or_sparse(self):
        doc = _make_doc([_para(100)])
        assert doc.is_moderate_text is True
        assert doc.is_dense_text is False
        assert doc.is_sparse_text is False

    def test_dense_not_moderate(self):
        doc = _make_doc([_para(250)])
        assert doc.is_dense_text is True
        assert doc.is_moderate_text is False

    def test_rich_sections_implies_paragraphs_per_section_over_5(self):
        doc = _make_doc([_para(50)] * 10, section_count=1)
        assert doc.has_rich_sections is True
        assert doc.paragraphs_per_section > 5
