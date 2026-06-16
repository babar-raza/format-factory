"""Sprint 67 — PPM / NDJSON / SYLK / DIF product deepening (R297).

Tests 8 new analytics functions:
  PPM: ppm_is_portrait, ppm_diagonal
  NDJSON: ndjson_list_field_count, ndjson_field_count_variance
  SYLK: sylk_is_single_column, sylk_cell_count_variance
  DIF: dif_is_single_vector, dif_vector_length_variance
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm import ppm_is_portrait, ppm_diagonal
from src.python.ndjson import ndjson_list_field_count, ndjson_field_count_variance
from src.python.sylk import sylk_is_single_column, sylk_cell_count_variance
from src.python.dif import dif_is_single_vector, dif_vector_length_variance

_PPM = _REPO / "samples" / "by-format" / "ppm" / "valid" / "2x2-rgbw.ppm"
_NDJSON = b'{"id":1,"name":"Alice"}\n{"id":2,"name":"Bob"}\n'
_SYLK = _REPO / "samples" / "by-format" / "sylk" / "valid" / "minimal-2x2.slk"
_DIF = _REPO / "samples" / "by-format" / "dif" / "valid" / "minimal-2x2.dif"


class TestPpmIsPortrait:
    def test_returns_bool(self):
        assert isinstance(ppm_is_portrait(_PPM), bool)


class TestPpmDiagonal:
    def test_returns_float(self):
        assert isinstance(ppm_diagonal(_PPM), (int, float))

    def test_positive(self):
        assert ppm_diagonal(_PPM) > 0.0


class TestNdjsonListFieldCount:
    def test_returns_int(self):
        assert isinstance(ndjson_list_field_count(_NDJSON), int)

    def test_nonnegative(self):
        assert ndjson_list_field_count(_NDJSON) >= 0


class TestNdjsonFieldCountVariance:
    def test_returns_float(self):
        assert isinstance(ndjson_field_count_variance(_NDJSON), (int, float))

    def test_nonnegative(self):
        assert ndjson_field_count_variance(_NDJSON) >= 0.0


class TestSylkIsSingleColumn:
    def test_returns_bool(self):
        assert isinstance(sylk_is_single_column(_SYLK), bool)


class TestSylkCellCountVariance:
    def test_returns_float(self):
        assert isinstance(sylk_cell_count_variance(_SYLK), (int, float))

    def test_nonnegative(self):
        assert sylk_cell_count_variance(_SYLK) >= 0.0


class TestDifIsSingleVector:
    def test_returns_bool(self):
        assert isinstance(dif_is_single_vector(_DIF), bool)


class TestDifVectorLengthVariance:
    def test_returns_float(self):
        assert isinstance(dif_vector_length_variance(_DIF), (int, float))

    def test_nonnegative(self):
        assert dif_vector_length_variance(_DIF) >= 0.0
