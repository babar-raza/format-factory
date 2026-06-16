"""
tests/python/dogfood/test_dogfood_dif_row_col_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-39
Dogfood export: DIF parse -> row/column analytics -> write as NDJSON -> verify.
Uses: dif_nonempty_row_count, dif_max_row_length, dif_string_row_count,
dif_has_header, dif_row_count, dif_column_count, dif_string_density, dif_total_cell_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif import (
    dif_nonempty_row_count,
    dif_max_row_length,
    dif_string_row_count,
    dif_has_header,
    dif_row_count,
    dif_column_count,
    dif_string_density,
    dif_total_cell_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"


def _valid_dif_files():
    return sorted(_DIF_DIR.glob("*.dif"))


class TestDifRowColAnalyticsNdjsonExport:
    """DIF -> row/column analytics -> NDJSON export -> roundtrip verification."""

    def test_row_col_counts(self):
        sample = str(_DIF_DIR / "minimal-2x2.dif")
        rows = dif_row_count(sample)
        cols = dif_column_count(sample)
        assert rows >= 0
        assert cols >= 0

    def test_nonempty_and_density(self):
        sample = str(_DIF_DIR / "minimal-2x2.dif")
        nonempty = dif_nonempty_row_count(sample)
        has_hdr = dif_has_header(sample)
        density = dif_string_density(sample)
        assert nonempty >= 0
        assert isinstance(has_hdr, bool)
        assert 0.0 <= density <= 1.0

    def test_row_col_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_dif_files():
            path = str(f)
            nonempty = dif_nonempty_row_count(path)
            max_len = dif_max_row_length(path)
            str_rows = dif_string_row_count(path)
            has_hdr = dif_has_header(path)
            rows = dif_row_count(path)
            cols = dif_column_count(path)
            density = dif_string_density(path)
            total = dif_total_cell_count(path)
            assert nonempty >= 0, f"nonempty_row_count must be >= 0 for {f.name}"
            assert max_len >= 0, f"max_row_length must be >= 0 for {f.name}"
            assert str_rows >= 0, f"string_row_count must be >= 0 for {f.name}"
            assert isinstance(has_hdr, bool), f"has_header must be bool for {f.name}"
            assert rows >= 0, f"row_count must be >= 0 for {f.name}"
            assert cols >= 0, f"column_count must be >= 0 for {f.name}"
            assert 0.0 <= density <= 1.0, f"string_density out of range for {f.name}"
            assert total >= 0, f"total_cell_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "nonempty_rows": nonempty,
                "max_row_length": max_len,
                "string_row_count": str_rows,
                "has_header": has_hdr,
                "row_count": rows,
                "column_count": cols,
                "string_density": density,
                "total_cells": total,
                "source_format": "dif",
            })
        dest = tmp_path / "dif-row-col.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_dif_files():
            path = str(f)
            records.append({
                "file": f.name,
                "row_count": dif_row_count(path),
                "has_header": dif_has_header(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["row_count"] == back["row_count"]
            assert orig["has_header"] == back["has_header"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_DIF_DIR / "minimal-2x2.dif")
        records = [{"file": "minimal-2x2.dif", "row_count": dif_row_count(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_density_and_header_export(self, tmp_path):
        records = []
        for f in _valid_dif_files():
            path = str(f)
            density = dif_string_density(path)
            has_hdr = dif_has_header(path)
            nonempty = dif_nonempty_row_count(path)
            assert 0.0 <= density <= 1.0, f"string_density out of range for {f.name}"
            assert isinstance(has_hdr, bool)
            assert nonempty >= 0
            records.append({
                "file": f.name,
                "string_density": density,
                "has_header": has_hdr,
                "nonempty_rows": nonempty,
                "format": "dif",
            })
        dest = tmp_path / "density-header.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "dif" for r in loaded)
        assert all(0.0 <= r["string_density"] <= 1.0 for r in loaded)
