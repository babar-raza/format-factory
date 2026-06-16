"""
tests/python/dogfood/test_dogfood_gnumeric_multisheet_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-43
Dogfood export: Gnumeric -> multi-sheet analytics -> write as NDJSON -> verify.
Uses: gnumeric_has_multiple_sheets, gnumeric_average_cells_per_sheet,
gnumeric_numeric_density, gnumeric_cell_count_file, gnumeric_sheet_count,
gnumeric_total_cell_count.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric import (
    gnumeric_has_multiple_sheets,
    gnumeric_average_cells_per_sheet,
    gnumeric_numeric_density,
    gnumeric_cell_count_file,
    gnumeric_sheet_count,
    gnumeric_total_cell_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"


def _ap(f):
    return os.path.abspath(str(f))


def _valid_gnumeric_files():
    return sorted(_GNUMERIC_DIR.glob("*.gnumeric"))


class TestGnumericMultisheetNdjsonExport:
    """Gnumeric -> multi-sheet analytics -> NDJSON export -> roundtrip verification."""

    def test_has_multiple_sheets(self):
        sample = _ap(next(_GNUMERIC_DIR.glob("*.gnumeric")))
        multi = gnumeric_has_multiple_sheets(sample)
        assert isinstance(multi, bool)

    def test_density_and_cell_count(self):
        sample = _ap(next(_GNUMERIC_DIR.glob("*.gnumeric")))
        density = gnumeric_numeric_density(sample)
        cells = gnumeric_cell_count_file(sample)
        avg = gnumeric_average_cells_per_sheet(sample)
        assert 0.0 <= density <= 1.0
        assert cells >= 0
        assert avg >= 0.0

    def test_multisheet_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_gnumeric_files():
            path = _ap(f)
            multi = gnumeric_has_multiple_sheets(path)
            avg = gnumeric_average_cells_per_sheet(path)
            density = gnumeric_numeric_density(path)
            cells = gnumeric_cell_count_file(path)
            sheets = gnumeric_sheet_count(path)
            total = gnumeric_total_cell_count(path)
            assert isinstance(multi, bool), f"has_multiple_sheets must be bool for {f.name}"
            assert avg >= 0.0, f"avg_cells_per_sheet must be >= 0 for {f.name}"
            assert 0.0 <= density <= 1.0, f"numeric_density out of range for {f.name}"
            assert cells >= 0, f"cell_count must be >= 0 for {f.name}"
            assert sheets >= 0, f"sheet_count must be >= 0 for {f.name}"
            assert total >= 0, f"total_cell_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "has_multiple_sheets": multi,
                "avg_cells_per_sheet": avg,
                "numeric_density": density,
                "cell_count": cells,
                "sheet_count": sheets,
                "total_cells": total,
                "source_format": "gnumeric",
            })
        dest = tmp_path / "gnumeric-multisheet.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_gnumeric_files():
            path = _ap(f)
            records.append({
                "file": f.name,
                "sheet_count": gnumeric_sheet_count(path),
                "has_multiple_sheets": gnumeric_has_multiple_sheets(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["sheet_count"] == back["sheet_count"]
            assert orig["has_multiple_sheets"] == back["has_multiple_sheets"]

    def test_json_lines_valid(self, tmp_path):
        sample = _ap(next(_GNUMERIC_DIR.glob("*.gnumeric")))
        records = [{"file": "sample.gnumeric", "numeric_density": gnumeric_numeric_density(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_density_multisheet_export(self, tmp_path):
        records = []
        for f in _valid_gnumeric_files():
            path = _ap(f)
            density = gnumeric_numeric_density(path)
            multi = gnumeric_has_multiple_sheets(path)
            avg = gnumeric_average_cells_per_sheet(path)
            assert 0.0 <= density <= 1.0
            assert isinstance(multi, bool)
            assert avg >= 0.0
            records.append({
                "file": f.name,
                "numeric_density": density,
                "has_multiple_sheets": multi,
                "avg_cells_per_sheet": avg,
                "format": "gnumeric",
            })
        dest = tmp_path / "density-multisheet.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "gnumeric" for r in loaded)
        assert all(0.0 <= r["numeric_density"] <= 1.0 for r in loaded)
