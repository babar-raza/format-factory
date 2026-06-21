"""Sprint R290J: TOML analytics deepening — null_value_count, distinct_key_count, avg_numeric_value."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from toml.toml_codec import (
    toml_null_value_count,
    toml_distinct_key_count,
    toml_avg_numeric_value,
)

SAMPLES = _REPO / "samples" / "by-format" / "toml"
MINIMAL = SAMPLES / "minimal.toml"


@pytest.fixture
def sample():
    if not MINIMAL.exists():
        pytest.skip("TOML minimal sample not available")
    return MINIMAL


class TestTomlNullValueCount:
    def test_returns_int(self, sample):
        assert isinstance(toml_null_value_count(sample), int)

    def test_nonnegative(self, sample):
        assert toml_null_value_count(sample) >= 0


class TestTomlDistinctKeyCount:
    def test_returns_int(self, sample):
        assert isinstance(toml_distinct_key_count(sample), int)

    def test_positive(self, sample):
        assert toml_distinct_key_count(sample) >= 1


class TestTomlAvgNumericValue:
    def test_returns_float(self, sample):
        assert isinstance(toml_avg_numeric_value(sample), float)

    def test_nonnegative(self, sample):
        assert toml_avg_numeric_value(sample) >= 0.0
