"""test_dogfood_pbm_analytics_gaps_ndjson_export.py

Dogfood export path: PBM analytics gap functions → NDJSON.

Covers: pbm_avg_row_density, pbm_border_black_count, pbm_row_density_variance,
pbm_is_checkerboard, pbm_is_all_black, pbm_total_black_in_border, pbm_center_black_ratio.

Concrete values (1x1-black.pbm):
  avg_row_density      = 1.0
  border_black_count   = 1
  is_all_black         = True
  is_checkerboard      = False
  row_density_variance = 0.0
  total_black_in_border = 1
  center_black_ratio   = 0.0

Sprint: product-deepening-pbm-analytics-gaps-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm.pbm_parser import (
    pbm_avg_row_density,
    pbm_border_black_count,
    pbm_row_density_variance,
    pbm_is_checkerboard,
    pbm_is_all_black,
    pbm_total_black_in_border,
    pbm_center_black_ratio,
)
from src.python.ndjson.ndjson_codec import write_ndjson

SAMPLES_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
BLACK_1X1 = SAMPLES_DIR / "1x1-black.pbm"
CHECKER = SAMPLES_DIR / "2x2-checker.pbm"
PATTERN = SAMPLES_DIR / "3x2-pattern.pbm"


def _export_pbm_gaps_record(path: Path) -> dict:
    return {
        "file": path.name,
        "avg_row_density": pbm_avg_row_density(path),
        "border_black_count": pbm_border_black_count(path),
        "row_density_variance": pbm_row_density_variance(path),
        "is_checkerboard": pbm_is_checkerboard(path),
        "is_all_black": pbm_is_all_black(path),
        "total_black_in_border": pbm_total_black_in_border(path),
        "center_black_ratio": pbm_center_black_ratio(path),
    }


class TestPbmAnalyticsGapsNdjsonExport:

    def test_black_1x1_avg_row_density_is_one(self):
        rec = _export_pbm_gaps_record(BLACK_1X1)
        assert abs(rec["avg_row_density"] - 1.0) < 0.001

    def test_black_1x1_border_black_count_is_one(self):
        rec = _export_pbm_gaps_record(BLACK_1X1)
        assert rec["border_black_count"] == 1

    def test_black_1x1_is_all_black(self):
        rec = _export_pbm_gaps_record(BLACK_1X1)
        assert rec["is_all_black"] is True

    def test_black_1x1_not_checkerboard(self):
        rec = _export_pbm_gaps_record(BLACK_1X1)
        assert rec["is_checkerboard"] is False

    def test_black_1x1_row_density_variance_zero(self):
        rec = _export_pbm_gaps_record(BLACK_1X1)
        assert rec["row_density_variance"] == 0.0

    def test_checker_not_all_black(self):
        rec = _export_pbm_gaps_record(CHECKER)
        assert rec["is_all_black"] is False

    def test_checker_avg_row_density_half(self):
        rec = _export_pbm_gaps_record(CHECKER)
        assert abs(rec["avg_row_density"] - 0.5) < 0.01

    def test_record_has_all_keys(self):
        rec = _export_pbm_gaps_record(BLACK_1X1)
        for key in ["file", "avg_row_density", "border_black_count",
                    "row_density_variance", "is_checkerboard", "is_all_black",
                    "total_black_in_border", "center_black_ratio"]:
            assert key in rec

    def test_ndjson_export_two_files(self, tmp_path):
        records = [_export_pbm_gaps_record(BLACK_1X1), _export_pbm_gaps_record(CHECKER)]
        out = tmp_path / "pbm_gap_analytics.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        for line in lines:
            parsed = json.loads(line)
            assert "border_black_count" in parsed

    def test_ndjson_file_key_correct(self, tmp_path):
        records = [_export_pbm_gaps_record(BLACK_1X1)]
        out = tmp_path / "single.ndjson"
        write_ndjson(records, str(out))
        parsed = json.loads(out.read_text(encoding="utf-8").strip())
        assert parsed["file"] == "1x1-black.pbm"

    def test_pattern_row_density_variance_positive(self):
        rec = _export_pbm_gaps_record(PATTERN)
        assert rec["row_density_variance"] >= 0.0

    def test_pattern_total_black_in_border_three(self):
        rec = _export_pbm_gaps_record(PATTERN)
        assert rec["total_black_in_border"] == 3
