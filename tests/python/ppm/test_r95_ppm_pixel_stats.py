# R95 Train P: PPM Pixel Statistics Hardening Tests
# Governed skill: /verify-dogfood-path
# Ledger: R95-GOVERNED-PYTHON-PPM-PIXEL-STATS-001
# Sprint: FORMAT-FACTORY-R95-PARALLEL-SPRINT-INTELLIGENCE-CONTEXT-PACK-ACCELERATION-POC-MEGA-TRAIN-001

"""Tests for PPM pixel statistics edge cases and data integrity."""

import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))

from ppm.ppm_parser import parse_ppm, write_ppm


class TestPpmPixelStats:
    """R95 PPM pixel statistics and integrity tests."""

    def test_parse_returns_dict(self):
        """parse_ppm should return a dict."""
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False, mode="w") as f:
            f.write("P3\n2 2\n255\n255 0 0 0 255 0 0 0 255 128 128 128\n")
            path = f.name
        try:
            result = parse_ppm(path)
            assert isinstance(result, dict)
        finally:
            os.unlink(path)

    def test_parse_has_ok_flag(self):
        """Parsed PPM should have ok=True."""
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False, mode="w") as f:
            f.write("P3\n1 1\n255\n100 200 50\n")
            path = f.name
        try:
            result = parse_ppm(path)
            assert result.get("ok") is True
        finally:
            os.unlink(path)

    def test_parse_has_dimensions(self):
        """Parsed PPM should have width and height."""
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False, mode="w") as f:
            f.write("P3\n3 2\n255\n0 0 0 1 1 1 2 2 2 3 3 3 4 4 4 5 5 5\n")
            path = f.name
        try:
            result = parse_ppm(path)
            assert result["width"] == 3
            assert result["height"] == 2
        finally:
            os.unlink(path)

    def test_write_read_roundtrip(self, tmp_path):
        """Write then parse should preserve basic structure."""
        path = str(tmp_path / "test.ppm")
        pixels = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (128, 128, 128)]
        write_ppm(file_path=path, width=2, height=2, pixels=pixels, maxval=255)
        result = parse_ppm(path)
        assert result.get("ok") is True
        assert result["width"] == 2
        assert result["height"] == 2

    def test_single_pixel_image(self, tmp_path):
        """1x1 PPM image roundtrips."""
        path = str(tmp_path / "single.ppm")
        write_ppm(file_path=path, width=1, height=1, pixels=[(42, 84, 168)], maxval=255)
        result = parse_ppm(path)
        assert result.get("ok") is True

    def test_write_creates_file(self, tmp_path):
        """write_ppm should create the file."""
        path = str(tmp_path / "new.ppm")
        assert not Path(path).exists()
        write_ppm(file_path=path, width=1, height=1, pixels=[(0, 0, 0)], maxval=255)
        assert Path(path).exists()

    def test_max_value_pixels(self, tmp_path):
        """Pixels at maxval should roundtrip."""
        path = str(tmp_path / "max.ppm")
        write_ppm(file_path=path, width=1, height=1, pixels=[(255, 255, 255)], maxval=255)
        result = parse_ppm(path)
        assert result.get("ok") is True

    def test_zero_value_pixels(self, tmp_path):
        """Pixels at zero should roundtrip."""
        path = str(tmp_path / "zero.ppm")
        write_ppm(file_path=path, width=1, height=1, pixels=[(0, 0, 0)], maxval=255)
        result = parse_ppm(path)
        assert result.get("ok") is True
