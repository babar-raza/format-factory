"""Sprint R290G: CSV analytics deepening — avg_row_width, total_value_count, string_field_ratio."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import (
    csv_avg_row_width,
    csv_total_value_count,
    csv_string_field_ratio,
)

SAMPLES = _REPO / "samples" / "by-format" / "csv"
MINIMAL = SAMPLES / "minimal-2x2.csv"
QUOTED = SAMPLES / "quoted-fields.csv"


@pytest.fixture
def sample():
    if not MINIMAL.exists():
        pytest.skip("CSV sample not available")
    return MINIMAL


@pytest.fixture
def quoted_sample():
    if not QUOTED.exists():
        pytest.skip("CSV quoted sample not available")
    return QUOTED


class TestCsvAvgRowWidth:
    def test_returns_float(self, sample):
        assert isinstance(csv_avg_row_width(sample), float)

    def test_positive(self, sample):
        assert csv_avg_row_width(sample) > 0.0


class TestCsvTotalValueCount:
    def test_returns_int(self, sample):
        assert isinstance(csv_total_value_count(sample), int)

    def test_positive(self, sample):
        assert csv_total_value_count(sample) > 0


class TestCsvStringFieldRatio:
    def test_returns_float(self, sample):
        assert isinstance(csv_string_field_ratio(sample), float)

    def test_between_zero_and_one(self, sample):
        r = csv_string_field_ratio(sample)
        assert 0.0 <= r <= 1.0
