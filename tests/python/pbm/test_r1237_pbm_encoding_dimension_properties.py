"""Tests for R1237: PbmDocument encoding and dimension analysis properties.

Properties under test:
    is_ascii   — magic == "P1"
    long_edge  — max(width, height)
    short_edge — min(width, height)

spec_fact_ref: SAL-PBM-00001
"""

import types
import pytest
from pbm.models import PbmDocument


def _make_doc(width: int, height: int, magic: str = "P1") -> PbmDocument:
    """Build a PbmDocument stub with given dimensions and magic."""
    parsed = types.SimpleNamespace(
        width=width,
        height=height,
        magic=magic,
        pixels=[],
        path="test.pbm",
    )
    return PbmDocument(parsed)


# ── is_ascii ──────────────────────────────────────────────────────────────────

class TestIsAscii:
    def test_p1_magic_is_ascii(self):
        doc = _make_doc(10, 10, magic="P1")
        assert doc.is_ascii is True

    def test_p4_magic_not_ascii(self):
        doc = _make_doc(10, 10, magic="P4")
        assert doc.is_ascii is False

    def test_is_ascii_inverse_of_is_binary(self):
        doc_p1 = _make_doc(10, 10, magic="P1")
        doc_p4 = _make_doc(10, 10, magic="P4")
        assert doc_p1.is_ascii is True
        assert doc_p1.is_binary is False
        assert doc_p4.is_ascii is False
        assert doc_p4.is_binary is True

    def test_ascii_zero_dimensions(self):
        doc = _make_doc(0, 0, magic="P1")
        assert doc.is_ascii is True

    def test_binary_large_image(self):
        doc = _make_doc(4096, 4096, magic="P4")
        assert doc.is_ascii is False


# ── long_edge ─────────────────────────────────────────────────────────────────

class TestLongEdge:
    def test_landscape_long_edge_is_width(self):
        doc = _make_doc(1920, 1080)
        assert doc.long_edge == 1920

    def test_portrait_long_edge_is_height(self):
        doc = _make_doc(1080, 1920)
        assert doc.long_edge == 1920

    def test_square_long_edge_equals_width(self):
        doc = _make_doc(512, 512)
        assert doc.long_edge == 512

    def test_zero_dimensions_long_edge(self):
        doc = _make_doc(0, 0)
        assert doc.long_edge == 0

    def test_tall_narrow_long_edge(self):
        doc = _make_doc(10, 1000)
        assert doc.long_edge == 1000

    def test_wide_short_long_edge(self):
        doc = _make_doc(5000, 100)
        assert doc.long_edge == 5000


# ── short_edge ────────────────────────────────────────────────────────────────

class TestShortEdge:
    def test_landscape_short_edge_is_height(self):
        doc = _make_doc(1920, 1080)
        assert doc.short_edge == 1080

    def test_portrait_short_edge_is_width(self):
        doc = _make_doc(1080, 1920)
        assert doc.short_edge == 1080

    def test_square_short_edge_equals_height(self):
        doc = _make_doc(512, 512)
        assert doc.short_edge == 512

    def test_zero_dimensions_short_edge(self):
        doc = _make_doc(0, 0)
        assert doc.short_edge == 0

    def test_tall_narrow_short_edge(self):
        doc = _make_doc(10, 1000)
        assert doc.short_edge == 10

    def test_wide_short_short_edge(self):
        doc = _make_doc(5000, 100)
        assert doc.short_edge == 100


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_long_edge_gte_short_edge(self):
        doc = _make_doc(800, 600)
        assert doc.long_edge >= doc.short_edge

    def test_square_long_equals_short(self):
        doc = _make_doc(256, 256)
        assert doc.long_edge == doc.short_edge

    def test_ascii_and_square(self):
        doc = _make_doc(100, 100, magic="P1")
        assert doc.is_ascii is True
        assert doc.is_square is True
        assert doc.long_edge == doc.short_edge == 100

    def test_binary_and_landscape(self):
        doc = _make_doc(1920, 1080, magic="P4")
        assert doc.is_ascii is False
        assert doc.is_binary is True
        assert doc.is_landscape is True
        assert doc.long_edge == 1920
        assert doc.short_edge == 1080
