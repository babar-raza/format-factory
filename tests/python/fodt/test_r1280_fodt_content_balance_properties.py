"""Tests for R1280: FodtDocument content balance and prose density properties.

Properties under test:
    paragraph_ratio     — fraction of total blocks that are paragraphs
    has_balanced_content — heading_ratio between 0.1 and 0.5
    is_prose_heavy      — paragraph_ratio > 0.8

spec_fact_ref: SAL-FODT-00001
"""

import pytest
from fodt.models import FodtDocument


def _make_doc(paragraphs: int, headings: int, tables: int = 0, lists: int = 0) -> FodtDocument:
    blocks = (
        [{"kind": "paragraph", "text": f"P{i}"} for i in range(paragraphs)]
        + [{"kind": "heading", "text": f"H{i}", "outline_level": 1} for i in range(headings)]
    )
    data = {
        "format_id": "fodt",
        "odf_version": "1.2",
        "blocks": blocks,
        "tables": [{}] * tables,
        "lists": [{}] * lists,
        "warnings": [],
    }
    return FodtDocument(data)


# ── paragraph_ratio ───────────────────────────────────────────────────────────

class TestParagraphRatio:
    def test_no_blocks_returns_zero(self):
        doc = _make_doc(0, 0)
        assert doc.paragraph_ratio == pytest.approx(0.0)

    def test_all_paragraphs_returns_one(self):
        doc = _make_doc(5, 0)
        assert doc.paragraph_ratio == pytest.approx(1.0)

    def test_all_headings_returns_zero(self):
        doc = _make_doc(0, 5)
        assert doc.paragraph_ratio == pytest.approx(0.0)

    def test_mixed_blocks(self):
        # 3 paragraphs + 1 heading → ratio = 3/4
        doc = _make_doc(3, 1)
        assert doc.paragraph_ratio == pytest.approx(0.75)

    def test_half_paragraphs(self):
        doc = _make_doc(5, 5)
        assert doc.paragraph_ratio == pytest.approx(0.5)


# ── has_balanced_content ──────────────────────────────────────────────────────

class TestHasBalancedContent:
    def test_no_headings_not_balanced(self):
        # heading_ratio = 0.0, below 0.1
        doc = _make_doc(10, 0)
        assert doc.has_balanced_content is False

    def test_all_headings_not_balanced(self):
        # heading_ratio = 1.0, above 0.5
        doc = _make_doc(0, 10)
        assert doc.has_balanced_content is False

    def test_one_heading_in_ten_balanced(self):
        # heading_ratio = 0.1 → edge: 0.1 ≤ 0.1 → True
        doc = _make_doc(9, 1)
        assert doc.has_balanced_content is True

    def test_half_headings_balanced(self):
        # heading_ratio = 0.5 → edge: 0.5 ≤ 0.5 → True
        doc = _make_doc(5, 5)
        assert doc.has_balanced_content is True

    def test_typical_document_balanced(self):
        # heading_ratio = 3/13 ≈ 0.23 → balanced
        doc = _make_doc(10, 3)
        assert doc.has_balanced_content is True

    def test_heading_heavy_not_balanced(self):
        # heading_ratio = 0.6 → above 0.5
        doc = _make_doc(4, 6)
        assert doc.has_balanced_content is False


# ── is_prose_heavy ────────────────────────────────────────────────────────────

class TestIsProseHeavy:
    def test_all_paragraphs_is_prose_heavy(self):
        doc = _make_doc(10, 0)
        assert doc.is_prose_heavy is True

    def test_mostly_paragraphs_is_prose_heavy(self):
        # 9 paragraphs + 1 heading → ratio = 0.9 > 0.8
        doc = _make_doc(9, 1)
        assert doc.is_prose_heavy is True

    def test_equal_split_not_prose_heavy(self):
        doc = _make_doc(5, 5)
        assert doc.is_prose_heavy is False

    def test_no_blocks_not_prose_heavy(self):
        doc = _make_doc(0, 0)
        assert doc.is_prose_heavy is False

    def test_eight_in_ten_not_prose_heavy(self):
        # paragraph_ratio = 0.8, NOT > 0.8
        doc = _make_doc(8, 2)
        assert doc.is_prose_heavy is False


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_prose_heavy_implies_not_outline_heavy(self):
        # All paragraphs → prose_heavy=True, outline_heavy=False
        doc = _make_doc(10, 0)
        assert doc.is_prose_heavy is True
        assert doc.is_outline_heavy is False

    def test_paragraph_ratio_plus_heading_ratio_equals_one(self):
        doc = _make_doc(7, 3)
        assert doc.paragraph_ratio + doc.heading_ratio == pytest.approx(1.0)

    def test_balanced_not_prose_heavy(self):
        # balanced requires heading_ratio ≥ 0.1, so paragraph_ratio ≤ 0.9 at best
        # If heading_ratio = 0.3 → paragraph_ratio = 0.7 < 0.8 → not prose_heavy
        doc = _make_doc(7, 3)
        assert doc.has_balanced_content is True
        assert doc.is_prose_heavy is False
