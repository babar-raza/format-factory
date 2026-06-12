"""Gate 4 prototype tests for PPM parser."""

import sys
import tempfile
from pathlib import Path

_src = Path(__file__).resolve().parents[3] / "src" / "python"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

import pytest
from ppm.ppm_parser import (
    PpmImage,
    PpmInvalidMagicError,
    parse_ppm,
    parse_ppm_strict,
    probe_ppm,
)

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "ppm"


class TestPpmParserValidSamples:
    """Parse tests against valid PPM samples."""

    def test_1x1_red(self):
        img = parse_ppm_strict(SAMPLES / "valid" / "1x1-red.ppm")
        assert isinstance(img, PpmImage)
        assert img.width == 1
        assert img.height == 1
        assert img.pixels[0] == (255, 0, 0)

    def test_2x2_rgbw(self):
        img = parse_ppm_strict(SAMPLES / "valid" / "2x2-rgbw.ppm")
        assert img.width == 2
        assert img.height == 2
        assert len(img.pixels) == 4
        assert img.pixels[0] == (255, 0, 0)    # red
        assert img.pixels[1] == (0, 255, 0)    # green
        assert img.pixels[2] == (0, 0, 255)    # blue
        assert img.pixels[3] == (255, 255, 255) # white

    def test_3x1_gradient(self):
        img = parse_ppm_strict(SAMPLES / "valid" / "3x1-gradient.ppm")
        assert img.width == 3
        assert img.height == 1
        assert len(img.pixels) == 3


class TestPpmParserInvalid:
    """Tests for invalid inputs."""

    def test_wrong_magic(self):
        with pytest.raises(PpmInvalidMagicError):
            parse_ppm_strict(SAMPLES / "invalid" / "wrong-magic.ppm")

    def test_nonexistent_file(self):
        result = parse_ppm("/nonexistent/file.ppm")
        assert result["ok"] is False

    def test_empty_file(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".ppm", delete=False)
        tmp.close()
        with pytest.raises(PpmInvalidMagicError):
            parse_ppm_strict(tmp.name)


class TestPpmDictOutput:
    """Tests for dict output structure."""

    def test_dict_has_expected_keys(self):
        result = parse_ppm(SAMPLES / "valid" / "1x1-red.ppm")
        assert result["ok"] is True
        assert "width" in result
        assert "height" in result
        assert "maxval" in result
        assert "pixel_count" in result

    def test_error_dict_has_expected_keys(self):
        result = parse_ppm("/nonexistent_path_that_does_not_exist_anywhere")
        assert result["ok"] is False
        assert "error" in result


class TestPpmProbe:
    """Tests for probe_ppm."""

    def test_probe_valid(self):
        result = probe_ppm(SAMPLES / "valid" / "1x1-red.ppm")
        assert result["valid_header"] is True
        assert result["width"] == 1
        assert result["height"] == 1
        assert result["magic"] == "P3"

    def test_probe_nonexistent(self):
        result = probe_ppm("/nonexistent_path_that_does_not_exist_anywhere")
        assert result["exists"] is False
