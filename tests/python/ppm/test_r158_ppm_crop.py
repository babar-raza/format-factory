"""
test_r158_ppm_crop.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT18-001
Added: 2026-06-10

Tests for PPM crop function.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm.ppm_parser import crop, write_ppm, parse_ppm_strict, PpmError


def _make_ppm(tmp_path: Path, pixels, w, h) -> Path:
    p = tmp_path / "source.ppm"
    write_ppm(pixels, w, h, 255, p)
    return p


class TestCrop:
    def test_full_crop(self, tmp_path):
        pixels = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        src = _make_ppm(tmp_path, pixels, 2, 2)
        dest = tmp_path / "cropped.ppm"
        result = crop(src, dest, 0, 0, 2, 2)
        assert result["ok"] is True
        assert result["width"] == 2
        assert result["height"] == 2
        assert result["pixel_count"] == 4

    def test_partial_crop(self, tmp_path):
        pixels = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        src = _make_ppm(tmp_path, pixels, 2, 2)
        dest = tmp_path / "cropped.ppm"
        result = crop(src, dest, 0, 0, 1, 1)
        assert result["pixel_count"] == 1
        img = parse_ppm_strict(dest)
        assert img.pixels[0] == (255, 0, 0)

    def test_crop_corner(self, tmp_path):
        pixels = [(1, 1, 1), (2, 2, 2), (3, 3, 3), (4, 4, 4)]
        src = _make_ppm(tmp_path, pixels, 2, 2)
        dest = tmp_path / "cropped.ppm"
        result = crop(src, dest, 1, 1, 1, 1)
        assert result["pixel_count"] == 1
        img = parse_ppm_strict(dest)
        assert img.pixels[0] == (4, 4, 4)

    def test_out_of_bounds(self, tmp_path):
        pixels = [(255, 0, 0)]
        src = _make_ppm(tmp_path, pixels, 1, 1)
        dest = tmp_path / "cropped.ppm"
        with pytest.raises(ValueError):
            crop(src, dest, 0, 0, 2, 1)

    def test_invalid_region(self, tmp_path):
        pixels = [(255, 0, 0)]
        src = _make_ppm(tmp_path, pixels, 1, 1)
        dest = tmp_path / "cropped.ppm"
        with pytest.raises(ValueError):
            crop(src, dest, -1, 0, 1, 1)

    def test_nonexistent_file(self, tmp_path):
        with pytest.raises(PpmError):
            crop(tmp_path / "ghost.ppm", tmp_path / "out.ppm", 0, 0, 1, 1)
