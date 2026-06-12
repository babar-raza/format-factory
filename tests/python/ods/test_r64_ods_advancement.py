"""
test_r64_ods_advancement.py -- R64 Train I: ODS format track advancement.

New capability: ods_sheet_name_list(ods_doc)
  Returns list of sheet names from the ODS data dict.

R64 Sprint: Train I -- ODS format track advancement
"""
from __future__ import annotations
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from src.python.ods.ods_stats import ods_sheet_name_list


def _doc(sheet_names):
    """Build minimal ODS doc with given sheet names."""
    return {"sheets": [{"name": n, "rows": []} for n in sheet_names]}


class TestOdsSheetNameList:
    def test_empty_doc(self):
        result = ods_sheet_name_list({"sheets": []})
        assert result == []

    def test_single_sheet(self):
        result = ods_sheet_name_list(_doc(["Sheet1"]))
        assert result == ["Sheet1"]

    def test_multiple_sheets_preserves_order(self):
        result = ods_sheet_name_list(_doc(["Alpha", "Beta", "Gamma"]))
        assert result == ["Alpha", "Beta", "Gamma"]

    def test_missing_sheets_key(self):
        result = ods_sheet_name_list({})
        assert result == []

    def test_sheet_with_empty_name(self):
        result = ods_sheet_name_list({"sheets": [{"rows": []}]})
        assert result == [""]

    def test_unicode_sheet_names(self):
        result = ods_sheet_name_list(_doc(["Feuille1", "Tabelle2"]))
        assert result == ["Feuille1", "Tabelle2"]

    def test_returns_list_type(self):
        result = ods_sheet_name_list(_doc(["X"]))
        assert isinstance(result, list)

    def test_callable_from_module(self):
        from src.python.ods import ods_stats
        assert callable(ods_stats.ods_sheet_name_list)
