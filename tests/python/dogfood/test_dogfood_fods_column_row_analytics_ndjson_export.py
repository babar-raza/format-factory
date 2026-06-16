"""
tests/python/dogfood/test_dogfood_fods_column_row_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-50
Dogfood export: FODS parse -> column/row analytics -> write as NDJSON -> verify.
Uses: parse_fods, workbook_column_count, workbook_max_column_count, workbook_row_count,
workbook_count_nonempty_cells, workbook_sheet_order, workbook_sheet_summary.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods import (
    parse_fods,
    workbook_column_count,
    workbook_max_column_count,
    workbook_row_count,
    workbook_count_nonempty_cells,
    workbook_sheet_order,
    workbook_sheet_summary,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODS_DIR = _REPO / "samples" / "by-format" / "fods"


def _valid_fods_files():
    return sorted(_FODS_DIR.glob("*.fods"))


class TestFodsColumnRowAnalyticsNdjsonExport:
    """FODS -> column/row analytics -> NDJSON export -> roundtrip verification."""

    def test_column_count_and_max(self):
        sample = str(next(_FODS_DIR.glob("*.fods")))
        wb = parse_fods(sample)
        col_count = workbook_column_count(wb)
        max_col = workbook_max_column_count(wb)
        assert isinstance(col_count, dict)
        assert max_col >= 0

    def test_row_count_and_nonempty_cells(self):
        sample = str(next(_FODS_DIR.glob("*.fods")))
        wb = parse_fods(sample)
        row_count = workbook_row_count(wb)
        nonempty = workbook_count_nonempty_cells(wb)
        sheet_order = workbook_sheet_order(wb)
        summary = workbook_sheet_summary(wb)
        assert row_count >= 0
        assert nonempty >= 0
        assert isinstance(sheet_order, list)
        assert isinstance(summary, list)

    def test_column_row_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_fods_files():
            path = str(f)
            wb = parse_fods(path)
            col_count = workbook_column_count(wb)
            max_col = workbook_max_column_count(wb)
            row_count = workbook_row_count(wb)
            nonempty = workbook_count_nonempty_cells(wb)
            sheet_order = workbook_sheet_order(wb)
            summary = workbook_sheet_summary(wb)
            assert isinstance(col_count, dict), f"column_count must be dict for {f.name}"
            assert max_col >= 0, f"max_column_count must be >= 0 for {f.name}"
            assert row_count >= 0, f"row_count must be >= 0 for {f.name}"
            assert nonempty >= 0, f"count_nonempty_cells must be >= 0 for {f.name}"
            assert isinstance(sheet_order, list), f"sheet_order must be list for {f.name}"
            assert isinstance(summary, list), f"sheet_summary must be list for {f.name}"
            records.append({
                "file": f.name,
                "sheet_count": len(col_count),
                "max_column_count": max_col,
                "row_count": row_count,
                "nonempty_cells": nonempty,
                "sheet_order": sheet_order,
                "sheet_summary_count": len(summary),
                "source_format": "fods",
            })
        dest = tmp_path / "fods-column-row.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_fods_files():
            wb = parse_fods(str(f))
            records.append({
                "file": f.name,
                "max_column_count": workbook_max_column_count(wb),
                "row_count": workbook_row_count(wb),
                "nonempty_cells": workbook_count_nonempty_cells(wb),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["max_column_count"] == back["max_column_count"]
            assert orig["row_count"] == back["row_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_FODS_DIR.glob("*.fods")))
        wb = parse_fods(sample)
        sheet_order = workbook_sheet_order(wb)
        records = [{"file": "sample.fods", "sheet_count": len(sheet_order)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_sheet_summary_export(self, tmp_path):
        records = []
        for f in _valid_fods_files():
            wb = parse_fods(str(f))
            summary = workbook_sheet_summary(wb)
            sheet_order = workbook_sheet_order(wb)
            max_col = workbook_max_column_count(wb)
            assert isinstance(summary, list)
            assert isinstance(sheet_order, list)
            assert max_col >= 0
            records.append({
                "file": f.name,
                "sheet_summary_count": len(summary),
                "sheet_order": sheet_order,
                "max_column_count": max_col,
                "format": "fods",
            })
        dest = tmp_path / "sheet-summary.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "fods" for r in loaded)
        assert all(r["max_column_count"] >= 0 for r in loaded)
