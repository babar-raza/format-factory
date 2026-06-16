"""Sprint 50: FODS fods_is_multi_sheet + fods_min_row_count (R260)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods.parser import parse_fods_strict
from fods.neutral_model import fods_is_multi_sheet, fods_min_row_count

FODS_DIR = _REPO / "samples" / "by-format" / "fods"

MINIMAL = FODS_DIR / "minimal-spreadsheet.fods"
MULTI = FODS_DIR / "multi-sheet-basic.fods"
FORMULA = FODS_DIR / "formula-basic.fods"
TYPED = FODS_DIR / "typed-values-basic.fods"


# --- fods_is_multi_sheet ---

def test_is_multi_sheet_single_returns_false_minimal():
    wb = parse_fods_strict(MINIMAL)
    assert fods_is_multi_sheet(wb) is False


def test_is_multi_sheet_multi_returns_true():
    wb = parse_fods_strict(MULTI)
    assert fods_is_multi_sheet(wb) is True


def test_is_multi_sheet_formula_single_returns_false():
    wb = parse_fods_strict(FORMULA)
    assert fods_is_multi_sheet(wb) is False


def test_is_multi_sheet_typed_single_returns_false():
    wb = parse_fods_strict(TYPED)
    assert fods_is_multi_sheet(wb) is False


def test_is_multi_sheet_empty_workbook_returns_false():
    assert fods_is_multi_sheet({}) is False


def test_is_multi_sheet_empty_sheets_returns_false():
    assert fods_is_multi_sheet({"sheets": []}) is False


# --- fods_min_row_count ---

def test_min_row_count_minimal_is_1():
    wb = parse_fods_strict(MINIMAL)
    assert fods_min_row_count(wb) == 1


def test_min_row_count_multi_sheet_is_1():
    wb = parse_fods_strict(MULTI)
    # multi-sheet-basic has sheets with >=1 row each, min is 1
    assert fods_min_row_count(wb) == 1


def test_min_row_count_formula_is_4():
    wb = parse_fods_strict(FORMULA)
    assert fods_min_row_count(wb) == 4


def test_min_row_count_typed_is_4():
    wb = parse_fods_strict(TYPED)
    assert fods_min_row_count(wb) == 4


def test_min_row_count_empty_workbook_is_0():
    assert fods_min_row_count({}) == 0


def test_min_row_count_empty_sheets_is_0():
    assert fods_min_row_count({"sheets": []}) == 0
