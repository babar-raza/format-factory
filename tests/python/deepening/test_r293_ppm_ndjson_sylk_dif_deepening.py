"""Sprint 63 — PPM / NDJSON / SYLK / DIF product deepening (R293).

Tests 8 new analytics functions:
  PPM: ppm_is_tall, ppm_pixel_density
  NDJSON: ndjson_is_empty, ndjson_avg_string_length
  SYLK: sylk_has_empty_rows, sylk_avg_numeric_cell_length
  DIF: dif_is_empty, dif_unique_value_count
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm import ppm_is_tall, ppm_pixel_density
from src.python.ndjson import ndjson_is_empty, ndjson_avg_string_length
from src.python.sylk import sylk_has_empty_rows, sylk_avg_numeric_cell_length
from src.python.dif import dif_is_empty, dif_unique_value_count

_PPM = _REPO / "samples" / "by-format" / "ppm" / "valid" / "2x2-rgbw.ppm"
_SYLK = _REPO / "samples" / "by-format" / "sylk" / "valid" / "minimal-2x2.slk"
_DIF = _REPO / "samples" / "by-format" / "dif" / "valid" / "minimal-2x2.dif"

_NDJSON_DATA = b'{"id":1,"name":"Alice"}\n{"id":2,"name":"Bob"}\n'


class TestPpmIsTall:
    def test_returns_bool(self):
        assert isinstance(ppm_is_tall(_PPM), bool)

    def test_2x2_not_tall(self):
        assert ppm_is_tall(_PPM) is False


class TestPpmPixelDensity:
    def test_returns_float(self):
        assert isinstance(ppm_pixel_density(_PPM), (int, float))

    def test_positive(self):
        assert ppm_pixel_density(_PPM) > 0.0


class TestNdjsonIsEmpty:
    def test_returns_bool(self):
        assert isinstance(ndjson_is_empty(_NDJSON_DATA), bool)

    def test_not_empty(self):
        assert ndjson_is_empty(_NDJSON_DATA) is False

    def test_empty(self):
        assert ndjson_is_empty(b'') is True


class TestNdjsonAvgStringLength:
    def test_returns_float(self):
        assert isinstance(ndjson_avg_string_length(_NDJSON_DATA), (int, float))

    def test_positive(self):
        assert ndjson_avg_string_length(_NDJSON_DATA) > 0.0


class TestSylkHasEmptyRows:
    def test_returns_bool(self):
        assert isinstance(sylk_has_empty_rows(_SYLK), bool)


class TestSylkAvgNumericCellLength:
    def test_returns_float(self):
        assert isinstance(sylk_avg_numeric_cell_length(_SYLK), (int, float))

    def test_nonnegative(self):
        assert sylk_avg_numeric_cell_length(_SYLK) >= 0.0


class TestDifIsEmpty:
    def test_returns_bool(self):
        assert isinstance(dif_is_empty(_DIF), bool)

    def test_minimal_not_empty(self):
        assert dif_is_empty(_DIF) is False


class TestDifUniqueValueCount:
    def test_returns_int(self):
        assert isinstance(dif_unique_value_count(_DIF), int)

    def test_nonnegative(self):
        assert dif_unique_value_count(_DIF) >= 0
