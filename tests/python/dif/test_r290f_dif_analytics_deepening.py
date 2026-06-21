"""Sprint R290F: DIF analytics deepening — avg_string_length, numeric_ratio, total_cell_value_count."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import (
    dif_avg_string_length,
    dif_numeric_ratio,
    dif_total_cell_value_count,
)

SAMPLES = _REPO / "samples" / "by-format" / "dif" / "valid"
MINIMAL = SAMPLES / "minimal-2x2.dif"
NUMERIC = SAMPLES / "numeric-row.dif"


@pytest.fixture
def sample():
    if not MINIMAL.exists():
        pytest.skip("DIF sample not available")
    return MINIMAL


@pytest.fixture
def numeric_sample():
    if not NUMERIC.exists():
        pytest.skip("DIF numeric sample not available")
    return NUMERIC


class TestDifAvgStringLength:
    def test_returns_float(self, sample):
        assert isinstance(dif_avg_string_length(sample), float)

    def test_nonnegative(self, sample):
        assert dif_avg_string_length(sample) >= 0.0


class TestDifNumericRatio:
    def test_returns_float(self, sample):
        assert isinstance(dif_numeric_ratio(sample), float)

    def test_between_zero_and_one(self, sample):
        r = dif_numeric_ratio(sample)
        assert 0.0 <= r <= 1.0

    def test_numeric_row_high_ratio(self, numeric_sample):
        assert dif_numeric_ratio(numeric_sample) > 0.0


class TestDifTotalCellValueCount:
    def test_returns_int(self, sample):
        assert isinstance(dif_total_cell_value_count(sample), int)

    def test_positive(self, sample):
        assert dif_total_cell_value_count(sample) > 0
