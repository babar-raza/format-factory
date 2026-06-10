"""
test_r161_ppm_invert_flipv.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT21-001
Added: 2026-06-10

Tests for PPM invert and flip_vertical functions.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm.ppm_parser import invert, flip_vertical, write_ppm, parse_ppm_strict, PpmError


class TestInvert:
    def test_invert_black_to_white(self, tmp_path):
        src = tmp_path / "src.ppm"
        write_ppm([(0, 0, 0)], 1, 1, 255, src)
        dest = tmp_path / "inv.ppm"
        result = invert(src, dest)
        assert result["ok"] is True
        img = parse_ppm_strict(dest)
        assert img.pixels == [(255, 255, 255)]

    def test_invert_white_to_black(self, tmp_path):
        src = tmp_path / "src.ppm"
        write_ppm([(255, 255, 255)], 1, 1, 255, src)
        dest = tmp_path / "inv.ppm"
        invert(src, dest)
        img = parse_ppm_strict(dest)
        assert img.pixels == [(0, 0, 0)]

    def test_invert_color(self, tmp_path):
        src = tmp_path / "src.ppm"
        write_ppm([(100, 150, 200)], 1, 1, 255, src)
        dest = tmp_path / "inv.ppm"
        invert(src, dest)
        img = parse_ppm_strict(dest)
        assert img.pixels == [(155, 105, 55)]

    def test_invert_preserves_dimensions(self, tmp_path):
        src = tmp_path / "src.ppm"
        write_ppm([(0, 0, 0)] * 6, 3, 2, 255, src)
        dest = tmp_path / "inv.ppm"
        result = invert(src, dest)
        assert result["width"] == 3
        assert result["height"] == 2

    def test_nonexistent_file(self, tmp_path):
        with pytest.raises(PpmError):
            invert(tmp_path / "ghost.ppm", tmp_path / "out.ppm")


class TestFlipVertical:
    def test_2x2(self, tmp_path):
        src = tmp_path / "src.ppm"
        pixels = [(1, 0, 0), (2, 0, 0), (3, 0, 0), (4, 0, 0)]
        write_ppm(pixels, 2, 2, 255, src)
        dest = tmp_path / "flipped.ppm"
        flip_vertical(src, dest)
        img = parse_ppm_strict(dest)
        assert img.pixels == [(3, 0, 0), (4, 0, 0), (1, 0, 0), (2, 0, 0)]

    def test_1x1(self, tmp_path):
        src = tmp_path / "src.ppm"
        write_ppm([(128, 128, 128)], 1, 1, 255, src)
        dest = tmp_path / "flipped.ppm"
        flip_vertical(src, dest)
        img = parse_ppm_strict(dest)
        assert img.pixels == [(128, 128, 128)]

    def test_3x1(self, tmp_path):
        src = tmp_path / "src.ppm"
        write_ppm([(1, 0, 0), (2, 0, 0), (3, 0, 0)], 3, 1, 255, src)
        dest = tmp_path / "flipped.ppm"
        flip_vertical(src, dest)
        img = parse_ppm_strict(dest)
        assert img.pixels == [(1, 0, 0), (2, 0, 0), (3, 0, 0)]

    def test_preserves_dimensions(self, tmp_path):
        src = tmp_path / "src.ppm"
        write_ppm([(0, 0, 0)] * 6, 3, 2, 255, src)
        dest = tmp_path / "flipped.ppm"
        result = flip_vertical(src, dest)
        assert result["width"] == 3
        assert result["height"] == 2

    def test_nonexistent_file(self, tmp_path):
        with pytest.raises(PpmError):
            flip_vertical(tmp_path / "ghost.ppm", tmp_path / "out.ppm")
