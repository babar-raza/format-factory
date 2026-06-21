"""Sprint 98 — PPM/NDJSON/SYLK/DIF cycle 7: 8 new analytics functions."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_parser import ppm_grayscale_pixel_count, ppm_neutral_pixel_count
from src.python.ndjson.ndjson_codec import ndjson_max_key_count, ndjson_empty_string_count
from src.python.sylk.sylk_parser import sylk_row_density_variance, sylk_max_row_sum
from src.python.dif.dif_parser import dif_row_width_variance, dif_distinct_numeric_count

_PPM = _REPO / "samples" / "by-format" / "ppm" / "valid"
_SYLK = _REPO / "samples" / "by-format" / "sylk" / "valid"
_DIF = _REPO / "samples" / "by-format" / "dif" / "valid"

_NDJSON_DATA = b'{"a":1,"b":"x"}\n{"a":2,"b":"y","c":true}\n'


@pytest.fixture
def ppm_sample():
    return next(_PPM.glob("*.ppm"))


@pytest.fixture
def sylk_sample():
    return next(_SYLK.glob("*.slk"))


@pytest.fixture
def dif_sample():
    return next(_DIF.glob("*.dif"))


# --- PPM ---

class TestPpmGrayscalePixelCount:
    def test_returns_int(self, ppm_sample):
        assert isinstance(ppm_grayscale_pixel_count(ppm_sample), int)

    def test_non_negative(self, ppm_sample):
        assert ppm_grayscale_pixel_count(ppm_sample) >= 0


class TestPpmNeutralPixelCount:
    def test_returns_int(self, ppm_sample):
        assert isinstance(ppm_neutral_pixel_count(ppm_sample), int)

    def test_non_negative(self, ppm_sample):
        assert ppm_neutral_pixel_count(ppm_sample) >= 0


# --- NDJSON ---

class TestNdjsonMaxKeyCount:
    def test_returns_int(self):
        assert isinstance(ndjson_max_key_count(_NDJSON_DATA), int)

    def test_correct_value(self):
        assert ndjson_max_key_count(_NDJSON_DATA) == 3

    def test_empty(self):
        assert ndjson_max_key_count(b"") == 0


class TestNdjsonEmptyStringCount:
    def test_returns_int(self):
        assert isinstance(ndjson_empty_string_count(_NDJSON_DATA), int)

    def test_no_empty_strings(self):
        assert ndjson_empty_string_count(_NDJSON_DATA) == 0

    def test_with_empty_strings(self):
        data = b'{"a":"","b":"x"}\n'
        assert ndjson_empty_string_count(data) == 1


# --- SYLK ---

class TestSylkRowDensityVariance:
    def test_returns_float(self, sylk_sample):
        assert isinstance(sylk_row_density_variance(sylk_sample), (int, float))

    def test_non_negative(self, sylk_sample):
        assert sylk_row_density_variance(sylk_sample) >= 0.0


class TestSylkMaxRowSum:
    def test_returns_float(self, sylk_sample):
        assert isinstance(sylk_max_row_sum(sylk_sample), (int, float))


# --- DIF ---

class TestDifRowWidthVariance:
    def test_returns_float(self, dif_sample):
        assert isinstance(dif_row_width_variance(dif_sample), (int, float))

    def test_non_negative(self, dif_sample):
        assert dif_row_width_variance(dif_sample) >= 0.0


class TestDifDistinctNumericCount:
    def test_returns_int(self, dif_sample):
        assert isinstance(dif_distinct_numeric_count(dif_sample), int)

    def test_non_negative(self, dif_sample):
        assert dif_distinct_numeric_count(dif_sample) >= 0
