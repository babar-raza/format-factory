"""
tests/python/dogfood/test_dogfood_ods_sheet_metadata_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-20
Dogfood export: ODS parse -> extract spreadsheet-level metadata -> write as NDJSON -> verify.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods import (
    ods_sheet_count,
    get_sheet_names,
    ods_has_merged_cells,
    ods_numeric_density,
    ods_average_cells_per_row,
    ods_row_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"


def _ap(f):
    return os.path.abspath(str(f))


class TestOdsSheetMetadataNdjsonExport:
    """ODS -> spreadsheet metadata extraction -> NDJSON export -> roundtrip verification."""

    def test_sheet_count(self):
        sample = _ap(_ODS_DIR / "minimal-spreadsheet.ods")
        count = ods_sheet_count(sample)
        assert count >= 1

    def test_sheet_names(self):
        sample = _ap(_ODS_DIR / "minimal-spreadsheet.ods")
        names = get_sheet_names(sample)
        assert isinstance(names, list)
        assert len(names) >= 1

    def test_sheet_metadata_to_ndjson(self, tmp_path):
        records = []
        for f in sorted(_ODS_DIR.glob("*.ods")):
            p = _ap(f)
            records.append({
                "file": f.name,
                "sheet_count": ods_sheet_count(p),
                "sheet_names": get_sheet_names(p),
                "has_merged_cells": ods_has_merged_cells(p),
                "numeric_density": ods_numeric_density(p),
                "avg_cells_per_row": ods_average_cells_per_row(p),
                "source_format": "ods",
            })
        dest = tmp_path / "ods-sheet-meta.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in sorted(_ODS_DIR.glob("*.ods")):
            p = _ap(f)
            records.append({
                "file": f.name,
                "sheet_count": ods_sheet_count(p),
                "has_merged_cells": ods_has_merged_cells(p),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["sheet_count"] == back["sheet_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = _ap(_ODS_DIR / "minimal-spreadsheet.ods")
        records = [{"file": "minimal-spreadsheet.ods", "sheets": ods_sheet_count(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_rows_per_sheet_in_export(self, tmp_path):
        records = []
        for f in sorted(_ODS_DIR.glob("*.ods")):
            p = _ap(f)
            sheets = ods_sheet_count(p)
            rows = ods_row_count(p)
            records.append({
                "file": f.name,
                "rows_per_sheet": rows / sheets if sheets > 0 else 0.0,
                "format": "ods",
            })
        dest = tmp_path / "rps.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "ods" for r in loaded)
