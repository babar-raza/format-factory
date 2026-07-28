"""Tests for R1277: PbmDocument scale and density classification properties.

Properties under test:
    is_banner          — is_narrow and is_landscape (wide strip)
    is_tall_strip      — is_narrow and is_portrait (tall strip)
    pixel_density_class — 'micro', 'small', 'medium', or 'large'

spec_fact_ref: SAL-PBM-00001
"""

import types
import pytest
from pbm.models import PbmDocument


def _make_doc(width: int, height: int, magic: str = "P4", maxval: int = 1) -> PbmDocument:
    parsed = types.SimpleNamespace(
        width=width,
        height=height,
        maxval=maxval,
        pixel_count=width * height,
        magic=magic,
        path="test.pbm",
    )
    return PbmDocument(parsed)


# ── is_banner ─────────────────────────────────────────────────────────────────

class TestIsBanner:
    def test_wide_narrow_landscape_is_banner(self):
        # 400x100 → ratio=4 > 3, landscape
        doc = _make_doc(400, 100)
        assert doc.is_banner is True

    def test_tall_narrow_not_banner(self):
        # 100x400 → narrow but portrait
        doc = _make_doc(100, 400)
        assert doc.is_banner is False

    def test_square_not_banner(self):
        doc = _make_doc(100, 100)
        assert doc.is_banner is False

    def test_wide_but_not_narrow_not_banner(self):
        # 200x100 → ratio=2, not > 3
        doc = _make_doc(200, 100)
        assert doc.is_banner is False


# ── is_tall_strip ─────────────────────────────────────────────────────────────

class TestIsTallStrip:
    def test_tall_narrow_portrait_is_tall_strip(self):
        # 100x400 → ratio=4 > 3, portrait
        doc = _make_doc(100, 400)
        assert doc.is_tall_strip is True

    def test_wide_narrow_not_tall_strip(self):
        # 400x100 → narrow but landscape
        doc = _make_doc(400, 100)
        assert doc.is_tall_strip is False

    def test_square_not_tall_strip(self):
        doc = _make_doc(100, 100)
        assert doc.is_tall_strip is False

    def test_tall_but_not_narrow_not_strip(self):
        # 100x200 → ratio=2, not > 3
        doc = _make_doc(100, 200)
        assert doc.is_tall_strip is False


# ── pixel_density_class ───────────────────────────────────────────────────────

class TestPixelDensityClass:
    def test_micro_64x64(self):
        doc = _make_doc(64, 64)
        assert doc.pixel_density_class == "micro"

    def test_small_100x100(self):
        doc = _make_doc(100, 100)
        assert doc.pixel_density_class == "small"

    def test_medium_500x500(self):
        # 250,000 pixels → medium
        doc = _make_doc(500, 500)
        assert doc.pixel_density_class == "medium"

    def test_large_2000x2000(self):
        # 4,000,000 pixels → large
        doc = _make_doc(2000, 2000)
        assert doc.pixel_density_class == "large"

    def test_zero_is_micro(self):
        doc = _make_doc(0, 0)
        assert doc.pixel_density_class == "micro"


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_banner_implies_narrow_and_landscape(self):
        doc = _make_doc(500, 100)
        assert doc.is_banner is True
        assert doc.is_narrow is True
        assert doc.is_landscape is True

    def test_tall_strip_implies_narrow_and_portrait(self):
        doc = _make_doc(100, 500)
        assert doc.is_tall_strip is True
        assert doc.is_narrow is True
        assert doc.is_portrait is True

    def test_banner_and_tall_strip_mutually_exclusive(self):
        doc = _make_doc(400, 100)
        assert doc.is_banner is True
        assert doc.is_tall_strip is False
