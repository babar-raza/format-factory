"""Sprint 87 — FODS/Gnumeric/ABW/TSV cycle 4: 8 new analytics functions."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods.parser import parse_fods
from src.python.fods.neutral_model import fods_total_text_length, fods_column_count_variance
from src.python.gnumeric.gnumeric_codec import gnumeric_total_numeric_sum, gnumeric_distinct_value_count
from src.python.abw.abw_codec import abw_avg_word_length, abw_has_headings
from src.python.tsv.tsv_parser import tsv_avg_field_length, tsv_column_type_ratio

_FODS = _REPO / "samples" / "by-format" / "fods"
_GNUMERIC = _REPO / "samples" / "by-format" / "gnumeric"
_ABW = _REPO / "samples" / "by-format" / "abw"
_TSV = _REPO / "samples" / "by-format" / "tsv"


@pytest.fixture
def fods_workbook():
    sample = next(_FODS.glob("*.fods"))
    return parse_fods(str(sample))


@pytest.fixture
def gnumeric_sample():
    return next(_GNUMERIC.glob("*.gnumeric"))


@pytest.fixture
def abw_sample():
    return next(_ABW.glob("*.abw"))


@pytest.fixture
def tsv_sample():
    return next(_TSV.glob("*.tsv"))


# --- FODS ---
class TestFodsTotalTextLength:
    def test_returns_int(self, fods_workbook):
        result = fods_total_text_length(fods_workbook)
        assert isinstance(result, int)

    def test_non_negative(self, fods_workbook):
        assert fods_total_text_length(fods_workbook) >= 0


class TestFodsColumnCountVariance:
    def test_returns_float(self, fods_workbook):
        result = fods_column_count_variance(fods_workbook)
        assert isinstance(result, float)

    def test_non_negative(self, fods_workbook):
        assert fods_column_count_variance(fods_workbook) >= 0.0


# --- Gnumeric ---
class TestGnumericTotalNumericSum:
    def test_returns_float(self, gnumeric_sample):
        result = gnumeric_total_numeric_sum(gnumeric_sample)
        assert isinstance(result, float)

    def test_is_number(self, gnumeric_sample):
        import math
        result = gnumeric_total_numeric_sum(gnumeric_sample)
        assert not math.isnan(result)


class TestGnumericDistinctValueCount:
    def test_returns_int(self, gnumeric_sample):
        result = gnumeric_distinct_value_count(gnumeric_sample)
        assert isinstance(result, int)

    def test_non_negative(self, gnumeric_sample):
        assert gnumeric_distinct_value_count(gnumeric_sample) >= 0


# --- ABW ---
class TestAbwAvgWordLength:
    def test_returns_float(self, abw_sample):
        result = abw_avg_word_length(abw_sample)
        assert isinstance(result, float)

    def test_non_negative(self, abw_sample):
        assert abw_avg_word_length(abw_sample) >= 0.0


class TestAbwHasHeadings:
    def test_returns_bool(self, abw_sample):
        result = abw_has_headings(abw_sample)
        assert isinstance(result, bool)

    def test_is_deterministic(self, abw_sample):
        assert abw_has_headings(abw_sample) == abw_has_headings(abw_sample)


# --- TSV ---
class TestTsvAvgFieldLength:
    def test_returns_float(self, tsv_sample):
        result = tsv_avg_field_length(tsv_sample)
        assert isinstance(result, float)

    def test_non_negative(self, tsv_sample):
        assert tsv_avg_field_length(tsv_sample) >= 0.0


class TestTsvColumnTypeRatio:
    def test_returns_float(self, tsv_sample):
        result = tsv_column_type_ratio(tsv_sample)
        assert isinstance(result, float)

    def test_between_zero_and_one(self, tsv_sample):
        result = tsv_column_type_ratio(tsv_sample)
        assert 0.0 <= result <= 1.0
