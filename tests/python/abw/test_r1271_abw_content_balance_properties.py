"""Tests for R1271: AbwDocument content balance and text density properties.

Properties under test:
    avg_section_length — total_text_length / section_count (0.0 if no sections)
    is_dense_text      — avg_paragraph_length > 200
    is_sparse_text     — avg_paragraph_length < 50 and paragraph_count > 0

spec_fact_ref: FACT-ABW-001
"""

import pytest
from abw.models import AbwDocument


def _make_doc(paragraphs: list[str], section_count: int = 1) -> AbwDocument:
    """Build an AbwDocument stub."""
    return AbwDocument({
        "is_abw": True,
        "section_count": section_count,
        "paragraph_count": len(paragraphs),
        "paragraphs": paragraphs,
    })


# ── avg_section_length ────────────────────────────────────────────────────────

class TestAvgSectionLength:
    def test_no_sections_returns_zero(self):
        doc = _make_doc([], section_count=0)
        assert doc.avg_section_length == pytest.approx(0.0)

    def test_single_section(self):
        doc = _make_doc(["hello world"], section_count=1)
        # total_text_length = 11
        assert doc.avg_section_length == pytest.approx(11.0)

    def test_two_sections(self):
        doc = _make_doc(["a" * 100, "b" * 100], section_count=2)
        # total_text_length = 200, sections = 2
        assert doc.avg_section_length == pytest.approx(100.0)

    def test_empty_paragraphs_with_sections(self):
        doc = _make_doc([], section_count=3)
        assert doc.avg_section_length == pytest.approx(0.0)

    def test_proportional_to_text_length(self):
        doc = _make_doc(["x" * 300], section_count=3)
        assert doc.avg_section_length == pytest.approx(100.0)


# ── is_dense_text ─────────────────────────────────────────────────────────────

class TestIsDenseText:
    def test_avg_over_200_is_dense(self):
        # One paragraph of 201 chars
        doc = _make_doc(["a" * 201])
        assert doc.is_dense_text is True

    def test_avg_exactly_200_not_dense(self):
        doc = _make_doc(["a" * 200])
        assert doc.is_dense_text is False

    def test_two_long_paragraphs(self):
        # avg = 250
        doc = _make_doc(["a" * 250, "b" * 250])
        assert doc.is_dense_text is True

    def test_short_paragraphs_not_dense(self):
        doc = _make_doc(["short"])
        assert doc.is_dense_text is False

    def test_empty_doc_not_dense(self):
        doc = _make_doc([])
        assert doc.is_dense_text is False


# ── is_sparse_text ────────────────────────────────────────────────────────────

class TestIsSparseText:
    def test_avg_below_50_is_sparse(self):
        doc = _make_doc(["hello"])  # len=5 < 50
        assert doc.is_sparse_text is True

    def test_avg_exactly_50_not_sparse(self):
        doc = _make_doc(["a" * 50])
        assert doc.is_sparse_text is False

    def test_empty_doc_not_sparse(self):
        doc = _make_doc([])
        assert doc.is_sparse_text is False

    def test_long_paragraphs_not_sparse(self):
        doc = _make_doc(["a" * 200])
        assert doc.is_sparse_text is False

    def test_mixed_short_paragraphs_sparse(self):
        # avg = (10+20) / 2 = 15 < 50
        doc = _make_doc(["a" * 10, "b" * 20])
        assert doc.is_sparse_text is True


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_dense_and_sparse_mutually_exclusive(self):
        # Long paragraphs: dense, not sparse
        doc = _make_doc(["a" * 300])
        assert doc.is_dense_text is True
        assert doc.is_sparse_text is False

    def test_sparse_implies_not_dense(self):
        doc = _make_doc(["hi"])
        assert doc.is_sparse_text is True
        assert doc.is_dense_text is False

    def test_avg_section_length_proportional(self):
        doc = _make_doc(["a" * 100, "b" * 200], section_count=2)
        assert doc.avg_section_length == pytest.approx(doc.total_text_length / 2)
