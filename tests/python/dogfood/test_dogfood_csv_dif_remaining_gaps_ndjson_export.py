"""test_dogfood_csv_dif_remaining_gaps_ndjson_export.py

Dogfood export path: CSV remaining + DIF remaining analytics gap functions -> NDJSON.

Covers CSV: csv_first_field_length, csv_has_blank_headers, csv_is_wider_than_tall,
            csv_max_column_name_length, csv_field_count_variance, csv_longest_field_value,
            csv_narrow_column_count
Covers DIF: dif_avg_cell_length_variance, dif_avg_row_cell_count, dif_cells_per_tuple,
            dif_column_fill_ratio, dif_is_wider_than_tall, dif_max_column_sum,
            dif_row_length_variance, dif_value_type_variance

Concrete values:
  CSV minimal-2x2: first_field_length=5, has_blank_headers=False, is_wider_than_tall=False,
                   max_column_name_length=4, field_count_variance=0.0, longest_field_value=5
  CSV quoted-fields: is_wider_than_tall=True, max_column_name_length=11, longest_field_value=22
  DIF minimal-2x2: avg_cell_length_variance=5.25, avg_row_cell_count=8.0, cells_per_tuple=4.0,
                   column_fill_ratio=4.0, is_wider_than_tall=False, max_column_sum=99.0
  DIF numeric-row: is_wider_than_tall=True, max_column_sum=3.0

Sprint: product-deepening-csv-dif-remaining-gaps-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import (
    csv_first_field_length,
    csv_has_blank_headers,
    csv_is_wider_than_tall,
    csv_max_column_name_length,
    csv_field_count_variance,
    csv_longest_field_value,
    csv_narrow_column_count,
)
from src.python.dif.dif_parser import (
    dif_avg_cell_length_variance,
    dif_avg_row_cell_count,
    dif_cells_per_tuple,
    dif_column_fill_ratio,
    dif_is_wider_than_tall,
    dif_max_column_sum,
    dif_row_length_variance,
    dif_value_type_variance,
)
from src.python.ndjson.ndjson_codec import write_ndjson

CSV_DIR = _REPO / "samples" / "by-format" / "csv"
DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"

CSV_MINIMAL = CSV_DIR / "minimal-2x2.csv"
CSV_QUOTED = CSV_DIR / "quoted-fields.csv"
CSV_SINGLE = CSV_DIR / "single-cell.csv"
DIF_MINIMAL = DIF_DIR / "minimal-2x2.dif"
DIF_NUMERIC = DIF_DIR / "numeric-row.dif"


class TestCsvDifRemainingGapsNdjsonExport:

    # CSV tests
    def test_csv_minimal_first_field_length(self):
        assert csv_first_field_length(CSV_MINIMAL) == 5

    def test_csv_single_first_field_length(self):
        assert csv_first_field_length(CSV_SINGLE) == 2

    def test_csv_minimal_has_blank_headers_false(self):
        assert csv_has_blank_headers(CSV_MINIMAL) is False

    def test_csv_quoted_has_blank_headers_false(self):
        assert csv_has_blank_headers(CSV_QUOTED) is False

    def test_csv_minimal_is_not_wider_than_tall(self):
        assert csv_is_wider_than_tall(CSV_MINIMAL) is False

    def test_csv_quoted_is_wider_than_tall(self):
        assert csv_is_wider_than_tall(CSV_QUOTED) is True

    def test_csv_minimal_max_column_name_length(self):
        assert csv_max_column_name_length(CSV_MINIMAL) == 4

    def test_csv_quoted_max_column_name_length(self):
        assert csv_max_column_name_length(CSV_QUOTED) == 11

    def test_csv_minimal_field_count_variance_zero(self):
        assert abs(csv_field_count_variance(CSV_MINIMAL)) < 0.01

    def test_csv_minimal_longest_field_value(self):
        assert csv_longest_field_value(CSV_MINIMAL) == 5

    def test_csv_quoted_longest_field_value(self):
        assert csv_longest_field_value(CSV_QUOTED) >= 10

    def test_csv_minimal_narrow_column_count(self):
        assert csv_narrow_column_count(CSV_MINIMAL) == 2

    # DIF tests
    def test_dif_minimal_avg_cell_length_variance(self):
        assert abs(dif_avg_cell_length_variance(DIF_MINIMAL) - 5.25) < 0.1

    def test_dif_numeric_avg_cell_length_variance_zero(self):
        assert abs(dif_avg_cell_length_variance(DIF_NUMERIC)) < 0.01

    def test_dif_minimal_avg_row_cell_count(self):
        assert abs(dif_avg_row_cell_count(DIF_MINIMAL) - 8.0) < 0.1

    def test_dif_minimal_cells_per_tuple(self):
        assert abs(dif_cells_per_tuple(DIF_MINIMAL) - 4.0) < 0.1

    def test_dif_minimal_column_fill_ratio(self):
        assert abs(dif_column_fill_ratio(DIF_MINIMAL) - 4.0) < 0.1

    def test_dif_minimal_is_not_wider_than_tall(self):
        assert dif_is_wider_than_tall(DIF_MINIMAL) is False

    def test_dif_numeric_is_wider_than_tall(self):
        assert dif_is_wider_than_tall(DIF_NUMERIC) is True

    def test_dif_minimal_max_column_sum(self):
        assert abs(dif_max_column_sum(DIF_MINIMAL) - 99.0) < 0.1

    def test_dif_minimal_row_length_variance_zero(self):
        assert abs(dif_row_length_variance(DIF_MINIMAL)) < 0.01

    def test_dif_minimal_value_type_variance_zero(self):
        assert abs(dif_value_type_variance(DIF_MINIMAL)) < 0.01

    def test_ndjson_export_csv_record(self, tmp_path):
        records = [{
            "file": CSV_QUOTED.name,
            "first_field_length": csv_first_field_length(CSV_QUOTED),
            "is_wider_than_tall": csv_is_wider_than_tall(CSV_QUOTED),
            "max_column_name_length": csv_max_column_name_length(CSV_QUOTED),
        }]
        out = tmp_path / "csv_remaining.ndjson"
        write_ndjson(records, str(out))
        parsed = json.loads(out.read_text(encoding="utf-8").strip())
        assert parsed["is_wider_than_tall"] is True

    def test_ndjson_export_dif_records(self, tmp_path):
        records = [
            {"file": DIF_MINIMAL.name, "max_column_sum": dif_max_column_sum(DIF_MINIMAL)},
            {"file": DIF_NUMERIC.name, "is_wider_than_tall": dif_is_wider_than_tall(DIF_NUMERIC)},
        ]
        out = tmp_path / "dif_remaining.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert abs(json.loads(lines[0])["max_column_sum"] - 99.0) < 0.1
        assert json.loads(lines[1])["is_wider_than_tall"] is True
