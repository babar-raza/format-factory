"""Sprint 74 — PPM / NDJSON / SYLK / DIF product deepening (R304).

Tests 8 new analytics functions:
  PPM: ppm_avg_brightness, ppm_color_variance
  NDJSON: ndjson_total_string_length, ndjson_numeric_density
  SYLK: sylk_avg_cell_length, sylk_column_span
  DIF: dif_avg_numeric_value, dif_row_length_variance
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm import ppm_avg_brightness, ppm_color_variance
from src.python.ndjson import ndjson_total_string_length, ndjson_numeric_density
from src.python.sylk import sylk_avg_cell_length, sylk_column_span
from src.python.dif import dif_avg_numeric_value, dif_row_length_variance

_PPM = _REPO / "samples" / "by-format" / "ppm" / "valid" / "2x2-rgbw.ppm"
_NDJSON_DATA = b'{"name":"a","val":1}\n{"name":"b","val":2}\n'
_SYLK = _REPO / "samples" / "by-format" / "sylk" / "valid" / "minimal-2x2.slk"
_DIF = _REPO / "samples" / "by-format" / "dif" / "valid" / "minimal-2x2.dif"


class TestPpmAvgBrightness:
    def test_returns_float(self):
        assert isinstance(ppm_avg_brightness(_PPM), float)

    def test_nonnegative(self):
        assert ppm_avg_brightness(_PPM) >= 0.0


class TestPpmColorVariance:
    def test_returns_float(self):
        assert isinstance(ppm_color_variance(_PPM), float)

    def test_nonnegative(self):
        assert ppm_color_variance(_PPM) >= 0.0


class TestNdjsonTotalStringLength:
    def test_returns_int(self):
        assert isinstance(ndjson_total_string_length(_NDJSON_DATA), int)

    def test_positive(self):
        assert ndjson_total_string_length(_NDJSON_DATA) > 0


class TestNdjsonNumericDensity:
    def test_returns_float(self):
        assert isinstance(ndjson_numeric_density(_NDJSON_DATA), float)

    def test_between_zero_and_one(self):
        val = ndjson_numeric_density(_NDJSON_DATA)
        assert 0.0 <= val <= 1.0


class TestSylkAvgCellLength:
    def test_returns_float(self):
        assert isinstance(sylk_avg_cell_length(_SYLK), float)

    def test_nonnegative(self):
        assert sylk_avg_cell_length(_SYLK) >= 0.0


class TestSylkColumnSpan:
    def test_returns_int(self):
        assert isinstance(sylk_column_span(_SYLK), int)

    def test_positive(self):
        assert sylk_column_span(_SYLK) > 0


class TestDifAvgNumericValue:
    def test_returns_float(self):
        assert isinstance(dif_avg_numeric_value(_DIF), (int, float))


class TestDifRowLengthVariance:
    def test_returns_float(self):
        assert isinstance(dif_row_length_variance(_DIF), float)

    def test_nonnegative(self):
        assert dif_row_length_variance(_DIF) >= 0.0
