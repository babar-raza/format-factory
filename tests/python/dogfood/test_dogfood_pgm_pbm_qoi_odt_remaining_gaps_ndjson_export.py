"""test_dogfood_pgm_pbm_qoi_odt_remaining_gaps_ndjson_export.py

Dogfood export path: PGM + PBM + QOI + ODT remaining analytics gap functions -> NDJSON.

Covers PGM: pgm_below_midpoint_count, pgm_bright_pixel_count, pgm_contrast_ratio.
Covers PBM: pbm_border_density, pbm_diagonal_pixel_count, pbm_is_portrait.
Covers QOI: qoi_avg_channel_value, qoi_color_count, qoi_is_bright.
Covers ODT: odt_is_multi_paragraph, odt_is_single_paragraph, odt_whitespace_ratio.

Concrete values:
  PGM 2x2-gradient: below_midpoint_count=2, bright_pixel_count=2, contrast_ratio=1.0
  PBM 2x2-checker: border_density=0.5, diagonal_pixel_count=2, is_portrait=False
  QOI 1x1-red: avg_channel_value=85.0, color_count=1, is_bright=False
  ODT minimal: is_multi_paragraph=False, is_single_paragraph=True
  ODT two-paragraphs: is_multi_paragraph=True, is_single_paragraph=False

Sprint: product-deepening-pgm-pbm-qoi-odt-remaining-gaps-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pgm.pgm_parser import (
    pgm_below_midpoint_count, pgm_bright_pixel_count, pgm_contrast_ratio,
)
from src.python.pbm.pbm_parser import (
    pbm_border_density, pbm_diagonal_pixel_count, pbm_is_portrait,
)
from src.python.qoi.qoi_parser import (
    qoi_avg_channel_value, qoi_color_count, qoi_is_bright,
)
from src.python.odt.odt_parser import (
    odt_is_multi_paragraph, odt_is_single_paragraph, odt_whitespace_ratio,
)
from src.python.ndjson.ndjson_codec import write_ndjson

PGM_DIR = (_REPO / "samples" / "by-format" / "pgm" / "valid").resolve()
PBM_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
QOI_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
ODT_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"

PGM_GRADIENT = PGM_DIR / "2x2-gradient.pgm"
PGM_WHITE = PGM_DIR / "1x1-white.pgm"
PBM_CHECKER = PBM_DIR / "2x2-checker.pbm"
PBM_BLACK = PBM_DIR / "1x1-black.pbm"
QOI_RED = QOI_DIR / "1x1-red.qoi"
QOI_BLACK = QOI_DIR / "2x2-black.qoi"
ODT_MINIMAL = ODT_DIR / "minimal-document.odt"
ODT_TWO_PARA = ODT_DIR / "two-paragraphs.odt"


class TestPgmPbmQoiOdtRemainingGapsNdjsonExport:

    def test_pgm_gradient_below_midpoint_count(self):
        assert pgm_below_midpoint_count(PGM_GRADIENT) == 2

    def test_pgm_gradient_bright_pixel_count(self):
        assert pgm_bright_pixel_count(PGM_GRADIENT) == 2

    def test_pgm_gradient_contrast_ratio(self):
        assert abs(pgm_contrast_ratio(PGM_GRADIENT) - 1.0) < 0.01

    def test_pbm_checker_border_density(self):
        assert abs(pbm_border_density(PBM_CHECKER) - 0.5) < 0.01

    def test_pbm_checker_diagonal_pixel_count(self):
        assert pbm_diagonal_pixel_count(PBM_CHECKER) == 2

    def test_pbm_checker_is_not_portrait(self):
        assert pbm_is_portrait(PBM_CHECKER) is False

    def test_qoi_red_avg_channel_value(self):
        assert abs(qoi_avg_channel_value(QOI_RED) - 85.0) < 1.0

    def test_qoi_red_color_count_one(self):
        assert qoi_color_count(QOI_RED) == 1

    def test_qoi_red_not_bright(self):
        assert qoi_is_bright(QOI_RED) is False

    def test_odt_minimal_is_single_paragraph(self):
        assert odt_is_single_paragraph(ODT_MINIMAL) is True

    def test_odt_minimal_not_multi_paragraph(self):
        assert odt_is_multi_paragraph(ODT_MINIMAL) is False

    def test_odt_two_para_is_multi_paragraph(self):
        assert odt_is_multi_paragraph(ODT_TWO_PARA) is True

    def test_odt_minimal_whitespace_ratio_positive(self):
        assert odt_whitespace_ratio(ODT_MINIMAL) > 0.0

    def test_ndjson_export_pgm_record(self, tmp_path):
        records = [{
            "file": PGM_GRADIENT.name,
            "below_midpoint_count": pgm_below_midpoint_count(PGM_GRADIENT),
            "bright_pixel_count": pgm_bright_pixel_count(PGM_GRADIENT),
            "contrast_ratio": pgm_contrast_ratio(PGM_GRADIENT),
        }]
        out = tmp_path / "pgm_remaining.ndjson"
        write_ndjson(records, str(out))
        parsed = json.loads(out.read_text(encoding="utf-8").strip())
        assert parsed["below_midpoint_count"] == 2

    def test_ndjson_export_odt_records(self, tmp_path):
        records = [
            {"file": ODT_MINIMAL.name, "is_multi": odt_is_multi_paragraph(ODT_MINIMAL)},
            {"file": ODT_TWO_PARA.name, "is_multi": odt_is_multi_paragraph(ODT_TWO_PARA)},
        ]
        out = tmp_path / "odt_remaining.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert json.loads(lines[0])["is_multi"] is False
        assert json.loads(lines[1])["is_multi"] is True
