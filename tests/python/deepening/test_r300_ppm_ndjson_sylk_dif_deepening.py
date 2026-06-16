"""Sprint 70 — PPM / NDJSON / SYLK / DIF product deepening (R300).

Tests 8 new analytics functions:
  PPM: ppm_is_monochrome, ppm_total_channel_sum
  NDJSON: ndjson_max_nesting_depth, ndjson_avg_numeric_value
  SYLK: sylk_is_all_numeric, sylk_row_span
  DIF: dif_is_all_string, dif_nonempty_cell_ratio
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm import ppm_is_monochrome, ppm_total_channel_sum
from src.python.ndjson import ndjson_max_nesting_depth, ndjson_avg_numeric_value
from src.python.sylk import sylk_is_all_numeric, sylk_row_span
from src.python.dif import dif_is_all_string, dif_nonempty_cell_ratio

_PPM = _REPO / "samples" / "by-format" / "ppm" / "valid" / "2x2-rgbw.ppm"
_NDJSON = b'{"name":"a","val":1}\n{"name":"b","val":2}\n'
_SYLK = _REPO / "samples" / "by-format" / "sylk" / "valid" / "minimal-2x2.slk"
_DIF = _REPO / "samples" / "by-format" / "dif" / "valid" / "minimal-2x2.dif"


class TestPpmIsMonochrome:
    def test_returns_bool(self):
        assert isinstance(ppm_is_monochrome(_PPM), bool)


class TestPpmTotalChannelSum:
    def test_returns_int(self):
        assert isinstance(ppm_total_channel_sum(_PPM), int)

    def test_nonnegative(self):
        assert ppm_total_channel_sum(_PPM) >= 0


class TestNdjsonMaxNestingDepth:
    def test_returns_int(self):
        assert isinstance(ndjson_max_nesting_depth(_NDJSON), int)

    def test_positive(self):
        assert ndjson_max_nesting_depth(_NDJSON) > 0


class TestNdjsonAvgNumericValue:
    def test_returns_float(self):
        assert isinstance(ndjson_avg_numeric_value(_NDJSON), (int, float))

    def test_positive(self):
        assert ndjson_avg_numeric_value(_NDJSON) > 0


class TestSylkIsAllNumeric:
    def test_returns_bool(self):
        assert isinstance(sylk_is_all_numeric(_SYLK), bool)


class TestSylkRowSpan:
    def test_returns_int(self):
        assert isinstance(sylk_row_span(_SYLK), int)

    def test_positive(self):
        assert sylk_row_span(_SYLK) > 0


class TestDifIsAllString:
    def test_returns_bool(self):
        assert isinstance(dif_is_all_string(_DIF), bool)


class TestDifNonemptyCellRatio:
    def test_returns_float(self):
        assert isinstance(dif_nonempty_cell_ratio(_DIF), (int, float))

    def test_between_zero_and_one(self):
        ratio = dif_nonempty_cell_ratio(_DIF)
        assert 0.0 <= ratio <= 1.0
