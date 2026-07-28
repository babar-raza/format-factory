"""Tests for R1257: PbmDocument geometry ratio properties.

Properties under test:
    edge_ratio — long_edge / short_edge (1.0 if short_edge is 0)
    is_narrow  — edge_ratio > 3.0
    is_micro   — width <= 64 and height <= 64

spec_fact_ref: SAL-PBM-00001
"""

import types
import pytest
from pbm.models import PbmDocument


def _make_doc(width: int, height: int, magic: str = "P4") -> PbmDocument:
    parsed = types.SimpleNamespace(
        width=width,
        height=height,
        pixel_count=width * height,
        magic=magic,
        path="test.pbm",
    )
    return PbmDocument(parsed)


# ── edge_ratio ────────────────────────────────────────────────────────────────

class TestEdgeRatio:
    def test_square_ratio_one(self):
        doc = _make_doc(100, 100)
        assert doc.edge_ratio == pytest.approx(1.0)

    def test_landscape_ratio(self):
        doc = _make_doc(300, 100)
        assert doc.edge_ratio == pytest.approx(3.0)

    def test_portrait_ratio(self):
        doc = _make_doc(100, 400)
        assert doc.edge_ratio == pytest.approx(4.0)

    def test_zero_short_edge_returns_one(self):
        doc = _make_doc(0, 0)
        assert doc.edge_ratio == pytest.approx(1.0)

    def test_two_to_one_ratio(self):
        doc = _make_doc(200, 100)
        assert doc.edge_ratio == pytest.approx(2.0)


# ── is_narrow ─────────────────────────────────────────────────────────────────

class TestIsNarrow:
    def test_ratio_gt_3_is_narrow(self):
        doc = _make_doc(400, 100)
        assert doc.is_narrow is True

    def test_ratio_exactly_3_not_narrow(self):
        doc = _make_doc(300, 100)
        assert doc.is_narrow is False

    def test_square_not_narrow(self):
        doc = _make_doc(100, 100)
        assert doc.is_narrow is False

    def test_very_narrow_portrait(self):
        doc = _make_doc(10, 1000)
        assert doc.is_narrow is True

    def test_ratio_2_not_narrow(self):
        doc = _make_doc(200, 100)
        assert doc.is_narrow is False


# ── is_micro ──────────────────────────────────────────────────────────────────

class TestIsMicro:
    def test_64x64_is_micro(self):
        doc = _make_doc(64, 64)
        assert doc.is_micro is True

    def test_65x65_not_micro(self):
        doc = _make_doc(65, 65)
        assert doc.is_micro is False

    def test_1x1_is_micro(self):
        doc = _make_doc(1, 1)
        assert doc.is_micro is True

    def test_64x65_not_micro(self):
        doc = _make_doc(64, 65)
        assert doc.is_micro is False

    def test_zero_by_zero_is_micro(self):
        doc = _make_doc(0, 0)
        assert doc.is_micro is True


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_narrow_implies_ratio_gt_3(self):
        doc = _make_doc(500, 100)
        assert doc.is_narrow is True
        assert doc.edge_ratio > 3.0

    def test_micro_square_not_narrow(self):
        doc = _make_doc(32, 32)
        assert doc.is_micro is True
        assert doc.is_narrow is False
