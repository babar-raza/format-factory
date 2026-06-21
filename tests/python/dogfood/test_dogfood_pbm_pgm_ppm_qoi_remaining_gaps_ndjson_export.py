"""test_dogfood_pbm_pgm_ppm_qoi_remaining_gaps_ndjson_export.py

Dogfood export path: PBM + PGM + PPM + QOI remaining analytics gap functions -> NDJSON.

Covers PBM: pbm_corner_pixel_sum, pbm_checkerboard_score, pbm_col_uniformity,
            pbm_avg_black_per_row, pbm_black_row_count, pbm_file_size_bytes, pbm_max_col_black_count
Covers PGM: pgm_pixel_range, pgm_shadow_pixel_count, pgm_col_uniformity, pgm_avg_pixel_per_row,
            pgm_file_size_bytes, pgm_unique_pixel_count
Covers PPM: ppm_max_channel_value, ppm_min_channel_value, ppm_file_size_bytes,
            ppm_unique_pixel_count, ppm_red_dominant_count, ppm_col_uniformity
Covers QOI: qoi_red_channel_avg, qoi_alpha_pixel_count, qoi_file_size_bytes, qoi_avg_red_channel,
            qoi_avg_green_channel, qoi_red_dominant_count, qoi_col_uniformity

Concrete values:
  PBM 1x1-black: corner_pixel_sum=4, checkerboard=0.0, col_uniformity=1.0,
                 avg_black_per_row=1.0, black_row_count=1, file_size=12, max_col_black=1
  PBM 2x2-checker: corner_pixel_sum=2, checkerboard=1.0, col_uniformity=0.0,
                   avg_black_per_row=1.0, black_row_count=0, file_size=19
  PGM 1x1-white: pixel_range=0, shadow=0, col_uniformity=1.0, avg_per_row=255.0, file_size=19, unique=1
  PGM 2x2-gradient: pixel_range=255, shadow=2, col_uniformity=0.0, avg=127.5, file_size=29, unique=4
  PPM 1x1-red: max_channel=255, min_channel=0, file_size=19, unique=1, red_dominant=1, col_uni=1.0
  PPM 2x2-rgbw: unique=4, red_dominant=1, col_uniformity=0.0, file_size=47
  PPM 3x1-gradient: unique=3, red_dominant=0, col_uniformity=1.0
  QOI 1x1-red: red_channel_avg=255.0, alpha_count=0, file_size=27, avg_red=255.0, avg_green=0.0,
               red_dominant=1, col_uni=1.0
  QOI 2x2-black: red_channel_avg=0.0, red_dominant=0, file_size=23
  QOI 4x1-gradient: red_channel_avg=127.5, avg_green=127.5

Sprint: product-deepening-pbm-pgm-ppm-qoi-remaining-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm.pbm_parser import (
    pbm_corner_pixel_sum,
    pbm_checkerboard_score,
    pbm_col_uniformity,
    pbm_avg_black_per_row,
    pbm_black_row_count,
    pbm_file_size_bytes,
    pbm_max_col_black_count,
)
from src.python.pgm.pgm_parser import (
    pgm_pixel_range,
    pgm_shadow_pixel_count,
    pgm_col_uniformity,
    pgm_avg_pixel_per_row,
    pgm_file_size_bytes,
    pgm_unique_pixel_count,
)
from src.python.ppm.ppm_parser import (
    ppm_max_channel_value,
    ppm_min_channel_value,
    ppm_file_size_bytes,
    ppm_unique_pixel_count,
    ppm_red_dominant_count,
    ppm_col_uniformity,
)
from src.python.qoi.qoi_parser import (
    qoi_red_channel_avg,
    qoi_alpha_pixel_count,
    qoi_file_size_bytes,
    qoi_avg_red_channel,
    qoi_avg_green_channel,
    qoi_red_dominant_count,
    qoi_col_uniformity,
)
from src.python.ndjson.ndjson_codec import write_ndjson

PBM_DIR = (_REPO / "samples" / "by-format" / "pbm" / "valid").resolve()
PGM_DIR = (_REPO / "samples" / "by-format" / "pgm" / "valid").resolve()
PPM_DIR = (_REPO / "samples" / "by-format" / "ppm" / "valid").resolve()
QOI_DIR = (_REPO / "samples" / "by-format" / "qoi" / "valid").resolve()

PBM_1X1_BLACK = PBM_DIR / "1x1-black.pbm"
PBM_2X2_CHECKER = PBM_DIR / "2x2-checker.pbm"
PGM_1X1_WHITE = PGM_DIR / "1x1-white.pgm"
PGM_2X2_GRADIENT = PGM_DIR / "2x2-gradient.pgm"
PGM_3X1_RAMP = PGM_DIR / "3x1-ramp.pgm"
PPM_1X1_RED = PPM_DIR / "1x1-red.ppm"
PPM_2X2_RGBW = PPM_DIR / "2x2-rgbw.ppm"
PPM_3X1_GRADIENT = PPM_DIR / "3x1-gradient.ppm"
QOI_1X1_RED = QOI_DIR / "1x1-red.qoi"
QOI_2X2_BLACK = QOI_DIR / "2x2-black.qoi"
QOI_4X1_GRADIENT = QOI_DIR / "4x1-gradient.qoi"


class TestPbmPgmPpmQoiRemainingGapsNdjsonExport:

    # PBM tests
    def test_pbm_1x1_corner_pixel_sum(self):
        assert pbm_corner_pixel_sum(PBM_1X1_BLACK) == 4

    def test_pbm_2x2_corner_pixel_sum(self):
        assert pbm_corner_pixel_sum(PBM_2X2_CHECKER) == 2

    def test_pbm_1x1_checkerboard_score_zero(self):
        assert abs(pbm_checkerboard_score(PBM_1X1_BLACK)) < 0.01

    def test_pbm_2x2_checkerboard_score_one(self):
        assert abs(pbm_checkerboard_score(PBM_2X2_CHECKER) - 1.0) < 0.01

    def test_pbm_1x1_col_uniformity_one(self):
        assert abs(pbm_col_uniformity(PBM_1X1_BLACK) - 1.0) < 0.01

    def test_pbm_2x2_col_uniformity_zero(self):
        assert abs(pbm_col_uniformity(PBM_2X2_CHECKER)) < 0.01

    def test_pbm_1x1_avg_black_per_row(self):
        assert abs(pbm_avg_black_per_row(PBM_1X1_BLACK) - 1.0) < 0.01

    def test_pbm_1x1_black_row_count(self):
        assert pbm_black_row_count(PBM_1X1_BLACK) == 1

    def test_pbm_2x2_black_row_count_zero(self):
        assert pbm_black_row_count(PBM_2X2_CHECKER) == 0

    def test_pbm_1x1_file_size_bytes(self):
        assert pbm_file_size_bytes(PBM_1X1_BLACK) == 12

    def test_pbm_2x2_file_size_bytes(self):
        assert pbm_file_size_bytes(PBM_2X2_CHECKER) == 19

    def test_pbm_1x1_max_col_black_count(self):
        assert pbm_max_col_black_count(PBM_1X1_BLACK) == 1

    # PGM tests
    def test_pgm_white_pixel_range_zero(self):
        assert pgm_pixel_range(PGM_1X1_WHITE) == 0

    def test_pgm_gradient_pixel_range(self):
        assert pgm_pixel_range(PGM_2X2_GRADIENT) == 255

    def test_pgm_white_shadow_pixel_count_zero(self):
        assert pgm_shadow_pixel_count(PGM_1X1_WHITE) == 0

    def test_pgm_gradient_shadow_pixel_count(self):
        assert pgm_shadow_pixel_count(PGM_2X2_GRADIENT) == 2

    def test_pgm_white_col_uniformity_one(self):
        assert abs(pgm_col_uniformity(PGM_1X1_WHITE) - 1.0) < 0.01

    def test_pgm_gradient_col_uniformity_zero(self):
        assert abs(pgm_col_uniformity(PGM_2X2_GRADIENT)) < 0.01

    def test_pgm_white_avg_pixel_per_row(self):
        assert abs(pgm_avg_pixel_per_row(PGM_1X1_WHITE) - 255.0) < 0.1

    def test_pgm_gradient_avg_pixel_per_row(self):
        assert abs(pgm_avg_pixel_per_row(PGM_2X2_GRADIENT) - 127.5) < 0.1

    def test_pgm_white_file_size_bytes(self):
        assert pgm_file_size_bytes(PGM_1X1_WHITE) == 19

    def test_pgm_white_unique_pixel_count(self):
        assert pgm_unique_pixel_count(PGM_1X1_WHITE) == 1

    def test_pgm_gradient_unique_pixel_count(self):
        assert pgm_unique_pixel_count(PGM_2X2_GRADIENT) == 4

    # PPM tests
    def test_ppm_1x1_max_channel_value(self):
        assert ppm_max_channel_value(PPM_1X1_RED) == 255

    def test_ppm_1x1_min_channel_value(self):
        assert ppm_min_channel_value(PPM_1X1_RED) == 0

    def test_ppm_1x1_file_size_bytes(self):
        assert ppm_file_size_bytes(PPM_1X1_RED) == 19

    def test_ppm_1x1_unique_pixel_count(self):
        assert ppm_unique_pixel_count(PPM_1X1_RED) == 1

    def test_ppm_2x2_unique_pixel_count(self):
        assert ppm_unique_pixel_count(PPM_2X2_RGBW) == 4

    def test_ppm_1x1_red_dominant_count(self):
        assert ppm_red_dominant_count(PPM_1X1_RED) == 1

    def test_ppm_3x1_red_dominant_count_zero(self):
        assert ppm_red_dominant_count(PPM_3X1_GRADIENT) == 0

    def test_ppm_1x1_col_uniformity_one(self):
        assert abs(ppm_col_uniformity(PPM_1X1_RED) - 1.0) < 0.01

    def test_ppm_2x2_col_uniformity_zero(self):
        assert abs(ppm_col_uniformity(PPM_2X2_RGBW)) < 0.01

    # QOI tests
    def test_qoi_1x1_red_channel_avg(self):
        assert abs(qoi_red_channel_avg(QOI_1X1_RED) - 255.0) < 0.1

    def test_qoi_black_red_channel_avg_zero(self):
        assert abs(qoi_red_channel_avg(QOI_2X2_BLACK)) < 0.1

    def test_qoi_1x1_alpha_pixel_count_zero(self):
        assert qoi_alpha_pixel_count(QOI_1X1_RED) == 0

    def test_qoi_1x1_file_size_bytes(self):
        assert qoi_file_size_bytes(QOI_1X1_RED) == 27

    def test_qoi_1x1_avg_red_channel(self):
        assert abs(qoi_avg_red_channel(QOI_1X1_RED) - 255.0) < 0.1

    def test_qoi_1x1_avg_green_channel_zero(self):
        assert abs(qoi_avg_green_channel(QOI_1X1_RED)) < 0.1

    def test_qoi_gradient_avg_green_channel(self):
        assert abs(qoi_avg_green_channel(QOI_4X1_GRADIENT) - 127.5) < 0.1

    def test_qoi_1x1_red_dominant_count(self):
        assert qoi_red_dominant_count(QOI_1X1_RED) == 1

    def test_qoi_black_red_dominant_count_zero(self):
        assert qoi_red_dominant_count(QOI_2X2_BLACK) == 0

    def test_qoi_1x1_col_uniformity_one(self):
        assert abs(qoi_col_uniformity(QOI_1X1_RED) - 1.0) < 0.01

    # NDJSON export pipeline
    def test_ndjson_export_pbm_qoi_records(self, tmp_path):
        records = [
            {
                "file": PBM_2X2_CHECKER.name,
                "checkerboard_score": pbm_checkerboard_score(PBM_2X2_CHECKER),
                "col_uniformity": pbm_col_uniformity(PBM_2X2_CHECKER),
            },
            {
                "file": QOI_1X1_RED.name,
                "red_channel_avg": qoi_red_channel_avg(QOI_1X1_RED),
                "red_dominant_count": qoi_red_dominant_count(QOI_1X1_RED),
            },
        ]
        out = tmp_path / "pbm_qoi_remaining.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert abs(json.loads(lines[0])["checkerboard_score"] - 1.0) < 0.01
        assert json.loads(lines[1])["red_dominant_count"] == 1
