"""Gap closure tests for PBM — covering 20 open gaps.

Gaps: GAP-PBM-FOSS-PARSE_PBM-001, GAP-PBM-FOSS-PARSE_PBM_ST-001,
      GAP-PBM-FOSS-GET_CAPABILI-001, GAP-PBM-FOSS-IMAGE_PIXEL_-001,
      GAP-PBM-FOSS-WRITE_PBM-001, GAP-PBM-FOSS-GET_DIMENSIO-001,
      GAP-PBM-FOSS-COUNT_BLACK-001, GAP-PBM-FOSS-FLIP_HORIZON-001,
      GAP-PBM-FOSS-ROTATE_90-001, GAP-PBM-FOSS-PBMERROR-001,
      GAP-PBM-FOSS-PBMINVALIDMA-001, GAP-PBM-FOSS-PBMINVALIDHE-001,
      GAP-PBM-FOSS-PBMSIZEERROR-001, GAP-PBM-FOSS-PBMDECODEERR-001,
      GAP-PBM-FOSS-PBMIMAGE-001, GAP-PBM-FOSS-PROBE_PBM-001,
      GAP-Netpbm-FOSS-PARSE_PBM-001, GAP-Netpbm-FOSS-WRITE_PBM-001,
      GAP-Netpbm-FOSS-PIXEL_STATS_-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm.pbm_parser import (
    PbmDecodeError,
    PbmError,
    PbmImage,
    PbmInvalidHeaderError,
    PbmInvalidMagicError,
    PbmSizeError,
    count_black,
    flip_horizontal,
    get_capabilities,
    get_dimensions,
    image_pixel_stats,
    parse_pbm,
    parse_pbm_strict,
    pixel_count,
    probe_pbm,
    rotate_90,
    write_pbm,
)


@pytest.fixture
def pbm_file(tmp_path):
    """4x2 PBM: checkerboard pattern."""
    pixels = [1, 0, 1, 0, 0, 1, 0, 1]
    f = tmp_path / "check.pbm"
    write_pbm(pixels, 4, 2, str(f))
    return f


class TestPbmError:
    def test_is_exception(self):
        assert issubclass(PbmError, Exception)


class TestPbmInvalidMagicError:
    def test_subclass(self):
        assert issubclass(PbmInvalidMagicError, PbmError)


class TestPbmInvalidHeaderError:
    def test_subclass(self):
        assert issubclass(PbmInvalidHeaderError, PbmError)


class TestPbmSizeError:
    def test_subclass(self):
        assert issubclass(PbmSizeError, PbmError)


class TestPbmDecodeError:
    def test_subclass(self):
        assert issubclass(PbmDecodeError, PbmError)


class TestPbmImage:
    def test_has_fields(self):
        img = PbmImage()
        assert hasattr(img, "width")
        assert hasattr(img, "height")
        assert hasattr(img, "pixels")


class TestWritePbm:
    def test_creates_file(self, pbm_file):
        assert pbm_file.exists()
        content = pbm_file.read_text()
        assert content.startswith("P1")


class TestParsePbm:
    def test_returns_dict(self, pbm_file):
        result = parse_pbm(str(pbm_file))
        assert isinstance(result, dict)
        assert result.get("width") == 4
        assert result.get("height") == 2


class TestParsePbmStrict:
    def test_returns_image(self, pbm_file):
        img = parse_pbm_strict(str(pbm_file))
        assert isinstance(img, PbmImage)
        assert img.width == 4
        assert img.height == 2


class TestProbePbm:
    def test_valid_file(self, pbm_file):
        result = probe_pbm(str(pbm_file))
        assert isinstance(result, dict)
        assert result.get("width") == 4

    def test_nonexistent(self, tmp_path):
        result = probe_pbm(str(tmp_path / "nope.pbm"))
        assert result.get("exists") is False


class TestGetCapabilities:
    def test_returns_dict(self):
        caps = get_capabilities()
        assert isinstance(caps, dict)
        assert len(caps) > 0


class TestImagePixelStats:
    def test_returns_dict(self, pbm_file):
        stats = image_pixel_stats(str(pbm_file))
        assert isinstance(stats, dict)
        assert stats.get("ok") is True

    def test_has_counts(self, pbm_file):
        stats = image_pixel_stats(str(pbm_file))
        assert stats.get("black_count") == 4
        assert stats.get("white_count") == 4


class TestGetDimensions:
    def test_dimensions(self, pbm_file):
        w, h = get_dimensions(str(pbm_file))
        assert w == 4
        assert h == 2


class TestCountBlack:
    def test_checkerboard(self, pbm_file):
        count = count_black(str(pbm_file))
        assert count == 4


class TestPixelCount:
    def test_total(self, pbm_file):
        assert pixel_count(str(pbm_file)) == 8


class TestFlipHorizontal:
    def test_flip_creates_file(self, pbm_file, tmp_path):
        dest = tmp_path / "flipped.pbm"
        result = flip_horizontal(str(pbm_file), str(dest))
        assert dest.exists()
        assert isinstance(result, dict)


class TestRotate90:
    def test_rotate_creates_file(self, pbm_file, tmp_path):
        dest = tmp_path / "rotated.pbm"
        result = rotate_90(str(pbm_file), str(dest))
        assert dest.exists()
        img = parse_pbm_strict(str(dest))
        assert img.width == 2  # swapped
        assert img.height == 4
