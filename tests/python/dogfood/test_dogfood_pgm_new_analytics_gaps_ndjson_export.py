"""test_dogfood_pgm_new_analytics_gaps_ndjson_export.py

Dogfood export path: PGM new analytics gap functions -> NDJSON.

Covers: pgm_saturated_pixel_ratio, pgm_normalized_mean, pgm_above_mean_ratio,
pgm_maxval, pgm_midpoint_gray.

Concrete values (1x1-white.pgm):
  saturated_pixel_ratio = 1.0
  normalized_mean       = 1.0
  above_mean_ratio      = 0.0
  maxval                = 255
  midpoint_gray         = 127.0

Concrete values (2x2-gradient.pgm):
  saturated_pixel_ratio = 0.25
  normalized_mean       = 0.5
  above_mean_ratio      = 0.5

Sprint: product-deepening-pgm-sylk-tsv-new-analytics-gaps-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pgm.pgm_parser import (
    pgm_saturated_pixel_ratio,
    pgm_normalized_mean,
    pgm_above_mean_ratio,
    pgm_maxval,
    pgm_midpoint_gray,
)
from src.python.ndjson.ndjson_codec import write_ndjson

SAMPLES_DIR = (_REPO / "samples" / "by-format" / "pgm" / "valid").resolve()
WHITE_1X1 = SAMPLES_DIR / "1x1-white.pgm"
GRADIENT_2X2 = SAMPLES_DIR / "2x2-gradient.pgm"
RAMP_3X1 = SAMPLES_DIR / "3x1-ramp.pgm"


def _export_pgm_new_record(path: Path) -> dict:
    p = path.resolve()
    return {
        "file": path.name,
        "saturated_pixel_ratio": pgm_saturated_pixel_ratio(p),
        "normalized_mean": pgm_normalized_mean(p),
        "above_mean_ratio": pgm_above_mean_ratio(p),
        "maxval": pgm_maxval(p),
        "midpoint_gray": pgm_midpoint_gray(p),
    }


class TestPgmNewAnalyticsGapsNdjsonExport:

    def test_white_saturated_pixel_ratio_is_one(self):
        rec = _export_pgm_new_record(WHITE_1X1)
        assert abs(rec["saturated_pixel_ratio"] - 1.0) < 0.001

    def test_gradient_saturated_pixel_ratio_quarter(self):
        rec = _export_pgm_new_record(GRADIENT_2X2)
        assert abs(rec["saturated_pixel_ratio"] - 0.25) < 0.01

    def test_white_normalized_mean_is_one(self):
        rec = _export_pgm_new_record(WHITE_1X1)
        assert abs(rec["normalized_mean"] - 1.0) < 0.001

    def test_gradient_normalized_mean_half(self):
        rec = _export_pgm_new_record(GRADIENT_2X2)
        assert abs(rec["normalized_mean"] - 0.5) < 0.01

    def test_white_above_mean_ratio_zero(self):
        rec = _export_pgm_new_record(WHITE_1X1)
        assert abs(rec["above_mean_ratio"]) < 0.001

    def test_gradient_above_mean_ratio_half(self):
        rec = _export_pgm_new_record(GRADIENT_2X2)
        assert abs(rec["above_mean_ratio"] - 0.5) < 0.01

    def test_white_maxval_is_255(self):
        rec = _export_pgm_new_record(WHITE_1X1)
        assert rec["maxval"] == 255

    def test_gradient_maxval_is_255(self):
        rec = _export_pgm_new_record(GRADIENT_2X2)
        assert rec["maxval"] == 255

    def test_white_midpoint_gray(self):
        rec = _export_pgm_new_record(WHITE_1X1)
        assert abs(rec["midpoint_gray"] - 127.0) < 1.0

    def test_record_has_all_keys(self):
        rec = _export_pgm_new_record(WHITE_1X1)
        for key in ["file", "saturated_pixel_ratio", "normalized_mean",
                    "above_mean_ratio", "maxval", "midpoint_gray"]:
            assert key in rec

    def test_ndjson_export_two_files(self, tmp_path):
        records = [_export_pgm_new_record(WHITE_1X1), _export_pgm_new_record(GRADIENT_2X2)]
        out = tmp_path / "pgm_new_analytics.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        for line in lines:
            parsed = json.loads(line)
            assert "normalized_mean" in parsed

    def test_ramp_above_mean_ratio_positive(self):
        rec = _export_pgm_new_record(RAMP_3X1)
        assert rec["above_mean_ratio"] >= 0.0
