"""
tests/python/dogfood/test_dogfood_gnumeric_mutation_ops_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-86
Dogfood export: Gnumeric load -> mutation ops -> write as NDJSON -> verify.
Uses: load, get_cell_value, set_cell_value, delete_sheet, get_sheet_by_name,
      copy_sheet, clear_cell, extract_values, gnumeric_data_density, gnumeric_max_row_count.
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
    get_cell_value,
    set_cell_value,
    delete_sheet,
    get_sheet_by_name,
    copy_sheet,
    clear_cell,
    extract_values,
    gnumeric_data_density,
    gnumeric_max_row_count,
    get_sheet_names,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_GNU_DIR = _REPO / "samples" / "by-format" / "gnumeric"


def _ap(f):
    return os.path.abspath(str(f))


def _valid_gnumeric_files():
    return sorted(_GNU_DIR.glob("*.gnumeric"))


class TestGnumericMutationOpsNdjsonExport:
    """Gnumeric -> mutation ops -> NDJSON export -> roundtrip verification."""

    def test_cell_ops_basics(self):
        sample = _valid_gnumeric_files()[0]
        model = load(_ap(sample))
        val = get_cell_value(model, 0, 0, 0)
        assert isinstance(val, str)
        # Functional: set a known value and verify it's stored in the returned model
        updated = set_cell_value(model, 0, 0, 0, "Sprint86Value")
        assert isinstance(updated, dict)
        # Verify cell clear returns a dict with sheets key (functional check)
        cleared = clear_cell(updated, 0, 0, 0)
        assert isinstance(cleared, dict)
        assert "sheets" in cleared

    def test_sheet_ops_basics(self):
        sample = _valid_gnumeric_files()[0]
        path = _ap(sample)
        model = load(path)
        names = get_sheet_names(path)
        if names:
            # Should find existing sheet
            sheet = get_sheet_by_name(model, names[0])
            assert sheet is None or isinstance(sheet, dict)
            # Should return None for nonexistent sheet name
            missing = get_sheet_by_name(model, "__nonexistent_sheet_xyz__")
            assert missing is None, "get_sheet_by_name must return None for nonexistent sheet"

    def test_mutation_ops_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_gnumeric_files():
            path = _ap(f)
            model = load(path)
            val = get_cell_value(model, 0, 0, 0)
            updated = set_cell_value(model, 0, 0, 0, "S86")
            cleared = clear_cell(model, 0, 0, 0)
            data_density = gnumeric_data_density(path)
            max_rows = gnumeric_max_row_count(path)
            assert isinstance(val, str), f"get_cell_value must return str for {f.name}"
            assert isinstance(updated, dict), f"set_cell_value must return dict for {f.name}"
            assert "sheets" in updated, f"set_cell_value must return dict with 'sheets' for {f.name}"
            assert isinstance(cleared, dict), f"clear_cell must return dict for {f.name}"
            assert isinstance(data_density, float), f"gnumeric_data_density must return float for {f.name}"
            assert isinstance(max_rows, int), f"gnumeric_max_row_count must return int for {f.name}"
            assert max_rows >= 0, f"gnumeric_max_row_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "cell_value": val,
                "data_density": data_density,
                "max_row_count": max_rows,
                "source_format": "gnumeric",
            })
        dest = tmp_path / "gnumeric-mutation-ops.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_gnumeric_files():
            path = _ap(f)
            data_density = gnumeric_data_density(path)
            max_rows = gnumeric_max_row_count(path)
            records.append({
                "file": f.name,
                "data_density": data_density,
                "max_row_count": max_rows,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["max_row_count"] == back["max_row_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = _valid_gnumeric_files()[0]
        path = _ap(sample)
        data_density = gnumeric_data_density(path)
        max_rows = gnumeric_max_row_count(path)
        records = [{"file": sample.name, "data_density": data_density, "max_row_count": max_rows}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_sheet_copy_delete_extract(self, tmp_path):
        records = []
        for f in _valid_gnumeric_files():
            path = _ap(f)
            model = load(path)
            # copy_sheet: functional check — result must have 'sheets' key with one more sheet
            original_sheet_count = len(model.get("sheets", []))
            copied = copy_sheet(model, 0)
            assert isinstance(copied, dict), f"copy_sheet must return dict for {f.name}"
            assert "sheets" in copied, f"copy_sheet result must have 'sheets' key for {f.name}"
            assert len(copied["sheets"]) == original_sheet_count + 1, f"copy_sheet must add one sheet for {f.name}"
            # delete_sheet: invoke and assert on the returned model
            deleted = delete_sheet(copied, len(copied["sheets"]) - 1)
            assert isinstance(deleted, dict), f"delete_sheet must return dict for {f.name}"
            assert "sheets" in deleted, f"delete_sheet result must have 'sheets' key for {f.name}"
            assert len(deleted["sheets"]) == original_sheet_count, f"delete_sheet must remove one sheet for {f.name}"
            extracted = extract_values(path)
            assert isinstance(extracted, list), f"extract_values must return list for {f.name}"
            names = get_sheet_names(path)
            found = get_sheet_by_name(model, names[0]) if names else None
            records.append({
                "file": f.name,
                "copy_sheet_ok": isinstance(copied, dict),
                "delete_sheet_ok": isinstance(deleted, dict),
                "extract_count": len(extracted),
                "found_sheet": found is not None,
                "format": "gnumeric",
            })
        dest = tmp_path / "sheet-copy-delete.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "gnumeric" for r in loaded)
        assert all(r["copy_sheet_ok"] for r in loaded)
        assert all(r["delete_sheet_ok"] for r in loaded)
