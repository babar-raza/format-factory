"""
test_r154_pbm_dimensions_invert.py

Sprint: FORMAT-FACTORY-MAINSTREAM-PRODUCT-DEEPENING-RNEXT12-001
Added: 2026-06-09

Tests for PBM get_dimensions and invert functions.
Authority: P5 (SAL-PBM-00001: P1 magic, SAL-PBM-00002: P4 magic)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm.pbm_parser import get_dimensions, invert, write_pbm, PbmError


def _make_pbm(tmp_path: Path, width: int, height: int, pixels: list[int]) -> Path:
    """Create a temporary PBM file."""
    p = tmp_path / "test.pbm"
    write_pbm(pixels, width, height, p)
    return p


class TestGetDimensions:
    """get_dimensions: return (width, height) of a PBM image."""

    def test_basic_dimensions(self, tmp_path):
        pixels = [0, 1, 1, 0, 1, 0]
        p = _make_pbm(tmp_path, 3, 2, pixels)
        assert get_dimensions(p) == (3, 2)

    def test_single_pixel(self, tmp_path):
        p = _make_pbm(tmp_path, 1, 1, [0])
        assert get_dimensions(p) == (1, 1)

    def test_wide_image(self, tmp_path):
        pixels = [0] * 100
        p = _make_pbm(tmp_path, 100, 1, pixels)
        assert get_dimensions(p) == (100, 1)

    def test_tall_image(self, tmp_path):
        pixels = [1] * 50
        p = _make_pbm(tmp_path, 1, 50, pixels)
        assert get_dimensions(p) == (1, 50)

    def test_nonexistent_file_raises(self, tmp_path):
        with pytest.raises(PbmError):
            get_dimensions(tmp_path / "nonexistent.pbm")


class TestInvert:
    """invert: invert a PBM image (swap 0 and 1)."""

    def test_invert_basic(self, tmp_path):
        pixels = [0, 1, 1, 0]
        src = _make_pbm(tmp_path, 2, 2, pixels)
        dst = tmp_path / "inverted.pbm"
        result = invert(src, dst)
        assert result["ok"] is True
        assert result["width"] == 2
        assert result["height"] == 2
        assert result["pixel_count"] == 4

    def test_invert_produces_valid_file(self, tmp_path):
        pixels = [0, 1, 1, 0, 0, 1]
        src = _make_pbm(tmp_path, 3, 2, pixels)
        dst = tmp_path / "inverted.pbm"
        invert(src, dst)
        w, h = get_dimensions(dst)
        assert (w, h) == (3, 2)

    def test_invert_swaps_values(self, tmp_path):
        from pbm.pbm_parser import parse_pbm_strict
        pixels = [0, 0, 1, 1]
        src = _make_pbm(tmp_path, 2, 2, pixels)
        dst = tmp_path / "inverted.pbm"
        invert(src, dst)
        img = parse_pbm_strict(dst)
        assert img.pixels == [1, 1, 0, 0]

    def test_double_invert_roundtrip(self, tmp_path):
        from pbm.pbm_parser import parse_pbm_strict
        pixels = [0, 1, 0, 1, 1, 0]
        src = _make_pbm(tmp_path, 3, 2, pixels)
        mid = tmp_path / "mid.pbm"
        final = tmp_path / "final.pbm"
        invert(src, mid)
        invert(mid, final)
        img = parse_pbm_strict(final)
        assert img.pixels == pixels

    def test_invert_nonexistent_source_raises(self, tmp_path):
        with pytest.raises(PbmError):
            invert(tmp_path / "ghost.pbm", tmp_path / "out.pbm")
