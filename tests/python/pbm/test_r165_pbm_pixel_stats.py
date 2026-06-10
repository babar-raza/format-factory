"""
test_r165_pbm_pixel_stats.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT29-001
Added: 2026-06-10

Tests for PBM image_pixel_stats function.
Authority: P4 (FACT-PBM-001: P1 magic, FACT-PBM-002: P4 magic)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm.pbm_parser import image_pixel_stats, write_pbm


def _make_pbm(tmp_path: Path, width: int, height: int, pixels: list[int]) -> Path:
    p = tmp_path / "test.pbm"
    write_pbm(pixels, width, height, p)
    return p


class TestImagePixelStats:

    def test_all_white(self, tmp_path):
        p = _make_pbm(tmp_path, 2, 2, [0, 0, 0, 0])
        result = image_pixel_stats(p)
        assert result["ok"] is True
        assert result["black_count"] == 0
        assert result["white_count"] == 4
        assert result["total_pixels"] == 4
        assert result["black_density"] == 0.0

    def test_all_black(self, tmp_path):
        p = _make_pbm(tmp_path, 2, 2, [1, 1, 1, 1])
        result = image_pixel_stats(p)
        assert result["ok"] is True
        assert result["black_count"] == 4
        assert result["white_count"] == 0
        assert result["black_density"] == 1.0

    def test_mixed(self, tmp_path):
        p = _make_pbm(tmp_path, 3, 2, [1, 0, 1, 0, 1, 0])
        result = image_pixel_stats(p)
        assert result["ok"] is True
        assert result["black_count"] == 3
        assert result["white_count"] == 3
        assert result["total_pixels"] == 6
        assert result["black_density"] == 0.5

    def test_single_pixel_black(self, tmp_path):
        p = _make_pbm(tmp_path, 1, 1, [1])
        result = image_pixel_stats(p)
        assert result["width"] == 1
        assert result["height"] == 1
        assert result["black_count"] == 1

    def test_single_pixel_white(self, tmp_path):
        p = _make_pbm(tmp_path, 1, 1, [0])
        result = image_pixel_stats(p)
        assert result["white_count"] == 1
        assert result["black_density"] == 0.0

    def test_has_magic(self, tmp_path):
        p = _make_pbm(tmp_path, 2, 1, [0, 1])
        result = image_pixel_stats(p)
        assert "magic" in result
        assert result["magic"] in ("P1", "P4")

    def test_dimensions_in_result(self, tmp_path):
        p = _make_pbm(tmp_path, 4, 3, [0] * 12)
        result = image_pixel_stats(p)
        assert result["width"] == 4
        assert result["height"] == 3

    def test_nonexistent_file(self, tmp_path):
        result = image_pixel_stats(tmp_path / "ghost.pbm")
        assert result.get("ok") is False or "error" in result
