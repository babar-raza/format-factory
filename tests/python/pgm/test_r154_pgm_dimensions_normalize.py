"""
test_r154_pgm_dimensions_normalize.py

Sprint: FORMAT-FACTORY-MAINSTREAM-PRODUCT-DEEPENING-RNEXT12-001
Added: 2026-06-09

Tests for PGM get_dimensions and normalize functions.
Authority: P5 (SAL-PGM-00001: P2 magic, SAL-PGM-00002: P5 magic)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pgm.pgm_parser import get_dimensions, normalize, write_pgm, parse_pgm_strict, PgmError


def _make_pgm(tmp_path: Path, width: int, height: int, maxval: int, pixels: list[int]) -> Path:
    """Create a temporary PGM file."""
    p = tmp_path / "test.pgm"
    write_pgm(pixels, width, height, maxval, p)
    return p


class TestGetDimensions:
    """get_dimensions: return (width, height) of a PGM image."""

    def test_basic_dimensions(self, tmp_path):
        pixels = [0, 128, 255, 64, 200, 100]
        p = _make_pgm(tmp_path, 3, 2, 255, pixels)
        assert get_dimensions(p) == (3, 2)

    def test_single_pixel(self, tmp_path):
        p = _make_pgm(tmp_path, 1, 1, 255, [127])
        assert get_dimensions(p) == (1, 1)

    def test_square_image(self, tmp_path):
        pixels = [i % 256 for i in range(16)]
        p = _make_pgm(tmp_path, 4, 4, 255, pixels)
        assert get_dimensions(p) == (4, 4)

    def test_nonexistent_file_raises(self, tmp_path):
        with pytest.raises(PgmError):
            get_dimensions(tmp_path / "nonexistent.pgm")


class TestNormalize:
    """normalize: rescale PGM pixel values to a new maxval."""

    def test_normalize_same_maxval_preserves(self, tmp_path):
        pixels = [0, 128, 255]
        src = _make_pgm(tmp_path, 3, 1, 255, pixels)
        dst = tmp_path / "normalized.pgm"
        result = normalize(src, dst, new_maxval=255)
        assert result["ok"] is True
        img = parse_pgm_strict(dst)
        assert img.pixels == pixels

    def test_normalize_upscale(self, tmp_path):
        pixels = [0, 5, 10]
        src = _make_pgm(tmp_path, 3, 1, 10, pixels)
        dst = tmp_path / "upscaled.pgm"
        result = normalize(src, dst, new_maxval=255)
        assert result["ok"] is True
        assert result["old_maxval"] == 10
        assert result["new_maxval"] == 255
        img = parse_pgm_strict(dst)
        assert img.pixels[0] == 0
        assert img.pixels[2] == 255  # 10/10 * 255 = 255

    def test_normalize_downscale(self, tmp_path):
        pixels = [0, 128, 255]
        src = _make_pgm(tmp_path, 3, 1, 255, pixels)
        dst = tmp_path / "downscaled.pgm"
        result = normalize(src, dst, new_maxval=10)
        assert result["ok"] is True
        img = parse_pgm_strict(dst)
        assert img.pixels[0] == 0
        assert img.pixels[2] == 10  # 255/255 * 10 = 10

    def test_normalize_result_keys(self, tmp_path):
        pixels = [50, 100]
        src = _make_pgm(tmp_path, 2, 1, 255, pixels)
        dst = tmp_path / "result.pgm"
        result = normalize(src, dst)
        assert "ok" in result
        assert "width" in result
        assert "height" in result
        assert "old_maxval" in result
        assert "new_maxval" in result
        assert "pixel_count" in result

    def test_normalize_preserves_dimensions(self, tmp_path):
        pixels = [10, 20, 30, 40, 50, 60]
        src = _make_pgm(tmp_path, 3, 2, 100, pixels)
        dst = tmp_path / "norm.pgm"
        normalize(src, dst, new_maxval=200)
        w, h = get_dimensions(dst)
        assert (w, h) == (3, 2)

    def test_normalize_invalid_maxval_raises(self, tmp_path):
        pixels = [100]
        src = _make_pgm(tmp_path, 1, 1, 255, pixels)
        with pytest.raises(ValueError):
            normalize(src, tmp_path / "out.pgm", new_maxval=0)

    def test_normalize_nonexistent_source_raises(self, tmp_path):
        with pytest.raises(PgmError):
            normalize(tmp_path / "ghost.pgm", tmp_path / "out.pgm")
