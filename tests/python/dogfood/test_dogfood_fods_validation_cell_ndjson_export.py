"""
tests/python/dogfood/test_dogfood_fods_validation_cell_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-57
Dogfood export: FODS parse -> validation/cell analytics -> write as NDJSON -> verify.
Uses: parse_fods, workbook_data_validation_summary, workbook_empty_rows,
workbook_cell_range, workbook_get_column_values, workbook_sheet_order.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods import (
    parse_fods,
    workbook_data_validation_summary,
    workbook_empty_rows,
    workbook_cell_range,
    workbook_get_column_values,
    workbook_sheet_order,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODS_DIR = _REPO / "samples" / "by-format" / "fods"


def _valid_fods_files():
    return sorted(_FODS_DIR.glob("*.fods"))


class TestFodsValidationCellNdjsonExport:
    """FODS -> validation/cell analytics -> NDJSON export -> roundtrip verification."""

    def test_data_validation_and_empty_rows(self):
        sample = str(next(_FODS_DIR.glob("*.fods")))
        wb = parse_fods(sample)
        validation = workbook_data_validation_summary(wb)
        empty_rows = workbook_empty_rows(wb)
        assert isinstance(validation, dict)
        assert isinstance(empty_rows, dict)

    def test_cell_range_and_column_values(self):
        sample = str(next(_FODS_DIR.glob("*.fods")))
        wb = parse_fods(sample)
        cell_range = workbook_cell_range(wb)
        col_values = workbook_get_column_values(wb, 0)
        sheet_order = workbook_sheet_order(wb)
        assert isinstance(cell_range, list)
        assert isinstance(col_values, list)
        assert isinstance(sheet_order, list)

    def test_validation_cell_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_fods_files():
            path = str(f)
            wb = parse_fods(path)
            validation = workbook_data_validation_summary(wb)
            empty_rows = workbook_empty_rows(wb)
            cell_range = workbook_cell_range(wb)
            col_values = workbook_get_column_values(wb, 0)
            sheet_order = workbook_sheet_order(wb)
            assert isinstance(validation, dict), f"data_validation_summary must be dict for {f.name}"
            assert isinstance(empty_rows, dict), f"empty_rows must be dict for {f.name}"
            assert isinstance(cell_range, list), f"cell_range must be list for {f.name}"
            assert isinstance(col_values, list), f"get_column_values must be list for {f.name}"
            assert isinstance(sheet_order, list), f"sheet_order must be list for {f.name}"
            records.append({
                "file": f.name,
                "validation_keys": len(validation),
                "empty_row_sheets": len(empty_rows),
                "cell_range_rows": len(cell_range),
                "col0_value_count": len(col_values),
                "sheet_count": len(sheet_order),
                "source_format": "fods",
            })
        dest = tmp_path / "fods-validation-cell.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_fods_files():
            wb = parse_fods(str(f))
            validation = workbook_data_validation_summary(wb)
            col_values = workbook_get_column_values(wb, 0)
            records.append({
                "file": f.name,
                "validation_keys": len(validation),
                "col0_value_count": len(col_values),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["validation_keys"] == back["validation_keys"]
            assert orig["col0_value_count"] == back["col0_value_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_FODS_DIR.glob("*.fods")))
        wb = parse_fods(sample)
        validation = workbook_data_validation_summary(wb)
        records = [{"file": "sample.fods", "validation_keys": len(validation)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_empty_rows_column_export(self, tmp_path):
        records = []
        for f in _valid_fods_files():
            wb = parse_fods(str(f))
            empty_rows = workbook_empty_rows(wb)
            col_values = workbook_get_column_values(wb, 0)
            cell_range = workbook_cell_range(wb)
            assert isinstance(empty_rows, dict)
            assert isinstance(col_values, list)
            assert isinstance(cell_range, list)
            records.append({
                "file": f.name,
                "empty_row_sheets": len(empty_rows),
                "col0_value_count": len(col_values),
                "cell_range_rows": len(cell_range),
                "format": "fods",
            })
        dest = tmp_path / "empty-rows-col.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "fods" for r in loaded)
        assert all(r["col0_value_count"] >= 0 for r in loaded)
