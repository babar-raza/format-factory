"""test_dogfood_fodg_tsv_remaining_analytics_gaps_ndjson_export.py

Dogfood export path: FODG + TSV remaining analytics gap functions -> NDJSON.

Covers FODG: fodg_total_text_items.
Covers TSV: tsv_is_square.

Concrete values (FODG):
  empty-page.fodg:     total_text_items = 0
  minimal-drawing.fodg: total_text_items = 1
  shapes-basic.fodg:   total_text_items = 2

Concrete values (TSV):
  minimal-2x2.tsv:   is_square = True  (2x2)
  multi-column.tsv:  is_square = False (1x4)

Sprint: product-deepening-fodg-tsv-remaining-analytics-gaps-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg.fodg_codec import fodg_total_text_items
from src.python.tsv.tsv_parser import tsv_is_square
from src.python.ndjson.ndjson_codec import write_ndjson

FODG_DIR = _REPO / "samples" / "by-format" / "fodg"
TSV_DIR = _REPO / "samples" / "by-format" / "tsv"

FODG_EMPTY = FODG_DIR / "empty-page.fodg"
FODG_MINIMAL = FODG_DIR / "minimal-drawing.fodg"
FODG_SHAPES = FODG_DIR / "shapes-basic.fodg"
TSV_MINIMAL = TSV_DIR / "minimal-2x2.tsv"
TSV_MULTI = TSV_DIR / "multi-column.tsv"


def _export_fodg_record(path: Path) -> dict:
    return {
        "file": path.name,
        "total_text_items": fodg_total_text_items(path),
    }


def _export_tsv_is_square_record(path: Path) -> dict:
    return {
        "file": path.name,
        "is_square": tsv_is_square(path),
    }


class TestFodgTsvRemainingAnalyticsGapsNdjsonExport:

    def test_fodg_empty_total_text_items_zero(self):
        rec = _export_fodg_record(FODG_EMPTY)
        assert rec["total_text_items"] == 0

    def test_fodg_minimal_total_text_items_one(self):
        rec = _export_fodg_record(FODG_MINIMAL)
        assert rec["total_text_items"] == 1

    def test_fodg_shapes_total_text_items_two(self):
        rec = _export_fodg_record(FODG_SHAPES)
        assert rec["total_text_items"] == 2

    def test_fodg_total_text_items_is_int(self):
        rec = _export_fodg_record(FODG_MINIMAL)
        assert isinstance(rec["total_text_items"], int)

    def test_tsv_minimal_is_square(self):
        rec = _export_tsv_is_square_record(TSV_MINIMAL)
        assert rec["is_square"] is True

    def test_tsv_multi_not_square(self):
        rec = _export_tsv_is_square_record(TSV_MULTI)
        assert rec["is_square"] is False

    def test_tsv_is_square_returns_bool(self):
        rec = _export_tsv_is_square_record(TSV_MINIMAL)
        assert isinstance(rec["is_square"], bool)

    def test_fodg_ndjson_export_three_files(self, tmp_path):
        records = [
            _export_fodg_record(FODG_EMPTY),
            _export_fodg_record(FODG_MINIMAL),
            _export_fodg_record(FODG_SHAPES),
        ]
        out = tmp_path / "fodg_text_items.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 3
        vals = [json.loads(l)["total_text_items"] for l in lines]
        assert vals == [0, 1, 2]

    def test_tsv_ndjson_export_two_files(self, tmp_path):
        records = [
            _export_tsv_is_square_record(TSV_MINIMAL),
            _export_tsv_is_square_record(TSV_MULTI),
        ]
        out = tmp_path / "tsv_is_square.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        assert json.loads(lines[0])["is_square"] is True
        assert json.loads(lines[1])["is_square"] is False

    def test_fodg_empty_file_key(self):
        rec = _export_fodg_record(FODG_EMPTY)
        assert rec["file"] == "empty-page.fodg"

    def test_tsv_minimal_file_key(self):
        rec = _export_tsv_is_square_record(TSV_MINIMAL)
        assert rec["file"] == "minimal-2x2.tsv"

    def test_fodg_greater_than_empty_has_items(self):
        empty_count = _export_fodg_record(FODG_EMPTY)["total_text_items"]
        shapes_count = _export_fodg_record(FODG_SHAPES)["total_text_items"]
        assert shapes_count > empty_count
