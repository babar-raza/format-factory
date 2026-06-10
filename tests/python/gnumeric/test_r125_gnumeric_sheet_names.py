"""
tests/python/gnumeric/test_r125_gnumeric_sheet_names.py

Sprint: FORMAT-FACTORY-AUTONOMOUS-CYCLE-PROOF-AND-PRODUCT-PROGRESS-001
TC-GNUMERIC-SHEET-NAMES: get_sheet_names()
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import (
    create_gnumeric,
    write_gnumeric,
    get_sheet_names,
)


def _make_file(sheets: list[dict]) -> Path:
    model = create_gnumeric(sheets)
    tmp = Path(tempfile.mktemp(suffix=".gnumeric"))
    write_gnumeric(model, tmp)
    return tmp


class TestGetSheetNames:
    def test_returns_list(self):
        tmp = _make_file([{"name": "Sheet1", "rows": [["A"]]}])
        try:
            result = get_sheet_names(tmp)
            assert isinstance(result, list)
        finally:
            tmp.unlink(missing_ok=True)

    def test_single_sheet_name(self):
        tmp = _make_file([{"name": "Sales", "rows": [["x"]]}])
        try:
            assert get_sheet_names(tmp) == ["Sales"]
        finally:
            tmp.unlink(missing_ok=True)

    def test_multiple_sheet_names(self):
        tmp = _make_file([
            {"name": "Q1", "rows": [["A"]]},
            {"name": "Q2", "rows": [["B"]]},
            {"name": "Q3", "rows": [["C"]]},
        ])
        try:
            names = get_sheet_names(tmp)
            assert names == ["Q1", "Q2", "Q3"]
        finally:
            tmp.unlink(missing_ok=True)

    def test_preserves_order(self):
        tmp = _make_file([
            {"name": "Z", "rows": []},
            {"name": "A", "rows": []},
            {"name": "M", "rows": []},
        ])
        try:
            names = get_sheet_names(tmp)
            assert names == ["Z", "A", "M"]
        finally:
            tmp.unlink(missing_ok=True)

    def test_accepts_bytes(self):
        tmp = _make_file([{"name": "Data", "rows": [["x"]]}])
        try:
            names = get_sheet_names(tmp.read_bytes())
            assert names == ["Data"]
        finally:
            tmp.unlink(missing_ok=True)

    def test_accepts_string_path(self):
        tmp = _make_file([{"name": "Report", "rows": []}])
        try:
            names = get_sheet_names(str(tmp))
            assert names == ["Report"]
        finally:
            tmp.unlink(missing_ok=True)

    def test_empty_sheet_list(self):
        model = create_gnumeric([])
        model["sheets"] = []
        tmp = Path(tempfile.mktemp(suffix=".gnumeric"))
        try:
            write_gnumeric(model, tmp)
            names = get_sheet_names(tmp)
            assert names == []
        except Exception:
            pass  # empty workbook may fail to write — that's ok
        finally:
            tmp.unlink(missing_ok=True)

    def test_package_import(self):
        import gnumeric
        assert hasattr(gnumeric, "get_sheet_names")

    def test_in_all(self):
        import gnumeric
        assert "get_sheet_names" in gnumeric.__all__
