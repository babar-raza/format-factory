"""Sprint 103 — FODS/GNUMERIC/ABW/TSV cycle 8: 8 new analytics functions."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

_FODS = _REPO / "samples" / "by-format" / "fods"
_GNUMERIC = _REPO / "samples" / "by-format" / "gnumeric"
_ABW = _REPO / "samples" / "by-format" / "abw"
_TSV = _REPO / "samples" / "by-format" / "tsv"


@pytest.fixture
def fods_sample():
    return _FODS / "minimal-spreadsheet.fods"


@pytest.fixture
def gnumeric_sample():
    return _GNUMERIC / "multi-cell-basic.gnumeric"


@pytest.fixture
def abw_sample():
    return _ABW / "two-paragraphs.abw"


@pytest.fixture
def tsv_sample():
    return _TSV / "minimal-2x2.tsv"


# ── FODS ──

def test_fods_empty_row_count_importable():
    from src.python.fods import fods_empty_row_count
    assert callable(fods_empty_row_count)


def test_fods_empty_row_count_returns_int(fods_sample):
    from src.python.fods import fods_empty_row_count
    from src.python.fods.parser import parse_fods
    wb = parse_fods(fods_sample)
    result = fods_empty_row_count(wb)
    assert isinstance(result, int)
    assert result >= 0


def test_fods_distinct_value_count_importable():
    from src.python.fods import fods_distinct_value_count
    assert callable(fods_distinct_value_count)


def test_fods_distinct_value_count_returns_int(fods_sample):
    from src.python.fods import fods_distinct_value_count
    from src.python.fods.parser import parse_fods
    wb = parse_fods(fods_sample)
    result = fods_distinct_value_count(wb)
    assert isinstance(result, int)
    assert result >= 0


# ── GNUMERIC ──

def test_gnumeric_numeric_range_importable():
    from src.python.gnumeric import gnumeric_numeric_range
    assert callable(gnumeric_numeric_range)


def test_gnumeric_numeric_range_returns_float(gnumeric_sample):
    from src.python.gnumeric import gnumeric_numeric_range
    result = gnumeric_numeric_range(gnumeric_sample)
    assert isinstance(result, (int, float))
    assert result >= 0.0


def test_gnumeric_distinct_string_count_importable():
    from src.python.gnumeric import gnumeric_distinct_string_count
    assert callable(gnumeric_distinct_string_count)


def test_gnumeric_distinct_string_count_returns_int(gnumeric_sample):
    from src.python.gnumeric import gnumeric_distinct_string_count
    result = gnumeric_distinct_string_count(gnumeric_sample)
    assert isinstance(result, int)
    assert result >= 0


# ── ABW ──

def test_abw_longest_word_length_importable():
    from src.python.abw import abw_longest_word_length
    assert callable(abw_longest_word_length)


def test_abw_longest_word_length_returns_int(abw_sample):
    from src.python.abw import abw_longest_word_length
    result = abw_longest_word_length(abw_sample)
    assert isinstance(result, int)
    assert result >= 0


def test_abw_empty_paragraph_ratio_importable():
    from src.python.abw import abw_empty_paragraph_ratio
    assert callable(abw_empty_paragraph_ratio)


def test_abw_empty_paragraph_ratio_returns_float(abw_sample):
    from src.python.abw import abw_empty_paragraph_ratio
    result = abw_empty_paragraph_ratio(abw_sample)
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


# ── TSV ──

def test_tsv_empty_field_count_importable():
    from src.python.tsv import tsv_empty_field_count
    assert callable(tsv_empty_field_count)


def test_tsv_empty_field_count_returns_int(tsv_sample):
    from src.python.tsv import tsv_empty_field_count
    result = tsv_empty_field_count(tsv_sample)
    assert isinstance(result, int)
    assert result >= 0


def test_tsv_distinct_field_count_importable():
    from src.python.tsv import tsv_distinct_field_count
    assert callable(tsv_distinct_field_count)


def test_tsv_distinct_field_count_returns_int(tsv_sample):
    from src.python.tsv import tsv_distinct_field_count
    result = tsv_distinct_field_count(tsv_sample)
    assert isinstance(result, int)
    assert result >= 0


# ── Cross-format ──

def test_all_eight_functions_callable():
    """Verify all 8 Sprint 103 functions are importable."""
    from src.python.fods import fods_empty_row_count, fods_distinct_value_count
    from src.python.gnumeric import gnumeric_numeric_range, gnumeric_distinct_string_count
    from src.python.abw import abw_longest_word_length, abw_empty_paragraph_ratio
    from src.python.tsv import tsv_empty_field_count, tsv_distinct_field_count
    for fn in [
        fods_empty_row_count, fods_distinct_value_count,
        gnumeric_numeric_range, gnumeric_distinct_string_count,
        abw_longest_word_length, abw_empty_paragraph_ratio,
        tsv_empty_field_count, tsv_distinct_field_count,
    ]:
        assert callable(fn)
