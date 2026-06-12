"""Tests for tsv_empty_row_count — rnext63 product deepening."""
from pathlib import Path
import tempfile

TSV_DIR = Path("samples/by-format/tsv")


def test_import():
    from src.python.tsv import tsv_empty_row_count
    assert callable(tsv_empty_row_count)


def test_no_empty_rows_in_minimal_2x2():
    from src.python.tsv import tsv_empty_row_count
    result = tsv_empty_row_count(TSV_DIR / "minimal-2x2.tsv")
    assert result == 0


def test_no_empty_rows_in_multi_column():
    from src.python.tsv import tsv_empty_row_count
    result = tsv_empty_row_count(TSV_DIR / "multi-column.tsv")
    assert result == 0


def test_no_empty_rows_in_single_cell():
    from src.python.tsv import tsv_empty_row_count
    result = tsv_empty_row_count(TSV_DIR / "single-cell.tsv")
    assert result == 0


def test_returns_int():
    from src.python.tsv import tsv_empty_row_count
    result = tsv_empty_row_count(TSV_DIR / "minimal-2x2.tsv")
    assert isinstance(result, int)


def test_result_nonnegative():
    from src.python.tsv import tsv_empty_row_count
    for fname in ["minimal-2x2.tsv", "multi-column.tsv", "single-cell.tsv"]:
        result = tsv_empty_row_count(TSV_DIR / fname)
        assert result >= 0
