"""
tests/python/dogfood/test_dogfood_fods_style_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-52
Dogfood export: FODS parse -> style analytics -> write as NDJSON -> verify.
Uses: parse_fods, workbook_style_family_list, workbook_column_style_summary,
workbook_row_style_summary, workbook_named_range_list, workbook_formula_list.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods import (
    parse_fods,
    workbook_style_family_list,
    workbook_column_style_summary,
    workbook_row_style_summary,
    workbook_named_range_list,
    workbook_formula_list,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODS_DIR = _REPO / "samples" / "by-format" / "fods"


def _valid_fods_files():
    return sorted(_FODS_DIR.glob("*.fods"))


class TestFodsStyleAnalyticsNdjsonExport:
    """FODS -> style analytics -> NDJSON export -> roundtrip verification."""

    def test_style_family_list(self):
        sample = str(next(_FODS_DIR.glob("*.fods")))
        wb = parse_fods(sample)
        styles = workbook_style_family_list(wb)
        assert isinstance(styles, list)

    def test_column_row_style_and_ranges(self):
        sample = str(next(_FODS_DIR.glob("*.fods")))
        wb = parse_fods(sample)
        col_styles = workbook_column_style_summary(wb)
        row_styles = workbook_row_style_summary(wb)
        named_ranges = workbook_named_range_list(wb)
        formulas = workbook_formula_list(wb)
        assert isinstance(col_styles, dict)
        assert isinstance(row_styles, dict)
        assert isinstance(named_ranges, list)
        assert isinstance(formulas, list)

    def test_style_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_fods_files():
            path = str(f)
            wb = parse_fods(path)
            styles = workbook_style_family_list(wb)
            col_styles = workbook_column_style_summary(wb)
            row_styles = workbook_row_style_summary(wb)
            named_ranges = workbook_named_range_list(wb)
            formulas = workbook_formula_list(wb)
            assert isinstance(styles, list), f"style_family_list must be list for {f.name}"
            assert isinstance(col_styles, dict), f"column_style_summary must be dict for {f.name}"
            assert isinstance(row_styles, dict), f"row_style_summary must be dict for {f.name}"
            assert isinstance(named_ranges, list), f"named_range_list must be list for {f.name}"
            assert isinstance(formulas, list), f"formula_list must be list for {f.name}"
            records.append({
                "file": f.name,
                "style_family_count": len(styles),
                "col_style_sheet_count": len(col_styles),
                "row_style_sheet_count": len(row_styles),
                "named_range_count": len(named_ranges),
                "formula_count": len(formulas),
                "source_format": "fods",
            })
        dest = tmp_path / "fods-style.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_fods_files():
            wb = parse_fods(str(f))
            records.append({
                "file": f.name,
                "style_family_count": len(workbook_style_family_list(wb)),
                "formula_count": len(workbook_formula_list(wb)),
                "named_range_count": len(workbook_named_range_list(wb)),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["formula_count"] == back["formula_count"]
            assert orig["named_range_count"] == back["named_range_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_FODS_DIR.glob("*.fods")))
        wb = parse_fods(sample)
        styles = workbook_style_family_list(wb)
        records = [{"file": "sample.fods", "style_count": len(styles)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_formula_range_export(self, tmp_path):
        records = []
        for f in _valid_fods_files():
            wb = parse_fods(str(f))
            formulas = workbook_formula_list(wb)
            named_ranges = workbook_named_range_list(wb)
            col_styles = workbook_column_style_summary(wb)
            assert isinstance(formulas, list)
            assert isinstance(named_ranges, list)
            assert isinstance(col_styles, dict)
            records.append({
                "file": f.name,
                "formula_count": len(formulas),
                "named_range_count": len(named_ranges),
                "col_style_count": len(col_styles),
                "format": "fods",
            })
        dest = tmp_path / "formula-range.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "fods" for r in loaded)
        assert all(r["formula_count"] >= 0 for r in loaded)
