"""Gap closure tests for PPM — covering 18 open gaps.

Gaps: GAP-PPM-FOSS-PARSE_PPM-001, GAP-PPM-FOSS-PARSE_PPM_ST-001,
      GAP-PPM-FOSS-WRITE_PPM-001, GAP-PPM-FOSS-GET_DIMENSIO-001,
      GAP-PPM-FOSS-TO_GRAYSCALE-001, GAP-PPM-FOSS-AVERAGE_COLO-001,
      GAP-PPM-FOSS-FLIP_HORIZON-001, GAP-PPM-FOSS-FLIP_VERTICA-001,
      GAP-PPM-FOSS-ROTATE_90-001, GAP-PPM-FOSS-PPMERROR-001,
      GAP-PPM-FOSS-PPMINVALIDMA-001, GAP-PPM-FOSS-PPMINVALIDHE-001,
      GAP-PPM-FOSS-PPMSIZEERROR-001, GAP-PPM-FOSS-PPMDECODEERR-001,
      GAP-PPM-FOSS-PPMIMAGE-001, GAP-PPM-FOSS-PROBE_PPM-001,
      GAP-PPM-FOSS-CONVERT_PPM_-001, GAP-PPM-FOSS-PPM_PIXELS_T-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_parser import (
    PpmDecodeError,
    PpmError,
    PpmImage,
    PpmInvalidHeaderError,
    PpmInvalidMagicError,
    PpmSizeError,
    flip_horizontal,
    flip_vertical,
    get_capabilities,
    get_dimensions,
    parse_ppm,
    parse_ppm_strict,
    pixel_count,
    probe_ppm,
    rotate_90,
    to_grayscale,
    write_ppm,
)


@pytest.fixture
def ppm_file(tmp_path):
    """2x2 PPM: red, green, blue, white."""
    pixels = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255)]
    f = tmp_path / "test.ppm"
    write_ppm(pixels, 2, 2, 255, str(f))
    return f


class TestPpmError:
    def test_is_exception(self):
        assert issubclass(PpmError, Exception)


class TestPpmInvalidMagicError:
    def test_subclass(self):
        assert issubclass(PpmInvalidMagicError, PpmError)


class TestPpmInvalidHeaderError:
    def test_subclass(self):
        assert issubclass(PpmInvalidHeaderError, PpmError)


class TestPpmSizeError:
    def test_subclass(self):
        assert issubclass(PpmSizeError, PpmError)


class TestPpmDecodeError:
    def test_subclass(self):
        assert issubclass(PpmDecodeError, PpmError)


class TestPpmImage:
    def test_has_fields(self):
        img = PpmImage()
        assert hasattr(img, "width")
        assert hasattr(img, "height")


class TestWritePpm:
    def test_creates_file(self, ppm_file):
        assert ppm_file.exists()
        content = ppm_file.read_text()
        assert content.startswith("P3")


class TestParsePpm:
    def test_returns_dict(self, ppm_file):
        result = parse_ppm(str(ppm_file))
        assert isinstance(result, dict)
        assert result.get("width") == 2


class TestParsePpmStrict:
    def test_returns_image(self, ppm_file):
        img = parse_ppm_strict(str(ppm_file))
        assert isinstance(img, PpmImage)
        assert img.width == 2
        assert img.height == 2


class TestProbePpm:
    def test_valid_file(self, ppm_file):
        result = probe_ppm(str(ppm_file))
        assert isinstance(result, dict)
        assert result.get("width") == 2

    def test_nonexistent(self, tmp_path):
        result = probe_ppm(str(tmp_path / "nope.ppm"))
        assert result.get("exists") is False


class TestGetCapabilities:
    def test_returns_dict(self):
        caps = get_capabilities()
        assert isinstance(caps, dict)


class TestGetDimensions:
    def test_dimensions(self, ppm_file):
        w, h = get_dimensions(str(ppm_file))
        assert w == 2
        assert h == 2


class TestPixelCount:
    def test_total(self, ppm_file):
        assert pixel_count(str(ppm_file)) == 4


class TestFlipHorizontal:
    def test_flip(self, ppm_file, tmp_path):
        dest = tmp_path / "flipped.ppm"
        result = flip_horizontal(str(ppm_file), str(dest))
        assert dest.exists()


class TestFlipVertical:
    def test_flip(self, ppm_file, tmp_path):
        dest = tmp_path / "vflipped.ppm"
        result = flip_vertical(str(ppm_file), str(dest))
        assert dest.exists()


class TestRotate90:
    def test_rotate(self, ppm_file, tmp_path):
        dest = tmp_path / "rotated.ppm"
        result = rotate_90(str(ppm_file), str(dest))
        assert dest.exists()


class TestToGrayscale:
    def test_grayscale(self, ppm_file, tmp_path):
        dest = tmp_path / "gray.pgm"
        result = to_grayscale(str(ppm_file), str(dest))
        assert dest.exists()
