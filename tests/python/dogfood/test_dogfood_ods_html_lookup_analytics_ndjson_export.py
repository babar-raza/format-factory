"""
tests/python/dogfood/test_dogfood_ods_html_lookup_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-61
Dogfood export: ODS parse -> html/lookup analytics -> write as NDJSON -> verify.
Uses: parse_ods, ods_to_html, get_sheet_as_dict_list, max_column_value,
min_column_value, sheet_name_order.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods import (
    parse_ods,
    ods_to_html,
    get_sheet_as_dict_list,
    max_column_value,
    min_column_value,
    sheet_name_order,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"


def _valid_ods_files():
    return sorted(_ODS_DIR.glob("*.ods"))


class TestOdsHtmlLookupAnalyticsNdjsonExport:
    """ODS -> html/lookup analytics -> NDJSON export -> roundtrip verification."""

    def test_html_export_and_sheet_dict(self):
        sample = str(next(_ODS_DIR.glob("*.ods")))
        html = ods_to_html(sample, 0)
        sheet_dicts = get_sheet_as_dict_list(sample, 0)
        assert isinstance(html, str)
        assert isinstance(sheet_dicts, list)

    def test_column_value_range_and_sheet_order(self):
        sample = str(next(_ODS_DIR.glob("*.ods")))
        doc = parse_ods(sample)
        order = sheet_name_order(doc)
        max_val = max_column_value(sample, 0)
        min_val = min_column_value(sample, 0)
        assert isinstance(order, list)
        # max/min may be None for empty columns

    def test_html_lookup_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_ods_files():
            path = str(f)
            doc = parse_ods(path)
            html = ods_to_html(path, 0)
            sheet_dicts = get_sheet_as_dict_list(path, 0)
            order = sheet_name_order(doc)
            max_val = max_column_value(path, 0)
            min_val = min_column_value(path, 0)
            assert isinstance(html, str), f"ods_to_html must be str for {f.name}"
            assert isinstance(sheet_dicts, list), f"get_sheet_as_dict_list must be list for {f.name}"
            assert isinstance(order, list), f"sheet_name_order must be list for {f.name}"
            records.append({
                "file": f.name,
                "html_length": len(html),
                "sheet_dict_count": len(sheet_dicts),
                "sheet_count": len(order),
                "has_max_value": max_val is not None,
                "has_min_value": min_val is not None,
                "source_format": "ods",
            })
        dest = tmp_path / "ods-html-lookup.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_ods_files():
            path = str(f)
            html = ods_to_html(path, 0)
            sheet_dicts = get_sheet_as_dict_list(path, 0)
            records.append({
                "file": f.name,
                "html_length": len(html),
                "sheet_dict_count": len(sheet_dicts),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["html_length"] == back["html_length"]
            assert orig["sheet_dict_count"] == back["sheet_dict_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_ODS_DIR.glob("*.ods")))
        html = ods_to_html(sample, 0)
        records = [{"file": "sample.ods", "html_length": len(html)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_sheet_order_html_export(self, tmp_path):
        records = []
        for f in _valid_ods_files():
            path = str(f)
            doc = parse_ods(path)
            order = sheet_name_order(doc)
            html = ods_to_html(path, 0)
            sheet_dicts = get_sheet_as_dict_list(path, 0)
            assert isinstance(order, list)
            assert isinstance(html, str)
            assert isinstance(sheet_dicts, list)
            records.append({
                "file": f.name,
                "sheet_count": len(order),
                "html_length": len(html),
                "sheet_dict_count": len(sheet_dicts),
                "format": "ods",
            })
        dest = tmp_path / "sheet-order-html.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "ods" for r in loaded)
        assert all(r["html_length"] >= 0 for r in loaded)
