"""Sprint 95 — FODS/Gnumeric/ABW/TSV cycle 6: 8 new analytics functions."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods.parser import parse_fods
from src.python.fods.neutral_model import fods_row_cell_variance, fods_min_cell_length
from src.python.gnumeric.gnumeric_codec import gnumeric_row_density, gnumeric_empty_cell_ratio
from src.python.abw.abw_codec import abw_capital_word_count, abw_avg_sentence_word_count
from src.python.tsv.tsv_parser import tsv_longest_row_length, tsv_shortest_row_length

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

class TestFodsRowCellVariance:
    def test_returns_float(self, fods_workbook):
        result = fods_row_cell_variance(fods_workbook)
        assert isinstance(result, (int, float))

    def test_non_negative(self, fods_workbook):
        assert fods_row_cell_variance(fods_workbook) >= 0.0

    def test_empty_workbook(self):
        assert fods_row_cell_variance({"sheets": []}) == 0.0

    def test_single_row(self):
        wb = {"sheets": [{"rows": [{"cells": [{"value": "a"}]}]}]}
        assert fods_row_cell_variance(wb) == 0.0


class TestFodsMinCellLength:
    def test_returns_int(self, fods_workbook):
        result = fods_min_cell_length(fods_workbook)
        assert isinstance(result, int)

    def test_non_negative(self, fods_workbook):
        assert fods_min_cell_length(fods_workbook) >= 0

    def test_empty_workbook(self):
        assert fods_min_cell_length({"sheets": []}) == 0

    def test_known_values(self):
        wb = {"sheets": [{"rows": [{"cells": [{"value": "ab"}, {"value": "cdef"}]}]}]}
        assert fods_min_cell_length(wb) == 2


# --- Gnumeric ---

class TestGnumericRowDensity:
    def test_returns_float(self, gnumeric_sample):
        result = gnumeric_row_density(gnumeric_sample)
        assert isinstance(result, (int, float))

    def test_non_negative(self, gnumeric_sample):
        assert gnumeric_row_density(gnumeric_sample) >= 0.0

    def test_non_negative_for_real_file(self, gnumeric_sample):
        assert gnumeric_row_density(gnumeric_sample) >= 0.0


class TestGnumericEmptyCellRatio:
    def test_returns_float(self, gnumeric_sample):
        result = gnumeric_empty_cell_ratio(gnumeric_sample)
        assert isinstance(result, (int, float))

    def test_bounded(self, gnumeric_sample):
        ratio = gnumeric_empty_cell_ratio(gnumeric_sample)
        assert 0.0 <= ratio <= 1.0


# --- ABW ---

class TestAbwCapitalWordCount:
    def test_returns_int(self, abw_sample):
        result = abw_capital_word_count(abw_sample)
        assert isinstance(result, int)

    def test_non_negative(self, abw_sample):
        assert abw_capital_word_count(abw_sample) >= 0

    def test_non_negative_for_real_file(self, abw_sample):
        assert abw_capital_word_count(abw_sample) >= 0


class TestAbwAvgSentenceWordCount:
    def test_returns_float(self, abw_sample):
        result = abw_avg_sentence_word_count(abw_sample)
        assert isinstance(result, (int, float))

    def test_non_negative(self, abw_sample):
        assert abw_avg_sentence_word_count(abw_sample) >= 0.0


# --- TSV ---

class TestTsvLongestRowLength:
    def test_returns_int(self, tsv_sample):
        result = tsv_longest_row_length(tsv_sample)
        assert isinstance(result, int)

    def test_positive(self, tsv_sample):
        assert tsv_longest_row_length(tsv_sample) > 0


class TestTsvShortestRowLength:
    def test_returns_int(self, tsv_sample):
        result = tsv_shortest_row_length(tsv_sample)
        assert isinstance(result, int)

    def test_positive(self, tsv_sample):
        assert tsv_shortest_row_length(tsv_sample) > 0

    def test_lte_longest(self, tsv_sample):
        assert tsv_shortest_row_length(tsv_sample) <= tsv_longest_row_length(tsv_sample)
