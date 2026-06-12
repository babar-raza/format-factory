"""
tests/python/fods/test_r194_fods_style_summary.py

Sprint: FORMAT-FACTORY-FODT-FODS-DEEPENING-001
Tests for workbook_row_style_summary(), workbook_column_style_summary(), workbook_style_family_list().
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods.neutral_model import (
    workbook_row_style_summary,
    workbook_column_style_summary,
    workbook_style_family_list,
)

SAMPLES = _REPO / "samples" / "by-format" / "fods"


class TestWorkbookRowStyleSummary:
    def test_empty_workbook_returns_empty_dict(self):
        result = workbook_row_style_summary({})
        assert result == {}

    def test_returns_dict(self):
        result = workbook_row_style_summary({})
        assert isinstance(result, dict)

    def test_real_file_returns_dict(self):
        from src.python.fods.parser import parse_fods
        model = parse_fods(str(SAMPLES / "minimal-spreadsheet.fods"))
        result = workbook_row_style_summary(model)
        assert isinstance(result, dict)


class TestWorkbookColumnStyleSummary:
    def test_empty_workbook_returns_empty_dict(self):
        result = workbook_column_style_summary({})
        assert result == {}

    def test_returns_dict(self):
        result = workbook_column_style_summary({})
        assert isinstance(result, dict)

    def test_real_file_returns_dict(self):
        from src.python.fods.parser import parse_fods
        model = parse_fods(str(SAMPLES / "minimal-spreadsheet.fods"))
        result = workbook_column_style_summary(model)
        assert isinstance(result, dict)


class TestWorkbookStyleFamilyList:
    def test_empty_workbook_returns_empty_list(self):
        result = workbook_style_family_list({})
        assert result == []

    def test_returns_list(self):
        result = workbook_style_family_list({})
        assert isinstance(result, list)

    def test_real_file_returns_list(self):
        from src.python.fods.parser import parse_fods
        model = parse_fods(str(SAMPLES / "minimal-spreadsheet.fods"))
        result = workbook_style_family_list(model)
        assert isinstance(result, list)

    def test_all_entries_are_strings(self):
        from src.python.fods.parser import parse_fods
        model = parse_fods(str(SAMPLES / "minimal-spreadsheet.fods"))
        result = workbook_style_family_list(model)
        for item in result:
            assert isinstance(item, str)
