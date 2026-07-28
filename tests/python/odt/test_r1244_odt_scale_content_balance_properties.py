"""Tests for R1244: OdtModelDocument scale and content balance properties.

Properties under test:
    is_large          — total_block_count > 50
    has_only_paragraphs — paragraph_count > 0 and heading_count == 0
    paragraph_ratio   — paragraph_count / total_block_count (0.0 if no blocks)

spec_fact_ref: SAL-ODT-01067
"""

import types
import pytest
from odt.models import OdtModelDocument


def _make_doc(paragraph_count: int, heading_count: int) -> OdtModelDocument:
    """Build an OdtModelDocument stub with given para/heading counts."""
    paragraphs = [types.SimpleNamespace(text=f"Para {i}") for i in range(paragraph_count)]
    headings = [types.SimpleNamespace(text=f"Heading {i}", level=1) for i in range(heading_count)]
    parsed = types.SimpleNamespace(
        paragraphs=paragraphs,
        headings=headings,
        path="test.odt",
    )
    return OdtModelDocument(parsed)


# ── is_large ──────────────────────────────────────────────────────────────────

class TestIsLarge:
    def test_51_total_blocks_is_large(self):
        doc = _make_doc(paragraph_count=50, heading_count=1)  # total = 51
        assert doc.is_large is True

    def test_exactly_50_not_large(self):
        doc = _make_doc(paragraph_count=45, heading_count=5)  # total = 50
        assert doc.is_large is False

    def test_below_50_not_large(self):
        doc = _make_doc(paragraph_count=10, heading_count=5)  # total = 15
        assert doc.is_large is False

    def test_empty_not_large(self):
        doc = _make_doc(paragraph_count=0, heading_count=0)
        assert doc.is_large is False

    def test_100_paragraphs_is_large(self):
        doc = _make_doc(paragraph_count=100, heading_count=0)
        assert doc.is_large is True

    def test_only_headings_large(self):
        doc = _make_doc(paragraph_count=0, heading_count=51)
        assert doc.is_large is True


# ── has_only_paragraphs ───────────────────────────────────────────────────────

class TestHasOnlyParagraphs:
    def test_paragraphs_no_headings(self):
        doc = _make_doc(paragraph_count=5, heading_count=0)
        assert doc.has_only_paragraphs is True

    def test_paragraphs_and_headings_not_only_paragraphs(self):
        doc = _make_doc(paragraph_count=5, heading_count=2)
        assert doc.has_only_paragraphs is False

    def test_only_headings_not_only_paragraphs(self):
        doc = _make_doc(paragraph_count=0, heading_count=3)
        assert doc.has_only_paragraphs is False

    def test_empty_not_only_paragraphs(self):
        doc = _make_doc(paragraph_count=0, heading_count=0)
        assert doc.has_only_paragraphs is False

    def test_single_paragraph_no_headings(self):
        doc = _make_doc(paragraph_count=1, heading_count=0)
        assert doc.has_only_paragraphs is True

    def test_one_heading_disqualifies(self):
        doc = _make_doc(paragraph_count=10, heading_count=1)
        assert doc.has_only_paragraphs is False


# ── paragraph_ratio ───────────────────────────────────────────────────────────

class TestParagraphRatio:
    def test_empty_returns_zero(self):
        doc = _make_doc(paragraph_count=0, heading_count=0)
        assert doc.paragraph_ratio == 0.0

    def test_all_paragraphs_ratio_one(self):
        doc = _make_doc(paragraph_count=10, heading_count=0)
        assert doc.paragraph_ratio == pytest.approx(1.0)

    def test_all_headings_ratio_zero(self):
        doc = _make_doc(paragraph_count=0, heading_count=5)
        assert doc.paragraph_ratio == pytest.approx(0.0)

    def test_half_paragraphs_ratio_half(self):
        doc = _make_doc(paragraph_count=5, heading_count=5)
        assert doc.paragraph_ratio == pytest.approx(0.5)

    def test_mixed_ratio(self):
        doc = _make_doc(paragraph_count=8, heading_count=2)  # 8/10 = 0.8
        assert doc.paragraph_ratio == pytest.approx(0.8)

    def test_single_paragraph_ratio(self):
        doc = _make_doc(paragraph_count=1, heading_count=0)
        assert doc.paragraph_ratio == pytest.approx(1.0)


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_paragraph_and_heading_ratio_sum_to_one(self):
        doc = _make_doc(paragraph_count=7, heading_count=3)
        assert doc.paragraph_ratio + doc.heading_ratio == pytest.approx(1.0)

    def test_large_and_only_paragraphs(self):
        doc = _make_doc(paragraph_count=55, heading_count=0)
        assert doc.is_large is True
        assert doc.has_only_paragraphs is True
        assert doc.paragraph_ratio == pytest.approx(1.0)

    def test_not_large_with_headings(self):
        doc = _make_doc(paragraph_count=3, heading_count=2)
        assert doc.is_large is False
        assert doc.has_only_paragraphs is False

    def test_large_mixed_content(self):
        doc = _make_doc(paragraph_count=40, heading_count=15)
        assert doc.is_large is True
        assert doc.has_only_paragraphs is False
        assert doc.paragraph_ratio == pytest.approx(40 / 55)
