"""Sprint 94 — PPM/NDJSON/SYLK/DIF cycle 6: 8 new analytics functions."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_parser import ppm_warm_pixel_count, ppm_cool_pixel_count
from src.python.ndjson.ndjson_codec import ndjson_record_type_variance, ndjson_avg_record_depth
from src.python.sylk.sylk_parser import sylk_numeric_column_count, sylk_string_column_count
from src.python.dif.dif_parser import dif_max_column_sum, dif_min_column_sum

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
class TestPpmWarmPixelCount:
    def test_returns_int(self, ppm_sample):
        result = ppm_warm_pixel_count(ppm_sample)
        assert isinstance(result, int)

    def test_non_negative(self, ppm_sample):
        assert ppm_warm_pixel_count(ppm_sample) >= 0


class TestPpmCoolPixelCount:
    def test_returns_int(self, ppm_sample):
        result = ppm_cool_pixel_count(ppm_sample)
        assert isinstance(result, int)

    def test_non_negative(self, ppm_sample):
        assert ppm_cool_pixel_count(ppm_sample) >= 0


# --- NDJSON ---
class TestNdjsonRecordTypeVariance:
    def test_returns_float(self):
        result = ndjson_record_type_variance(_NDJSON_DATA)
        assert isinstance(result, float)

    def test_non_negative(self):
        assert ndjson_record_type_variance(_NDJSON_DATA) >= 0.0


class TestNdjsonAvgRecordDepth:
    def test_returns_float(self):
        result = ndjson_avg_record_depth(_NDJSON_DATA)
        assert isinstance(result, float)

    def test_non_negative(self):
        assert ndjson_avg_record_depth(_NDJSON_DATA) >= 0.0


# --- SYLK ---
class TestSylkNumericColumnCount:
    def test_returns_int(self, sylk_sample):
        result = sylk_numeric_column_count(sylk_sample)
        assert isinstance(result, int)

    def test_non_negative(self, sylk_sample):
        assert sylk_numeric_column_count(sylk_sample) >= 0


class TestSylkStringColumnCount:
    def test_returns_int(self, sylk_sample):
        result = sylk_string_column_count(sylk_sample)
        assert isinstance(result, int)

    def test_non_negative(self, sylk_sample):
        assert sylk_string_column_count(sylk_sample) >= 0


# --- DIF ---
class TestDifMaxColumnSum:
    def test_returns_float(self, dif_sample):
        result = dif_max_column_sum(dif_sample)
        assert isinstance(result, float)

    def test_non_negative(self, dif_sample):
        assert dif_max_column_sum(dif_sample) >= 0.0


class TestDifMinColumnSum:
    def test_returns_float(self, dif_sample):
        result = dif_min_column_sum(dif_sample)
        assert isinstance(result, float)

    def test_deterministic(self, dif_sample):
        assert dif_min_column_sum(dif_sample) == dif_min_column_sum(dif_sample)
