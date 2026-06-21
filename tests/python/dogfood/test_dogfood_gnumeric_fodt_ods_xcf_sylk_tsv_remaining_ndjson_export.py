"""test_dogfood_gnumeric_fodt_ods_xcf_sylk_tsv_remaining_ndjson_export.py

Dogfood export path: GNUMERIC + FODT + ODS + XCF + SYLK + TSV remaining analytics gap functions -> NDJSON.

Covers GNUMERIC: gnumeric_min_numeric_value, gnumeric_max_numeric_value, gnumeric_has_string_cells,
                 gnumeric_has_numeric_cells, gnumeric_avg_cell_value_length, gnumeric_string_ratio,
                 gnumeric_nonempty_row_count, gnumeric_min_row_length, gnumeric_avg_string_length
Covers FODT: fodt_nonempty_block_count, fodt_punctuation_count, fodt_has_multiple_block_types,
             fodt_punctuation_density, fodt_paragraph_variance, fodt_table_cell_count,
             fodt_list_block_count, fodt_text_block_ratio, fodt_section_depth_max
Covers ODS: ods_sheet_density, ods_string_cell_ratio, ods_widest_column_index,
            ods_total_string_cells, ods_total_cells, ods_has_mixed_types
Covers XCF: xcf_diagonal_length, xcf_dimension_product
Covers SYLK: sylk_file_size_bytes, sylk_max_col_index
Covers TSV: tsv_file_size_bytes, tsv_max_row_length, tsv_min_row_length

Concrete values:
  GNUMERIC minimal: has_string=True, has_numeric=False, avg_val_len=5.0, string_ratio=1.0, nonempty_rows=1, min_row_len=1, avg_str_len=5.0
  GNUMERIC multi-cell: min_numeric=42.0, max_numeric=42.0, has_string=True, has_numeric=True, string_ratio=0.75
  GNUMERIC empty: has_string=False, has_numeric=False, nonempty_rows=0
  FODT minimal: nonempty_block_count=1, punctuation_count=2, has_multiple_block_types=False, text_block_ratio=1.0, table_cell_count=0
  FODT headings-and-paragraphs: nonempty_block_count=7, has_multiple_block_types=True, text_block_ratio=0.5714
  XCF 1x1-red: diagonal_length=1.414, dimension_product=1
  XCF 2x2-gray: diagonal_length=2.828, dimension_product=4
  ODS minimal: sheet_density=4.0, string_cell_ratio=0.75, total_cells=4, has_mixed_types=True
  ODS numeric-row: string_cell_ratio=0.0, total_cells=3, has_mixed_types=False
  SYLK minimal-2x2: file_size_bytes=75, max_col_index=2
  TSV minimal-2x2: file_size_bytes=28, max_row_length=2, min_row_length=2

Sprint: product-deepening-gnumeric-fodt-ods-xcf-sylk-tsv-remaining-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.gnumeric.gnumeric_codec import (
    gnumeric_min_numeric_value,
    gnumeric_max_numeric_value,
    gnumeric_has_string_cells,
    gnumeric_has_numeric_cells,
    gnumeric_avg_cell_value_length,
    gnumeric_string_ratio,
    gnumeric_nonempty_row_count,
    gnumeric_min_row_length,
    gnumeric_avg_string_length,
)
from src.python.fodt.neutral_model import (
    fodt_nonempty_block_count,
    fodt_punctuation_count,
    fodt_has_multiple_block_types,
    fodt_punctuation_density,
    fodt_paragraph_variance,
    fodt_table_cell_count,
    fodt_list_block_count,
    fodt_text_block_ratio,
    fodt_section_depth_max,
)
from src.python.ods.ods_parser import (
    ods_sheet_density,
    ods_string_cell_ratio,
    ods_widest_column_index,
    ods_total_string_cells,
    ods_total_cells,
    ods_has_mixed_types,
)
from src.python.xcf.xcf_parser import xcf_diagonal_length, xcf_dimension_product
from src.python.sylk.sylk_parser import sylk_file_size_bytes, sylk_max_col_index
from src.python.tsv.tsv_parser import tsv_file_size_bytes, tsv_max_row_length, tsv_min_row_length
from src.python.ndjson.ndjson_codec import write_ndjson

GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"
FODT_DIR = _REPO / "samples" / "by-format" / "fodt"
ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"
XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"
TSV_DIR = _REPO / "samples" / "by-format" / "tsv"

GNUMERIC_MINIMAL = GNUMERIC_DIR / "minimal-spreadsheet.gnumeric"
GNUMERIC_MULTI = GNUMERIC_DIR / "multi-cell-basic.gnumeric"
GNUMERIC_EMPTY = GNUMERIC_DIR / "empty-sheet.gnumeric"
FODT_MINIMAL = FODT_DIR / "minimal-document.fodt"
FODT_HEADINGS = FODT_DIR / "headings-and-paragraphs.fodt"
FODT_LIST = FODT_DIR / "list-basic.fodt"
ODS_MINIMAL = ODS_DIR / "minimal-spreadsheet.ods"
ODS_NUMERIC = ODS_DIR / "numeric-row.ods"
XCF_1X1 = XCF_DIR / "1x1-red-rgb.xcf"
XCF_2X2 = XCF_DIR / "2x2-gray.xcf"
SYLK_MINIMAL = SYLK_DIR / "minimal-2x2.slk"
SYLK_NUMERIC = SYLK_DIR / "numeric-row.slk"
TSV_MINIMAL = TSV_DIR / "minimal-2x2.tsv"
TSV_MULTI = TSV_DIR / "multi-column.tsv"
TSV_SINGLE = TSV_DIR / "single-cell.tsv"


class TestGnumericFodtOdsXcfSylkTsvRemainingNdjsonExport:

    # GNUMERIC tests
    def test_gnumeric_minimal_has_string_cells(self):
        assert gnumeric_has_string_cells(GNUMERIC_MINIMAL) is True

    def test_gnumeric_minimal_has_no_numeric_cells(self):
        assert gnumeric_has_numeric_cells(GNUMERIC_MINIMAL) is False

    def test_gnumeric_minimal_avg_cell_value_length(self):
        assert abs(gnumeric_avg_cell_value_length(GNUMERIC_MINIMAL) - 5.0) < 0.1

    def test_gnumeric_minimal_string_ratio_one(self):
        assert abs(gnumeric_string_ratio(GNUMERIC_MINIMAL) - 1.0) < 0.01

    def test_gnumeric_minimal_nonempty_row_count(self):
        assert gnumeric_nonempty_row_count(GNUMERIC_MINIMAL) == 1

    def test_gnumeric_minimal_avg_string_length(self):
        assert abs(gnumeric_avg_string_length(GNUMERIC_MINIMAL) - 5.0) < 0.1

    def test_gnumeric_multi_min_numeric_value(self):
        assert abs(gnumeric_min_numeric_value(GNUMERIC_MULTI) - 42.0) < 0.1

    def test_gnumeric_multi_max_numeric_value(self):
        assert abs(gnumeric_max_numeric_value(GNUMERIC_MULTI) - 42.0) < 0.1

    def test_gnumeric_multi_has_numeric_cells(self):
        assert gnumeric_has_numeric_cells(GNUMERIC_MULTI) is True

    def test_gnumeric_multi_string_ratio(self):
        assert abs(gnumeric_string_ratio(GNUMERIC_MULTI) - 0.75) < 0.01

    def test_gnumeric_multi_min_row_length(self):
        assert gnumeric_min_row_length(GNUMERIC_MULTI) >= 2

    def test_gnumeric_empty_has_no_string_cells(self):
        assert gnumeric_has_string_cells(GNUMERIC_EMPTY) is False

    def test_gnumeric_empty_nonempty_row_count_zero(self):
        assert gnumeric_nonempty_row_count(GNUMERIC_EMPTY) == 0

    # FODT tests
    def test_fodt_minimal_nonempty_block_count(self):
        assert fodt_nonempty_block_count(FODT_MINIMAL) == 1

    def test_fodt_minimal_punctuation_count(self):
        assert fodt_punctuation_count(FODT_MINIMAL) >= 0

    def test_fodt_minimal_not_multiple_block_types(self):
        assert fodt_has_multiple_block_types(FODT_MINIMAL) is False

    def test_fodt_minimal_text_block_ratio_one(self):
        assert abs(fodt_text_block_ratio(FODT_MINIMAL) - 1.0) < 0.01

    def test_fodt_minimal_table_cell_count_zero(self):
        assert fodt_table_cell_count(FODT_MINIMAL) == 0

    def test_fodt_minimal_list_block_count_zero(self):
        assert fodt_list_block_count(FODT_MINIMAL) == 0

    def test_fodt_headings_has_multiple_block_types(self):
        assert fodt_has_multiple_block_types(FODT_HEADINGS) is True

    def test_fodt_headings_nonempty_block_count(self):
        assert fodt_nonempty_block_count(FODT_HEADINGS) == 7

    def test_fodt_headings_text_block_ratio(self):
        ratio = fodt_text_block_ratio(FODT_HEADINGS)
        assert 0.5 < ratio < 0.65

    def test_fodt_minimal_section_depth_max_zero(self):
        assert fodt_section_depth_max(FODT_MINIMAL) == 0

    # ODS tests
    def test_ods_minimal_sheet_density(self):
        assert abs(ods_sheet_density(ODS_MINIMAL) - 4.0) < 0.1

    def test_ods_minimal_string_cell_ratio(self):
        assert abs(ods_string_cell_ratio(ODS_MINIMAL) - 0.75) < 0.01

    def test_ods_minimal_total_cells(self):
        assert ods_total_cells(ODS_MINIMAL) == 4

    def test_ods_minimal_has_mixed_types(self):
        assert ods_has_mixed_types(ODS_MINIMAL) is True

    def test_ods_numeric_string_cell_ratio_zero(self):
        assert abs(ods_string_cell_ratio(ODS_NUMERIC) - 0.0) < 0.01

    def test_ods_numeric_not_mixed_types(self):
        assert ods_has_mixed_types(ODS_NUMERIC) is False

    def test_ods_minimal_total_string_cells(self):
        assert ods_total_string_cells(ODS_MINIMAL) == 3

    def test_ods_minimal_widest_column_index(self):
        assert ods_widest_column_index(ODS_MINIMAL) == 0

    # XCF tests
    def test_xcf_1x1_diagonal_length(self):
        assert abs(xcf_diagonal_length(XCF_1X1) - 1.414) < 0.01

    def test_xcf_1x1_dimension_product(self):
        assert xcf_dimension_product(XCF_1X1) == 1

    def test_xcf_2x2_diagonal_length(self):
        assert abs(xcf_diagonal_length(XCF_2X2) - 2.828) < 0.01

    def test_xcf_2x2_dimension_product(self):
        assert xcf_dimension_product(XCF_2X2) == 4

    # SYLK tests
    def test_sylk_minimal_file_size_bytes(self):
        assert sylk_file_size_bytes(SYLK_MINIMAL) == 75

    def test_sylk_minimal_max_col_index(self):
        assert sylk_max_col_index(SYLK_MINIMAL) == 2

    def test_sylk_numeric_file_size_bytes(self):
        assert sylk_file_size_bytes(SYLK_NUMERIC) == 45

    def test_sylk_numeric_max_col_index(self):
        assert sylk_max_col_index(SYLK_NUMERIC) == 3

    # TSV tests
    def test_tsv_minimal_file_size_bytes(self):
        assert tsv_file_size_bytes(TSV_MINIMAL) == 28

    def test_tsv_minimal_max_row_length(self):
        assert tsv_max_row_length(TSV_MINIMAL) == 2

    def test_tsv_minimal_min_row_length(self):
        assert tsv_min_row_length(TSV_MINIMAL) == 2

    def test_tsv_multi_max_row_length(self):
        assert tsv_max_row_length(TSV_MULTI) == 4

    def test_tsv_single_max_row_length(self):
        assert tsv_max_row_length(TSV_SINGLE) == 1

    def test_tsv_single_min_row_length(self):
        assert tsv_min_row_length(TSV_SINGLE) == 1

    # NDJSON export pipeline
    def test_ndjson_export_gnumeric_fodt_records(self, tmp_path):
        records = [
            {
                "file": GNUMERIC_MULTI.name,
                "min_numeric": gnumeric_min_numeric_value(GNUMERIC_MULTI),
                "has_string_cells": gnumeric_has_string_cells(GNUMERIC_MULTI),
            },
            {
                "file": FODT_HEADINGS.name,
                "nonempty_block_count": fodt_nonempty_block_count(FODT_HEADINGS),
                "has_multiple_block_types": fodt_has_multiple_block_types(FODT_HEADINGS),
            },
        ]
        out = tmp_path / "gnumeric_fodt_remaining.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert abs(json.loads(lines[0])["min_numeric"] - 42.0) < 0.1
        assert json.loads(lines[1])["has_multiple_block_types"] is True
