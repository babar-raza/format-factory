"""
tests/python/dogfood/test_dogfood_gnumeric_row_col_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-37
Dogfood export: Gnumeric -> row/column/density analytics -> write as NDJSON -> verify.
Uses: gnumeric_row_count_file, gnumeric_column_count_file, gnumeric_nonempty_cell_count_file,
gnumeric_string_density, gnumeric_max_cell_length.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric import (
    gnumeric_row_count_file,
    gnumeric_column_count_file,
    gnumeric_nonempty_cell_count_file,
    gnumeric_string_density,
    gnumeric_max_cell_length,
    gnumeric_sheet_count,
    gnumeric_total_cell_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"


def _ap(f):
    return os.path.abspath(str(f))


def _valid_gnumeric_files():
    return sorted(_GNUMERIC_DIR.glob("*.gnumeric"))


class TestGnumericRowColAnalyticsNdjsonExport:
    """Gnumeric -> row/column/density analytics -> NDJSON export -> roundtrip verification."""

    def test_row_col_counts(self):
        sample = _ap(next(_GNUMERIC_DIR.glob("*.gnumeric")))
        rows = gnumeric_row_count_file(sample)
        cols = gnumeric_column_count_file(sample)
        assert rows >= 0
        assert cols >= 0

    def test_nonempty_and_density(self):
        sample = _ap(next(_GNUMERIC_DIR.glob("*.gnumeric")))
        nonempty = gnumeric_nonempty_cell_count_file(sample)
        sd = gnumeric_string_density(sample)
        mcl = gnumeric_max_cell_length(sample)
        assert nonempty >= 0
        assert 0.0 <= sd <= 1.0
        assert mcl >= 0

    def test_row_col_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_gnumeric_files():
            path = _ap(f)
            rows = gnumeric_row_count_file(path)
            cols = gnumeric_column_count_file(path)
            nonempty = gnumeric_nonempty_cell_count_file(path)
            sd = gnumeric_string_density(path)
            mcl = gnumeric_max_cell_length(path)
            sheets = gnumeric_sheet_count(path)
            total = gnumeric_total_cell_count(path)
            assert rows >= 0, f"row_count must be >= 0 for {f.name}"
            assert cols >= 0, f"col_count must be >= 0 for {f.name}"
            assert nonempty >= 0, f"nonempty_cells must be >= 0 for {f.name}"
            assert 0.0 <= sd <= 1.0, f"string_density out of range for {f.name}"
            assert mcl >= 0, f"max_cell_length must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "row_count": rows,
                "column_count": cols,
                "nonempty_cells": nonempty,
                "string_density": sd,
                "max_cell_length": mcl,
                "sheet_count": sheets,
                "total_cells": total,
                "source_format": "gnumeric",
            })
        dest = tmp_path / "gnumeric-row-col.ndjson"
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
                "row_count": gnumeric_row_count_file(path),
                "column_count": gnumeric_column_count_file(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["row_count"] == back["row_count"]
            assert orig["column_count"] == back["column_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = _ap(next(_GNUMERIC_DIR.glob("*.gnumeric")))
        records = [{"file": "sample.gnumeric", "string_density": gnumeric_string_density(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_density_analytics_export(self, tmp_path):
        records = []
        for f in _valid_gnumeric_files():
            path = _ap(f)
            sd = gnumeric_string_density(path)
            mcl = gnumeric_max_cell_length(path)
            nonempty = gnumeric_nonempty_cell_count_file(path)
            assert 0.0 <= sd <= 1.0, f"string_density out of range for {f.name}"
            assert mcl >= 0, f"max_cell_length must be >= 0 for {f.name}"
            assert nonempty >= 0, f"nonempty_cells must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "string_density": sd,
                "max_cell_length": mcl,
                "nonempty_cells": nonempty,
                "format": "gnumeric",
            })
        dest = tmp_path / "density.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "gnumeric" for r in loaded)
        assert all(0.0 <= r["string_density"] <= 1.0 for r in loaded)
