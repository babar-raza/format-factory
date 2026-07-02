"""Tests for ods_data_density and ods_max_cell_value_length.

Product deepening: ODS analytics — R238.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods import ods_data_density, ods_max_cell_value_length

_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"


def _first_ods():
    files = sorted(_ODS_DIR.glob("*.ods"))
    assert files is not None, f"No ODS samples in {_ODS_DIR}"
    return str(files[0])


class TestOdsDataDensity:
    def test_returns_float(self):
        result = ods_data_density(_first_ods())
        assert isinstance(result, float)

    def test_range(self):
        result = ods_data_density(_first_ods())
        assert 0.0 <= result <= 1.0

    def test_nonnegative(self):
        assert ods_data_density(_first_ods()) >= 0.0


class TestOdsMaxCellValueLength:
    def test_returns_int(self):
        result = ods_max_cell_value_length(_first_ods())
        assert isinstance(result, int)

    def test_nonnegative(self):
        assert ods_max_cell_value_length(_first_ods()) >= 0

    def test_positive_for_nonempty(self):
        result = ods_max_cell_value_length(_first_ods())
        assert result >= 0
