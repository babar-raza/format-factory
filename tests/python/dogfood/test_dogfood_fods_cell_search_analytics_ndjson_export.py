"""
tests/python/dogfood/test_dogfood_fods_cell_search_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-65
Dogfood export: FODS parse -> cell search analytics -> write as NDJSON -> verify.
Uses: parse_fods, workbook_find_cells, workbook_count_matching_cells,
workbook_cell_text_at, workbook_to_csv, workbook_get_cell_value.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods import (
    parse_fods,
    workbook_find_cells,
    workbook_count_matching_cells,
    workbook_cell_text_at,
    workbook_to_csv,
    workbook_get_cell_value,
    fods_sheet_names,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODS_DIR = _REPO / "samples" / "by-format" / "fods"


def _valid_fods_files():
    return sorted(_FODS_DIR.glob("*.fods"))


class TestFodsCellSearchAnalyticsNdjsonExport:
    """FODS -> cell search analytics -> NDJSON export -> roundtrip verification."""

    def test_find_cells_and_count_matching(self):
        sample = str(next(_FODS_DIR.glob("*.fods")))
        wb = parse_fods(sample)
        found = workbook_find_cells(wb, None)
        count = workbook_count_matching_cells(wb, None)
        assert isinstance(found, list)
        assert count >= 0

    def test_cell_text_and_to_csv(self):
        sample = str(next(_FODS_DIR.glob("*.fods")))
        wb = parse_fods(sample)
        text = workbook_cell_text_at(wb, 0, 0, 0)
        csv_str = workbook_to_csv(wb)
        assert isinstance(text, str)
        assert isinstance(csv_str, str)

    def test_cell_search_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_fods_files():
            path = str(f)
            wb = parse_fods(path)
            found = workbook_find_cells(wb, None)
            count = workbook_count_matching_cells(wb, None)
            text = workbook_cell_text_at(wb, 0, 0, 0)
            csv_str = workbook_to_csv(wb)
            sheet_names = fods_sheet_names(wb)
            cell_val = workbook_get_cell_value(wb, sheet_names[0], 0, 0) if sheet_names else None
            assert isinstance(found, list), f"workbook_find_cells must be list for {f.name}"
            assert count >= 0, f"workbook_count_matching_cells must be >= 0 for {f.name}"
            assert isinstance(text, str), f"workbook_cell_text_at must be str for {f.name}"
            assert isinstance(csv_str, str), f"workbook_to_csv must be str for {f.name}"
            records.append({
                "file": f.name,
                "null_cell_count": len(found),
                "matching_cell_count": count,
                "cell_0_0_text": text,
                "csv_length": len(csv_str),
                "has_cell_value": cell_val is not None,
                "source_format": "fods",
            })
        dest = tmp_path / "fods-cell-search.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_fods_files():
            path = str(f)
            wb = parse_fods(path)
            count = workbook_count_matching_cells(wb, None)
            csv_str = workbook_to_csv(wb)
            records.append({
                "file": f.name,
                "matching_cell_count": count,
                "csv_length": len(csv_str),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["matching_cell_count"] == back["matching_cell_count"]
            assert orig["csv_length"] == back["csv_length"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_FODS_DIR.glob("*.fods")))
        wb = parse_fods(sample)
        count = workbook_count_matching_cells(wb, None)
        records = [{"file": "sample.fods", "matching_cell_count": count}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_find_csv_text_export(self, tmp_path):
        records = []
        for f in _valid_fods_files():
            path = str(f)
            wb = parse_fods(path)
            found = workbook_find_cells(wb, None)
            csv_str = workbook_to_csv(wb)
            text = workbook_cell_text_at(wb, 0, 0, 0)
            assert isinstance(found, list)
            assert isinstance(csv_str, str)
            assert isinstance(text, str)
            records.append({
                "file": f.name,
                "null_cell_count": len(found),
                "csv_length": len(csv_str),
                "cell_0_0_text": text,
                "format": "fods",
            })
        dest = tmp_path / "find-csv-text.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "fods" for r in loaded)
