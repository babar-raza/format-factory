"""R84 Train M: Tests for PPM parser (P3 ASCII)."""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))
from ppm.ppm_parser import (
    parse_ppm, parse_ppm_strict, probe_ppm, get_capabilities,
    PpmError, PpmInvalidMagicError,
)

SAMPLES = os.path.join(os.path.dirname(__file__), "..", "..", "..", "samples", "by-format", "ppm")


class TestPpmParser:
    def test_parse_1x1_red(self):
        img = parse_ppm_strict(os.path.join(SAMPLES, "valid", "1x1-red.ppm"))
        assert img.width == 1
        assert img.height == 1
        assert img.magic == "P3"
        assert len(img.pixels) == 1
        r, g, b = img.pixels[0]
        assert r > 0  # red pixel has non-zero red channel

    def test_parse_2x2_rgbw(self):
        img = parse_ppm_strict(os.path.join(SAMPLES, "valid", "2x2-rgbw.ppm"))
        assert img.width == 2
        assert img.height == 2
        assert len(img.pixels) == 4

    def test_parse_3x1_gradient(self):
        img = parse_ppm_strict(os.path.join(SAMPLES, "valid", "3x1-gradient.ppm"))
        assert img.width == 3
        assert img.height == 1
        assert len(img.pixels) == 3

    def test_pixels_are_rgb_tuples(self):
        img = parse_ppm_strict(os.path.join(SAMPLES, "valid", "1x1-red.ppm"))
        for pixel in img.pixels:
            assert len(pixel) == 3
            r, g, b = pixel
            assert 0 <= r <= img.maxval
            assert 0 <= g <= img.maxval
            assert 0 <= b <= img.maxval

    def test_wrong_magic_raises_invalid_magic_error(self):
        with pytest.raises(PpmInvalidMagicError):
            parse_ppm_strict(os.path.join(SAMPLES, "invalid", "wrong-magic.ppm"))

    def test_missing_file_raises_ppm_error(self):
        with pytest.raises(PpmError):
            parse_ppm_strict("/nonexistent/path/file.ppm")

    def test_parse_ppm_never_raises(self):
        result = parse_ppm("/nonexistent/path/file.ppm")
        assert result["ok"] is False
        assert "error" in result

    def test_probe_ppm_returns_metadata(self):
        probe = probe_ppm(os.path.join(SAMPLES, "valid", "1x1-red.ppm"))
        assert probe["exists"] is True
        assert probe.get("valid_header") is True
        assert probe.get("magic") == "P3"

    def test_get_capabilities_format_is_ppm(self):
        caps = get_capabilities()
        assert caps["format"] == "ppm"
        assert "p3_ascii_parse" in caps["supported"]

    def test_maxval_in_image(self):
        img = parse_ppm_strict(os.path.join(SAMPLES, "valid", "1x1-red.ppm"))
        assert img.maxval > 0
