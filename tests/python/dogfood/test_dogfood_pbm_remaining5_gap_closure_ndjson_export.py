"""
tests/python/dogfood/test_dogfood_pbm_remaining5_gap_closure_ndjson_export.py

Sprint: dogfood-analytics-gap-closure-batch3-20260617
Dogfood export: PBM remaining 5 uncovered analytics -> NDJSON roundtrip.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm.pbm_parser import (
    pbm_black_minus_white,
    pbm_center_black_count,
    pbm_is_all_white,
    pbm_total_pixels_minus_black,
    pbm_white_count_exceeds_row_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_PBM_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_S = str(_PBM_DIR / "2x2-checker.pbm")


class TestPbmRemaining5GapClosureNdjsonExport:
    """5 remaining uncovered PBM analytics -> NDJSON dogfood export."""

    def test_black_minus_white(self):
        assert pbm_black_minus_white(_S) == 0

    def test_center_black_count(self):
        assert pbm_center_black_count(_S) == 1

    def test_is_all_white(self):
        assert pbm_is_all_white(_S) is False

    def test_total_pixels_minus_black(self):
        assert pbm_total_pixels_minus_black(_S) == 2

    def test_white_count_exceeds_row_count(self):
        assert pbm_white_count_exceeds_row_count(_S) is False

    def test_ndjson_roundtrip(self, tmp_path):
        out = tmp_path / "pbm_remaining.ndjson"
        records = [
            {"fn": "black_minus_white", "value": pbm_black_minus_white(_S)},
            {"fn": "total_pixels_minus_black", "value": pbm_total_pixels_minus_black(_S)},
            {"fn": "is_all_white", "value": pbm_is_all_white(_S)},
        ]
        write_ndjson(records, str(out))
        loaded = load_ndjson(str(out))
        assert len(loaded) == 3
        assert loaded[0]["value"] == 0
        assert loaded[1]["value"] == 2
        assert loaded[2]["value"] is False
