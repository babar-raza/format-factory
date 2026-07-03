"""Sprint 50: ODS ods_is_single_row + ods_avg_row_length (R260)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_analytics import ods_is_single_row, ods_avg_row_length

ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"

MINIMAL = ODS_DIR / "minimal-spreadsheet.ods"
NUMERIC = ODS_DIR / "numeric-row.ods"
SINGLE = ODS_DIR / "single-cell.ods"


# --- ods_is_single_row ---

def test_is_single_row_minimal_returns_false():
    assert ods_is_single_row(MINIMAL) is False


def test_is_single_row_numeric_returns_true():
    assert ods_is_single_row(NUMERIC) is True


def test_is_single_row_single_cell_returns_true():
    assert ods_is_single_row(SINGLE) is True


def test_is_single_row_invalid_sheet_index_returns_false():
    assert ods_is_single_row(MINIMAL, sheet_index=99) is False


def test_is_single_row_returns_bool_minimal():
    result = ods_is_single_row(MINIMAL)
    assert isinstance(result, bool)


def test_is_single_row_returns_bool_numeric():
    result = ods_is_single_row(NUMERIC)
    assert isinstance(result, bool)


# --- ods_avg_row_length ---

def test_avg_row_length_minimal_is_2():
    assert ods_avg_row_length(MINIMAL) == 2.0


def test_avg_row_length_numeric_is_3():
    assert ods_avg_row_length(NUMERIC) == 3.0


def test_avg_row_length_single_cell_is_1():
    assert ods_avg_row_length(SINGLE) == 1.0


def test_avg_row_length_invalid_sheet_returns_0():
    assert ods_avg_row_length(MINIMAL, sheet_index=99) == 0.0


def test_avg_row_length_returns_float_minimal():
    result = ods_avg_row_length(MINIMAL)
    assert isinstance(result, float)


def test_avg_row_length_returns_float_numeric():
    result = ods_avg_row_length(NUMERIC)
    assert isinstance(result, float)
