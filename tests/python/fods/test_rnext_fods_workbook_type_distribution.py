"""
test_rnext_fods_workbook_type_distribution.py -- Dedicated test coverage for workbook_type_distribution.

Gap: GAP-FODS-FOSS-WORKBOOK_TYP-001 (missing_test_coverage)
"""
from __future__ import annotations
import sys
from pathlib import Path
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods.neutral_model import workbook_type_distribution


def _wb(sheets=None):
    return {"sheets": sheets or []}

def _sheet(name="Sheet1", rows=None):
    return {"name": name, "rows": rows or []}

def _row(cells=None):
    return {"cells": cells or []}

def _cell(value="", value_type="string"):
    return {"value": value, "value_type": value_type}


class TestWorkbookTypeDistribution:
    def test_returns_dict(self):
        assert isinstance(workbook_type_distribution(_wb()), dict)

    def test_empty_workbook(self):
        r = workbook_type_distribution(_wb())
        assert r["total_cells"] == 0

    def test_has_by_type(self):
        r = workbook_type_distribution(_wb([_sheet("S", [_row([_cell("x")])])]))
        assert "by_type" in r
        assert isinstance(r["by_type"], dict)

    def test_string_cells_counted(self):
        s = _sheet("S", [_row([_cell("a", "string"), _cell("b", "string")])])
        r = workbook_type_distribution(_wb([s]))
        assert r["by_type"].get("string", 0) >= 2

    def test_mixed_types(self):
        s = _sheet("S", [_row([_cell("1", "float"), _cell("x", "string")])])
        r = workbook_type_distribution(_wb([s]))
        assert r["by_type"].get("float", 0) >= 1
        assert r["by_type"].get("string", 0) >= 1

    def test_total_cells_correct(self):
        s = _sheet("S", [_row([_cell("a"), _cell("b"), _cell("c")])])
        r = workbook_type_distribution(_wb([s]))
        assert r["total_cells"] >= 3

    def test_has_per_sheet(self):
        r = workbook_type_distribution(_wb([_sheet("A"), _sheet("B")]))
        assert "per_sheet" in r
        assert isinstance(r["per_sheet"], list)

    def test_multi_sheet_aggregate(self):
        s1 = _sheet("S1", [_row([_cell("x", "string")])])
        s2 = _sheet("S2", [_row([_cell("1", "float")])])
        r = workbook_type_distribution(_wb([s1, s2]))
        assert r["total_cells"] >= 2
