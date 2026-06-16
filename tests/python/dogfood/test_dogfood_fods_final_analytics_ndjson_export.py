"""
tests/python/dogfood/test_dogfood_fods_final_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-86
Dogfood export: FODS parse -> final analytics -> write as NDJSON -> verify.
Uses: parse_fods, write_fods, find_sheet_by_name, workbook_rename_sheet,
      workbook_remove_sheet, fods_numeric_density, fods_data_density,
      fods_string_density, fods_is_single_sheet.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods import (
    parse_fods,
    write_fods,
    find_sheet_by_name,
    workbook_rename_sheet,
    workbook_remove_sheet,
    fods_numeric_density,
    fods_data_density,
    fods_string_density,
    fods_is_single_sheet,
    workbook_add_sheet,
    fods_sheet_names,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODS_DIR = _REPO / "samples" / "by-format" / "fods"


def _valid_fods_files():
    return sorted(_FODS_DIR.glob("*.fods"))


class TestFodsFinalAnalyticsNdjsonExport:
    """FODS -> final analytics -> NDJSON export -> roundtrip verification."""

    def test_density_analytics_basics(self):
        sample = _valid_fods_files()[0]
        wb = parse_fods(str(sample))
        num_density = fods_numeric_density(wb)
        data_density = fods_data_density(wb)
        str_density = fods_string_density(wb)
        is_single = fods_is_single_sheet(wb)
        assert isinstance(num_density, float) and num_density >= 0.0
        assert isinstance(data_density, float) and data_density >= 0.0
        assert isinstance(str_density, float) and str_density >= 0.0
        assert isinstance(is_single, bool)

    def test_find_sheet_basics(self):
        sample = _valid_fods_files()[0]
        wb = parse_fods(str(sample))
        names = fods_sheet_names(wb)
        if names:
            result = find_sheet_by_name(wb, names[0])
            assert result is None or isinstance(result, dict)

    def test_final_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_fods_files():
            wb = parse_fods(str(f))
            num_density = fods_numeric_density(wb)
            data_density = fods_data_density(wb)
            str_density = fods_string_density(wb)
            is_single = fods_is_single_sheet(wb)
            names = fods_sheet_names(wb)
            found = find_sheet_by_name(wb, names[0]) if names else None
            assert isinstance(num_density, float), f"fods_numeric_density must be float for {f.name}"
            assert isinstance(data_density, float), f"fods_data_density must be float for {f.name}"
            assert isinstance(str_density, float), f"fods_string_density must be float for {f.name}"
            assert isinstance(is_single, bool), f"fods_is_single_sheet must be bool for {f.name}"
            records.append({
                "file": f.name,
                "numeric_density": num_density,
                "data_density": data_density,
                "string_density": str_density,
                "is_single_sheet": is_single,
                "found_sheet": found is not None,
                "source_format": "fods",
            })
        dest = tmp_path / "fods-final-analytics.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_fods_files():
            wb = parse_fods(str(f))
            num_density = fods_numeric_density(wb)
            is_single = fods_is_single_sheet(wb)
            records.append({
                "file": f.name,
                "numeric_density": num_density,
                "is_single_sheet": is_single,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["is_single_sheet"] == back["is_single_sheet"]

    def test_json_lines_valid(self, tmp_path):
        sample = _valid_fods_files()[0]
        wb = parse_fods(str(sample))
        num_density = fods_numeric_density(wb)
        data_density = fods_data_density(wb)
        records = [{"file": sample.name, "numeric_density": num_density, "data_density": data_density}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_write_rename_remove_export(self, tmp_path):
        records = []
        for f in _valid_fods_files():
            wb = parse_fods(str(f))
            out = tmp_path / f"out_{f.name}"
            write_fods(wb, str(out))
            assert out.exists()
            ok_add, _ = workbook_add_sheet(wb, "_S86Sheet")
            ok_ren, msg_ren = workbook_rename_sheet(wb, "_S86Sheet", "_S86Renamed")
            ok_rem, msg_rem = workbook_remove_sheet(wb, "_S86Renamed")
            assert isinstance(ok_ren, bool), f"workbook_rename_sheet must return bool for {f.name}"
            assert isinstance(ok_rem, bool), f"workbook_remove_sheet must return bool for {f.name}"
            records.append({
                "file": f.name,
                "written_bytes": out.stat().st_size,
                "rename_ok": ok_ren,
                "remove_ok": ok_rem,
                "format": "fods",
            })
        dest = tmp_path / "write-rename-remove.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "fods" for r in loaded)
        assert all(r["written_bytes"] > 0 for r in loaded)
