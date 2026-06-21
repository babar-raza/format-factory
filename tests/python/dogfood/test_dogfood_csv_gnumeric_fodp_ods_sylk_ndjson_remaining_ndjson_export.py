"""test_dogfood_csv_gnumeric_fodp_ods_sylk_ndjson_remaining_ndjson_export.py

Dogfood export path: CSV + GNUMERIC + FODP + ODS + SYLK + NDJSON remaining analytics gap functions -> NDJSON.

Covers CSV: csv_widest_field_length, csv_empty_field_count, csv_numeric_field_count,
            csv_numeric_range, csv_has_only_one_row, csv_file_size_bytes, csv_total_field_count
Covers GNUMERIC: gnumeric_is_single_cell, gnumeric_has_mixed_types
Covers FODP: fodp_min_shape_count, fodp_note_count
Covers ODS: ods_min_row_cell_count, ods_numeric_cell_sum, ods_is_wider_than_tall,
            ods_has_more_strings_than_numerics
Covers SYLK: sylk_column_fill_rate, sylk_distinct_string_count, sylk_has_multi_col_rows,
             sylk_avg_cols_per_row
Covers NDJSON: ndjson_avg_key_count, ndjson_distinct_key_count, ndjson_bool_field_count,
               ndjson_unique_key_count, ndjson_avg_string_value_length

Concrete values:
  CSV minimal-2x2: widest=5, empty_fields=0, numeric_fields=2, numeric_range=5.0, one_row=False, file_size=25, total_fields=4
  CSV single-cell: widest=5, one_row=True, numeric_fields=1, total_fields=1
  GNUMERIC minimal: is_single_cell=True, has_mixed=False
  GNUMERIC multi-cell: is_single_cell=False, has_mixed=True
  FODP minimal: min_shapes=1, note_count=0
  FODP title-only: min_shapes=0
  ODS minimal: min_row=2, numeric_sum=42.0, wider=False, more_str=True
  ODS numeric-row: numeric_sum=6.0, wider=True, more_str=False
  SYLK minimal-2x2: fill_rate=0.444, distinct_str=3, multi_col=True, avg_cols=2.0
  SYLK numeric-row: distinct_str=0, avg_cols=3.0
  NDJSON tmp: avg_key_count=3.0, distinct_key_count=3, bool_field_count=2, unique_key_count=3, avg_str_val_len=5.0

Sprint: product-deepening-csv-gnumeric-fodp-ods-sylk-ndjson-remaining-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import (
    csv_widest_field_length,
    csv_empty_field_count,
    csv_numeric_field_count,
    csv_numeric_range,
    csv_has_only_one_row,
    csv_file_size_bytes,
    csv_total_field_count,
)
from src.python.gnumeric.gnumeric_codec import gnumeric_is_single_cell, gnumeric_has_mixed_types
from src.python.fodp.fodp_codec import fodp_min_shape_count, fodp_note_count
from src.python.ods.ods_parser import (
    ods_min_row_cell_count,
    ods_numeric_cell_sum,
    ods_is_wider_than_tall,
    ods_has_more_strings_than_numerics,
)
from src.python.sylk.sylk_parser import (
    sylk_column_fill_rate,
    sylk_distinct_string_count,
    sylk_has_multi_col_rows,
    sylk_avg_cols_per_row,
)
from src.python.ndjson.ndjson_codec import (
    ndjson_avg_key_count,
    ndjson_distinct_key_count,
    ndjson_bool_field_count,
    ndjson_unique_key_count,
    ndjson_avg_string_value_length,
    write_ndjson,
)

CSV_DIR = _REPO / "samples" / "by-format" / "csv"
GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"
FODP_DIR = _REPO / "samples" / "by-format" / "fodp"
ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"
SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"

CSV_MINIMAL = CSV_DIR / "minimal-2x2.csv"
CSV_SINGLE = CSV_DIR / "single-cell.csv"
CSV_QUOTED = CSV_DIR / "quoted-fields.csv"
GNUMERIC_MINIMAL = GNUMERIC_DIR / "minimal-spreadsheet.gnumeric"
GNUMERIC_MULTI = GNUMERIC_DIR / "multi-cell-basic.gnumeric"
FODP_MINIMAL = FODP_DIR / "minimal-presentation.fodp"
FODP_TITLE_ONLY = FODP_DIR / "title-only.fodp"
ODS_MINIMAL = ODS_DIR / "minimal-spreadsheet.ods"
ODS_NUMERIC = ODS_DIR / "numeric-row.ods"
SYLK_MINIMAL = SYLK_DIR / "minimal-2x2.slk"
SYLK_NUMERIC = SYLK_DIR / "numeric-row.slk"


class TestCsvGnumericFodpOdsSylkNdjsonRemainingNdjsonExport:

    # CSV tests
    def test_csv_minimal_widest_field_length(self):
        assert csv_widest_field_length(CSV_MINIMAL) == 5

    def test_csv_quoted_widest_field_length(self):
        assert csv_widest_field_length(CSV_QUOTED) == 22

    def test_csv_minimal_empty_field_count_zero(self):
        assert csv_empty_field_count(CSV_MINIMAL) == 0

    def test_csv_minimal_numeric_field_count(self):
        assert csv_numeric_field_count(CSV_MINIMAL) == 2

    def test_csv_minimal_numeric_range(self):
        assert abs(csv_numeric_range(CSV_MINIMAL) - 5.0) < 0.1

    def test_csv_minimal_not_only_one_row(self):
        assert csv_has_only_one_row(CSV_MINIMAL) is False

    def test_csv_single_has_only_one_row(self):
        assert csv_has_only_one_row(CSV_SINGLE) is True

    def test_csv_minimal_file_size_bytes(self):
        assert csv_file_size_bytes(CSV_MINIMAL) == 25

    def test_csv_minimal_total_field_count(self):
        assert csv_total_field_count(CSV_MINIMAL) == 4

    def test_csv_single_total_field_count(self):
        assert csv_total_field_count(CSV_SINGLE) == 1

    # GNUMERIC tests
    def test_gnumeric_minimal_is_single_cell(self):
        assert gnumeric_is_single_cell(GNUMERIC_MINIMAL) is True

    def test_gnumeric_multi_not_single_cell(self):
        assert gnumeric_is_single_cell(GNUMERIC_MULTI) is False

    def test_gnumeric_minimal_no_mixed_types(self):
        assert gnumeric_has_mixed_types(GNUMERIC_MINIMAL) is False

    def test_gnumeric_multi_has_mixed_types(self):
        assert gnumeric_has_mixed_types(GNUMERIC_MULTI) is True

    # FODP tests
    def test_fodp_minimal_min_shape_count(self):
        assert fodp_min_shape_count(FODP_MINIMAL) == 1

    def test_fodp_title_only_min_shape_count_zero(self):
        assert fodp_min_shape_count(FODP_TITLE_ONLY) == 0

    def test_fodp_minimal_note_count_zero(self):
        assert fodp_note_count(FODP_MINIMAL) == 0

    # ODS tests
    def test_ods_minimal_min_row_cell_count(self):
        assert ods_min_row_cell_count(ODS_MINIMAL) == 2

    def test_ods_minimal_numeric_cell_sum(self):
        assert abs(ods_numeric_cell_sum(ODS_MINIMAL) - 42.0) < 0.1

    def test_ods_minimal_not_wider_than_tall(self):
        assert ods_is_wider_than_tall(ODS_MINIMAL) is False

    def test_ods_numeric_is_wider_than_tall(self):
        assert ods_is_wider_than_tall(ODS_NUMERIC) is True

    def test_ods_minimal_has_more_strings(self):
        assert ods_has_more_strings_than_numerics(ODS_MINIMAL) is True

    def test_ods_numeric_not_more_strings(self):
        assert ods_has_more_strings_than_numerics(ODS_NUMERIC) is False

    def test_ods_numeric_cell_sum(self):
        assert abs(ods_numeric_cell_sum(ODS_NUMERIC) - 6.0) < 0.1

    # SYLK tests
    def test_sylk_minimal_column_fill_rate(self):
        assert abs(sylk_column_fill_rate(SYLK_MINIMAL) - 0.444) < 0.01

    def test_sylk_minimal_distinct_string_count(self):
        assert sylk_distinct_string_count(SYLK_MINIMAL) == 3

    def test_sylk_minimal_has_multi_col_rows(self):
        assert sylk_has_multi_col_rows(SYLK_MINIMAL) is True

    def test_sylk_minimal_avg_cols_per_row(self):
        assert abs(sylk_avg_cols_per_row(SYLK_MINIMAL) - 2.0) < 0.1

    def test_sylk_numeric_distinct_string_count_zero(self):
        assert sylk_distinct_string_count(SYLK_NUMERIC) == 0

    def test_sylk_numeric_avg_cols_per_row(self):
        assert abs(sylk_avg_cols_per_row(SYLK_NUMERIC) - 3.0) < 0.1

    # NDJSON tests (using tmp_path)
    def test_ndjson_avg_key_count(self, tmp_path):
        ndjson_file = tmp_path / "test.ndjson"
        ndjson_file.write_text(
            '{"a": 1, "b": "hello", "c": true}\n{"a": 2, "b": "world", "c": false}\n',
            encoding="utf-8"
        )
        assert abs(ndjson_avg_key_count(ndjson_file) - 3.0) < 0.01

    def test_ndjson_distinct_key_count(self, tmp_path):
        ndjson_file = tmp_path / "test.ndjson"
        ndjson_file.write_text(
            '{"a": 1, "b": "hello", "c": true}\n{"a": 2, "b": "world", "c": false}\n',
            encoding="utf-8"
        )
        assert ndjson_distinct_key_count(ndjson_file) == 3

    def test_ndjson_bool_field_count(self, tmp_path):
        ndjson_file = tmp_path / "test.ndjson"
        ndjson_file.write_text(
            '{"a": 1, "b": "hello", "c": true}\n{"a": 2, "b": "world", "c": false}\n',
            encoding="utf-8"
        )
        assert ndjson_bool_field_count(ndjson_file) == 2

    def test_ndjson_unique_key_count(self, tmp_path):
        ndjson_file = tmp_path / "test.ndjson"
        ndjson_file.write_text(
            '{"a": 1, "b": "hello", "c": true}\n{"a": 2, "b": "world", "c": false}\n',
            encoding="utf-8"
        )
        assert ndjson_unique_key_count(ndjson_file) == 3

    def test_ndjson_avg_string_value_length(self, tmp_path):
        ndjson_file = tmp_path / "test.ndjson"
        ndjson_file.write_text(
            '{"a": 1, "b": "hello", "c": true}\n{"a": 2, "b": "world", "c": false}\n',
            encoding="utf-8"
        )
        assert abs(ndjson_avg_string_value_length(ndjson_file) - 5.0) < 0.1

    def test_ndjson_export_csv_gnumeric_records(self, tmp_path):
        records = [
            {
                "file": CSV_MINIMAL.name,
                "widest_field": csv_widest_field_length(CSV_MINIMAL),
                "total_fields": csv_total_field_count(CSV_MINIMAL),
            },
            {
                "file": GNUMERIC_MULTI.name,
                "is_single_cell": gnumeric_is_single_cell(GNUMERIC_MULTI),
                "has_mixed_types": gnumeric_has_mixed_types(GNUMERIC_MULTI),
            },
        ]
        out = tmp_path / "csv_gnumeric_remaining.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert json.loads(lines[0])["total_fields"] == 4
        assert json.loads(lines[1])["has_mixed_types"] is True
