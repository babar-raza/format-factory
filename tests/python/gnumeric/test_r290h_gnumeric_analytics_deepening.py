"""Sprint R290H: Gnumeric analytics deepening — cell_density, value_type_count, max_column_index."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import (
    gnumeric_cell_density,
    gnumeric_value_type_count,
    gnumeric_max_column_index,
)

SAMPLES = _REPO / "samples" / "by-format" / "gnumeric"
MINIMAL = SAMPLES / "minimal-spreadsheet.gnumeric"
MULTI = SAMPLES / "multi-cell-basic.gnumeric"


@pytest.fixture
def sample():
    if not MINIMAL.exists():
        pytest.skip("Gnumeric sample not available")
    return MINIMAL


@pytest.fixture
def multi_sample():
    if not MULTI.exists():
        pytest.skip("Gnumeric multi-cell sample not available")
    return MULTI


class TestGnumericCellDensity:
    def test_returns_float(self, sample):
        assert isinstance(gnumeric_cell_density(sample), float)

    def test_between_zero_and_one(self, sample):
        d = gnumeric_cell_density(sample)
        assert 0.0 <= d <= 1.0


class TestGnumericValueTypeCount:
    def test_returns_int(self, sample):
        assert isinstance(gnumeric_value_type_count(sample), int)

    def test_positive(self, sample):
        assert gnumeric_value_type_count(sample) >= 1


class TestGnumericMaxColumnIndex:
    def test_returns_int(self, sample):
        assert isinstance(gnumeric_max_column_index(sample), int)

    def test_nonnegative(self, sample):
        assert gnumeric_max_column_index(sample) >= 0
