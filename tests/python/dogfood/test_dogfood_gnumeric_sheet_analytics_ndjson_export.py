"""
tests/python/dogfood/test_dogfood_gnumeric_sheet_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-29
Dogfood export: Gnumeric parse -> sheet-level analytics -> write as NDJSON -> verify.
Uses deeper Gnumeric analytics: multiple sheets, avg cells/sheet, numeric density, empty cells.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric import (
    gnumeric_sheet_count,
    gnumeric_cell_count_file,
    gnumeric_has_multiple_sheets,
    gnumeric_average_cells_per_sheet,
    gnumeric_numeric_density,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"


def _ap(f):
    return os.path.abspath(str(f))


class TestGnumericSheetAnalyticsNdjsonExport:
    """Gnumeric -> sheet-level analytics -> NDJSON export -> roundtrip verification."""

    def test_sheet_count(self):
        sample = _ap(_GNUMERIC_DIR / "minimal-spreadsheet.gnumeric")
        count = gnumeric_sheet_count(sample)
        assert isinstance(count, int)
        assert count >= 1

    def test_numeric_density(self):
        sample = _ap(_GNUMERIC_DIR / "minimal-spreadsheet.gnumeric")
        density = gnumeric_numeric_density(sample)
        assert isinstance(density, (int, float))
        assert 0.0 <= density <= 1.0

    def test_sheet_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in sorted(_GNUMERIC_DIR.glob("*.gnumeric")):
            p = _ap(f)
            total = gnumeric_cell_count_file(p)
            sheets = gnumeric_sheet_count(p)
            avg = gnumeric_average_cells_per_sheet(p)
            assert sheets >= 1, f"sheet_count must be >= 1 for {f.name}"
            assert total >= 0, f"total_cells must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "sheet_count": sheets,
                "total_cells": total,
                "has_multiple": gnumeric_has_multiple_sheets(p),
                "avg_per_sheet": avg,
                "numeric_density": gnumeric_numeric_density(p),
                "source_format": "gnumeric",
            })
        dest = tmp_path / "gnumeric-sheet-analytics.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in sorted(_GNUMERIC_DIR.glob("*.gnumeric")):
            p = _ap(f)
            records.append({
                "file": f.name,
                "sheet_count": gnumeric_sheet_count(p),
                "total_cells": gnumeric_cell_count_file(p),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["sheet_count"] == back["sheet_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = _ap(_GNUMERIC_DIR / "minimal-spreadsheet.gnumeric")
        records = [{"file": "minimal-spreadsheet.gnumeric", "sheets": gnumeric_sheet_count(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_multi_sheet_flag_export(self, tmp_path):
        records = []
        for f in sorted(_GNUMERIC_DIR.glob("*.gnumeric")):
            p = _ap(f)
            records.append({
                "file": f.name,
                "has_multiple": gnumeric_has_multiple_sheets(p),
                "density": gnumeric_numeric_density(p),
                "format": "gnumeric",
            })
        dest = tmp_path / "multi.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "gnumeric" for r in loaded)
        assert all(isinstance(r["has_multiple"], bool) for r in loaded)
