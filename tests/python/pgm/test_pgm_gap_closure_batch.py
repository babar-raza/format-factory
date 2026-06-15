"""Gap closure tests for PGM — covering 18 open gaps.

Gaps: GAP-PGM-FOSS-PARSE_PGM-001, GAP-PGM-FOSS-PARSE_PGM_ST-001,
      GAP-PGM-FOSS-GET_CAPABILI-001, GAP-PGM-FOSS-IMAGE_PIXEL_-001,
      GAP-PGM-FOSS-WRITE_PGM-001, GAP-PGM-FOSS-GET_DIMENSIO-001,
      GAP-PGM-FOSS-AVERAGE_GRAY-001, GAP-PGM-FOSS-COUNT_ABOVE_-001,
      GAP-PGM-FOSS-MIN_MAX_GRAY-001, GAP-PGM-FOSS-FLIP_HORIZON-001,
      GAP-PGM-FOSS-ROTATE_90-001, GAP-PGM-FOSS-PGMERROR-001,
      GAP-PGM-FOSS-PGMINVALIDMA-001, GAP-PGM-FOSS-PGMINVALIDHE-001,
      GAP-PGM-FOSS-PGMSIZEERROR-001, GAP-PGM-FOSS-PGMDECODEERR-001,
      GAP-PGM-FOSS-PGMIMAGE-001, GAP-PGM-FOSS-PROBE_PGM-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pgm.pgm_parser import (
    PgmDecodeError,
    PgmError,
    PgmImage,
    PgmInvalidHeaderError,
    PgmInvalidMagicError,
    PgmSizeError,
    average_gray,
    count_above_threshold,
    flip_horizontal,
    get_capabilities,
    get_dimensions,
    image_pixel_stats,
    min_max_gray,
    parse_pgm,
    parse_pgm_strict,
    pixel_count,
    probe_pgm,
    rotate_90,
    write_pgm,
)


@pytest.fixture
def pgm_file(tmp_path):
    """2x2 PGM: gradient."""
    pixels = [0, 100, 200, 255]
    f = tmp_path / "grad.pgm"
    write_pgm(pixels, 2, 2, 255, str(f))
    return f


class TestPgmError:
    def test_is_exception(self):
        assert issubclass(PgmError, Exception)


class TestPgmInvalidMagicError:
    def test_subclass(self):
        assert issubclass(PgmInvalidMagicError, PgmError)


class TestPgmInvalidHeaderError:
    def test_subclass(self):
        assert issubclass(PgmInvalidHeaderError, PgmError)


class TestPgmSizeError:
    def test_subclass(self):
        assert issubclass(PgmSizeError, PgmError)


class TestPgmDecodeError:
    def test_subclass(self):
        assert issubclass(PgmDecodeError, PgmError)


class TestPgmImage:
    def test_has_fields(self):
        img = PgmImage()
        assert hasattr(img, "width")
        assert hasattr(img, "height")


class TestWritePgm:
    def test_creates_file(self, pgm_file):
        assert pgm_file.exists()
        content = pgm_file.read_text()
        assert content.startswith("P2")


class TestParsePgm:
    def test_returns_dict(self, pgm_file):
        result = parse_pgm(str(pgm_file))
        assert isinstance(result, dict)
        assert result.get("width") == 2


class TestParsePgmStrict:
    def test_returns_image(self, pgm_file):
        img = parse_pgm_strict(str(pgm_file))
        assert isinstance(img, PgmImage)
        assert img.width == 2
        assert img.height == 2


class TestProbePgm:
    def test_valid_file(self, pgm_file):
        result = probe_pgm(str(pgm_file))
        assert isinstance(result, dict)
        assert result.get("width") == 2

    def test_nonexistent(self, tmp_path):
        result = probe_pgm(str(tmp_path / "nope.pgm"))
        assert result.get("exists") is False


class TestGetCapabilities:
    def test_returns_dict(self):
        caps = get_capabilities()
        assert isinstance(caps, dict)


class TestImagePixelStats:
    def test_returns_dict(self, pgm_file):
        stats = image_pixel_stats(str(pgm_file))
        assert isinstance(stats, dict)
        assert stats.get("ok") is True


class TestGetDimensions:
    def test_dimensions(self, pgm_file):
        w, h = get_dimensions(str(pgm_file))
        assert w == 2
        assert h == 2


class TestPixelCount:
    def test_total(self, pgm_file):
        assert pixel_count(str(pgm_file)) == 4


class TestAverageGray:
    def test_average(self, pgm_file):
        avg = average_gray(str(pgm_file))
        # average of [0, 100, 200, 255] = 138.75
        assert 130 < avg < 145


class TestCountAboveThreshold:
    def test_above_128(self, pgm_file):
        count = count_above_threshold(str(pgm_file), 128)
        assert count == 2  # 200, 255


class TestMinMaxGray:
    def test_min_max(self, pgm_file):
        mn, mx = min_max_gray(str(pgm_file))
        assert mn == 0
        assert mx == 255


class TestFlipHorizontal:
    def test_flip(self, pgm_file, tmp_path):
        dest = tmp_path / "flipped.pgm"
        result = flip_horizontal(str(pgm_file), str(dest))
        assert dest.exists()


class TestRotate90:
    def test_rotate(self, pgm_file, tmp_path):
        dest = tmp_path / "rotated.pgm"
        result = rotate_90(str(pgm_file), str(dest))
        assert dest.exists()
        img = parse_pgm_strict(str(dest))
        assert img.width == 2  # swapped
        assert img.height == 2
