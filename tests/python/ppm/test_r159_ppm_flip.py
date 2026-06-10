"""
test_r159_ppm_flip.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT19-001
Added: 2026-06-10

Tests for PPM flip_horizontal function.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm.ppm_parser import flip_horizontal, write_ppm, parse_ppm_strict, PpmError


class TestFlipHorizontal:
    def test_2x1(self, tmp_path):
        src = tmp_path / "src.ppm"
        write_ppm([(255, 0, 0), (0, 0, 255)], 2, 1, 255, src)
        dest = tmp_path / "flipped.ppm"
        result = flip_horizontal(src, dest)
        assert result["ok"] is True
        img = parse_ppm_strict(dest)
        assert img.pixels == [(0, 0, 255), (255, 0, 0)]

    def test_1x1(self, tmp_path):
        src = tmp_path / "src.ppm"
        write_ppm([(128, 128, 128)], 1, 1, 255, src)
        dest = tmp_path / "flipped.ppm"
        flip_horizontal(src, dest)
        img = parse_ppm_strict(dest)
        assert img.pixels == [(128, 128, 128)]

    def test_2x2(self, tmp_path):
        src = tmp_path / "src.ppm"
        pixels = [(1, 0, 0), (2, 0, 0), (3, 0, 0), (4, 0, 0)]
        write_ppm(pixels, 2, 2, 255, src)
        dest = tmp_path / "flipped.ppm"
        flip_horizontal(src, dest)
        img = parse_ppm_strict(dest)
        assert img.pixels == [(2, 0, 0), (1, 0, 0), (4, 0, 0), (3, 0, 0)]

    def test_preserves_dimensions(self, tmp_path):
        src = tmp_path / "src.ppm"
        write_ppm([(0, 0, 0)] * 6, 3, 2, 255, src)
        dest = tmp_path / "flipped.ppm"
        result = flip_horizontal(src, dest)
        assert result["width"] == 3
        assert result["height"] == 2

    def test_nonexistent_file(self, tmp_path):
        with pytest.raises(PpmError):
            flip_horizontal(tmp_path / "ghost.ppm", tmp_path / "out.ppm")
