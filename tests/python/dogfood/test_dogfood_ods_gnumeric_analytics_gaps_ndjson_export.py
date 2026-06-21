"""test_dogfood_ods_gnumeric_analytics_gaps_ndjson_export.py

Dogfood export path: ODS + Gnumeric analytics gap functions -> NDJSON.

Covers ODS: ods_numeric_ratio, ods_is_square.
Covers Gnumeric: gnumeric_cell_to_row_ratio.

Concrete values (minimal-spreadsheet.ods):
  numeric_ratio = 0.250
  is_square     = True

Concrete values (numeric-row.ods):
  numeric_ratio = 1.0
  is_square     = False

Concrete values (Gnumeric multi-cell-basic.gnumeric):
  cell_to_row_ratio = 2.0

Sprint: product-deepening-xcf-ods-gnumeric-analytics-gaps-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods.ods_parser import ods_numeric_ratio, ods_is_square
from src.python.gnumeric.gnumeric_codec import gnumeric_cell_to_row_ratio
from src.python.ndjson.ndjson_codec import write_ndjson

ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"
GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"

ODS_MINIMAL = ODS_DIR / "minimal-spreadsheet.ods"
ODS_NUMERIC = ODS_DIR / "numeric-row.ods"
ODS_SINGLE = ODS_DIR / "single-cell.ods"
GNUMERIC_MINIMAL = GNUMERIC_DIR / "minimal-spreadsheet.gnumeric"
GNUMERIC_MULTI = GNUMERIC_DIR / "multi-cell-basic.gnumeric"
GNUMERIC_EMPTY = GNUMERIC_DIR / "empty-sheet.gnumeric"


def _export_ods_gaps_record(path: Path) -> dict:
    return {
        "file": path.name,
        "numeric_ratio": ods_numeric_ratio(path),
        "is_square": ods_is_square(path),
    }


def _export_gnumeric_gaps_record(path: Path) -> dict:
    return {
        "file": path.name,
        "cell_to_row_ratio": gnumeric_cell_to_row_ratio(path),
    }


class TestOdsGnumericAnalyticsGapsNdjsonExport:

    def test_minimal_numeric_ratio(self):
        rec = _export_ods_gaps_record(ODS_MINIMAL)
        assert abs(rec["numeric_ratio"] - 0.25) < 0.01

    def test_numeric_row_ratio_is_one(self):
        rec = _export_ods_gaps_record(ODS_NUMERIC)
        assert abs(rec["numeric_ratio"] - 1.0) < 0.01

    def test_single_cell_numeric_ratio_zero(self):
        rec = _export_ods_gaps_record(ODS_SINGLE)
        assert abs(rec["numeric_ratio"]) < 0.01

    def test_minimal_is_square(self):
        rec = _export_ods_gaps_record(ODS_MINIMAL)
        assert rec["is_square"] is True

    def test_numeric_row_not_square(self):
        rec = _export_ods_gaps_record(ODS_NUMERIC)
        assert rec["is_square"] is False

    def test_gnumeric_empty_cell_to_row_ratio_zero(self):
        rec = _export_gnumeric_gaps_record(GNUMERIC_EMPTY)
        assert abs(rec["cell_to_row_ratio"]) < 0.01

    def test_gnumeric_minimal_cell_to_row_ratio_one(self):
        rec = _export_gnumeric_gaps_record(GNUMERIC_MINIMAL)
        assert abs(rec["cell_to_row_ratio"] - 1.0) < 0.01

    def test_gnumeric_multi_cell_to_row_ratio_two(self):
        rec = _export_gnumeric_gaps_record(GNUMERIC_MULTI)
        assert abs(rec["cell_to_row_ratio"] - 2.0) < 0.01

    def test_ods_record_has_all_keys(self):
        rec = _export_ods_gaps_record(ODS_MINIMAL)
        assert "numeric_ratio" in rec
        assert "is_square" in rec

    def test_gnumeric_record_has_all_keys(self):
        rec = _export_gnumeric_gaps_record(GNUMERIC_MINIMAL)
        assert "cell_to_row_ratio" in rec

    def test_ndjson_export_ods_files(self, tmp_path):
        records = [_export_ods_gaps_record(ODS_MINIMAL), _export_ods_gaps_record(ODS_NUMERIC)]
        out = tmp_path / "ods_gap_analytics.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        for line in lines:
            parsed = json.loads(line)
            assert "numeric_ratio" in parsed

    def test_ndjson_export_gnumeric_files(self, tmp_path):
        records = [
            _export_gnumeric_gaps_record(GNUMERIC_MINIMAL),
            _export_gnumeric_gaps_record(GNUMERIC_MULTI),
        ]
        out = tmp_path / "gnumeric_gap_analytics.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        for line in lines:
            parsed = json.loads(line)
            assert "cell_to_row_ratio" in parsed
