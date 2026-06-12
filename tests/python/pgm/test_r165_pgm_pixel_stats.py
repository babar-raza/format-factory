"""
test_r165_pgm_pixel_stats.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT29-001
Added: 2026-06-10

Tests for PGM image_pixel_stats function.
Authority: P5 (FACT-PGM-001: P2 magic, FACT-PGM-002: P5 magic)
"""
from __future__ import annotations

import sys
from pathlib import Path


_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pgm.pgm_parser import image_pixel_stats, write_pgm


def _make_pgm(tmp_path: Path, width: int, height: int, maxval: int, pixels: list[int]) -> Path:
    p = tmp_path / "test.pgm"
    write_pgm(pixels, width, height, maxval, p)
    return p


class TestImagePixelStats:

    def test_uniform_zero(self, tmp_path):
        p = _make_pgm(tmp_path, 2, 2, 255, [0, 0, 0, 0])
        result = image_pixel_stats(p)
        assert result["ok"] is True
        assert result["min_value"] == 0
        assert result["max_value"] == 0
        assert result["total_pixels"] == 4
        assert result["mean_approx"] == 0.0

    def test_uniform_max(self, tmp_path):
        p = _make_pgm(tmp_path, 2, 2, 255, [255, 255, 255, 255])
        result = image_pixel_stats(p)
        assert result["min_value"] == 255
        assert result["max_value"] == 255
        assert result["mean_approx"] == 255.0

    def test_mixed_values(self, tmp_path):
        p = _make_pgm(tmp_path, 4, 1, 255, [0, 100, 200, 255])
        result = image_pixel_stats(p)
        assert result["ok"] is True
        assert result["min_value"] == 0
        assert result["max_value"] == 255
        assert result["total_pixels"] == 4

    def test_single_pixel(self, tmp_path):
        p = _make_pgm(tmp_path, 1, 1, 255, [128])
        result = image_pixel_stats(p)
        assert result["width"] == 1
        assert result["height"] == 1
        assert result["min_value"] == 128
        assert result["max_value"] == 128

    def test_has_maxval(self, tmp_path):
        p = _make_pgm(tmp_path, 2, 1, 100, [50, 75])
        result = image_pixel_stats(p)
        assert result["maxval"] == 100

    def test_has_magic(self, tmp_path):
        p = _make_pgm(tmp_path, 2, 1, 255, [0, 255])
        result = image_pixel_stats(p)
        assert "magic" in result
        assert result["magic"] in ("P2", "P5")

    def test_dimensions_in_result(self, tmp_path):
        p = _make_pgm(tmp_path, 3, 4, 255, [0] * 12)
        result = image_pixel_stats(p)
        assert result["width"] == 3
        assert result["height"] == 4

    def test_nonexistent_file(self, tmp_path):
        result = image_pixel_stats(tmp_path / "ghost.pgm")
        assert result.get("ok") is False or "error" in result
