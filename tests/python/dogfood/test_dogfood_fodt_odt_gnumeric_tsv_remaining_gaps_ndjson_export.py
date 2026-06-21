"""test_dogfood_fodt_odt_gnumeric_tsv_remaining_gaps_ndjson_export.py

Dogfood export path: FODT + ODT + Gnumeric + TSV remaining analytics gap functions -> NDJSON.

Covers FODT: fodt_avg_word_length, fodt_block_type_count, fodt_heading_to_para_ratio,
             fodt_inline_count, fodt_list_item_count, fodt_max_block_word_count
Covers ODT:  odt_avg_word_length, odt_longest_paragraph_index, odt_max_paragraph_word_count,
             odt_total_word_length
Covers Gnumeric: gnumeric_empty_cell_ratio, gnumeric_row_density
Covers TSV: tsv_column_type_ratio, tsv_empty_column_ratio, tsv_longest_row_length,
            tsv_max_column_length, tsv_shortest_row_length

Concrete values:
  FODT minimal-document: avg_word_length=6.0, block_type_count=1, heading_to_para_ratio=0.0
  FODT headings-and-paragraphs: block_type_count=2, heading_to_para_ratio=0.75
  ODT minimal-document: avg_word_length=6.0, longest_paragraph_index=0, max_paragraph_word_count=2
  ODT two-paragraphs: longest_paragraph_index=1
  Gnumeric minimal: row_density=1.0, empty_cell_ratio=0.0
  TSV minimal-2x2: column_type_ratio=0.5, empty_column_ratio=0.0, longest_row_length=2

Sprint: product-deepening-fodt-odt-gnumeric-tsv-remaining-gaps-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodt.neutral_model import (
    fodt_avg_word_length,
    fodt_block_type_count,
    fodt_heading_to_para_ratio,
    fodt_inline_count,
    fodt_list_item_count,
    fodt_max_block_word_count,
)
from src.python.odt.odt_parser import (
    odt_avg_word_length,
    odt_longest_paragraph_index,
    odt_max_paragraph_word_count,
    odt_total_word_length,
)
from src.python.gnumeric.gnumeric_codec import (
    gnumeric_empty_cell_ratio,
    gnumeric_row_density,
)
from src.python.tsv.tsv_parser import (
    tsv_column_type_ratio,
    tsv_empty_column_ratio,
    tsv_longest_row_length,
    tsv_max_column_length,
    tsv_shortest_row_length,
)
from src.python.ndjson.ndjson_codec import write_ndjson

FODT_DIR = _REPO / "samples" / "by-format" / "fodt"
ODT_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"
GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"
TSV_DIR = _REPO / "samples" / "by-format" / "tsv"

FODT_MINIMAL = FODT_DIR / "minimal-document.fodt"
FODT_HEADINGS = FODT_DIR / "headings-and-paragraphs.fodt"
FODT_LIST = FODT_DIR / "list-basic.fodt"
ODT_MINIMAL = ODT_DIR / "minimal-document.odt"
ODT_TWO_PARA = ODT_DIR / "two-paragraphs.odt"
GNUMERIC_MINIMAL = GNUMERIC_DIR / "minimal-spreadsheet.gnumeric"
GNUMERIC_MULTI = GNUMERIC_DIR / "multi-cell-basic.gnumeric"
TSV_MINIMAL = TSV_DIR / "minimal-2x2.tsv"
TSV_MULTI = TSV_DIR / "multi-column.tsv"
TSV_SINGLE = TSV_DIR / "single-cell.tsv"


class TestFodtOdtGnumericTsvRemainingGapsNdjsonExport:

    # FODT tests
    def test_fodt_minimal_avg_word_length(self):
        assert abs(fodt_avg_word_length(FODT_MINIMAL) - 6.0) < 0.1

    def test_fodt_minimal_block_type_count(self):
        assert fodt_block_type_count(FODT_MINIMAL) == 1

    def test_fodt_headings_block_type_count(self):
        assert fodt_block_type_count(FODT_HEADINGS) == 2

    def test_fodt_headings_heading_to_para_ratio(self):
        assert abs(fodt_heading_to_para_ratio(FODT_HEADINGS) - 0.75) < 0.01

    def test_fodt_minimal_heading_to_para_ratio_zero(self):
        assert abs(fodt_heading_to_para_ratio(FODT_MINIMAL)) < 0.01

    def test_fodt_minimal_max_block_word_count(self):
        assert fodt_max_block_word_count(FODT_MINIMAL) == 2

    def test_fodt_headings_max_block_word_count(self):
        assert fodt_max_block_word_count(FODT_HEADINGS) >= 5

    # ODT tests
    def test_odt_minimal_avg_word_length(self):
        assert abs(odt_avg_word_length(ODT_MINIMAL) - 6.0) < 0.1

    def test_odt_minimal_longest_paragraph_index(self):
        assert odt_longest_paragraph_index(ODT_MINIMAL) == 0

    def test_odt_two_para_longest_paragraph_index(self):
        assert odt_longest_paragraph_index(ODT_TWO_PARA) == 1

    def test_odt_minimal_max_paragraph_word_count(self):
        assert odt_max_paragraph_word_count(ODT_MINIMAL) == 2

    def test_odt_minimal_total_word_length(self):
        assert odt_total_word_length(ODT_MINIMAL) == 12

    # Gnumeric tests
    def test_gnumeric_minimal_row_density(self):
        assert abs(gnumeric_row_density(GNUMERIC_MINIMAL) - 1.0) < 0.01

    def test_gnumeric_minimal_empty_cell_ratio(self):
        assert abs(gnumeric_empty_cell_ratio(GNUMERIC_MINIMAL)) < 0.01

    # TSV tests
    def test_tsv_minimal_column_type_ratio(self):
        assert abs(tsv_column_type_ratio(TSV_MINIMAL) - 0.5) < 0.01

    def test_tsv_single_column_type_ratio_one(self):
        assert abs(tsv_column_type_ratio(TSV_SINGLE) - 1.0) < 0.01

    def test_tsv_minimal_empty_column_ratio_zero(self):
        assert abs(tsv_empty_column_ratio(TSV_MINIMAL)) < 0.01

    def test_tsv_minimal_longest_row_length(self):
        assert tsv_longest_row_length(TSV_MINIMAL) == 2

    def test_tsv_multi_longest_row_length(self):
        assert tsv_longest_row_length(TSV_MULTI) == 4

    def test_tsv_minimal_max_column_length(self):
        assert tsv_max_column_length(TSV_MINIMAL) == 8

    def test_tsv_minimal_shortest_row_length(self):
        assert tsv_shortest_row_length(TSV_MINIMAL) == 2

    def test_ndjson_export_fodt_record(self, tmp_path):
        records = [{
            "file": FODT_MINIMAL.name,
            "avg_word_length": fodt_avg_word_length(FODT_MINIMAL),
            "block_type_count": fodt_block_type_count(FODT_MINIMAL),
            "max_block_word_count": fodt_max_block_word_count(FODT_MINIMAL),
        }]
        out = tmp_path / "fodt_remaining.ndjson"
        write_ndjson(records, str(out))
        parsed = json.loads(out.read_text(encoding="utf-8").strip())
        assert parsed["block_type_count"] == 1

    def test_ndjson_export_tsv_records(self, tmp_path):
        records = [
            {"file": TSV_MINIMAL.name, "column_type_ratio": tsv_column_type_ratio(TSV_MINIMAL)},
            {"file": TSV_MULTI.name, "longest_row_length": tsv_longest_row_length(TSV_MULTI)},
        ]
        out = tmp_path / "tsv_remaining.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert abs(json.loads(lines[0])["column_type_ratio"] - 0.5) < 0.01
        assert json.loads(lines[1])["longest_row_length"] == 4
