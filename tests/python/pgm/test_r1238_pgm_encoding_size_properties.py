"""Tests for R1238: PgmDocument encoding and size classification properties.

Properties under test:
    is_ascii       — magic == "P2"
    is_large_image — pixel_count > 1_000_000
    long_edge      — max(width, height)
    short_edge     — min(width, height)

spec_fact_ref: SAL-PGM-00001
"""

import types
import pytest
from pgm.models import PgmDocument


def _make_doc(width: int, height: int, magic: str = "P2", maxval: int = 255) -> PgmDocument:
    """Build a PgmDocument stub with given dimensions and magic."""
    parsed = types.SimpleNamespace(
        width=width,
        height=height,
        maxval=maxval,
        magic=magic,
        pixels=[],
        path="test.pgm",
    )
    return PgmDocument(parsed)


# ── is_ascii ──────────────────────────────────────────────────────────────────

class TestIsAscii:
    def test_p2_magic_is_ascii(self):
        doc = _make_doc(10, 10, magic="P2")
        assert doc.is_ascii is True

    def test_p5_magic_not_ascii(self):
        doc = _make_doc(10, 10, magic="P5")
        assert doc.is_ascii is False

    def test_is_ascii_inverse_of_is_binary(self):
        doc_p2 = _make_doc(10, 10, magic="P2")
        doc_p5 = _make_doc(10, 10, magic="P5")
        assert doc_p2.is_ascii is True
        assert doc_p2.is_binary is False
        assert doc_p5.is_ascii is False
        assert doc_p5.is_binary is True

    def test_ascii_zero_dimensions(self):
        doc = _make_doc(0, 0, magic="P2")
        assert doc.is_ascii is True


# ── is_large_image ────────────────────────────────────────────────────────────

class TestIsLargeImage:
    def test_over_1mp_is_large(self):
        doc = _make_doc(1001, 1000)  # 1_001_000 > 1_000_000
        assert doc.is_large_image is True

    def test_exactly_1mp_not_large(self):
        doc = _make_doc(1000, 1000)  # exactly 1_000_000 — not > 1_000_000
        assert doc.is_large_image is False

    def test_below_1mp_not_large(self):
        doc = _make_doc(800, 600)  # 480_000
        assert doc.is_large_image is False

    def test_zero_pixels_not_large(self):
        doc = _make_doc(0, 0)
        assert doc.is_large_image is False

    def test_full_hd_is_large(self):
        doc = _make_doc(1920, 1080)  # 2_073_600
        assert doc.is_large_image is True

    def test_small_image_not_large(self):
        doc = _make_doc(64, 64)
        assert doc.is_large_image is False


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

    def test_wide_short_short_edge(self):
        doc = _make_doc(5000, 100)
        assert doc.short_edge == 100


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_long_edge_gte_short_edge(self):
        doc = _make_doc(800, 600)
        assert doc.long_edge >= doc.short_edge

    def test_large_image_has_high_pixel_count(self):
        doc = _make_doc(2000, 1500)
        assert doc.is_large_image is True
        assert doc.pixel_count > 1_000_000

    def test_ascii_and_large(self):
        doc = _make_doc(1920, 1080, magic="P2")
        assert doc.is_ascii is True
        assert doc.is_large_image is True

    def test_binary_and_landscape_with_edges(self):
        doc = _make_doc(1920, 1080, magic="P5")
        assert doc.is_ascii is False
        assert doc.is_binary is True
        assert doc.long_edge == 1920
        assert doc.short_edge == 1080
