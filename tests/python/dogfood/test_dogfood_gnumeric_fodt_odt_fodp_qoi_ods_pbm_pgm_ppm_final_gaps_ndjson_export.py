"""test_dogfood_gnumeric_fodt_odt_fodp_qoi_ods_pbm_pgm_ppm_final_gaps_ndjson_export.py

Dogfood export path: GNUMERIC + FODT + ODT + FODP + QOI + ODS + PBM + PGM + PPM
                     final remaining analytics gap functions -> NDJSON.

Covers GNUMERIC: gnumeric_numeric_range, gnumeric_distinct_string_count, gnumeric_file_size_bytes,
                 gnumeric_unique_value_count, gnumeric_max_sheet_cell_count,
                 gnumeric_min_sheet_cell_count, gnumeric_avg_sheet_cell_count
Covers FODT: fodt_heading_text_ratio, fodt_longest_heading_length, fodt_file_size_bytes,
             fodt_unique_block_type_count, fodt_avg_paragraph_length
Covers ODT: odt_all_words_unique, odt_avg_word_count_per_para
Covers FODP: fodp_avg_text_per_slide, fodp_shape_slide_ratio
Covers QOI: qoi_green_channel_avg, qoi_blue_channel_avg
Covers ODS: ods_column_fill_rate, ods_file_size_bytes, ods_unique_value_count,
            ods_max_sheet_cell_count, ods_min_sheet_cell_count, ods_avg_nonempty_cells_per_sheet
Covers PBM: pbm_is_single_pixel, pbm_black_exceeds_white, pbm_edge_pixel_sum, pbm_center_pixel_value
Covers PGM: pgm_is_single_pixel, pgm_has_only_extremes, pgm_highlight_count, pgm_column_mean
Covers PPM: ppm_avg_red_channel, ppm_is_single_pixel, ppm_warm_pixel_ratio

Concrete values:
  GNUMERIC minimal: numeric_range=0.0, distinct_str=1, file_size=307, unique=1, max_sheet=1, avg=1.0
  GNUMERIC multi: distinct_str=4, file_size=337, unique=4, max_sheet=4
  GNUMERIC empty: distinct_str=0, unique=0
  FODT minimal: heading_ratio=0.0, longest_heading=0, file_size=1030, unique_block=1, avg_para=13.0
  FODT headings: heading_ratio=0.4285, longest=16, file_size=2063, unique_block=2, avg_para=59.25
  ODT minimal: all_unique=True, avg_word_count=2.0
  ODT two-para: all_unique=False, avg_word_count=2.0
  FODP minimal: avg_text=0.0, shape_ratio=0.0
  QOI 1x1-red: green_avg=0.0, blue_avg=0.0
  QOI 4x1-gradient: green_avg=127.5, blue_avg=127.5
  ODS minimal: col_fill=1.0, file_size=1338, unique=4, max_sheet=4, avg=4.0
  ODS single-cell: unique=1, max_sheet=1
  PBM 1x1-black: is_single=True, black_exceeds=True, edge_sum=1, center=1
  PBM 2x2-checker: is_single=False, black_exceeds=False, edge_sum=2
  PGM 1x1-white: is_single=True, has_extremes=True, highlight=1, col_mean=255.0
  PGM 2x2-gradient: is_single=False, has_extremes=False, highlight=2, col_mean=127.5
  PPM 1x1-red: avg_red=255.0, is_single=True, warm_ratio=1.0
  PPM 2x2-rgbw: avg_red=127.5, is_single=False, warm_ratio=0.25
  PPM 3x1-gradient: warm_ratio=0.0

Sprint: product-deepening-final-gaps-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.gnumeric.gnumeric_codec import (
    gnumeric_numeric_range,
    gnumeric_distinct_string_count,
    gnumeric_file_size_bytes,
    gnumeric_unique_value_count,
    gnumeric_max_sheet_cell_count,
    gnumeric_min_sheet_cell_count,
    gnumeric_avg_sheet_cell_count,
)
from src.python.fodt.neutral_model import (
    fodt_heading_text_ratio,
    fodt_longest_heading_length,
    fodt_file_size_bytes,
    fodt_unique_block_type_count,
    fodt_avg_paragraph_length,
)
from src.python.odt.odt_parser import odt_all_words_unique, odt_avg_word_count_per_para
from src.python.fodp.fodp_codec import fodp_avg_text_per_slide, fodp_shape_slide_ratio
from src.python.qoi.qoi_parser import qoi_green_channel_avg, qoi_blue_channel_avg
from src.python.ods.ods_parser import (
    ods_column_fill_rate,
    ods_file_size_bytes,
    ods_unique_value_count,
    ods_max_sheet_cell_count,
    ods_min_sheet_cell_count,
    ods_avg_nonempty_cells_per_sheet,
)
from src.python.pbm.pbm_parser import (
    pbm_is_single_pixel,
    pbm_black_exceeds_white,
    pbm_edge_pixel_sum,
    pbm_center_pixel_value,
)
from src.python.pgm.pgm_parser import (
    pgm_is_single_pixel,
    pgm_has_only_extremes,
    pgm_highlight_count,
    pgm_column_mean,
)
from src.python.ppm.ppm_parser import ppm_avg_red_channel, ppm_is_single_pixel, ppm_warm_pixel_ratio
from src.python.ndjson.ndjson_codec import write_ndjson

GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"
FODT_DIR = _REPO / "samples" / "by-format" / "fodt"
ODT_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"
FODP_DIR = _REPO / "samples" / "by-format" / "fodp"
QOI_DIR = (_REPO / "samples" / "by-format" / "qoi" / "valid").resolve()
ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"
PBM_DIR = (_REPO / "samples" / "by-format" / "pbm" / "valid").resolve()
PGM_DIR = (_REPO / "samples" / "by-format" / "pgm" / "valid").resolve()
PPM_DIR = (_REPO / "samples" / "by-format" / "ppm" / "valid").resolve()

GNUMERIC_MINIMAL = GNUMERIC_DIR / "minimal-spreadsheet.gnumeric"
GNUMERIC_MULTI = GNUMERIC_DIR / "multi-cell-basic.gnumeric"
GNUMERIC_EMPTY = GNUMERIC_DIR / "empty-sheet.gnumeric"
FODT_MINIMAL = FODT_DIR / "minimal-document.fodt"
FODT_HEADINGS = FODT_DIR / "headings-and-paragraphs.fodt"
ODT_MINIMAL = ODT_DIR / "minimal-document.odt"
ODT_TWO_PARA = ODT_DIR / "two-paragraphs.odt"
FODP_MINIMAL = FODP_DIR / "minimal-presentation.fodp"
QOI_1X1_RED = QOI_DIR / "1x1-red.qoi"
QOI_4X1_GRADIENT = QOI_DIR / "4x1-gradient.qoi"
QOI_2X2_BLACK = QOI_DIR / "2x2-black.qoi"
ODS_MINIMAL = ODS_DIR / "minimal-spreadsheet.ods"
ODS_SINGLE = ODS_DIR / "single-cell.ods"
PBM_1X1_BLACK = PBM_DIR / "1x1-black.pbm"
PBM_2X2_CHECKER = PBM_DIR / "2x2-checker.pbm"
PGM_1X1_WHITE = PGM_DIR / "1x1-white.pgm"
PGM_2X2_GRADIENT = PGM_DIR / "2x2-gradient.pgm"
PPM_1X1_RED = PPM_DIR / "1x1-red.ppm"
PPM_2X2_RGBW = PPM_DIR / "2x2-rgbw.ppm"
PPM_3X1_GRADIENT = PPM_DIR / "3x1-gradient.ppm"


class TestFinalGapsNdjsonExport:

    # GNUMERIC tests
    def test_gnumeric_minimal_numeric_range_zero(self):
        assert abs(gnumeric_numeric_range(GNUMERIC_MINIMAL)) < 0.01

    def test_gnumeric_minimal_distinct_string_count(self):
        assert gnumeric_distinct_string_count(GNUMERIC_MINIMAL) == 1

    def test_gnumeric_multi_distinct_string_count(self):
        assert gnumeric_distinct_string_count(GNUMERIC_MULTI) == 4

    def test_gnumeric_empty_distinct_string_count_zero(self):
        assert gnumeric_distinct_string_count(GNUMERIC_EMPTY) == 0

    def test_gnumeric_minimal_file_size_bytes(self):
        assert gnumeric_file_size_bytes(GNUMERIC_MINIMAL) == 307

    def test_gnumeric_minimal_unique_value_count(self):
        assert gnumeric_unique_value_count(GNUMERIC_MINIMAL) == 1

    def test_gnumeric_multi_unique_value_count(self):
        assert gnumeric_unique_value_count(GNUMERIC_MULTI) == 4

    def test_gnumeric_minimal_max_sheet_cell_count(self):
        assert gnumeric_max_sheet_cell_count(GNUMERIC_MINIMAL) == 1

    def test_gnumeric_multi_max_sheet_cell_count(self):
        assert gnumeric_max_sheet_cell_count(GNUMERIC_MULTI) == 4

    def test_gnumeric_minimal_avg_sheet_cell_count(self):
        assert abs(gnumeric_avg_sheet_cell_count(GNUMERIC_MINIMAL) - 1.0) < 0.01

    # FODT tests
    def test_fodt_minimal_heading_text_ratio_zero(self):
        assert abs(fodt_heading_text_ratio(FODT_MINIMAL)) < 0.01

    def test_fodt_headings_heading_text_ratio(self):
        ratio = fodt_heading_text_ratio(FODT_HEADINGS)
        assert 0.4 < ratio < 0.5

    def test_fodt_minimal_longest_heading_zero(self):
        assert fodt_longest_heading_length(FODT_MINIMAL) == 0

    def test_fodt_headings_longest_heading(self):
        assert fodt_longest_heading_length(FODT_HEADINGS) == 16

    def test_fodt_minimal_file_size_bytes(self):
        assert fodt_file_size_bytes(FODT_MINIMAL) == 1030

    def test_fodt_minimal_unique_block_type_count(self):
        assert fodt_unique_block_type_count(FODT_MINIMAL) == 1

    def test_fodt_headings_unique_block_type_count(self):
        assert fodt_unique_block_type_count(FODT_HEADINGS) == 2

    def test_fodt_minimal_avg_paragraph_length(self):
        assert abs(fodt_avg_paragraph_length(FODT_MINIMAL) - 13.0) < 0.1

    # ODT tests
    def test_odt_minimal_all_words_unique(self):
        assert odt_all_words_unique(ODT_MINIMAL) is True

    def test_odt_two_para_not_all_words_unique(self):
        assert odt_all_words_unique(ODT_TWO_PARA) is False

    def test_odt_minimal_avg_word_count_per_para(self):
        assert abs(odt_avg_word_count_per_para(ODT_MINIMAL) - 2.0) < 0.1

    # FODP tests
    def test_fodp_minimal_avg_text_per_slide_zero(self):
        assert abs(fodp_avg_text_per_slide(FODP_MINIMAL)) < 0.01

    def test_fodp_minimal_shape_slide_ratio_zero(self):
        assert abs(fodp_shape_slide_ratio(FODP_MINIMAL)) < 0.01

    # QOI tests
    def test_qoi_1x1_green_channel_avg_zero(self):
        assert abs(qoi_green_channel_avg(QOI_1X1_RED)) < 0.1

    def test_qoi_1x1_blue_channel_avg_zero(self):
        assert abs(qoi_blue_channel_avg(QOI_1X1_RED)) < 0.1

    def test_qoi_gradient_green_channel_avg(self):
        assert abs(qoi_green_channel_avg(QOI_4X1_GRADIENT) - 127.5) < 0.1

    def test_qoi_gradient_blue_channel_avg(self):
        assert abs(qoi_blue_channel_avg(QOI_4X1_GRADIENT) - 127.5) < 0.1

    # ODS tests
    def test_ods_minimal_column_fill_rate_one(self):
        assert abs(ods_column_fill_rate(ODS_MINIMAL) - 1.0) < 0.01

    def test_ods_minimal_file_size_bytes(self):
        assert ods_file_size_bytes(ODS_MINIMAL) == 1338

    def test_ods_minimal_unique_value_count(self):
        assert ods_unique_value_count(ODS_MINIMAL) == 4

    def test_ods_single_unique_value_count(self):
        assert ods_unique_value_count(ODS_SINGLE) == 1

    def test_ods_minimal_max_sheet_cell_count(self):
        assert ods_max_sheet_cell_count(ODS_MINIMAL) == 4

    def test_ods_minimal_avg_nonempty_cells_per_sheet(self):
        assert abs(ods_avg_nonempty_cells_per_sheet(ODS_MINIMAL) - 4.0) < 0.01

    # PBM tests
    def test_pbm_1x1_is_single_pixel(self):
        assert pbm_is_single_pixel(PBM_1X1_BLACK) is True

    def test_pbm_2x2_not_single_pixel(self):
        assert pbm_is_single_pixel(PBM_2X2_CHECKER) is False

    def test_pbm_1x1_black_exceeds_white(self):
        assert pbm_black_exceeds_white(PBM_1X1_BLACK) is True

    def test_pbm_2x2_black_not_exceeds_white(self):
        assert pbm_black_exceeds_white(PBM_2X2_CHECKER) is False

    def test_pbm_1x1_edge_pixel_sum(self):
        assert pbm_edge_pixel_sum(PBM_1X1_BLACK) == 1

    def test_pbm_2x2_edge_pixel_sum(self):
        assert pbm_edge_pixel_sum(PBM_2X2_CHECKER) == 2

    def test_pbm_1x1_center_pixel_value(self):
        assert pbm_center_pixel_value(PBM_1X1_BLACK) == 1

    # PGM tests
    def test_pgm_1x1_is_single_pixel(self):
        assert pgm_is_single_pixel(PGM_1X1_WHITE) is True

    def test_pgm_2x2_not_single_pixel(self):
        assert pgm_is_single_pixel(PGM_2X2_GRADIENT) is False

    def test_pgm_1x1_has_only_extremes(self):
        assert pgm_has_only_extremes(PGM_1X1_WHITE) is True

    def test_pgm_2x2_not_only_extremes(self):
        assert pgm_has_only_extremes(PGM_2X2_GRADIENT) is False

    def test_pgm_1x1_highlight_count(self):
        assert pgm_highlight_count(PGM_1X1_WHITE) == 1

    def test_pgm_2x2_highlight_count(self):
        assert pgm_highlight_count(PGM_2X2_GRADIENT) == 2

    def test_pgm_1x1_column_mean(self):
        assert abs(pgm_column_mean(PGM_1X1_WHITE) - 255.0) < 0.1

    def test_pgm_2x2_column_mean(self):
        assert abs(pgm_column_mean(PGM_2X2_GRADIENT) - 127.5) < 0.1

    # PPM tests
    def test_ppm_1x1_avg_red_channel(self):
        assert abs(ppm_avg_red_channel(PPM_1X1_RED) - 255.0) < 0.1

    def test_ppm_2x2_avg_red_channel(self):
        assert abs(ppm_avg_red_channel(PPM_2X2_RGBW) - 127.5) < 0.1

    def test_ppm_1x1_is_single_pixel(self):
        assert ppm_is_single_pixel(PPM_1X1_RED) is True

    def test_ppm_2x2_not_single_pixel(self):
        assert ppm_is_single_pixel(PPM_2X2_RGBW) is False

    def test_ppm_1x1_warm_pixel_ratio_one(self):
        assert abs(ppm_warm_pixel_ratio(PPM_1X1_RED) - 1.0) < 0.01

    def test_ppm_3x1_warm_pixel_ratio_zero(self):
        assert abs(ppm_warm_pixel_ratio(PPM_3X1_GRADIENT)) < 0.01

    # NDJSON export pipeline
    def test_ndjson_export_gnumeric_ods_records(self, tmp_path):
        records = [
            {
                "file": GNUMERIC_MULTI.name,
                "distinct_string_count": gnumeric_distinct_string_count(GNUMERIC_MULTI),
                "unique_value_count": gnumeric_unique_value_count(GNUMERIC_MULTI),
            },
            {
                "file": ODS_MINIMAL.name,
                "unique_value_count": ods_unique_value_count(ODS_MINIMAL),
                "avg_nonempty_cells": ods_avg_nonempty_cells_per_sheet(ODS_MINIMAL),
            },
        ]
        out = tmp_path / "gnumeric_ods_final.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert json.loads(lines[0])["distinct_string_count"] == 4
        assert json.loads(lines[1])["unique_value_count"] == 4
