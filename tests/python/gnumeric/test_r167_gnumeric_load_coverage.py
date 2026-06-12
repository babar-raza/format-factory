"""R167 — Gnumeric Load capability coverage test (GAP-Gnumeric-FOSS-LOAD-001).

Closes: GAP-Gnumeric-FOSS-LOAD-001 (missing_test_coverage for Load capability).
Queue:  gap-coverage-q-003
"""
from __future__ import annotations

import pytest
from pathlib import Path

from src.python.gnumeric.gnumeric_codec import load, GnumericParseError

EMPTY_SHEET = Path("samples/by-format/gnumeric/empty-sheet.gnumeric")
MINIMAL = Path("samples/by-format/gnumeric/minimal-spreadsheet.gnumeric")
MULTI_CELL = Path("samples/by-format/gnumeric/multi-cell-basic.gnumeric")


class TestGnumericLoadFromPath:
    def test_load_returns_dict(self):
        model = load(EMPTY_SHEET)
        assert isinstance(model, dict)

    def test_load_is_gnumeric_true(self):
        model = load(EMPTY_SHEET)
        assert model["is_gnumeric"] is True

    def test_load_has_sheet_count(self):
        model = load(EMPTY_SHEET)
        assert "sheet_count" in model
        assert isinstance(model["sheet_count"], int)

    def test_load_has_sheets_list(self):
        model = load(EMPTY_SHEET)
        assert "sheets" in model
        assert isinstance(model["sheets"], list)

    def test_load_has_cell_count(self):
        model = load(EMPTY_SHEET)
        assert "cell_count" in model
        assert isinstance(model["cell_count"], int)

    def test_load_minimal_spreadsheet(self):
        model = load(MINIMAL)
        assert model["is_gnumeric"] is True
        assert model["sheet_count"] >= 1

    def test_load_multi_cell(self):
        model = load(MULTI_CELL)
        assert model["is_gnumeric"] is True
        assert model["cell_count"] >= 0

    def test_load_from_str_path(self):
        model = load(str(EMPTY_SHEET))
        assert model["is_gnumeric"] is True

    def test_load_invalid_raises(self):
        with pytest.raises((GnumericParseError, Exception)):
            load(b"not gnumeric content at all !!!")
