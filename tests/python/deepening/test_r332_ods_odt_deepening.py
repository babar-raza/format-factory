"""Sprint 122 — ODS (ods_bytes_per_cell, ods_bytes_per_row)
and ODT (odt_bytes_per_word, odt_bytes_per_sentence).
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods.ods_parser import ods_bytes_per_cell, ods_bytes_per_row
from src.python.odt.odt_parser import odt_bytes_per_word, odt_bytes_per_sentence

ODS = _REPO / "samples" / "by-format" / "ods" / "valid"
ODT = _REPO / "samples" / "by-format" / "odt" / "valid"


class TestOdsBytesPerCell:
    def test_minimal_value(self):
        assert abs(ods_bytes_per_cell(ODS / "minimal-spreadsheet.ods") - 334.5) < 0.1

    def test_numeric_value(self):
        assert abs(ods_bytes_per_cell(ODS / "numeric-row.ods") - 438.0) < 0.1

    def test_single_value(self):
        assert abs(ods_bytes_per_cell(ODS / "single-cell.ods") - 1294.0) < 0.1

    def test_returns_float(self):
        assert isinstance(ods_bytes_per_cell(ODS / "minimal-spreadsheet.ods"), float)

    def test_positive(self):
        assert ods_bytes_per_cell(ODS / "minimal-spreadsheet.ods") > 0.0


class TestOdsBytesPerRow:
    def test_minimal_value(self):
        assert abs(ods_bytes_per_row(ODS / "minimal-spreadsheet.ods") - 669.0) < 0.1

    def test_numeric_value(self):
        assert abs(ods_bytes_per_row(ODS / "numeric-row.ods") - 1314.0) < 0.1

    def test_single_value(self):
        assert abs(ods_bytes_per_row(ODS / "single-cell.ods") - 1294.0) < 0.1

    def test_returns_float(self):
        assert isinstance(ods_bytes_per_row(ODS / "minimal-spreadsheet.ods"), float)

    def test_positive(self):
        assert ods_bytes_per_row(ODS / "numeric-row.ods") > 0.0


class TestOdtBytesPerWord:
    def test_minimal_value(self):
        assert abs(odt_bytes_per_word(ODT / "minimal-document.odt") - 606.0) < 0.1

    def test_two_value(self):
        assert abs(odt_bytes_per_word(ODT / "two-paragraphs.odt") - 306.0) < 0.1

    def test_unicode_value(self):
        assert abs(odt_bytes_per_word(ODT / "unicode-text.odt") - 409.0) < 0.1

    def test_returns_float(self):
        assert isinstance(odt_bytes_per_word(ODT / "minimal-document.odt"), float)

    def test_positive(self):
        assert odt_bytes_per_word(ODT / "two-paragraphs.odt") > 0.0


class TestOdtBytesPerSentence:
    def test_minimal_value(self):
        assert abs(odt_bytes_per_sentence(ODT / "minimal-document.odt") - 1212.0) < 0.1

    def test_two_value(self):
        assert abs(odt_bytes_per_sentence(ODT / "two-paragraphs.odt") - 612.0) < 0.1

    def test_unicode_value(self):
        assert abs(odt_bytes_per_sentence(ODT / "unicode-text.odt") - 0.0) < 0.1

    def test_returns_float(self):
        assert isinstance(odt_bytes_per_sentence(ODT / "minimal-document.odt"), float)

    def test_non_negative(self):
        assert odt_bytes_per_sentence(ODT / "unicode-text.odt") >= 0.0
