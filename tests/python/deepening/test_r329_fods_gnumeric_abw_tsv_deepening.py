"""Sprint 99 — FODS/GNUMERIC/ABW/TSV cycle 7: 8 new analytics functions."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

# --- Samples ---
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


def test_fods_numeric_range_importable():
    from src.python.fods import fods_numeric_range
    assert callable(fods_numeric_range)


def test_fods_numeric_range_returns_float(fods_sample):
    from src.python.fods import fods_numeric_range
    from src.python.fods.parser import parse_fods
    wb = parse_fods(fods_sample)
    result = fods_numeric_range(wb)
    assert isinstance(result, (int, float))
    assert result >= 0.0


def test_fods_column_density_importable():
    from src.python.fods import fods_column_density
    assert callable(fods_column_density)


def test_fods_column_density_returns_float(fods_sample):
    from src.python.fods import fods_column_density
    from src.python.fods.parser import parse_fods
    wb = parse_fods(fods_sample)
    result = fods_column_density(wb)
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


# ── GNUMERIC ──


def test_gnumeric_string_ratio_importable():
    from src.python.gnumeric import gnumeric_string_ratio
    assert callable(gnumeric_string_ratio)


def test_gnumeric_string_ratio_returns_float(gnumeric_sample):
    from src.python.gnumeric import gnumeric_string_ratio
    result = gnumeric_string_ratio(gnumeric_sample)
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


def test_gnumeric_nonempty_row_count_importable():
    from src.python.gnumeric import gnumeric_nonempty_row_count
    assert callable(gnumeric_nonempty_row_count)


def test_gnumeric_nonempty_row_count_returns_int(gnumeric_sample):
    from src.python.gnumeric import gnumeric_nonempty_row_count
    result = gnumeric_nonempty_row_count(gnumeric_sample)
    assert isinstance(result, int)
    assert result >= 0


# ── ABW ──


def test_abw_avg_paragraph_words_importable():
    from src.python.abw import abw_avg_paragraph_words
    assert callable(abw_avg_paragraph_words)


def test_abw_avg_paragraph_words_returns_float(abw_sample):
    from src.python.abw import abw_avg_paragraph_words
    result = abw_avg_paragraph_words(abw_sample)
    assert isinstance(result, (int, float))
    assert result >= 0.0


def test_abw_text_density_importable():
    from src.python.abw import abw_text_density
    assert callable(abw_text_density)


def test_abw_text_density_returns_float(abw_sample):
    from src.python.abw import abw_text_density
    result = abw_text_density(abw_sample)
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


# ── TSV ──


def test_tsv_header_length_avg_importable():
    from src.python.tsv import tsv_header_length_avg
    assert callable(tsv_header_length_avg)


def test_tsv_header_length_avg_returns_float(tsv_sample):
    from src.python.tsv import tsv_header_length_avg
    result = tsv_header_length_avg(tsv_sample)
    assert isinstance(result, (int, float))
    assert result >= 0.0


def test_tsv_data_completeness_importable():
    from src.python.tsv import tsv_data_completeness
    assert callable(tsv_data_completeness)


def test_tsv_data_completeness_returns_float(tsv_sample):
    from src.python.tsv import tsv_data_completeness
    result = tsv_data_completeness(tsv_sample)
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


# ── Cross-format ──


def test_all_eight_functions_callable():
    """Verify all 8 Sprint 99 functions are importable."""
    from src.python.fods import fods_numeric_range, fods_column_density
    from src.python.gnumeric import gnumeric_string_ratio, gnumeric_nonempty_row_count
    from src.python.abw import abw_avg_paragraph_words, abw_text_density
    from src.python.tsv import tsv_header_length_avg, tsv_data_completeness
    for fn in [
        fods_numeric_range, fods_column_density,
        gnumeric_string_ratio, gnumeric_nonempty_row_count,
        abw_avg_paragraph_words, abw_text_density,
        tsv_header_length_avg, tsv_data_completeness,
    ]:
        assert callable(fn)
