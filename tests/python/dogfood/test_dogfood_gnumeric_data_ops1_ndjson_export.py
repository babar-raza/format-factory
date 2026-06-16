"""
tests/python/dogfood/test_dogfood_gnumeric_data_ops1_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-87
Dogfood export: Gnumeric load -> data ops batch 1 -> write as NDJSON -> verify.
Uses: load, fill_column, fill_row, get_row, get_column, get_all_values, clear_sheet.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric import (
    load,
    fill_column,
    fill_row,
    get_row,
    get_column,
    get_all_values,
    clear_sheet,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_GNU_DIR = _REPO / "samples" / "by-format" / "gnumeric"


def _ap(f):
    return os.path.abspath(str(f))


def _valid_gnumeric_files():
    return sorted(_GNU_DIR.glob("*.gnumeric"))


class TestGnumericDataOps1NdjsonExport:
    """Gnumeric -> data ops batch 1 -> NDJSON export -> roundtrip verification."""

    def test_get_row_column_basics(self):
        sample = _valid_gnumeric_files()[0]
        model = load(_ap(sample))
        row = get_row(model, 0, 0)
        col = get_column(model, 0, 0)
        assert isinstance(row, list)
        assert isinstance(col, list)

    def test_fill_ops_basics(self):
        sample = _valid_gnumeric_files()[0]
        model = load(_ap(sample))
        filled_col = fill_column(model, 0, 0, ["a", "b", "c"])
        assert isinstance(filled_col, dict) and "sheets" in filled_col
        filled_row = fill_row(model, 0, 0, ["x", "y", "z"])
        assert isinstance(filled_row, dict) and "sheets" in filled_row

    def test_data_ops1_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_gnumeric_files():
            model = load(_ap(f))
            row = get_row(model, 0, 0)
            col = get_column(model, 0, 0)
            all_vals = get_all_values(model, 0)
            filled_col = fill_column(model, 0, 0, ["p", "q", "r"])
            filled_row = fill_row(model, 0, 0, ["u", "v", "w"])
            cleared = clear_sheet(model, 0)
            assert isinstance(row, list), f"get_row must return list for {f.name}"
            assert isinstance(col, list), f"get_column must return list for {f.name}"
            assert isinstance(all_vals, list), f"get_all_values must return list for {f.name}"
            assert isinstance(filled_col, dict) and "sheets" in filled_col, f"fill_column must return dict with sheets for {f.name}"
            assert isinstance(filled_row, dict) and "sheets" in filled_row, f"fill_row must return dict with sheets for {f.name}"
            assert isinstance(cleared, dict) and "sheets" in cleared, f"clear_sheet must return dict with sheets for {f.name}"
            records.append({
                "file": f.name,
                "row_length": len(row),
                "col_length": len(col),
                "all_values_count": len(all_vals),
                "fill_col_ok": isinstance(filled_col, dict),
                "fill_row_ok": isinstance(filled_row, dict),
                "clear_sheet_ok": isinstance(cleared, dict),
                "source_format": "gnumeric",
            })
        dest = tmp_path / "gnumeric-data-ops1.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_gnumeric_files():
            model = load(_ap(f))
            row = get_row(model, 0, 0)
            all_vals = get_all_values(model, 0)
            records.append({
                "file": f.name,
                "row_length": len(row),
                "all_values_count": len(all_vals),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["row_length"] == back["row_length"]

    def test_json_lines_valid(self, tmp_path):
        sample = _valid_gnumeric_files()[0]
        model = load(_ap(sample))
        row = get_row(model, 0, 0)
        col = get_column(model, 0, 0)
        records = [{"file": sample.name, "row_length": len(row), "col_length": len(col)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_fill_clear_functional(self, tmp_path):
        records = []
        for f in _valid_gnumeric_files():
            model = load(_ap(f))
            # fill_column adds data — verify it returns model with sheets
            fc = fill_column(model, 0, 0, ["1", "2", "3"])
            assert "sheets" in fc
            # fill_row adds data — verify it returns model with sheets
            fr = fill_row(model, 0, 0, ["a", "b", "c"])
            assert "sheets" in fr
            # clear_sheet blanks sheet — verify it returns model with sheets
            cs = clear_sheet(model, 0)
            assert "sheets" in cs
            records.append({
                "file": f.name,
                "fill_col_ok": True,
                "fill_row_ok": True,
                "clear_sheet_ok": True,
                "format": "gnumeric",
            })
        dest = tmp_path / "fill-clear.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "gnumeric" for r in loaded)
        assert all(r["fill_col_ok"] for r in loaded)
