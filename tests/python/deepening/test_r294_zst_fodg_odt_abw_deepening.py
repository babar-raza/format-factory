"""Sprint 64 — ZST / FODG / ODT / ABW product deepening (R294).

Tests 8 new analytics functions:
  ZST: zst_frame_size_range, zst_is_multi_frame
  FODG: fodg_shape_count_variance, fodg_is_text_only
  ODT: odt_list_density, odt_heading_per_paragraph
  ABW: abw_is_multi_paragraph, abw_heading_density
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst import zst_frame_size_range, zst_is_multi_frame
from src.python.fodg import fodg_shape_count_variance, fodg_is_text_only
from src.python.odt import odt_list_density, odt_heading_per_paragraph
from src.python.abw import abw_is_multi_paragraph, abw_heading_density

_ZST = _REPO / "samples" / "by-format" / "zst" / "valid" / "block-128k.zst"
_FODG = _REPO / "samples" / "by-format" / "fodg" / "shapes-basic.fodg"
_ODT = _REPO / "samples" / "by-format" / "odt" / "valid" / "minimal-document.odt"
_ABW = _REPO / "samples" / "by-format" / "abw" / "minimal-document.abw"


class TestZstFrameSizeRange:
    def test_returns_int(self):
        assert isinstance(zst_frame_size_range(_ZST), int)

    def test_nonnegative(self):
        assert zst_frame_size_range(_ZST) >= 0


class TestZstIsMultiFrame:
    def test_returns_bool(self):
        assert isinstance(zst_is_multi_frame(_ZST), bool)


class TestFodgShapeCountVariance:
    def test_returns_float(self):
        assert isinstance(fodg_shape_count_variance(_FODG), (int, float))

    def test_nonnegative(self):
        assert fodg_shape_count_variance(_FODG) >= 0.0


class TestFodgIsTextOnly:
    def test_returns_bool(self):
        assert isinstance(fodg_is_text_only(_FODG), bool)


class TestOdtListDensity:
    def test_returns_float(self):
        assert isinstance(odt_list_density(_ODT), (int, float))

    def test_bounded(self):
        val = odt_list_density(_ODT)
        assert 0.0 <= val <= 1.0


class TestOdtHeadingPerParagraph:
    def test_returns_float(self):
        assert isinstance(odt_heading_per_paragraph(_ODT), (int, float))

    def test_bounded(self):
        val = odt_heading_per_paragraph(_ODT)
        assert 0.0 <= val <= 1.0


class TestAbwIsMultiParagraph:
    def test_returns_bool(self):
        assert isinstance(abw_is_multi_paragraph(_ABW), bool)


class TestAbwHeadingDensity:
    def test_returns_float(self):
        assert isinstance(abw_heading_density(_ABW), (int, float))

    def test_nonnegative(self):
        assert abw_heading_density(_ABW) >= 0.0
