"""Tests for ods_empty_cell_count — rnext65 product deepening."""
from pathlib import Path

ODS_DIR = Path("samples/by-format/ods/valid")


def test_import():
    from src.python.ods import ods_empty_cell_count
    assert callable(ods_empty_cell_count)


def test_numeric_row_has_no_empty_cells():
    from src.python.ods import ods_empty_cell_count
    result = ods_empty_cell_count(ODS_DIR / "numeric-row.ods")
    assert result == 0


def test_single_cell_has_no_empty_cells():
    from src.python.ods import ods_empty_cell_count
    result = ods_empty_cell_count(ODS_DIR / "single-cell.ods")
    assert result == 0


def test_minimal_spreadsheet_has_no_empty_cells():
    from src.python.ods import ods_empty_cell_count
    result = ods_empty_cell_count(ODS_DIR / "minimal-spreadsheet.ods")
    assert result == 0


def test_returns_int():
    from src.python.ods import ods_empty_cell_count
    result = ods_empty_cell_count(ODS_DIR / "numeric-row.ods")
    assert isinstance(result, int)


def test_result_nonnegative():
    from src.python.ods import ods_empty_cell_count
    for fname in ["numeric-row.ods", "single-cell.ods", "minimal-spreadsheet.ods"]:
        result = ods_empty_cell_count(ODS_DIR / fname)
        assert result >= 0
