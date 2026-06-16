"""
tests/python/dogfood/test_dogfood_ods_row_structure_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-39
Dogfood export: ODS parse -> row structure analytics -> write as NDJSON -> verify.
Uses: ods_max_row_length, ods_empty_row_count, ods_column_count, ods_has_empty_rows,
ods_sheet_count, ods_total_cell_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods import (
    ods_max_row_length,
    ods_empty_row_count,
    ods_column_count,
    ods_has_empty_rows,
    ods_sheet_count,
    ods_total_cell_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"


def _valid_ods_files():
    return sorted(_ODS_DIR.glob("*.ods"))


class TestOdsRowStructureNdjsonExport:
    """ODS -> row structure analytics -> NDJSON export -> roundtrip verification."""

    def test_row_structure_basics(self):
        sample = str(_ODS_DIR / "minimal-spreadsheet.ods")
        max_len = ods_max_row_length(sample)
        cols = ods_column_count(sample)
        assert max_len >= 0
        assert cols >= 0

    def test_empty_row_detection(self):
        sample = str(_ODS_DIR / "minimal-spreadsheet.ods")
        empty_rows = ods_empty_row_count(sample)
        has_empty = ods_has_empty_rows(sample)
        assert empty_rows >= 0
        assert isinstance(has_empty, bool)

    def test_row_structure_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_ods_files():
            path = str(f)
            max_len = ods_max_row_length(path)
            empty_rows = ods_empty_row_count(path)
            cols = ods_column_count(path)
            has_empty = ods_has_empty_rows(path)
            sheets = ods_sheet_count(path)
            total = ods_total_cell_count(path)
            assert max_len >= 0, f"max_row_length must be >= 0 for {f.name}"
            assert empty_rows >= 0, f"empty_row_count must be >= 0 for {f.name}"
            assert cols >= 0, f"column_count must be >= 0 for {f.name}"
            assert isinstance(has_empty, bool), f"has_empty_rows must be bool for {f.name}"
            assert sheets >= 0, f"sheet_count must be >= 0 for {f.name}"
            assert total >= 0, f"total_cell_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "max_row_length": max_len,
                "empty_row_count": empty_rows,
                "column_count": cols,
                "has_empty_rows": has_empty,
                "sheet_count": sheets,
                "total_cells": total,
                "source_format": "ods",
            })
        dest = tmp_path / "ods-row-structure.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_ods_files():
            path = str(f)
            records.append({
                "file": f.name,
                "max_row_length": ods_max_row_length(path),
                "has_empty_rows": ods_has_empty_rows(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["max_row_length"] == back["max_row_length"]
            assert orig["has_empty_rows"] == back["has_empty_rows"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_ODS_DIR / "minimal-spreadsheet.ods")
        records = [{"file": "minimal-spreadsheet.ods", "max_row_length": ods_max_row_length(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_empty_row_export(self, tmp_path):
        records = []
        for f in _valid_ods_files():
            path = str(f)
            empty_rows = ods_empty_row_count(path)
            has_empty = ods_has_empty_rows(path)
            cols = ods_column_count(path)
            assert empty_rows >= 0
            assert isinstance(has_empty, bool)
            assert cols >= 0
            records.append({
                "file": f.name,
                "empty_row_count": empty_rows,
                "has_empty_rows": has_empty,
                "column_count": cols,
                "format": "ods",
            })
        dest = tmp_path / "empty-rows.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "ods" for r in loaded)
        assert all(r["empty_row_count"] >= 0 for r in loaded)
