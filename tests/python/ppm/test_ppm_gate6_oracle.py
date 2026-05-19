"""Gate 6 deterministic oracle tests for PPM parser.

Oracle strategy: Build PPM files from known pixel data,
decode them, and compare pixel arrays against expected values.
No external tool dependency.
"""

import sys
import tempfile
from pathlib import Path

_src = Path(__file__).resolve().parents[3] / "src" / "python"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from ppm.ppm_parser import parse_ppm, parse_ppm_strict

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "ppm"


def _make_ppm(width, height, maxval, pixels_text) -> Path:
    content = f"P3\n{width} {height}\n{maxval}\n{pixels_text}\n"
    tmp = tempfile.NamedTemporaryFile(suffix=".ppm", delete=False, mode="w",
                                      encoding="ascii")
    tmp.write(content)
    tmp.close()
    return Path(tmp.name)


class TestPpmOracleKnownValues:
    """Deterministic oracle: compare decoded pixels against expected values."""

    def test_known_1x1_red_oracle(self):
        """Oracle: 1x1-red.ppm decodes to exactly (255, 0, 0)."""
        img = parse_ppm_strict(SAMPLES / "valid" / "1x1-red.ppm")
        assert img.pixels[0] == (255, 0, 0)

    def test_known_2x2_rgbw_oracle(self):
        """Oracle: 2x2-rgbw.ppm decodes to R, G, B, W pixels."""
        img = parse_ppm_strict(SAMPLES / "valid" / "2x2-rgbw.ppm")
        assert len(img.pixels) == 4
        assert img.pixels[0] == (255, 0, 0)
        assert img.pixels[1] == (0, 255, 0)
        assert img.pixels[2] == (0, 0, 255)
        assert img.pixels[3] == (255, 255, 255)

    def test_known_3x1_gradient_oracle(self):
        """Oracle: 3x1-gradient.ppm has 3 pixels."""
        img = parse_ppm_strict(SAMPLES / "valid" / "3x1-gradient.ppm")
        assert len(img.pixels) == 3
        assert img.pixels[0] == (0, 0, 0)
        assert img.pixels[1] == (128, 128, 128)
        assert img.pixels[2] == (255, 255, 255)

    def test_synthetic_single_white_pixel_oracle(self):
        """Oracle: synthetic 1x1 white pixel."""
        path = _make_ppm(1, 1, 255, "255 255 255")
        img = parse_ppm_strict(path)
        assert img.pixels[0] == (255, 255, 255)

    def test_synthetic_2x2_uniform_oracle(self):
        """Oracle: 2x2 all same color."""
        path = _make_ppm(2, 2, 255, "100 200 50 100 200 50 100 200 50 100 200 50")
        img = parse_ppm_strict(path)
        assert len(img.pixels) == 4
        for px in img.pixels:
            assert px == (100, 200, 50)

    def test_synthetic_3x2_oracle(self):
        """Oracle: 3x2 grid with known pixel values."""
        pixels = "0 0 0 255 0 0 0 255 0 0 0 255 255 255 0 255 0 255"
        path = _make_ppm(3, 2, 255, pixels)
        img = parse_ppm_strict(path)
        assert len(img.pixels) == 6
        assert img.pixels[0] == (0, 0, 0)
        assert img.pixels[1] == (255, 0, 0)
        assert img.pixels[2] == (0, 255, 0)
        assert img.pixels[3] == (0, 0, 255)
        assert img.pixels[4] == (255, 255, 0)
        assert img.pixels[5] == (255, 0, 255)

    def test_synthetic_low_maxval_oracle(self):
        """Oracle: PPM with maxval=15 parses correctly."""
        path = _make_ppm(1, 1, 15, "15 0 8")
        img = parse_ppm_strict(path)
        assert img.maxval == 15
        assert img.pixels[0] == (15, 0, 8)

    def test_synthetic_comment_handling_oracle(self):
        """Oracle: comments in PPM are stripped correctly."""
        content = "P3\n# This is a comment\n1 1\n255\n# Another comment\n128 64 32\n"
        tmp = tempfile.NamedTemporaryFile(suffix=".ppm", delete=False, mode="w",
                                          encoding="ascii")
        tmp.write(content)
        tmp.close()
        img = parse_ppm_strict(tmp.name)
        assert img.pixels[0] == (128, 64, 32)

    def test_dict_api_oracle(self):
        """Oracle: parse_ppm dict API returns correct structure."""
        result = parse_ppm(SAMPLES / "valid" / "1x1-red.ppm")
        assert result["ok"] is True
        assert result["width"] == 1
        assert result["height"] == 1
        assert result["maxval"] == 255
        assert result["pixel_count"] == 1

    def test_probe_matches_parse_oracle(self):
        """Oracle: probe and parse return consistent values."""
        from ppm.ppm_parser import probe_ppm
        img = parse_ppm_strict(SAMPLES / "valid" / "2x2-rgbw.ppm")
        probe = probe_ppm(SAMPLES / "valid" / "2x2-rgbw.ppm")
        assert probe["width"] == img.width == 2
        assert probe["height"] == img.height == 2
