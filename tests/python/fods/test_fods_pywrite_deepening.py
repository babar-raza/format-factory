"""TC-EXEC-001: FODS Python write deepening tests.

Verifies that FODS write→reload produces semantically equivalent content —
cell values, types, sheet names, row counts, formula text, and typed values.
"""
import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from src.python.fods import parse_fods_strict, workbook_to_xml, write_fods
from src.python.fods.writer import FodsInputError


def _cell(value, value_type="string", formula=None):
    c = {"value": value, "value_type": value_type}
    if formula is not None:
        c["formula"] = formula
    return c


def _row(cells):
    return {"cells": cells}


def _sheet(name, rows):
    return {"name": name, "rows": rows}


def _wb(sheets):
    return {"sheets": sheets}


def _roundtrip(workbook):
    """Write workbook to temp file, parse back, return parsed workbook."""
    with tempfile.NamedTemporaryFile(
        suffix=".fods", delete=False, mode="w", encoding="utf-8"
    ) as f:
        tmp = Path(f.name)
    try:
        write_fods(workbook, tmp)
        return parse_fods_strict(str(tmp))
    finally:
        tmp.unlink(missing_ok=True)


class TestFodsWriteDeepeningSheets:
    def test_single_sheet_name_preserved(self):
        """Sheet name survives write→reload."""
        wb = _wb([_sheet("MyData", [_row([_cell("x")])])])
        wb2 = _roundtrip(wb)
        assert wb2["sheet_count"] == 1
        assert wb2["sheets"][0]["name"] == "MyData"

    def test_multi_sheet_names_preserved(self):
        """All sheet names survive write→reload in correct order."""
        wb = _wb([
            _sheet("Alpha", [_row([_cell("a")])]),
            _sheet("Beta", [_row([_cell("b")])]),
            _sheet("Gamma", [_row([_cell("c")])]),
        ])
        wb2 = _roundtrip(wb)
        assert wb2["sheet_count"] == 3
        names = [s["name"] for s in wb2["sheets"]]
        assert names == ["Alpha", "Beta", "Gamma"]


class TestFodsWriteDeepeningCellValues:
    def test_string_cell_value_preserved(self):
        """String cell value survives round-trip."""
        wb = _wb([_sheet("S", [_row([_cell("hello world", "string")])])])
        wb2 = _roundtrip(wb)
        cell = wb2["sheets"][0]["rows"][0]["cells"][0]
        assert cell["value"] == "hello world"
        assert cell["value_type"] == "string"

    def test_numeric_cell_value_preserved(self):
        """Float cell value survives round-trip."""
        wb = _wb([_sheet("S", [_row([_cell(42.5, "float")])])])
        wb2 = _roundtrip(wb)
        cell = wb2["sheets"][0]["rows"][0]["cells"][0]
        assert cell["value"] == pytest.approx(42.5)

    def test_multiple_cells_per_row_preserved(self):
        """Multiple cells in a row survive round-trip with correct order."""
        cells_in = [_cell("A", "string"), _cell(1.0, "float"), _cell("C", "string")]
        wb = _wb([_sheet("S", [_row(cells_in)])])
        wb2 = _roundtrip(wb)
        cells_out = wb2["sheets"][0]["rows"][0]["cells"]
        assert len(cells_out) == 3
        assert cells_out[0]["value"] == "A"
        assert cells_out[1]["value"] == pytest.approx(1.0)
        assert cells_out[2]["value"] == "C"


class TestFodsWriteDeepeningRowCounts:
    def test_row_count_per_sheet_preserved(self):
        """Row count per sheet survives round-trip."""
        rows = [_row([_cell(str(i))]) for i in range(5)]
        wb = _wb([_sheet("S", rows)])
        wb2 = _roundtrip(wb)
        assert len(wb2["sheets"][0]["rows"]) == 5

    def test_multi_sheet_row_counts_independent(self):
        """Each sheet's row count is correct after round-trip."""
        wb = _wb([
            _sheet("A", [_row([_cell("x")]), _row([_cell("y")])]),
            _sheet("B", [_row([_cell("z")])]),
        ])
        wb2 = _roundtrip(wb)
        assert len(wb2["sheets"][0]["rows"]) == 2
        assert len(wb2["sheets"][1]["rows"]) == 1


class TestFodsWriteDeepeningFormulas:
    def test_formula_text_preserved_passthrough(self):
        """Formula attribute text is preserved through write→reload (passthrough)."""
        wb = _wb([_sheet("S", [_row([_cell(10.0, "float", formula="of:=[.A1]+1")])])])
        wb2 = _roundtrip(wb)
        cell = wb2["sheets"][0]["rows"][0]["cells"][0]
        assert cell.get("formula") == "of:=[.A1]+1"


class TestFodsWriteDeepeningEdgeCases:
    def test_empty_workbook_produces_valid_fods(self):
        """An empty workbook writes and re-parses without error."""
        wb = _wb([])
        wb2 = _roundtrip(wb)
        assert wb2["sheet_count"] == 0
        assert wb2["sheets"] == []

    def test_invalid_input_raises(self):
        """write_fods raises on non-dict input."""
        with pytest.raises(Exception):
            workbook_to_xml("not a dict")
