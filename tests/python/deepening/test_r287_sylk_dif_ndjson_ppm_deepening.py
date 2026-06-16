"""Sprint 57 — SYLK / DIF / NDJSON / PPM product deepening (R287).

Tests 8 new analytics functions:
  SYLK:   sylk_column_variance, sylk_is_empty
  DIF:    dif_col_count_variance, dif_numeric_mean
  NDJSON: ndjson_avg_field_name_length, ndjson_record_size_variance
  PPM:    ppm_megapixels, ppm_channel_balance
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.sylk import sylk_column_variance, sylk_is_empty
from src.python.dif import dif_col_count_variance, dif_numeric_mean
from src.python.ndjson import ndjson_avg_field_name_length, ndjson_record_size_variance
from src.python.ppm import ppm_megapixels, ppm_channel_balance

_SYLK = _REPO / "samples" / "by-format" / "sylk" / "valid" / "minimal-2x2.slk"
_DIF = _REPO / "samples" / "by-format" / "dif" / "valid" / "minimal-2x2.dif"
_NDJSON = _REPO / "reports" / "capability-layer-rnext" / "sample-outputs" / "ndjson-sample.ndjson"
_PPM = _REPO / "samples" / "by-format" / "ppm" / "valid" / "2x2-rgbw.ppm"


# ── SYLK ─────────────────────────────────────────────────────────────

class TestSylkColumnVariance:
    def test_returns_float(self):
        result = sylk_column_variance(_SYLK)
        assert isinstance(result, (int, float))

    def test_nonnegative(self):
        assert sylk_column_variance(_SYLK) >= 0.0


class TestSylkIsEmpty:
    def test_returns_bool(self):
        result = sylk_is_empty(_SYLK)
        assert isinstance(result, bool)

    def test_not_empty(self):
        assert sylk_is_empty(_SYLK) is False


# ── DIF ──────────────────────────────────────────────────────────────

class TestDifColCountVariance:
    def test_returns_float(self):
        result = dif_col_count_variance(_DIF)
        assert isinstance(result, (int, float))

    def test_nonnegative(self):
        assert dif_col_count_variance(_DIF) >= 0.0


class TestDifNumericMean:
    def test_returns_float(self):
        result = dif_numeric_mean(_DIF)
        assert isinstance(result, (int, float))


# ── NDJSON ───────────────────────────────────────────────────────────

class TestNdjsonAvgFieldNameLength:
    def test_returns_float(self):
        result = ndjson_avg_field_name_length(_NDJSON)
        assert isinstance(result, (int, float))

    def test_positive(self):
        assert ndjson_avg_field_name_length(_NDJSON) > 0.0


class TestNdjsonRecordSizeVariance:
    def test_returns_float(self):
        result = ndjson_record_size_variance(_NDJSON)
        assert isinstance(result, (int, float))

    def test_nonnegative(self):
        assert ndjson_record_size_variance(_NDJSON) >= 0.0


# ── PPM ──────────────────────────────────────────────────────────────

class TestPpmMegapixels:
    def test_returns_float(self):
        result = ppm_megapixels(_PPM)
        assert isinstance(result, (int, float))

    def test_small_image(self):
        assert ppm_megapixels(_PPM) < 1.0


class TestPpmChannelBalance:
    def test_returns_float(self):
        result = ppm_channel_balance(_PPM)
        assert isinstance(result, (int, float))

    def test_range(self):
        result = ppm_channel_balance(_PPM)
        assert -0.1 <= result <= 1.1  # allow slight float imprecision
