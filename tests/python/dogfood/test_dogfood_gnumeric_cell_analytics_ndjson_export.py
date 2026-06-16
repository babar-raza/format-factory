"""
tests/python/dogfood/test_dogfood_gnumeric_cell_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-23
Dogfood export: Gnumeric load -> cell-level analytics -> write as NDJSON -> verify.
Uses path-based analytics functions for cell count and sheet metadata.
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
    gnumeric_total_cell_count,
    gnumeric_has_multiple_sheets,
    gnumeric_average_cells_per_sheet,
    gnumeric_numeric_density,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"


def _ap(f):
    return os.path.abspath(str(f))


class TestGnumericCellAnalyticsNdjsonExport:
    """Gnumeric -> cell-level analytics -> NDJSON export -> roundtrip verification."""

    def test_sheet_count(self):
        sample = _ap(_GNUMERIC_DIR / "minimal-spreadsheet.gnumeric")
        count = gnumeric_sheet_count(sample)
        assert count >= 1

    def test_cell_count(self):
        sample = _ap(_GNUMERIC_DIR / "minimal-spreadsheet.gnumeric")
        count = gnumeric_cell_count_file(sample)
        assert count >= 1

    def test_cell_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in sorted(_GNUMERIC_DIR.glob("*.gnumeric")):
            p = _ap(f)
            records.append({
                "file": f.name,
                "sheet_count": gnumeric_sheet_count(p),
                "total_cells": gnumeric_cell_count_file(p),
                "has_multiple_sheets": gnumeric_has_multiple_sheets(p),
                "avg_cells_per_sheet": gnumeric_average_cells_per_sheet(p),
                "numeric_density": gnumeric_numeric_density(p),
                "source_format": "gnumeric",
            })
        dest = tmp_path / "gnumeric-cells.ndjson"
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
                "total_cells": gnumeric_cell_count_file(p),
                "numeric_density": gnumeric_numeric_density(p),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["total_cells"] == back["total_cells"]

    def test_json_lines_valid(self, tmp_path):
        sample = _ap(_GNUMERIC_DIR / "minimal-spreadsheet.gnumeric")
        records = [{"file": "minimal-spreadsheet.gnumeric", "cells": gnumeric_cell_count_file(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_cells_per_sheet_export(self, tmp_path):
        records = []
        for f in sorted(_GNUMERIC_DIR.glob("*.gnumeric")):
            p = _ap(f)
            records.append({
                "file": f.name,
                "avg_cells_per_sheet": gnumeric_average_cells_per_sheet(p),
                "format": "gnumeric",
            })
        dest = tmp_path / "cps.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "gnumeric" for r in loaded)
