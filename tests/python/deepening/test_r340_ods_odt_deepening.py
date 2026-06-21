"""Sprint 130 deepening – ODS rows_per_sheet/is_empty_spreadsheet, ODT words_per_paragraph/chars_per_paragraph."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods.ods_parser import ods_rows_per_sheet, ods_is_empty_spreadsheet
from src.python.odt.odt_parser import odt_words_per_paragraph, odt_chars_per_paragraph

ODS = _REPO / "samples" / "by-format" / "ods" / "valid"
ODT = _REPO / "samples" / "by-format" / "odt" / "valid"


class TestOdsRowsPerSheet:
    def test_minimal(self):
        assert abs(ods_rows_per_sheet(ODS / "minimal-spreadsheet.ods") - 2.0) < 0.01

    def test_numeric(self):
        assert abs(ods_rows_per_sheet(ODS / "numeric-row.ods") - 1.0) < 0.01

    def test_single(self):
        assert abs(ods_rows_per_sheet(ODS / "single-cell.ods") - 1.0) < 0.01

    def test_returns_float(self):
        assert isinstance(ods_rows_per_sheet(ODS / "minimal-spreadsheet.ods"), float)

    def test_positive(self):
        assert ods_rows_per_sheet(ODS / "minimal-spreadsheet.ods") > 0


class TestOdsIsEmptySpreadsheet:
    def test_minimal_not_empty(self):
        assert ods_is_empty_spreadsheet(ODS / "minimal-spreadsheet.ods") is False

    def test_numeric_not_empty(self):
        assert ods_is_empty_spreadsheet(ODS / "numeric-row.ods") is False

    def test_single_not_empty(self):
        assert ods_is_empty_spreadsheet(ODS / "single-cell.ods") is False

    def test_returns_bool(self):
        assert isinstance(ods_is_empty_spreadsheet(ODS / "minimal-spreadsheet.ods"), bool)

    def test_consistency(self):
        assert not ods_is_empty_spreadsheet(ODS / "minimal-spreadsheet.ods")


class TestOdtWordsPerParagraph:
    def test_minimal(self):
        assert abs(odt_words_per_paragraph(ODT / "minimal-document.odt") - 2.0) < 0.01

    def test_two(self):
        assert abs(odt_words_per_paragraph(ODT / "two-paragraphs.odt") - 2.0) < 0.01

    def test_unicode(self):
        assert abs(odt_words_per_paragraph(ODT / "unicode-text.odt") - 3.0) < 0.01

    def test_returns_float(self):
        assert isinstance(odt_words_per_paragraph(ODT / "minimal-document.odt"), float)

    def test_positive(self):
        assert odt_words_per_paragraph(ODT / "minimal-document.odt") > 0


class TestOdtCharsPerParagraph:
    def test_minimal(self):
        assert abs(odt_chars_per_paragraph(ODT / "minimal-document.odt") - 13.0) < 0.01

    def test_two(self):
        assert abs(odt_chars_per_paragraph(ODT / "two-paragraphs.odt") - 16.5) < 0.01

    def test_unicode(self):
        assert abs(odt_chars_per_paragraph(ODT / "unicode-text.odt") - 13.0) < 0.01

    def test_returns_float(self):
        assert isinstance(odt_chars_per_paragraph(ODT / "minimal-document.odt"), float)

    def test_positive(self):
        assert odt_chars_per_paragraph(ODT / "minimal-document.odt") > 0
