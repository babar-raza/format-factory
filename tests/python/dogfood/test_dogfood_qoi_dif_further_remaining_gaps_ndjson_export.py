"""test_dogfood_qoi_dif_further_remaining_gaps_ndjson_export.py

Dogfood export path: QOI remaining + DIF further remaining analytics gap functions -> NDJSON.

Covers QOI: qoi_dark_pixel_count, qoi_luminance_range
Covers DIF: dif_all_numeric, dif_avg_numeric_value, dif_col_count_variance,
            dif_column_density, dif_data_density, dif_longest_row_index,
            dif_max_numeric_length, dif_max_string_length, dif_min_row_index,
            dif_vectors_tuples_sum

Concrete values:
  QOI 1x1-red: dark_pixel_count=0, luminance_range=0.0
  QOI 2x2-black: dark_pixel_count=4, luminance_range=0.0
  QOI 4x1-gradient: dark_pixel_count=1, luminance_range=255.0
  DIF minimal-2x2: all_numeric=False, avg_numeric_value=70.5, column_density=1.0,
                   data_density=1.0, longest_row_index=0, max_numeric_length=4,
                   max_string_length=7, min_row_index=0, vectors_tuples_sum=4
  DIF numeric-row: all_numeric=True, avg_numeric_value=2.0, max_string_length=0

Sprint: product-deepening-qoi-dif-further-remaining-gaps-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.qoi.qoi_parser import (
    qoi_dark_pixel_count,
    qoi_luminance_range,
)
from src.python.dif.dif_parser import (
    dif_all_numeric,
    dif_avg_numeric_value,
    dif_col_count_variance,
    dif_column_density,
    dif_data_density,
    dif_longest_row_index,
    dif_max_numeric_length,
    dif_max_string_length,
    dif_min_row_index,
    dif_vectors_tuples_sum,
)
from src.python.ndjson.ndjson_codec import write_ndjson

QOI_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"

QOI_RED = QOI_DIR / "1x1-red.qoi"
QOI_BLACK = QOI_DIR / "2x2-black.qoi"
QOI_GRADIENT = QOI_DIR / "4x1-gradient.qoi"
DIF_MINIMAL = DIF_DIR / "minimal-2x2.dif"
DIF_NUMERIC = DIF_DIR / "numeric-row.dif"


class TestQoiDifFurtherRemainingGapsNdjsonExport:

    # QOI tests
    def test_qoi_red_dark_pixel_count_zero(self):
        assert qoi_dark_pixel_count(QOI_RED) == 0

    def test_qoi_black_dark_pixel_count_four(self):
        assert qoi_dark_pixel_count(QOI_BLACK) == 4

    def test_qoi_gradient_dark_pixel_count_one(self):
        assert qoi_dark_pixel_count(QOI_GRADIENT) == 1

    def test_qoi_red_luminance_range_zero(self):
        assert abs(qoi_luminance_range(QOI_RED)) < 0.01

    def test_qoi_black_luminance_range_zero(self):
        assert abs(qoi_luminance_range(QOI_BLACK)) < 0.01

    def test_qoi_gradient_luminance_range_positive(self):
        assert qoi_luminance_range(QOI_GRADIENT) > 0.0

    # DIF tests
    def test_dif_minimal_not_all_numeric(self):
        assert dif_all_numeric(DIF_MINIMAL) is False

    def test_dif_numeric_all_numeric(self):
        assert dif_all_numeric(DIF_NUMERIC) is True

    def test_dif_minimal_avg_numeric_value(self):
        assert abs(dif_avg_numeric_value(DIF_MINIMAL) - 70.5) < 0.1

    def test_dif_numeric_avg_numeric_value(self):
        assert abs(dif_avg_numeric_value(DIF_NUMERIC) - 2.0) < 0.1

    def test_dif_minimal_col_count_variance_zero(self):
        assert abs(dif_col_count_variance(DIF_MINIMAL)) < 0.01

    def test_dif_minimal_column_density_one(self):
        assert abs(dif_column_density(DIF_MINIMAL) - 1.0) < 0.01

    def test_dif_minimal_data_density_one(self):
        assert abs(dif_data_density(DIF_MINIMAL) - 1.0) < 0.01

    def test_dif_minimal_longest_row_index_zero(self):
        assert dif_longest_row_index(DIF_MINIMAL) == 0

    def test_dif_minimal_max_numeric_length(self):
        assert dif_max_numeric_length(DIF_MINIMAL) == 4

    def test_dif_minimal_max_string_length(self):
        assert dif_max_string_length(DIF_MINIMAL) == 7

    def test_dif_numeric_max_string_length_zero(self):
        assert dif_max_string_length(DIF_NUMERIC) == 0

    def test_dif_minimal_min_row_index_zero(self):
        assert dif_min_row_index(DIF_MINIMAL) == 0

    def test_dif_minimal_vectors_tuples_sum(self):
        assert dif_vectors_tuples_sum(DIF_MINIMAL) == 4

    def test_ndjson_export_qoi_records(self, tmp_path):
        records = [
            {"file": QOI_RED.name, "dark_pixel_count": qoi_dark_pixel_count(QOI_RED), "luminance_range": qoi_luminance_range(QOI_RED)},
            {"file": QOI_BLACK.name, "dark_pixel_count": qoi_dark_pixel_count(QOI_BLACK)},
        ]
        out = tmp_path / "qoi_remaining.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert json.loads(lines[0])["dark_pixel_count"] == 0
        assert json.loads(lines[1])["dark_pixel_count"] == 4

    def test_ndjson_export_dif_record(self, tmp_path):
        records = [{
            "file": DIF_NUMERIC.name,
            "all_numeric": dif_all_numeric(DIF_NUMERIC),
            "max_string_length": dif_max_string_length(DIF_NUMERIC),
        }]
        out = tmp_path / "dif_further.ndjson"
        write_ndjson(records, str(out))
        parsed = json.loads(out.read_text(encoding="utf-8").strip())
        assert parsed["all_numeric"] is True
