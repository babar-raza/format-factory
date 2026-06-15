"""
test_rnext_ppm_flip_horizontal.py -- Dedicated test coverage for flip_horizontal.

Gap: GAP-PPM-FOSS-FLIP_HORIZON-001 (missing_test_coverage)
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm.ppm_parser import write_ppm, parse_ppm_strict, flip_horizontal


def _create_ppm(tmp_path, pixels, width, height, maxval=255, name="test.ppm"):
    path = tmp_path / name
    write_ppm(pixels, width, height, maxval, str(path))
    return path


class TestFlipHorizontalBasic:
    def test_returns_dict(self, tmp_path):
        pixels = [(255, 0, 0), (0, 255, 0)]
        src = _create_ppm(tmp_path, pixels, 2, 1)
        dest = tmp_path / "flipped.ppm"
        result = flip_horizontal(str(src), str(dest))
        assert isinstance(result, dict)
        assert result["ok"] is True

    def test_creates_output_file(self, tmp_path):
        pixels = [(255, 0, 0), (0, 255, 0)]
        src = _create_ppm(tmp_path, pixels, 2, 1)
        dest = tmp_path / "flipped.ppm"
        flip_horizontal(str(src), str(dest))
        assert dest.exists()

    def test_dimensions_preserved(self, tmp_path):
        pixels = [(1, 2, 3)] * 6
        src = _create_ppm(tmp_path, pixels, 3, 2)
        dest = tmp_path / "flipped.ppm"
        result = flip_horizontal(str(src), str(dest))
        assert result["width"] == 3
        assert result["height"] == 2

    def test_pixel_count_preserved(self, tmp_path):
        pixels = [(1, 2, 3)] * 4
        src = _create_ppm(tmp_path, pixels, 2, 2)
        dest = tmp_path / "flipped.ppm"
        result = flip_horizontal(str(src), str(dest))
        assert result["pixel_count"] == 4

    def test_single_row_flipped(self, tmp_path):
        pixels = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        src = _create_ppm(tmp_path, pixels, 3, 1)
        dest = tmp_path / "flipped.ppm"
        flip_horizontal(str(src), str(dest))
        img = parse_ppm_strict(str(dest))
        assert img.pixels[0] == (0, 0, 255)
        assert img.pixels[2] == (255, 0, 0)

    def test_double_flip_restores(self, tmp_path):
        pixels = [(10, 20, 30), (40, 50, 60), (70, 80, 90), (100, 110, 120)]
        src = _create_ppm(tmp_path, pixels, 2, 2)
        mid = tmp_path / "mid.ppm"
        final = tmp_path / "final.ppm"
        flip_horizontal(str(src), str(mid))
        flip_horizontal(str(mid), str(final))
        original = parse_ppm_strict(str(src))
        restored = parse_ppm_strict(str(final))
        assert original.pixels == restored.pixels

    def test_1x1_image_unchanged(self, tmp_path):
        pixels = [(128, 64, 32)]
        src = _create_ppm(tmp_path, pixels, 1, 1)
        dest = tmp_path / "flipped.ppm"
        flip_horizontal(str(src), str(dest))
        img = parse_ppm_strict(str(dest))
        assert img.pixels[0] == (128, 64, 32)
