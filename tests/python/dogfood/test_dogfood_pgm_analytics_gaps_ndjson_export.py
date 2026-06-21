"""test_dogfood_pgm_analytics_gaps_ndjson_export.py

Dogfood export path: PGM analytics gap functions → NDJSON.

Covers: pgm_is_high_contrast, pgm_avg_row_brightness, pgm_is_bright, pgm_dark_pixel_ratio.

Concrete values (1x1-white.pgm):
  is_high_contrast  = False
  is_bright         = True
  dark_pixel_ratio  = 0.0
  avg_row_brightness = [255.0]

Concrete values (2x2-gradient.pgm):
  is_high_contrast  = True
  is_bright         = False
  dark_pixel_ratio  = 0.5
  avg_row_brightness = [42.5, 212.5]

Sprint: product-deepening-pgm-analytics-gaps-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pgm.pgm_parser import (
    pgm_is_high_contrast,
    pgm_avg_row_brightness,
    pgm_is_bright,
    pgm_dark_pixel_ratio,
)
from src.python.ndjson.ndjson_codec import write_ndjson

SAMPLES_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
WHITE_1X1 = SAMPLES_DIR / "1x1-white.pgm"
GRADIENT = SAMPLES_DIR / "2x2-gradient.pgm"


def _export_pgm_gaps_record(path: Path) -> dict:
    avg_rows = pgm_avg_row_brightness(path)
    return {
        "file": path.name,
        "is_high_contrast": pgm_is_high_contrast(path),
        "is_bright": pgm_is_bright(path),
        "dark_pixel_ratio": pgm_dark_pixel_ratio(path),
        "avg_row_brightness_first": avg_rows[0] if avg_rows else 0.0,
        "row_count": len(avg_rows),
    }


class TestPgmAnalyticsGapsNdjsonExport:

    def test_white_not_high_contrast(self):
        rec = _export_pgm_gaps_record(WHITE_1X1)
        assert rec["is_high_contrast"] is False

    def test_white_is_bright(self):
        rec = _export_pgm_gaps_record(WHITE_1X1)
        assert rec["is_bright"] is True

    def test_white_dark_pixel_ratio_zero(self):
        rec = _export_pgm_gaps_record(WHITE_1X1)
        assert rec["dark_pixel_ratio"] == 0.0

    def test_white_avg_row_brightness_255(self):
        rec = _export_pgm_gaps_record(WHITE_1X1)
        assert abs(rec["avg_row_brightness_first"] - 255.0) < 0.01

    def test_gradient_is_high_contrast(self):
        rec = _export_pgm_gaps_record(GRADIENT)
        assert rec["is_high_contrast"] is True

    def test_gradient_not_bright(self):
        rec = _export_pgm_gaps_record(GRADIENT)
        assert rec["is_bright"] is False

    def test_gradient_dark_pixel_ratio_quarter(self):
        rec = _export_pgm_gaps_record(GRADIENT)
        assert abs(rec["dark_pixel_ratio"] - 0.25) < 0.01

    def test_gradient_row_count_is_two(self):
        rec = _export_pgm_gaps_record(GRADIENT)
        assert rec["row_count"] == 2

    def test_record_has_all_keys(self):
        rec = _export_pgm_gaps_record(WHITE_1X1)
        for key in ["file", "is_high_contrast", "is_bright",
                    "dark_pixel_ratio", "avg_row_brightness_first", "row_count"]:
            assert key in rec

    def test_ndjson_export_two_files(self, tmp_path):
        records = [_export_pgm_gaps_record(WHITE_1X1), _export_pgm_gaps_record(GRADIENT)]
        out = tmp_path / "pgm_gap_analytics.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        for line in lines:
            parsed = json.loads(line)
            assert "dark_pixel_ratio" in parsed

    def test_ndjson_file_key_correct(self, tmp_path):
        records = [_export_pgm_gaps_record(WHITE_1X1)]
        out = tmp_path / "single.ndjson"
        write_ndjson(records, str(out))
        parsed = json.loads(out.read_text(encoding="utf-8").strip())
        assert parsed["file"] == "1x1-white.pgm"

    def test_white_row_count_is_one(self):
        rec = _export_pgm_gaps_record(WHITE_1X1)
        assert rec["row_count"] == 1
