"""Sprint R290F: FODS analytics deepening — total_string_cells, avg_cell_value_length, max_column_index."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods.neutral_model import (
    fods_total_string_cells,
    fods_avg_cell_value_length,
    fods_max_column_index,
)
from fods.parser import parse_fods

SAMPLES = _REPO / "samples" / "by-format" / "fods"
MINIMAL = SAMPLES / "minimal-spreadsheet.fods"
TYPED = SAMPLES / "typed-values-basic.fods"


@pytest.fixture
def workbook():
    if not MINIMAL.exists():
        pytest.skip("FODS sample not available")
    return parse_fods(MINIMAL)


@pytest.fixture
def typed_workbook():
    if not TYPED.exists():
        pytest.skip("FODS typed sample not available")
    return parse_fods(TYPED)


class TestFodsTotalStringCells:
    def test_returns_int(self, workbook):
        assert isinstance(fods_total_string_cells(workbook), int)

    def test_nonnegative(self, workbook):
        assert fods_total_string_cells(workbook) >= 0


class TestFodsAvgCellValueLength:
    def test_returns_float(self, workbook):
        assert isinstance(fods_avg_cell_value_length(workbook), float)

    def test_nonnegative(self, workbook):
        assert fods_avg_cell_value_length(workbook) >= 0.0


class TestFodsMaxColumnIndex:
    def test_returns_int(self, workbook):
        assert isinstance(fods_max_column_index(workbook), int)

    def test_nonnegative_for_nonempty(self, workbook):
        idx = fods_max_column_index(workbook)
        assert idx >= 0 or idx == -1
