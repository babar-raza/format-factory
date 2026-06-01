"""
test_r87_ppm_hardening.py — PPM writer edge-case hardening tests.

Sprint: FORMAT-FACTORY-R87-CLEAN-SUPERVISOR-CLOSEOUT-REVIEW-PACKAGE-POC-PRODUCT-FACTORY-DEEPENING-MEGA-TRAIN-001
Train L: Python Netpbm FOSS advancement — PPM writer hardening
"""

import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

from ppm.ppm_parser import write_ppm, parse_ppm_strict


class TestWritePpmEdgeCases:
    """Train L: PPM writer edge-case hardening."""

    def test_maxval_1_binary_image(self):
        """Write PPM with maxval=1 (binary-like color image)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "binary.ppm"
            pixels = [(0, 0, 0), (1, 1, 1)]
            write_ppm(pixels, 2, 1, 1, path)
            img = parse_ppm_strict(path)
            assert img.maxval == 1
            assert img.pixels[0] == (0, 0, 0)
            assert img.pixels[1] == (1, 1, 1)

    def test_large_image_10x10(self):
        """Write and read back a 10x10 gradient image."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "gradient.ppm"
            pixels = [(i, i, i) for i in range(100)]
            write_ppm(pixels, 10, 10, 255, path)
            img = parse_ppm_strict(path)
            assert img.width == 10
            assert img.height == 10
            assert len(img.pixels) == 100
            assert img.pixels[50] == (50, 50, 50)

    def test_rgb_distinct_channels(self):
        """Write PPM with distinct R, G, B values and verify roundtrip."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "rgb.ppm"
            pixels = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
            write_ppm(pixels, 3, 1, 255, path)
            img = parse_ppm_strict(path)
            assert img.pixels[0] == (255, 0, 0)
            assert img.pixels[1] == (0, 255, 0)
            assert img.pixels[2] == (0, 0, 255)

    def test_comment_preserved_in_file(self):
        """Comment should appear in the PPM file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "commented.ppm"
            write_ppm([(128, 64, 32)], 1, 1, 255, path, comment="R87 test comment")
            content = path.read_text(encoding="ascii")
            assert "R87 test comment" in content

    def test_empty_comment_allowed(self):
        """Empty comment should not cause errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nocomment.ppm"
            write_ppm([(0, 0, 0)], 1, 1, 255, path, comment="")
            img = parse_ppm_strict(path)
            assert img.pixels == [(0, 0, 0)]

    def test_maxval_boundary_255(self):
        """All channels at maxval=255."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "max.ppm"
            write_ppm([(255, 255, 255)], 1, 1, 255, path)
            img = parse_ppm_strict(path)
            assert img.pixels[0] == (255, 255, 255)

    def test_negative_dimension_raises(self):
        """Negative dimensions should raise ValueError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "bad.ppm"
            with pytest.raises(ValueError):
                write_ppm([(0, 0, 0)], -1, 1, 255, path)

    def test_pixel_value_exceeds_maxval_raises(self):
        """Pixel values exceeding maxval should raise ValueError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "bad2.ppm"
            with pytest.raises(ValueError):
                write_ppm([(300, 0, 0)], 1, 1, 255, path)
