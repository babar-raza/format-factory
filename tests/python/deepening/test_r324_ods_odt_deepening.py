"""Tests for ods_avg_cells_per_row, ods_string_percentage,
odt_chars_per_sentence, odt_words_per_char (Sprint 114, R324).
"""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods.ods_parser import ods_avg_cells_per_row, ods_string_percentage
from src.python.odt.odt_parser import odt_chars_per_sentence, odt_words_per_char

ODS = _REPO / "samples" / "by-format" / "ods" / "valid"
ODT = _REPO / "samples" / "by-format" / "odt" / "valid"


def test_ods_avg_cells_minimal():
    assert abs(ods_avg_cells_per_row(ODS / "minimal-spreadsheet.ods") - 2.0) < 0.01


def test_ods_avg_cells_numeric():
    assert abs(ods_avg_cells_per_row(ODS / "numeric-row.ods") - 3.0) < 0.01


def test_ods_avg_cells_single():
    assert abs(ods_avg_cells_per_row(ODS / "single-cell.ods") - 1.0) < 0.01


def test_ods_avg_cells_returns_float():
    assert isinstance(ods_avg_cells_per_row(ODS / "minimal-spreadsheet.ods"), float)


def test_ods_avg_cells_positive():
    assert ods_avg_cells_per_row(ODS / "minimal-spreadsheet.ods") > 0.0


def test_ods_string_pct_minimal():
    assert abs(ods_string_percentage(ODS / "minimal-spreadsheet.ods") - 75.0) < 0.1


def test_ods_string_pct_numeric():
    assert abs(ods_string_percentage(ODS / "numeric-row.ods") - 0.0) < 0.1


def test_ods_string_pct_single():
    assert abs(ods_string_percentage(ODS / "single-cell.ods") - 100.0) < 0.1


def test_ods_string_pct_returns_float():
    assert isinstance(ods_string_percentage(ODS / "minimal-spreadsheet.ods"), float)


def test_ods_string_pct_nonnegative():
    assert ods_string_percentage(ODS / "minimal-spreadsheet.ods") >= 0.0


def test_odt_chars_per_sentence_minimal():
    assert abs(odt_chars_per_sentence(ODT / "minimal-document.odt") - 13.0) < 0.1


def test_odt_chars_per_sentence_two():
    assert abs(odt_chars_per_sentence(ODT / "two-paragraphs.odt") - 16.5) < 0.1


def test_odt_chars_per_sentence_unicode():
    assert abs(odt_chars_per_sentence(ODT / "unicode-text.odt") - 0.0) < 0.01


def test_odt_chars_per_sentence_returns_float():
    assert isinstance(odt_chars_per_sentence(ODT / "minimal-document.odt"), float)


def test_odt_chars_per_sentence_nonnegative():
    assert odt_chars_per_sentence(ODT / "minimal-document.odt") >= 0.0


def test_odt_words_per_char_minimal():
    assert abs(odt_words_per_char(ODT / "minimal-document.odt") - 0.1538) < 0.01


def test_odt_words_per_char_two():
    assert abs(odt_words_per_char(ODT / "two-paragraphs.odt") - 0.1212) < 0.01


def test_odt_words_per_char_unicode():
    assert abs(odt_words_per_char(ODT / "unicode-text.odt") - 0.2308) < 0.01


def test_odt_words_per_char_returns_float():
    assert isinstance(odt_words_per_char(ODT / "minimal-document.odt"), float)


def test_odt_words_per_char_positive():
    assert odt_words_per_char(ODT / "minimal-document.odt") > 0.0
