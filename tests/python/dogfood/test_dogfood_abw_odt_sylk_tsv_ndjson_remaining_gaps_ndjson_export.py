"""test_dogfood_abw_odt_sylk_tsv_ndjson_remaining_gaps_ndjson_export.py

Dogfood export path: ABW + ODT + SYLK + TSV + NDJSON remaining analytics gap functions -> NDJSON.

Covers ABW: abw_text_density, abw_total_word_length
Covers ODT: odt_has_repeated_words, odt_word_length_range
Covers SYLK: sylk_avg_value_length, sylk_has_string_cols, sylk_max_row_sum,
             sylk_row_density_variance, sylk_value_length_sum
Covers TSV: tsv_data_completeness, tsv_has_only_numeric, tsv_header_length_avg,
            tsv_is_wider_than_tall
Covers NDJSON: ndjson_avg_field_count, ndjson_empty_string_count, ndjson_max_key_count,
               ndjson_nonempty_record_count, ndjson_nonempty_record_ratio

Concrete values:
  ABW minimal: text_density=1.0, total_word_length=5
  ABW two-paragraphs: text_density=0.91, total_word_length=31
  ODT minimal: has_repeated_words=False, word_length_range=0
  ODT two-paragraphs: has_repeated_words=True, word_length_range=5
  SYLK minimal-2x2: avg_value_length=4.0, has_string_cols=True, max_row_sum=42.0,
                    row_density_variance=0.0, value_length_sum=16
  SYLK numeric-row: has_string_cols=False, max_row_sum=6.0, value_length_sum=3
  TSV minimal-2x2: completeness=1.0, has_only_numeric=False, header_len_avg=3.5, is_wider=False
  TSV single-cell: has_only_numeric=True
  TSV multi-column: is_wider=True
  NDJSON test: avg_field_count=3.0, empty_string_count=2, max_key_count=3, nonempty_record_count=2

Sprint: product-deepening-abw-odt-sylk-tsv-ndjson-remaining-gaps-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.abw.abw_codec import abw_text_density, abw_total_word_length
from src.python.odt.odt_parser import odt_has_repeated_words, odt_word_length_range
from src.python.sylk.sylk_parser import (
    sylk_avg_value_length,
    sylk_has_string_cols,
    sylk_max_row_sum,
    sylk_row_density_variance,
    sylk_value_length_sum,
)
from src.python.tsv.tsv_parser import (
    tsv_data_completeness,
    tsv_has_only_numeric,
    tsv_header_length_avg,
    tsv_is_wider_than_tall,
)
from src.python.ndjson.ndjson_codec import (
    ndjson_avg_field_count,
    ndjson_empty_string_count,
    ndjson_max_key_count,
    ndjson_nonempty_record_count,
    ndjson_nonempty_record_ratio,
    write_ndjson,
)

ABW_DIR = _REPO / "samples" / "by-format" / "abw"
ODT_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"
SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"
TSV_DIR = _REPO / "samples" / "by-format" / "tsv"

ABW_MINIMAL = ABW_DIR / "minimal-document.abw"
ABW_TWO_PARA = ABW_DIR / "two-paragraphs.abw"
ODT_MINIMAL = ODT_DIR / "minimal-document.odt"
ODT_TWO_PARA = ODT_DIR / "two-paragraphs.odt"
SYLK_MINIMAL = SYLK_DIR / "minimal-2x2.slk"
SYLK_NUMERIC = SYLK_DIR / "numeric-row.slk"
TSV_MINIMAL = TSV_DIR / "minimal-2x2.tsv"
TSV_MULTI = TSV_DIR / "multi-column.tsv"
TSV_SINGLE = TSV_DIR / "single-cell.tsv"


class TestAbwOdtSylkTsvNdjsonRemainingGapsNdjsonExport:

    # ABW tests
    def test_abw_minimal_text_density_one(self):
        assert abs(abw_text_density(ABW_MINIMAL) - 1.0) < 0.01

    def test_abw_two_para_text_density(self):
        val = abw_text_density(ABW_TWO_PARA)
        assert 0.8 < val < 1.0

    def test_abw_minimal_total_word_length(self):
        assert abw_total_word_length(ABW_MINIMAL) == 5

    def test_abw_two_para_total_word_length(self):
        assert abw_total_word_length(ABW_TWO_PARA) == 31

    # ODT tests
    def test_odt_minimal_no_repeated_words(self):
        assert odt_has_repeated_words(ODT_MINIMAL) is False

    def test_odt_two_para_has_repeated_words(self):
        assert odt_has_repeated_words(ODT_TWO_PARA) is True

    def test_odt_minimal_word_length_range_zero(self):
        assert odt_word_length_range(ODT_MINIMAL) == 0

    def test_odt_two_para_word_length_range_positive(self):
        assert odt_word_length_range(ODT_TWO_PARA) > 0

    # SYLK tests
    def test_sylk_minimal_avg_value_length(self):
        assert abs(sylk_avg_value_length(SYLK_MINIMAL) - 4.0) < 0.1

    def test_sylk_numeric_avg_value_length(self):
        assert abs(sylk_avg_value_length(SYLK_NUMERIC) - 1.0) < 0.1

    def test_sylk_minimal_has_string_cols(self):
        assert sylk_has_string_cols(SYLK_MINIMAL) is True

    def test_sylk_numeric_has_no_string_cols(self):
        assert sylk_has_string_cols(SYLK_NUMERIC) is False

    def test_sylk_minimal_max_row_sum(self):
        assert abs(sylk_max_row_sum(SYLK_MINIMAL) - 42.0) < 0.1

    def test_sylk_minimal_row_density_variance_zero(self):
        assert abs(sylk_row_density_variance(SYLK_MINIMAL)) < 0.01

    def test_sylk_minimal_value_length_sum(self):
        assert sylk_value_length_sum(SYLK_MINIMAL) == 16

    def test_sylk_numeric_value_length_sum(self):
        assert sylk_value_length_sum(SYLK_NUMERIC) == 3

    # TSV tests
    def test_tsv_minimal_data_completeness_one(self):
        assert abs(tsv_data_completeness(TSV_MINIMAL) - 1.0) < 0.01

    def test_tsv_minimal_not_only_numeric(self):
        assert tsv_has_only_numeric(TSV_MINIMAL) is False

    def test_tsv_single_has_only_numeric(self):
        assert tsv_has_only_numeric(TSV_SINGLE) is True

    def test_tsv_minimal_header_length_avg(self):
        assert abs(tsv_header_length_avg(TSV_MINIMAL) - 3.5) < 0.1

    def test_tsv_minimal_not_wider_than_tall(self):
        assert tsv_is_wider_than_tall(TSV_MINIMAL) is False

    def test_tsv_multi_is_wider_than_tall(self):
        assert tsv_is_wider_than_tall(TSV_MULTI) is True

    # NDJSON tests (using tmp_path)
    def test_ndjson_avg_field_count(self, tmp_path):
        ndjson_file = tmp_path / "test.ndjson"
        ndjson_file.write_text(
            '{"a": 1, "b": "hello", "c": ""}\n{"a": 2, "b": "world", "c": ""}\n',
            encoding="utf-8"
        )
        assert abs(ndjson_avg_field_count(ndjson_file) - 3.0) < 0.01

    def test_ndjson_empty_string_count(self, tmp_path):
        ndjson_file = tmp_path / "test.ndjson"
        ndjson_file.write_text(
            '{"a": 1, "b": "hello", "c": ""}\n{"a": 2, "b": "world", "c": ""}\n',
            encoding="utf-8"
        )
        assert ndjson_empty_string_count(ndjson_file) == 2

    def test_ndjson_max_key_count(self, tmp_path):
        ndjson_file = tmp_path / "test.ndjson"
        ndjson_file.write_text(
            '{"a": 1, "b": 2, "c": 3}\n{"x": 1}\n',
            encoding="utf-8"
        )
        assert ndjson_max_key_count(ndjson_file) == 3

    def test_ndjson_nonempty_record_count(self, tmp_path):
        ndjson_file = tmp_path / "test.ndjson"
        write_ndjson([{"a": 1}, {"b": 2}], str(ndjson_file))
        assert ndjson_nonempty_record_count(ndjson_file) == 2

    def test_ndjson_nonempty_record_ratio(self, tmp_path):
        ndjson_file = tmp_path / "test.ndjson"
        write_ndjson([{"a": 1}, {"b": 2}], str(ndjson_file))
        assert abs(ndjson_nonempty_record_ratio(ndjson_file) - 1.0) < 0.01

    def test_ndjson_export_abw_sylk_records(self, tmp_path):
        records = [
            {"file": ABW_MINIMAL.name, "text_density": abw_text_density(ABW_MINIMAL), "total_word_length": abw_total_word_length(ABW_MINIMAL)},
            {"file": SYLK_MINIMAL.name, "has_string_cols": sylk_has_string_cols(SYLK_MINIMAL), "value_length_sum": sylk_value_length_sum(SYLK_MINIMAL)},
        ]
        out = tmp_path / "abw_sylk_remaining.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert json.loads(lines[0])["total_word_length"] == 5
        assert json.loads(lines[1])["has_string_cols"] is True
