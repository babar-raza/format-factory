"""
tests/python/dogfood/test_dogfood_dif_string_empty_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-69
Dogfood export: DIF parse -> string/empty analytics -> write as NDJSON -> verify.
Uses: dif_nonempty_row_count, dif_string_density, dif_numeric_cell_count,
dif_max_cell_length, dif_has_empty_cells, dif_row_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif import (
    dif_nonempty_row_count,
    dif_string_density,
    dif_numeric_cell_count,
    dif_max_cell_length,
    dif_has_empty_cells,
    dif_row_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"


def _valid_dif_files():
    return sorted(_DIF_DIR.glob("*.dif"))


class TestDifStringEmptyAnalyticsNdjsonExport:
    """DIF -> string/empty analytics -> NDJSON export -> roundtrip verification."""

    def test_nonempty_and_density_basics(self):
        sample = str(next(_DIF_DIR.glob("*.dif")))
        nonempty = dif_nonempty_row_count(sample)
        density = dif_string_density(sample)
        has_empty = dif_has_empty_cells(sample)
        assert nonempty >= 0
        assert isinstance(density, float)
        assert isinstance(has_empty, bool)

    def test_numeric_and_length_basics(self):
        sample = str(next(_DIF_DIR.glob("*.dif")))
        numeric = dif_numeric_cell_count(sample)
        max_len = dif_max_cell_length(sample)
        row_count = dif_row_count(sample)
        assert numeric >= 0
        assert max_len >= 0
        assert row_count >= 0

    def test_string_empty_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_dif_files():
            path = str(f)
            nonempty = dif_nonempty_row_count(path)
            density = dif_string_density(path)
            numeric = dif_numeric_cell_count(path)
            max_len = dif_max_cell_length(path)
            has_empty = dif_has_empty_cells(path)
            row_count = dif_row_count(path)
            assert nonempty >= 0, f"dif_nonempty_row_count must be >= 0 for {f.name}"
            assert isinstance(density, float), f"dif_string_density must be float for {f.name}"
            assert numeric >= 0, f"dif_numeric_cell_count must be >= 0 for {f.name}"
            assert max_len >= 0, f"dif_max_cell_length must be >= 0 for {f.name}"
            assert isinstance(has_empty, bool), f"dif_has_empty_cells must be bool for {f.name}"
            assert row_count >= 0, f"dif_row_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "nonempty_row_count": nonempty,
                "string_density": density,
                "numeric_cell_count": numeric,
                "max_cell_length": max_len,
                "has_empty_cells": has_empty,
                "row_count": row_count,
                "source_format": "dif",
            })
        dest = tmp_path / "dif-string-empty.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_dif_files():
            path = str(f)
            nonempty = dif_nonempty_row_count(path)
            density = dif_string_density(path)
            records.append({
                "file": f.name,
                "nonempty_row_count": nonempty,
                "string_density": density,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["nonempty_row_count"] == back["nonempty_row_count"]
            assert orig["string_density"] == back["string_density"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_DIF_DIR.glob("*.dif")))
        nonempty = dif_nonempty_row_count(sample)
        has_empty = dif_has_empty_cells(sample)
        records = [{"file": "sample.dif", "nonempty_row_count": nonempty, "has_empty_cells": has_empty}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_string_empty_export(self, tmp_path):
        records = []
        for f in _valid_dif_files():
            path = str(f)
            nonempty = dif_nonempty_row_count(path)
            density = dif_string_density(path)
            has_empty = dif_has_empty_cells(path)
            numeric = dif_numeric_cell_count(path)
            assert nonempty >= 0
            assert isinstance(density, float)
            assert isinstance(has_empty, bool)
            assert numeric >= 0
            records.append({
                "file": f.name,
                "nonempty_row_count": nonempty,
                "string_density": density,
                "has_empty_cells": has_empty,
                "numeric_cell_count": numeric,
                "format": "dif",
            })
        dest = tmp_path / "string-empty.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "dif" for r in loaded)
        assert all(isinstance(r["has_empty_cells"], bool) for r in loaded)
