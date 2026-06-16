"""Tests for fods_numeric_cell_count and fods_max_row_count."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods.neutral_model import fods_numeric_cell_count, fods_max_row_count
from src.python.fods import parse_fods

_SAMPLES = _REPO / "samples" / "by-format" / "fods"

_TYPED = _SAMPLES / "typed-values-basic.fods"
_MINIMAL = _SAMPLES / "minimal-spreadsheet.fods"
_MULTI = _SAMPLES / "multi-sheet-basic.fods"


class TestFodsNumericCellCount:
    def test_import(self):
        assert callable(fods_numeric_cell_count)

    def test_returns_int(self):
        wb = parse_fods(_TYPED)
        assert isinstance(fods_numeric_cell_count(wb), int)

    def test_nonnegative(self):
        wb = parse_fods(_MINIMAL)
        assert fods_numeric_cell_count(wb) >= 0

    def test_typed_file_has_numeric_cells(self):
        wb = parse_fods(_TYPED)
        assert fods_numeric_cell_count(wb) >= 1

    def test_empty_workbook_is_zero(self):
        wb = {"sheets": []}
        assert fods_numeric_cell_count(wb) == 0

    def test_string_only_cells_not_counted(self):
        wb = {"sheets": [{"rows": [{"cells": [{"value_type": "string", "value": "hello"}]}]}]}
        assert fods_numeric_cell_count(wb) == 0

    def test_float_cell_counted(self):
        wb = {"sheets": [{"rows": [{"cells": [{"value_type": "float", "value": 42.0}]}]}]}
        assert fods_numeric_cell_count(wb) == 1

    def test_multi_sheet_counts_all(self):
        wb = {
            "sheets": [
                {"rows": [{"cells": [{"value_type": "float", "value": 1.0}]}]},
                {"rows": [{"cells": [{"value_type": "float", "value": 2.0}]}]},
            ]
        }
        assert fods_numeric_cell_count(wb) == 2


class TestFodsMaxRowCount:
    def test_import(self):
        assert callable(fods_max_row_count)

    def test_returns_int(self):
        wb = parse_fods(_MINIMAL)
        assert isinstance(fods_max_row_count(wb), int)

    def test_nonnegative(self):
        wb = parse_fods(_MINIMAL)
        assert fods_max_row_count(wb) >= 0

    def test_empty_workbook_is_zero(self):
        assert fods_max_row_count({"sheets": []}) == 0

    def test_single_sheet(self):
        wb = {"sheets": [{"rows": [{"cells": []}, {"cells": []}]}]}
        assert fods_max_row_count(wb) == 2

    def test_multi_sheet_returns_max(self):
        wb = {
            "sheets": [
                {"rows": [{"cells": []}]},
                {"rows": [{"cells": []}, {"cells": []}, {"cells": []}]},
            ]
        }
        assert fods_max_row_count(wb) == 3

    def test_real_file_positive(self):
        wb = parse_fods(_MULTI)
        assert fods_max_row_count(wb) >= 1

    def test_leq_total_rows_across_sheets(self):
        wb = parse_fods(_MULTI)
        max_r = fods_max_row_count(wb)
        total = sum(len(s.get("rows", [])) for s in wb.get("sheets", []))
        assert max_r <= total
