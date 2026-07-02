"""Tests for sylk_data_sparsity and sylk_max_cell_value_length.

Product deepening: SYLK analytics — R238.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk import sylk_data_sparsity, sylk_max_cell_value_length

_SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"


def _first_sylk():
    files = sorted(_SYLK_DIR.glob("*.slk"))
    assert files is not None, f"No SYLK samples in {_SYLK_DIR}"
    return str(files[0])


class TestSylkDataSparsity:
    def test_returns_float(self):
        result = sylk_data_sparsity(_first_sylk())
        assert isinstance(result, float)

    def test_range(self):
        result = sylk_data_sparsity(_first_sylk())
        assert 0.0 <= result <= 1.0

    def test_nonnegative(self):
        assert sylk_data_sparsity(_first_sylk()) >= 0.0


class TestSylkMaxCellValueLength:
    def test_returns_int(self):
        result = sylk_max_cell_value_length(_first_sylk())
        assert isinstance(result, int)

    def test_nonnegative(self):
        assert sylk_max_cell_value_length(_first_sylk()) >= 0

    def test_positive_for_nonempty(self):
        result = sylk_max_cell_value_length(_first_sylk())
        assert result > 0
