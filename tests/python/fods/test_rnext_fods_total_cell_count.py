"""Tests for fods_total_cell_count function."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods.neutral_model import fods_total_cell_count
from fods.parser import parse_fods_strict


_SAMPLES = _REPO / "samples" / "by-format" / "fods"


class TestFodsTotalCellCount:
    def _load(self, name: str) -> dict:
        return parse_fods_strict(str(_SAMPLES / name))

    def test_minimal_has_cells(self):
        wb = self._load("minimal-spreadsheet.fods")
        count = fods_total_cell_count(wb)
        assert isinstance(count, int)
        assert count >= 1

    def test_empty_workbook(self):
        wb = {"sheets": []}
        assert fods_total_cell_count(wb) == 0

    def test_empty_sheet_no_rows(self):
        wb = {"sheets": [{"rows": []}]}
        assert fods_total_cell_count(wb) == 0

    def test_sheet_with_none_cells(self):
        wb = {"sheets": [{"rows": [{"cells": [None, None]}]}]}
        assert fods_total_cell_count(wb) == 0

    def test_sheet_with_values(self):
        wb = {"sheets": [{"rows": [
            {"cells": [{"value": 1}, {"value": "hello"}, None]},
            {"cells": [{"value": None, "text": None}, {"text": "world"}]},
        ]}]}
        assert fods_total_cell_count(wb) == 3  # 1, "hello", "world"

    def test_return_type(self):
        wb = {"sheets": []}
        assert isinstance(fods_total_cell_count(wb), int)

    def test_non_negative(self):
        wb = self._load("minimal-spreadsheet.fods")
        assert fods_total_cell_count(wb) >= 0

    def test_importable_from_package(self):
        from fods import fods_total_cell_count as fn
        assert callable(fn)
