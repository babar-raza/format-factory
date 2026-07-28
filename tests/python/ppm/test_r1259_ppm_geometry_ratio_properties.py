"""Tests for R1259: PpmDocument geometry ratio properties.

Properties under test:
    edge_ratio — long_edge / short_edge (1.0 if short_edge is 0)
    is_narrow  — edge_ratio > 3.0
    is_micro   — width <= 64 and height <= 64

spec_fact_ref: SAL-PPM-00001
"""

import types
import pytest
from ppm.models import PpmDocument


def _make_doc(width: int, height: int, magic: str = "P6", maxval: int = 255) -> PpmDocument:
    parsed = types.SimpleNamespace(
        width=width,
        height=height,
        maxval=maxval,
        pixel_count=width * height,
        magic=magic,
        path="test.ppm",
    )
    return PpmDocument(parsed)


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

    def test_ascii_vs_binary_independent_of_shape(self):
        ascii_doc = _make_doc(300, 100, magic="P3")
        binary_doc = _make_doc(300, 100, magic="P6")
        assert ascii_doc.is_ascii is True
        assert binary_doc.is_ascii is False
        assert ascii_doc.edge_ratio == pytest.approx(binary_doc.edge_ratio)
