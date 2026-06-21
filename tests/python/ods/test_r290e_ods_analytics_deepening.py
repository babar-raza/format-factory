"""Sprint R290E: ODS analytics deepening — max_string_cell_length, total_cell_count_all, has_empty_sheets."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_parser import (
    ods_max_string_cell_length,
    ods_total_cell_count_all,
    ods_has_empty_sheets,
)

SAMPLES = _REPO / "samples" / "by-format" / "ods" / "valid"
MINIMAL = SAMPLES / "minimal-spreadsheet.ods"
SINGLE = SAMPLES / "single-cell.ods"


@pytest.fixture
def sample():
    if not MINIMAL.exists():
        pytest.skip("ODS sample not available")
    return MINIMAL


@pytest.fixture
def single_sample():
    if not SINGLE.exists():
        pytest.skip("ODS single-cell sample not available")
    return SINGLE


class TestOdsMaxStringCellLength:
    def test_returns_int(self, sample):
        assert isinstance(ods_max_string_cell_length(sample), int)

    def test_nonnegative(self, sample):
        assert ods_max_string_cell_length(sample) >= 0


class TestOdsTotalCellCountAll:
    def test_returns_int(self, sample):
        assert isinstance(ods_total_cell_count_all(sample), int)

    def test_positive(self, sample):
        assert ods_total_cell_count_all(sample) > 0

    def test_single_cell(self, single_sample):
        assert ods_total_cell_count_all(single_sample) >= 1


class TestOdsHasEmptySheets:
    def test_returns_bool(self, sample):
        assert isinstance(ods_has_empty_sheets(sample), bool)
