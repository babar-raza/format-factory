"""Sprint 78 — PPM/NDJSON/SYLK/DIF product deepening cycle 2."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm import ppm_red_ratio, ppm_border_brightness
from src.python.ndjson import ndjson_boolean_density, ndjson_max_field_value_length
from src.python.sylk import sylk_numeric_variance, sylk_max_row_cell_count
from src.python.dif import dif_avg_cell_length_variance, dif_column_density

_PPM = _REPO / "samples" / "by-format" / "ppm" / "valid" / "2x2-rgbw.ppm"
_NDJSON_BYTES = b'{"name":"alice","age":30,"active":true}\n{"name":"bob","age":25,"active":false}\n'
_SYLK = _REPO / "samples" / "by-format" / "sylk" / "valid"
_DIF = _REPO / "samples" / "by-format" / "dif" / "valid" / "minimal-2x2.dif"


def _sylk_sample():
    candidates = list(_SYLK.glob("*.slk"))
    assert candidates, "No .slk sample found"
    return candidates[0]


class TestPpmRedRatio:
    def test_returns_float(self):
        result = ppm_red_ratio(_PPM)
        assert isinstance(result, float)

    def test_between_zero_and_one(self):
        result = ppm_red_ratio(_PPM)
        assert 0.0 <= result <= 1.0


class TestPpmBorderBrightness:
    def test_returns_float(self):
        result = ppm_border_brightness(_PPM)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = ppm_border_brightness(_PPM)
        assert result >= 0.0


class TestNdjsonBooleanDensity:
    def test_returns_float(self):
        result = ndjson_boolean_density(_NDJSON_BYTES)
        assert isinstance(result, float)

    def test_between_zero_and_one(self):
        result = ndjson_boolean_density(_NDJSON_BYTES)
        assert 0.0 <= result <= 1.0


class TestNdjsonMaxFieldValueLength:
    def test_returns_int(self):
        result = ndjson_max_field_value_length(_NDJSON_BYTES)
        assert isinstance(result, int)

    def test_positive(self):
        result = ndjson_max_field_value_length(_NDJSON_BYTES)
        assert result > 0


class TestSylkNumericVariance:
    def test_returns_float(self):
        result = sylk_numeric_variance(_sylk_sample())
        assert isinstance(result, float)

    def test_non_negative(self):
        result = sylk_numeric_variance(_sylk_sample())
        assert result >= 0.0


class TestSylkMaxRowCellCount:
    def test_returns_int(self):
        result = sylk_max_row_cell_count(_sylk_sample())
        assert isinstance(result, int)


class TestDifAvgCellLengthVariance:
    def test_returns_float(self):
        result = dif_avg_cell_length_variance(_DIF)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = dif_avg_cell_length_variance(_DIF)
        assert result >= 0.0


class TestDifColumnDensity:
    def test_returns_float(self):
        result = dif_column_density(_DIF)
        assert isinstance(result, float)

    def test_between_zero_and_one(self):
        result = dif_column_density(_DIF)
        assert 0.0 <= result <= 1.0
