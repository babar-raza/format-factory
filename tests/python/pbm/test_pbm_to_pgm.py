"""Tests for pbm_to_pgm dogfood export."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_PBM = _REPO / "samples" / "by-format" / "pbm" / "valid" / "2x2-checker.pbm"
from src.python.pbm.pbm_to_pgm import convert_pbm_to_pgm, pbm_pixels_to_pgm_pixels


class TestPbmToPgmBasic:
    def test_returns_dict(self, tmp_path):
        dest = tmp_path / "out.pgm"
        result = convert_pbm_to_pgm(MINIMAL_PBM, dest)
        assert isinstance(result, dict)

    def test_output_file_created(self, tmp_path):
        dest = tmp_path / "out.pgm"
        convert_pbm_to_pgm(MINIMAL_PBM, dest)
        assert dest.exists()

    def test_result_has_dimensions(self, tmp_path):
        dest = tmp_path / "out.pgm"
        result = convert_pbm_to_pgm(MINIMAL_PBM, dest)
        assert "width" in result and "height" in result

    def test_output_nonempty(self, tmp_path):
        dest = tmp_path / "out.pgm"
        convert_pbm_to_pgm(MINIMAL_PBM, dest)
        assert dest.stat().st_size > 0


class TestPbmPixelsToPgmPixels:
    def test_black_maps_to_zero(self):
        result = pbm_pixels_to_pgm_pixels([1], maxval=255)
        assert result == [0]

    def test_white_maps_to_maxval(self):
        result = pbm_pixels_to_pgm_pixels([0], maxval=255)
        assert result == [255]

    def test_length_preserved(self):
        pixels = [0, 1, 0, 1]
        result = pbm_pixels_to_pgm_pixels(pixels)
        assert len(result) == 4
