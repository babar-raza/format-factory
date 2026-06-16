"""
tests/python/dogfood/test_dogfood_fods_mutation_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-76
Dogfood export: FODS parse -> mutation/analytics -> write as NDJSON -> verify.
Uses: parse_fods, fods_all_sheets_have_data, fods_max_string_length,
workbook_warnings_for_unsupported_edit, workbook_add_sheet, workbook_set_cell_value.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods import (
    parse_fods,
    fods_all_sheets_have_data,
    fods_max_string_length,
    fods_sheet_names,
    workbook_warnings_for_unsupported_edit,
    workbook_add_sheet,
    workbook_set_cell_value,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODS_DIR = _REPO / "samples" / "by-format" / "fods"


def _valid_fods_files():
    return sorted(_FODS_DIR.glob("*.fods"))


class TestFodsMutationAnalyticsNdjsonExport:
    """FODS -> mutation/analytics -> NDJSON export -> roundtrip verification."""

    def test_analytics_basics(self):
        sample = str(next(_FODS_DIR.glob("*.fods")))
        wb = parse_fods(sample)
        all_have_data = fods_all_sheets_have_data(wb)
        max_str_len = fods_max_string_length(wb)
        assert isinstance(all_have_data, bool)
        assert max_str_len >= 0

    def test_mutation_basics(self):
        sample = str(next(_FODS_DIR.glob("*.fods")))
        wb = parse_fods(sample)
        names = fods_sheet_names(wb)
        ok, msg = workbook_add_sheet(wb, "_TestSheet_76")
        assert isinstance(ok, bool)
        assert isinstance(msg, str)
        warnings = workbook_warnings_for_unsupported_edit(wb, names[0], 0, 0) if names else []
        assert isinstance(warnings, list)

    def test_mutation_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_fods_files():
            path = str(f)
            wb = parse_fods(path)
            all_have_data = fods_all_sheets_have_data(wb)
            max_str_len = fods_max_string_length(wb)
            names = fods_sheet_names(wb)
            ok_add, _ = workbook_add_sheet(wb, f"_Sheet76_{f.stem}")
            warnings = workbook_warnings_for_unsupported_edit(wb, names[0], 0, 0) if names else []
            ok_set, _ = workbook_set_cell_value(wb, names[0], 0, 0, "test") if names else (False, "no sheets")
            assert isinstance(all_have_data, bool), f"fods_all_sheets_have_data must be bool for {f.name}"
            assert max_str_len >= 0, f"fods_max_string_length must be >= 0 for {f.name}"
            assert isinstance(ok_add, bool), f"workbook_add_sheet must return bool for {f.name}"
            assert isinstance(warnings, list), f"workbook_warnings_for_unsupported_edit must be list for {f.name}"
            assert isinstance(ok_set, bool), f"workbook_set_cell_value must return bool for {f.name}"
            records.append({
                "file": f.name,
                "all_sheets_have_data": all_have_data,
                "max_string_length": max_str_len,
                "add_sheet_ok": ok_add,
                "warning_count": len(warnings),
                "set_cell_ok": ok_set,
                "source_format": "fods",
            })
        dest = tmp_path / "fods-mutation.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_fods_files():
            path = str(f)
            wb = parse_fods(path)
            all_have_data = fods_all_sheets_have_data(wb)
            max_str_len = fods_max_string_length(wb)
            records.append({
                "file": f.name,
                "all_sheets_have_data": all_have_data,
                "max_string_length": max_str_len,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["all_sheets_have_data"] == back["all_sheets_have_data"]
            assert orig["max_string_length"] == back["max_string_length"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_FODS_DIR.glob("*.fods")))
        wb = parse_fods(sample)
        all_have_data = fods_all_sheets_have_data(wb)
        max_str_len = fods_max_string_length(wb)
        records = [{"file": "sample.fods", "all_sheets_have_data": all_have_data, "max_string_length": max_str_len}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_add_and_set_export(self, tmp_path):
        records = []
        for f in _valid_fods_files():
            path = str(f)
            wb = parse_fods(path)
            names = fods_sheet_names(wb)
            ok_add, _ = workbook_add_sheet(wb, f"_Export76_{f.stem}")
            ok_set, _ = workbook_set_cell_value(wb, names[0], 0, 0, "export") if names else (False, "no sheets")
            all_have_data = fods_all_sheets_have_data(wb)
            assert isinstance(ok_add, bool)
            assert isinstance(ok_set, bool)
            assert isinstance(all_have_data, bool)
            records.append({
                "file": f.name,
                "add_sheet_ok": ok_add,
                "set_cell_ok": ok_set,
                "all_sheets_have_data": all_have_data,
                "format": "fods",
            })
        dest = tmp_path / "add-set.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "fods" for r in loaded)
        assert all(isinstance(r["all_sheets_have_data"], bool) for r in loaded)
