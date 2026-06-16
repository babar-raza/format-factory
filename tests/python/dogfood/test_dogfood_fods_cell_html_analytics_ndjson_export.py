"""
tests/python/dogfood/test_dogfood_fods_cell_html_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-60
Dogfood export: FODS parse -> cell/html analytics -> write as NDJSON -> verify.
Uses: parse_fods, workbook_formula_edit_policy, workbook_column_width_summary,
workbook_cell_type_matrix, workbook_to_html, fods_has_empty_sheets.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods import (
    parse_fods,
    workbook_formula_edit_policy,
    workbook_column_width_summary,
    workbook_cell_type_matrix,
    workbook_to_html,
    fods_has_empty_sheets,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODS_DIR = _REPO / "samples" / "by-format" / "fods"


def _valid_fods_files():
    return sorted(_FODS_DIR.glob("*.fods"))


class TestFodsCellHtmlAnalyticsNdjsonExport:
    """FODS -> cell/html analytics -> NDJSON export -> roundtrip verification."""

    def test_formula_edit_policy_and_column_widths(self):
        sample = str(next(_FODS_DIR.glob("*.fods")))
        wb = parse_fods(sample)
        policy = workbook_formula_edit_policy(wb)
        widths = workbook_column_width_summary(wb)
        assert isinstance(policy, dict)
        assert isinstance(widths, list)

    def test_cell_type_matrix_and_html(self):
        sample = str(next(_FODS_DIR.glob("*.fods")))
        wb = parse_fods(sample)
        matrix = workbook_cell_type_matrix(wb)
        html = workbook_to_html(wb, 0)
        has_empty = fods_has_empty_sheets(wb)
        assert isinstance(matrix, list)
        assert isinstance(html, str)
        assert isinstance(has_empty, bool)

    def test_cell_html_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_fods_files():
            path = str(f)
            wb = parse_fods(path)
            policy = workbook_formula_edit_policy(wb)
            widths = workbook_column_width_summary(wb)
            matrix = workbook_cell_type_matrix(wb)
            html = workbook_to_html(wb, 0)
            has_empty = fods_has_empty_sheets(wb)
            assert isinstance(policy, dict), f"formula_edit_policy must be dict for {f.name}"
            assert isinstance(widths, list), f"column_width_summary must be list for {f.name}"
            assert isinstance(matrix, list), f"cell_type_matrix must be list for {f.name}"
            assert isinstance(html, str), f"workbook_to_html must be str for {f.name}"
            assert isinstance(has_empty, bool), f"fods_has_empty_sheets must be bool for {f.name}"
            records.append({
                "file": f.name,
                "policy_keys": len(policy),
                "column_width_count": len(widths),
                "cell_type_matrix_count": len(matrix),
                "html_length": len(html),
                "has_empty_sheets": has_empty,
                "source_format": "fods",
            })
        dest = tmp_path / "fods-cell-html.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_fods_files():
            path = str(f)
            wb = parse_fods(path)
            widths = workbook_column_width_summary(wb)
            html = workbook_to_html(wb, 0)
            records.append({
                "file": f.name,
                "column_width_count": len(widths),
                "html_length": len(html),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["column_width_count"] == back["column_width_count"]
            assert orig["html_length"] == back["html_length"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_FODS_DIR.glob("*.fods")))
        wb = parse_fods(sample)
        policy = workbook_formula_edit_policy(wb)
        records = [{"file": "sample.fods", "policy_keys": len(policy)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_matrix_html_export(self, tmp_path):
        records = []
        for f in _valid_fods_files():
            path = str(f)
            wb = parse_fods(path)
            matrix = workbook_cell_type_matrix(wb)
            html = workbook_to_html(wb, 0)
            has_empty = fods_has_empty_sheets(wb)
            assert isinstance(matrix, list)
            assert isinstance(html, str)
            assert isinstance(has_empty, bool)
            records.append({
                "file": f.name,
                "cell_type_matrix_count": len(matrix),
                "html_length": len(html),
                "has_empty_sheets": has_empty,
                "format": "fods",
            })
        dest = tmp_path / "matrix-html.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "fods" for r in loaded)
        assert all(isinstance(r["has_empty_sheets"], bool) for r in loaded)
