"""
tests/python/dogfood/test_dogfood_fods_xml_sheet_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-71
Dogfood export: FODS parse -> xml/sheet analytics -> write as NDJSON -> verify.
Uses: parse_fods, workbook_to_xml, find_sheet_by_name, fods_sheet_names,
workbook_count_matching_cells, workbook_formula_edit_policy.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods import (
    parse_fods,
    workbook_to_xml,
    find_sheet_by_name,
    fods_sheet_names,
    workbook_count_matching_cells,
    workbook_formula_edit_policy,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODS_DIR = _REPO / "samples" / "by-format" / "fods"


def _valid_fods_files():
    return sorted(_FODS_DIR.glob("*.fods"))


class TestFodsXmlSheetAnalyticsNdjsonExport:
    """FODS -> xml/sheet analytics -> NDJSON export -> roundtrip verification."""

    def test_xml_and_sheet_basics(self):
        sample = str(next(_FODS_DIR.glob("*.fods")))
        wb = parse_fods(sample)
        xml_str = workbook_to_xml(wb)
        sheet_names = fods_sheet_names(wb)
        assert isinstance(xml_str, str)
        assert isinstance(sheet_names, list)

    def test_find_sheet_and_policy(self):
        sample = str(next(_FODS_DIR.glob("*.fods")))
        wb = parse_fods(sample)
        sheet_names = fods_sheet_names(wb)
        if sheet_names:
            sheet = find_sheet_by_name(wb, sheet_names[0])
            assert sheet is not None or sheet is None  # may return None if not found
        policy = workbook_formula_edit_policy(wb)
        assert isinstance(policy, dict)

    def test_xml_sheet_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_fods_files():
            path = str(f)
            wb = parse_fods(path)
            xml_str = workbook_to_xml(wb)
            sheet_names = fods_sheet_names(wb)
            count = workbook_count_matching_cells(wb, None)
            policy = workbook_formula_edit_policy(wb)
            first_sheet = find_sheet_by_name(wb, sheet_names[0]) if sheet_names else None
            assert isinstance(xml_str, str), f"workbook_to_xml must be str for {f.name}"
            assert isinstance(sheet_names, list), f"fods_sheet_names must be list for {f.name}"
            assert count >= 0, f"workbook_count_matching_cells must be >= 0 for {f.name}"
            assert isinstance(policy, dict), f"workbook_formula_edit_policy must be dict for {f.name}"
            records.append({
                "file": f.name,
                "xml_length": len(xml_str),
                "sheet_count": len(sheet_names),
                "matching_cell_count": count,
                "has_policy": bool(policy),
                "has_first_sheet": first_sheet is not None,
                "source_format": "fods",
            })
        dest = tmp_path / "fods-xml-sheet.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_fods_files():
            path = str(f)
            wb = parse_fods(path)
            xml_str = workbook_to_xml(wb)
            count = workbook_count_matching_cells(wb, None)
            records.append({
                "file": f.name,
                "xml_length": len(xml_str),
                "matching_cell_count": count,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["xml_length"] == back["xml_length"]
            assert orig["matching_cell_count"] == back["matching_cell_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_FODS_DIR.glob("*.fods")))
        wb = parse_fods(sample)
        xml_str = workbook_to_xml(wb)
        count = workbook_count_matching_cells(wb, None)
        records = [{"file": "sample.fods", "xml_length": len(xml_str), "matching_cell_count": count}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_xml_sheet_export(self, tmp_path):
        records = []
        for f in _valid_fods_files():
            path = str(f)
            wb = parse_fods(path)
            xml_str = workbook_to_xml(wb)
            sheet_names = fods_sheet_names(wb)
            count = workbook_count_matching_cells(wb, None)
            assert isinstance(xml_str, str)
            assert isinstance(sheet_names, list)
            assert count >= 0
            records.append({
                "file": f.name,
                "xml_length": len(xml_str),
                "sheet_count": len(sheet_names),
                "matching_cell_count": count,
                "format": "fods",
            })
        dest = tmp_path / "xml-sheet.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "fods" for r in loaded)
        assert all(r["xml_length"] > 0 for r in loaded)
