"""Sprint R290J: ODS analytics deepening — distinct_value_count, avg_value_text_length, total_sheet_count."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_parser import (
    ods_distinct_value_count,
    ods_avg_value_text_length,
    ods_total_sheet_count,
)

SAMPLES = _REPO / "samples" / "by-format" / "ods" / "valid"
MINIMAL = SAMPLES / "minimal-spreadsheet.ods"


@pytest.fixture
def sample():
    if not MINIMAL.exists():
        pytest.skip("ODS minimal sample not available")
    return MINIMAL


class TestOdsDistinctValueCount:
    def test_returns_int(self, sample):
        assert isinstance(ods_distinct_value_count(sample), int)

    def test_nonnegative(self, sample):
        assert ods_distinct_value_count(sample) >= 0


class TestOdsAvgValueTextLength:
    def test_returns_float(self, sample):
        assert isinstance(ods_avg_value_text_length(sample), float)

    def test_nonnegative(self, sample):
        assert ods_avg_value_text_length(sample) >= 0.0


class TestOdsTotalSheetCount:
    def test_returns_int(self, sample):
        assert isinstance(ods_total_sheet_count(sample), int)

    def test_positive(self, sample):
        assert ods_total_sheet_count(sample) >= 1
