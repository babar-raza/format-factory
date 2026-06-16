"""
tests/python/dogfood/test_dogfood_dif_column_type_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-53
Dogfood export: DIF parse -> column type analytics -> write as NDJSON -> verify.
Uses: parse_dif, dif_column_types, dif_has_empty_cells, dif_row_value_counts,
dif_string_value_list, dif_column_count, dif_row_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif import (
    parse_dif,
    dif_column_types,
    dif_has_empty_cells,
    dif_row_value_counts,
    dif_string_value_list,
    dif_column_count,
    dif_row_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"


def _valid_dif_files():
    return sorted(_DIF_DIR.glob("*.dif"))


class TestDifColumnTypeAnalyticsNdjsonExport:
    """DIF -> column type analytics -> NDJSON export -> roundtrip verification."""

    def test_column_types_and_empty_cells(self):
        sample = str(next(_DIF_DIR.glob("*.dif")))
        col_types = dif_column_types(sample)
        has_empty = dif_has_empty_cells(sample)
        assert isinstance(col_types, list)
        assert isinstance(has_empty, bool)

    def test_row_value_counts_and_string_values(self):
        sample = str(next(_DIF_DIR.glob("*.dif")))
        row_counts = dif_row_value_counts(sample)
        doc = parse_dif(sample)
        string_values = dif_string_value_list(doc)
        col_count = dif_column_count(sample)
        row_count = dif_row_count(sample)
        assert isinstance(row_counts, list)
        assert isinstance(string_values, list)
        assert col_count >= 0
        assert row_count >= 0

    def test_column_type_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_dif_files():
            path = str(f)
            col_types = dif_column_types(path)
            has_empty = dif_has_empty_cells(path)
            row_counts = dif_row_value_counts(path)
            doc = parse_dif(path)
            string_values = dif_string_value_list(doc)
            col_count = dif_column_count(path)
            row_count = dif_row_count(path)
            assert isinstance(col_types, list), f"column_types must be list for {f.name}"
            assert isinstance(has_empty, bool), f"has_empty_cells must be bool for {f.name}"
            assert isinstance(row_counts, list), f"row_value_counts must be list for {f.name}"
            assert isinstance(string_values, list), f"string_value_list must be list for {f.name}"
            assert col_count >= 0, f"column_count must be >= 0 for {f.name}"
            assert row_count >= 0, f"row_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "column_type_count": len(col_types),
                "has_empty_cells": has_empty,
                "row_count": row_count,
                "column_count": col_count,
                "string_value_count": len(string_values),
                "row_value_counts": len(row_counts),
                "source_format": "dif",
            })
        dest = tmp_path / "dif-column-type.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_dif_files():
            path = str(f)
            col_types = dif_column_types(path)
            has_empty = dif_has_empty_cells(path)
            records.append({
                "file": f.name,
                "column_type_count": len(col_types),
                "has_empty_cells": has_empty,
                "row_count": dif_row_count(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["column_type_count"] == back["column_type_count"]
            assert orig["has_empty_cells"] == back["has_empty_cells"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_DIF_DIR.glob("*.dif")))
        col_types = dif_column_types(sample)
        records = [{"file": "sample.dif", "column_type_count": len(col_types)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_string_value_export(self, tmp_path):
        records = []
        for f in _valid_dif_files():
            path = str(f)
            doc = parse_dif(path)
            string_values = dif_string_value_list(doc)
            has_empty = dif_has_empty_cells(path)
            col_types = dif_column_types(path)
            assert isinstance(string_values, list)
            assert isinstance(has_empty, bool)
            assert isinstance(col_types, list)
            records.append({
                "file": f.name,
                "string_value_count": len(string_values),
                "has_empty_cells": has_empty,
                "column_type_count": len(col_types),
                "format": "dif",
            })
        dest = tmp_path / "string-value.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "dif" for r in loaded)
        assert all(r["string_value_count"] >= 0 for r in loaded)
