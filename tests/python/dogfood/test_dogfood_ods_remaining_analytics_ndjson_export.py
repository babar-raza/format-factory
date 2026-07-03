"""
tests/python/dogfood/test_dogfood_ods_remaining_analytics_ndjson_export.py

Sprint: PRODUCT-DEEPENING-SPRINT-51
Dogfood export: ODS remaining uncovered analytics -> write as NDJSON -> verify.
Uses: ods_has_numeric_cells, ods_has_string_cells, ods_is_empty,
      ods_max_numeric_value, ods_min_numeric_value, ods_nonempty_row_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_analytics import ods_has_numeric_cells, ods_has_string_cells, ods_is_empty, ods_max_numeric_value, ods_min_numeric_value, ods_nonempty_row_count
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"


def _valid_ods_files():
    return sorted(_ODS_DIR.glob("*.ods"))


class TestOdsRemainingAnalyticsNdjsonExport:
    """ODS remaining analytics -> NDJSON export -> roundtrip verification."""

    def test_has_numeric_and_string_cells(self):
        s_min = str(_ODS_DIR / "minimal-spreadsheet.ods")
        s_num = str(_ODS_DIR / "numeric-row.ods")
        s_single = str(_ODS_DIR / "single-cell.ods")
        assert ods_has_numeric_cells(s_min) is True
        assert ods_has_string_cells(s_min) is True
        assert ods_has_numeric_cells(s_num) is True
        assert ods_has_string_cells(s_num) is False
        assert ods_has_numeric_cells(s_single) is False
        assert ods_has_string_cells(s_single) is True

    def test_is_empty_and_nonempty_row_count(self):
        s_min = str(_ODS_DIR / "minimal-spreadsheet.ods")
        s_num = str(_ODS_DIR / "numeric-row.ods")
        assert ods_is_empty(s_min) is False
        assert ods_nonempty_row_count(s_min) == 2
        assert ods_is_empty(s_num) is False
        assert ods_nonempty_row_count(s_num) == 1

    def test_max_and_min_numeric_value(self):
        s_min = str(_ODS_DIR / "minimal-spreadsheet.ods")
        s_num = str(_ODS_DIR / "numeric-row.ods")
        s_single = str(_ODS_DIR / "single-cell.ods")
        assert ods_max_numeric_value(s_min) == 42.0
        assert ods_min_numeric_value(s_min) == 42.0
        assert ods_max_numeric_value(s_num) == 3.0
        assert ods_min_numeric_value(s_num) == 1.0
        assert ods_max_numeric_value(s_single) is None
        assert ods_min_numeric_value(s_single) is None

    def test_ods_remaining_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_ods_files():
            path = str(f)
            has_num = ods_has_numeric_cells(path)
            has_str = ods_has_string_cells(path)
            is_empty = ods_is_empty(path)
            max_num = ods_max_numeric_value(path)
            min_num = ods_min_numeric_value(path)
            nonempty = ods_nonempty_row_count(path)
            assert isinstance(has_num, bool), f"has_numeric_cells must be bool for {f.name}"
            assert isinstance(has_str, bool), f"has_string_cells must be bool for {f.name}"
            assert isinstance(is_empty, bool), f"is_empty must be bool for {f.name}"
            assert nonempty >= 0, f"nonempty_row_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "has_numeric_cells": has_num,
                "has_string_cells": has_str,
                "is_empty": is_empty,
                "max_numeric_value": float(max_num) if max_num is not None else None,
                "min_numeric_value": float(min_num) if min_num is not None else None,
                "nonempty_row_count": nonempty,
                "source_format": "ods",
            })
        dest = tmp_path / "ods-remaining.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_ods_files():
            path = str(f)
            records.append({
                "file": f.name,
                "has_numeric_cells": ods_has_numeric_cells(path),
                "nonempty_row_count": ods_nonempty_row_count(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["has_numeric_cells"] == back["has_numeric_cells"]
            assert orig["nonempty_row_count"] == back["nonempty_row_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_ODS_DIR / "minimal-spreadsheet.ods")
        records = [{
            "file": "minimal-spreadsheet.ods",
            "has_numeric_cells": ods_has_numeric_cells(sample),
            "is_empty": ods_is_empty(sample),
            "format": "ods",
        }]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_numeric_file_has_no_string_cells(self):
        s_num = str(_ODS_DIR / "numeric-row.ods")
        assert ods_has_numeric_cells(s_num) is True
        assert ods_has_string_cells(s_num) is False
        assert ods_max_numeric_value(s_num) == 3.0
        assert ods_min_numeric_value(s_num) == 1.0
        assert ods_nonempty_row_count(s_num) == 1
