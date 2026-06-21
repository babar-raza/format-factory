"""Sprint R290G: TSV analytics deepening — avg_row_width, max_field_value_length, numeric_field_count."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from tsv.tsv_parser import (
    tsv_avg_row_width,
    tsv_max_field_value_length,
    tsv_numeric_field_count,
)

SAMPLES = _REPO / "samples" / "by-format" / "tsv"
MINIMAL = SAMPLES / "minimal-2x2.tsv"
MULTI = SAMPLES / "multi-column.tsv"


@pytest.fixture
def sample():
    if not MINIMAL.exists():
        pytest.skip("TSV sample not available")
    return MINIMAL


@pytest.fixture
def multi_sample():
    if not MULTI.exists():
        pytest.skip("TSV multi-column sample not available")
    return MULTI


class TestTsvAvgRowWidth:
    def test_returns_float(self, sample):
        assert isinstance(tsv_avg_row_width(sample), float)

    def test_positive(self, sample):
        assert tsv_avg_row_width(sample) > 0.0


class TestTsvMaxFieldValueLength:
    def test_returns_int(self, sample):
        assert isinstance(tsv_max_field_value_length(sample), int)

    def test_positive(self, sample):
        assert tsv_max_field_value_length(sample) > 0


class TestTsvNumericFieldCount:
    def test_returns_int(self, sample):
        assert isinstance(tsv_numeric_field_count(sample), int)

    def test_nonnegative(self, sample):
        assert tsv_numeric_field_count(sample) >= 0
