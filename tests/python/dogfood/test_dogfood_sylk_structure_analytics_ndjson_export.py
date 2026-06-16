"""
tests/python/dogfood/test_dogfood_sylk_structure_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-38
Dogfood export: SYLK parse -> structure analytics -> write as NDJSON -> verify.
Uses: sylk_nonempty_rows, sylk_max_column_index, sylk_empty_cell_count,
sylk_cell_type_distribution, sylk_has_header.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk import (
    sylk_nonempty_rows,
    sylk_max_column_index,
    sylk_empty_cell_count,
    sylk_cell_type_distribution,
    sylk_has_header,
    sylk_row_count,
    sylk_total_cell_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"


def _valid_sylk_files():
    return sorted(_SYLK_DIR.glob("*.slk"))


class TestSylkStructureAnalyticsNdjsonExport:
    """SYLK -> structure analytics -> NDJSON export -> roundtrip verification."""

    def test_nonempty_rows_and_max_col(self):
        sample = str(_SYLK_DIR / "minimal-2x2.slk")
        nonempty = sylk_nonempty_rows(sample)
        max_col = sylk_max_column_index(sample)
        assert nonempty >= 0
        assert max_col >= 0

    def test_empty_cells_and_distribution(self):
        sample = str(_SYLK_DIR / "minimal-2x2.slk")
        empty = sylk_empty_cell_count(sample)
        dist = sylk_cell_type_distribution(sample)
        has_hdr = sylk_has_header(sample)
        assert empty >= 0
        assert isinstance(dist, dict)
        assert isinstance(has_hdr, bool)

    def test_structure_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_sylk_files():
            path = str(f)
            nonempty = sylk_nonempty_rows(path)
            max_col = sylk_max_column_index(path)
            empty = sylk_empty_cell_count(path)
            dist = sylk_cell_type_distribution(path)
            has_hdr = sylk_has_header(path)
            rows = sylk_row_count(path)
            total = sylk_total_cell_count(path)
            assert nonempty >= 0, f"nonempty_rows must be >= 0 for {f.name}"
            assert max_col >= 0, f"max_column_index must be >= 0 for {f.name}"
            assert empty >= 0, f"empty_cell_count must be >= 0 for {f.name}"
            assert isinstance(dist, dict), f"cell_type_distribution must be dict for {f.name}"
            assert isinstance(has_hdr, bool), f"has_header must be bool for {f.name}"
            assert rows >= 0, f"row_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "nonempty_rows": nonempty,
                "max_column_index": max_col,
                "empty_cell_count": empty,
                "cell_type_distribution": dist,
                "has_header": has_hdr,
                "row_count": rows,
                "total_cells": total,
                "source_format": "sylk",
            })
        dest = tmp_path / "sylk-structure.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_sylk_files():
            path = str(f)
            records.append({
                "file": f.name,
                "nonempty_rows": sylk_nonempty_rows(path),
                "has_header": sylk_has_header(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["nonempty_rows"] == back["nonempty_rows"]
            assert orig["has_header"] == back["has_header"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_SYLK_DIR / "minimal-2x2.slk")
        records = [{"file": "minimal-2x2.slk", "empty_cells": sylk_empty_cell_count(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_header_distribution_export(self, tmp_path):
        records = []
        for f in _valid_sylk_files():
            path = str(f)
            has_hdr = sylk_has_header(path)
            dist = sylk_cell_type_distribution(path)
            empty = sylk_empty_cell_count(path)
            assert isinstance(has_hdr, bool)
            assert isinstance(dist, dict)
            assert empty >= 0
            records.append({
                "file": f.name,
                "has_header": has_hdr,
                "cell_type_distribution": dist,
                "empty_cell_count": empty,
                "format": "sylk",
            })
        dest = tmp_path / "header-dist.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "sylk" for r in loaded)
        assert all(isinstance(r["has_header"], bool) for r in loaded)
