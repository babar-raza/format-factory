"""
tests/python/dogfood/test_dogfood_ods_cell_type_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-27
Dogfood export: ODS parse -> cell type distribution analytics -> write as NDJSON -> verify.
Uses deeper ODS analytics: numeric density, string/empty counts, merged cells, avg cells per row.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods import (
    ods_numeric_density,
    ods_numeric_cell_count,
    ods_string_cell_count,
    ods_empty_cell_count,
    ods_has_merged_cells,
    ods_average_cells_per_row,
    ods_total_cell_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"


def _ap(f):
    return os.path.abspath(str(f))


class TestOdsCellTypeNdjsonExport:
    """ODS -> cell type distribution analytics -> NDJSON export -> roundtrip verification."""

    def test_numeric_density(self):
        sample = _ap(_ODS_DIR / "minimal-spreadsheet.ods")
        density = ods_numeric_density(sample)
        assert isinstance(density, (int, float))
        assert 0.0 <= density <= 1.0

    def test_cell_type_counts(self):
        sample = _ap(_ODS_DIR / "minimal-spreadsheet.ods")
        total = ods_total_cell_count(sample)
        numeric = ods_numeric_cell_count(sample)
        string = ods_string_cell_count(sample)
        empty = ods_empty_cell_count(sample)
        assert numeric + string + empty >= 0
        assert total >= numeric

    def test_cell_type_to_ndjson(self, tmp_path):
        records = []
        for f in sorted(_ODS_DIR.glob("*.ods")):
            p = _ap(f)
            total = ods_total_cell_count(p)
            numeric = ods_numeric_cell_count(p)
            records.append({
                "file": f.name,
                "total_cells": total,
                "numeric_cells": numeric,
                "string_cells": ods_string_cell_count(p),
                "empty_cells": ods_empty_cell_count(p),
                "numeric_density": ods_numeric_density(p),
                "has_merged": ods_has_merged_cells(p),
                "avg_cells_per_row": ods_average_cells_per_row(p),
                "source_format": "ods",
            })
            assert numeric <= total, f"numeric ({numeric}) > total ({total})"
        dest = tmp_path / "ods-cell-types.ndjson"
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
                "total_cells": ods_total_cell_count(p),
                "numeric_density": ods_numeric_density(p),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["total_cells"] == back["total_cells"]

    def test_json_lines_valid(self, tmp_path):
        sample = _ap(_ODS_DIR / "minimal-spreadsheet.ods")
        records = [{"file": "minimal-spreadsheet.ods", "density": ods_numeric_density(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_merged_cells_export(self, tmp_path):
        records = []
        for f in sorted(_ODS_DIR.glob("*.ods")):
            p = _ap(f)
            records.append({
                "file": f.name,
                "has_merged": ods_has_merged_cells(p),
                "avg_per_row": ods_average_cells_per_row(p),
                "format": "ods",
            })
        dest = tmp_path / "merged.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "ods" for r in loaded)
        assert all(isinstance(r["has_merged"], bool) for r in loaded)
