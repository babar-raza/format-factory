"""test_dogfood_dif_fodp_ndjson_odt_sylk_tsv_ppm_batch2_remaining_ndjson_export.py

Dogfood export path: DIF + FODP + NDJSON + ODT + SYLK + TSV + PPM batch-2 remaining analytics gap functions -> NDJSON.

Covers DIF: dif_string_field_count, dif_total_char_count, dif_avg_row_width, dif_header_count
Covers FODP: fodp_file_size_bytes, fodp_max_slide_text_length, fodp_min_slide_text_length,
             fodp_unique_slide_title_count, fodp_avg_shape_text_length
Covers NDJSON: ndjson_record_size_max, ndjson_nested_object_count
Covers ODT: odt_max_word_count_para, odt_min_word_count_para, odt_unique_paragraph_count,
            odt_avg_char_count_per_para
Covers SYLK: sylk_max_column_sum, sylk_empty_row_count
Covers TSV: tsv_string_field_count, tsv_total_field_count
Covers PPM: ppm_channel_sum, ppm_pixel_brightness_avg

Concrete values:
  DIF minimal-2x2: str_fields=6, total_chars=28, avg_row_width=8.0, headers=2
  DIF numeric-row: str_fields=0, total_chars=0, avg_row_width=3.0, headers=3
  FODP minimal: file_size=1713, max_text=0, min_text=0, unique_titles=0, avg_shape=0.0
  FODP two-slides: file_size=2240
  NDJSON tmp: record_size_max=2, nested_obj_count=1
  ODT minimal: max_word=2, min_word=2, unique_para=1, avg_char=13.0
  ODT two-paragraphs: unique_para=2, avg_char=16.5
  SYLK minimal-2x2: max_col_sum=42.0, empty_rows=0
  SYLK numeric-row: max_col_sum=3.0
  TSV minimal-2x2: str_fields=2, total_fields=4
  TSV single-cell: str_fields=0, total_fields=1
  PPM 1x1-red: channel_sum=255, brightness_avg=85.0
  PPM 2x2-rgbw: channel_sum=1530, brightness_avg=127.5

Sprint: product-deepening-dif-fodp-ndjson-odt-sylk-tsv-ppm-batch2-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.dif.dif_parser import (
    dif_string_field_count,
    dif_total_char_count,
    dif_avg_row_width,
    dif_header_count,
)
from src.python.fodp.fodp_codec import (
    fodp_file_size_bytes,
    fodp_max_slide_text_length,
    fodp_min_slide_text_length,
    fodp_unique_slide_title_count,
    fodp_avg_shape_text_length,
)
from src.python.ndjson.ndjson_codec import ndjson_record_size_max, ndjson_nested_object_count, write_ndjson
from src.python.odt.odt_parser import (
    odt_max_word_count_para,
    odt_min_word_count_para,
    odt_unique_paragraph_count,
    odt_avg_char_count_per_para,
)
from src.python.sylk.sylk_parser import sylk_max_column_sum, sylk_empty_row_count
from src.python.tsv.tsv_parser import tsv_string_field_count, tsv_total_field_count
from src.python.ppm.ppm_parser import ppm_channel_sum, ppm_pixel_brightness_avg

DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
FODP_DIR = _REPO / "samples" / "by-format" / "fodp"
ODT_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"
SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"
TSV_DIR = _REPO / "samples" / "by-format" / "tsv"
PPM_DIR = (_REPO / "samples" / "by-format" / "ppm" / "valid").resolve()

DIF_MINIMAL = DIF_DIR / "minimal-2x2.dif"
DIF_NUMERIC = DIF_DIR / "numeric-row.dif"
FODP_MINIMAL = FODP_DIR / "minimal-presentation.fodp"
FODP_TWO_SLIDES = FODP_DIR / "two-slides-basic.fodp"
ODT_MINIMAL = ODT_DIR / "minimal-document.odt"
ODT_TWO_PARA = ODT_DIR / "two-paragraphs.odt"
SYLK_MINIMAL = SYLK_DIR / "minimal-2x2.slk"
SYLK_NUMERIC = SYLK_DIR / "numeric-row.slk"
TSV_MINIMAL = TSV_DIR / "minimal-2x2.tsv"
TSV_SINGLE = TSV_DIR / "single-cell.tsv"
PPM_1X1_RED = PPM_DIR / "1x1-red.ppm"
PPM_2X2_RGBW = PPM_DIR / "2x2-rgbw.ppm"


class TestDifFodpNdjsonOdtSylkTsvPpmBatch2RemainingNdjsonExport:

    # DIF tests
    def test_dif_minimal_string_field_count(self):
        assert dif_string_field_count(DIF_MINIMAL) == 6

    def test_dif_numeric_string_field_count_zero(self):
        assert dif_string_field_count(DIF_NUMERIC) == 0

    def test_dif_minimal_total_char_count(self):
        assert dif_total_char_count(DIF_MINIMAL) == 28

    def test_dif_numeric_total_char_count_zero(self):
        assert dif_total_char_count(DIF_NUMERIC) == 0

    def test_dif_minimal_avg_row_width(self):
        assert abs(dif_avg_row_width(DIF_MINIMAL) - 8.0) < 0.1

    def test_dif_numeric_avg_row_width(self):
        assert abs(dif_avg_row_width(DIF_NUMERIC) - 3.0) < 0.1

    def test_dif_minimal_header_count(self):
        assert dif_header_count(DIF_MINIMAL) == 2

    def test_dif_numeric_header_count(self):
        assert dif_header_count(DIF_NUMERIC) == 3

    # FODP tests
    def test_fodp_minimal_file_size_bytes(self):
        assert fodp_file_size_bytes(FODP_MINIMAL) == 1713

    def test_fodp_two_slides_file_size_bytes(self):
        assert fodp_file_size_bytes(FODP_TWO_SLIDES) == 2240

    def test_fodp_minimal_max_slide_text_length_zero(self):
        assert fodp_max_slide_text_length(FODP_MINIMAL) == 0

    def test_fodp_minimal_min_slide_text_length_zero(self):
        assert fodp_min_slide_text_length(FODP_MINIMAL) == 0

    def test_fodp_minimal_unique_slide_title_count_zero(self):
        assert fodp_unique_slide_title_count(FODP_MINIMAL) == 0

    def test_fodp_minimal_avg_shape_text_length_zero(self):
        assert abs(fodp_avg_shape_text_length(FODP_MINIMAL)) < 0.01

    # NDJSON tests (using tmp_path)
    def test_ndjson_record_size_max(self, tmp_path):
        ndjson_file = tmp_path / "test.ndjson"
        ndjson_file.write_text(
            '{"a": 1, "b": {"c": 2}}\n{"x": "hello"}\n',
            encoding="utf-8"
        )
        assert ndjson_record_size_max(ndjson_file) == 2

    def test_ndjson_nested_object_count(self, tmp_path):
        ndjson_file = tmp_path / "test.ndjson"
        ndjson_file.write_text(
            '{"a": 1, "b": {"c": 2}}\n{"x": "hello"}\n',
            encoding="utf-8"
        )
        assert ndjson_nested_object_count(ndjson_file) == 1

    # ODT tests
    def test_odt_minimal_max_word_count_para(self):
        assert odt_max_word_count_para(ODT_MINIMAL) == 2

    def test_odt_minimal_min_word_count_para(self):
        assert odt_min_word_count_para(ODT_MINIMAL) == 2

    def test_odt_minimal_unique_paragraph_count(self):
        assert odt_unique_paragraph_count(ODT_MINIMAL) == 1

    def test_odt_two_para_unique_paragraph_count(self):
        assert odt_unique_paragraph_count(ODT_TWO_PARA) == 2

    def test_odt_minimal_avg_char_count_per_para(self):
        assert abs(odt_avg_char_count_per_para(ODT_MINIMAL) - 13.0) < 0.1

    def test_odt_two_para_avg_char_count_per_para(self):
        assert abs(odt_avg_char_count_per_para(ODT_TWO_PARA) - 16.5) < 0.1

    # SYLK tests
    def test_sylk_minimal_max_column_sum(self):
        assert abs(sylk_max_column_sum(SYLK_MINIMAL) - 42.0) < 0.1

    def test_sylk_numeric_max_column_sum(self):
        assert abs(sylk_max_column_sum(SYLK_NUMERIC) - 3.0) < 0.1

    def test_sylk_minimal_empty_row_count_zero(self):
        assert sylk_empty_row_count(SYLK_MINIMAL) == 0

    # TSV tests
    def test_tsv_minimal_string_field_count(self):
        assert tsv_string_field_count(TSV_MINIMAL) == 2

    def test_tsv_single_string_field_count_zero(self):
        assert tsv_string_field_count(TSV_SINGLE) == 0

    def test_tsv_minimal_total_field_count(self):
        assert tsv_total_field_count(TSV_MINIMAL) == 4

    def test_tsv_single_total_field_count(self):
        assert tsv_total_field_count(TSV_SINGLE) == 1

    # PPM tests
    def test_ppm_1x1_channel_sum(self):
        assert ppm_channel_sum(PPM_1X1_RED) == 255

    def test_ppm_2x2_channel_sum(self):
        assert ppm_channel_sum(PPM_2X2_RGBW) == 1530

    def test_ppm_1x1_pixel_brightness_avg(self):
        assert abs(ppm_pixel_brightness_avg(PPM_1X1_RED) - 85.0) < 0.1

    def test_ppm_2x2_pixel_brightness_avg(self):
        assert abs(ppm_pixel_brightness_avg(PPM_2X2_RGBW) - 127.5) < 0.1

    # NDJSON export pipeline
    def test_ndjson_export_dif_odt_records(self, tmp_path):
        records = [
            {
                "file": DIF_MINIMAL.name,
                "string_field_count": dif_string_field_count(DIF_MINIMAL),
                "header_count": dif_header_count(DIF_MINIMAL),
            },
            {
                "file": ODT_TWO_PARA.name,
                "unique_paragraphs": odt_unique_paragraph_count(ODT_TWO_PARA),
                "avg_char_per_para": odt_avg_char_count_per_para(ODT_TWO_PARA),
            },
        ]
        out = tmp_path / "dif_odt_batch2.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert json.loads(lines[0])["string_field_count"] == 6
        assert json.loads(lines[1])["unique_paragraphs"] == 2
