"""Tests for R1264: OdtModelDocument content balance and structure properties.

Properties under test:
    is_outline_heavy    — heading_ratio > 0.3
    has_balanced_content — heading_ratio in [0.1, 0.5]
    is_prose_heavy      — paragraph_ratio > 0.8

spec_fact_ref: SAL-ODT-01067
"""

import types
import pytest
from odt.models import OdtModelDocument


def _make_doc(paragraph_count: int, heading_count: int) -> OdtModelDocument:
    parsed = types.SimpleNamespace(
        paragraphs=[types.SimpleNamespace(text=f"p{i}") for i in range(paragraph_count)],
        headings=[types.SimpleNamespace(text=f"h{i}") for i in range(heading_count)],
        path="test.odt",
    )
    return OdtModelDocument(parsed)


# ── is_outline_heavy ──────────────────────────────────────────────────────────

class TestIsOutlineHeavy:
    def test_more_than_30_pct_headings(self):
        # 4 headings, 6 paragraphs → ratio = 0.4
        doc = _make_doc(6, 4)
        assert doc.is_outline_heavy is True

    def test_exactly_30_pct_not_outline_heavy(self):
        # 3 headings, 7 paragraphs → ratio = 0.3
        doc = _make_doc(7, 3)
        assert doc.is_outline_heavy is False

    def test_no_headings_not_outline_heavy(self):
        doc = _make_doc(10, 0)
        assert doc.is_outline_heavy is False

    def test_all_headings_is_outline_heavy(self):
        # 5 headings, 0 paragraphs → ratio = 1.0
        doc = _make_doc(0, 5)
        assert doc.is_outline_heavy is True

    def test_empty_doc_not_outline_heavy(self):
        doc = _make_doc(0, 0)
        assert doc.is_outline_heavy is False


# ── has_balanced_content ──────────────────────────────────────────────────────

class TestHasBalancedContent:
    def test_exactly_10_pct_headings_is_balanced(self):
        # 1 heading, 9 paragraphs → ratio = 0.1
        doc = _make_doc(9, 1)
        assert doc.has_balanced_content is True

    def test_exactly_50_pct_headings_is_balanced(self):
        # 5 headings, 5 paragraphs → ratio = 0.5
        doc = _make_doc(5, 5)
        assert doc.has_balanced_content is True

    def test_no_headings_not_balanced(self):
        # ratio = 0.0 < 0.1
        doc = _make_doc(10, 0)
        assert doc.has_balanced_content is False

    def test_all_headings_not_balanced(self):
        # ratio = 1.0 > 0.5
        doc = _make_doc(0, 10)
        assert doc.has_balanced_content is False

    def test_moderate_heading_density(self):
        # 2 headings, 8 paragraphs → ratio = 0.2
        doc = _make_doc(8, 2)
        assert doc.has_balanced_content is True

    def test_empty_doc_not_balanced(self):
        doc = _make_doc(0, 0)
        assert doc.has_balanced_content is False


# ── is_prose_heavy ────────────────────────────────────────────────────────────

class TestIsProseHeavy:
    def test_90_pct_paragraphs_is_prose_heavy(self):
        # 9 paragraphs, 1 heading → paragraph_ratio = 0.9
        doc = _make_doc(9, 1)
        assert doc.is_prose_heavy is True

    def test_exactly_80_pct_paragraphs_not_prose_heavy(self):
        # 8 paragraphs, 2 headings → paragraph_ratio = 0.8 (not > 0.8)
        doc = _make_doc(8, 2)
        assert doc.is_prose_heavy is False

    def test_no_headings_is_prose_heavy(self):
        # all paragraphs → ratio = 1.0
        doc = _make_doc(10, 0)
        assert doc.is_prose_heavy is True

    def test_no_paragraphs_not_prose_heavy(self):
        doc = _make_doc(0, 5)
        assert doc.is_prose_heavy is False

    def test_empty_not_prose_heavy(self):
        doc = _make_doc(0, 0)
        assert doc.is_prose_heavy is False


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_prose_heavy_implies_not_outline_heavy(self):
        # 9 paragraphs, 1 heading
        doc = _make_doc(9, 1)
        assert doc.is_prose_heavy is True
        assert doc.is_outline_heavy is False

    def test_outline_heavy_implies_not_prose_heavy(self):
        # 4 headings, 6 paragraphs
        doc = _make_doc(6, 4)
        assert doc.is_outline_heavy is True
        assert doc.is_prose_heavy is False

    def test_balanced_and_prose_heavy_mutually_exclusive_with_no_heading(self):
        doc = _make_doc(10, 0)
        assert doc.is_prose_heavy is True
        assert doc.has_balanced_content is False

    def test_heading_ratio_plus_paragraph_ratio_equals_one(self):
        doc = _make_doc(7, 3)
        assert doc.heading_ratio + doc.paragraph_ratio == pytest.approx(1.0)
