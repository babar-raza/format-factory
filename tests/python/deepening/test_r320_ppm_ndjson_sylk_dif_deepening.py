"""Sprint 90 — PPM/NDJSON/SYLK/DIF cycle 5: 8 new analytics functions."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_parser import ppm_luminance_sum, ppm_dark_pixel_ratio
from src.python.ndjson.ndjson_codec import ndjson_total_keys, ndjson_deepest_nesting
from src.python.sylk.sylk_parser import sylk_avg_cell_length_per_row, sylk_max_value_count
from src.python.dif.dif_parser import dif_column_fill_ratio, dif_avg_row_cell_count

_PPM = _REPO / "samples" / "by-format" / "ppm" / "valid"
_SYLK = _REPO / "samples" / "by-format" / "sylk" / "valid"
_DIF = _REPO / "samples" / "by-format" / "dif" / "valid"
_NDJSON_DATA = b'{"name":"alice","age":30,"tags":["a","b"]}\n{"name":"bob","age":25,"meta":{"x":1}}\n'


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
class TestPpmLuminanceSum:
    def test_returns_float(self, ppm_sample):
        result = ppm_luminance_sum(ppm_sample)
        assert isinstance(result, float)

    def test_non_negative(self, ppm_sample):
        assert ppm_luminance_sum(ppm_sample) >= 0.0


class TestPpmDarkPixelRatio:
    def test_returns_float(self, ppm_sample):
        result = ppm_dark_pixel_ratio(ppm_sample)
        assert isinstance(result, float)

    def test_between_zero_and_one(self, ppm_sample):
        result = ppm_dark_pixel_ratio(ppm_sample)
        assert 0.0 <= result <= 1.0


# --- NDJSON ---
class TestNdjsonTotalKeys:
    def test_returns_int(self):
        result = ndjson_total_keys(_NDJSON_DATA)
        assert isinstance(result, int)

    def test_positive(self):
        assert ndjson_total_keys(_NDJSON_DATA) > 0


class TestNdjsonDeepestNesting:
    def test_returns_int(self):
        result = ndjson_deepest_nesting(_NDJSON_DATA)
        assert isinstance(result, int)

    def test_positive(self):
        assert ndjson_deepest_nesting(_NDJSON_DATA) > 0


# --- SYLK ---
class TestSylkAvgCellLengthPerRow:
    def test_returns_float(self, sylk_sample):
        result = sylk_avg_cell_length_per_row(sylk_sample)
        assert isinstance(result, float)

    def test_non_negative(self, sylk_sample):
        assert sylk_avg_cell_length_per_row(sylk_sample) >= 0.0


class TestSylkMaxValueCount:
    def test_returns_int(self, sylk_sample):
        result = sylk_max_value_count(sylk_sample)
        assert isinstance(result, int)

    def test_positive(self, sylk_sample):
        assert sylk_max_value_count(sylk_sample) > 0


# --- DIF ---
class TestDifColumnFillRatio:
    def test_returns_float(self, dif_sample):
        result = dif_column_fill_ratio(dif_sample)
        assert isinstance(result, float)

    def test_non_negative(self, dif_sample):
        result = dif_column_fill_ratio(dif_sample)
        assert result >= 0.0


class TestDifAvgRowCellCount:
    def test_returns_float(self, dif_sample):
        result = dif_avg_row_cell_count(dif_sample)
        assert isinstance(result, float)

    def test_non_negative(self, dif_sample):
        assert dif_avg_row_cell_count(dif_sample) >= 0.0
