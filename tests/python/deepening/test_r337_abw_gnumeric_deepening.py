"""Sprint 127 deepening – ABW bytes_per_word/bytes_per_paragraph, Gnumeric bytes_per_cell/bytes_per_sheet."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.abw.abw_codec import abw_bytes_per_word, abw_bytes_per_paragraph
from src.python.gnumeric.gnumeric_codec import gnumeric_bytes_per_cell, gnumeric_bytes_per_sheet

ABW = _REPO / "samples" / "by-format" / "abw"
GNU = _REPO / "samples" / "by-format" / "gnumeric"


# --- abw_bytes_per_word ---

class TestAbwBytesPerWord:
    def test_minimal(self):
        assert abs(abw_bytes_per_word(ABW / "minimal-document.abw") - 284.0) < 0.01

    def test_two(self):
        assert abs(abw_bytes_per_word(ABW / "two-paragraphs.abw") - 92.25) < 0.01

    def test_empty(self):
        assert abw_bytes_per_word(ABW / "empty-section.abw") == 0.0

    def test_returns_float(self):
        assert isinstance(abw_bytes_per_word(ABW / "minimal-document.abw"), float)

    def test_positive(self):
        assert abw_bytes_per_word(ABW / "minimal-document.abw") > 0


# --- abw_bytes_per_paragraph ---

class TestAbwBytesPerParagraph:
    def test_minimal(self):
        assert abs(abw_bytes_per_paragraph(ABW / "minimal-document.abw") - 284.0) < 0.01

    def test_two(self):
        assert abs(abw_bytes_per_paragraph(ABW / "two-paragraphs.abw") - 184.5) < 0.01

    def test_empty(self):
        assert abw_bytes_per_paragraph(ABW / "empty-section.abw") == 0.0

    def test_returns_float(self):
        assert isinstance(abw_bytes_per_paragraph(ABW / "minimal-document.abw"), float)

    def test_positive(self):
        assert abw_bytes_per_paragraph(ABW / "minimal-document.abw") > 0


# --- gnumeric_bytes_per_cell ---

class TestGnumericBytesPerCell:
    def test_minimal(self):
        assert abs(gnumeric_bytes_per_cell(GNU / "minimal-spreadsheet.gnumeric") - 307.0) < 0.01

    def test_multi(self):
        assert abs(gnumeric_bytes_per_cell(GNU / "multi-cell-basic.gnumeric") - 84.25) < 0.01

    def test_empty(self):
        assert gnumeric_bytes_per_cell(GNU / "empty-sheet.gnumeric") == 0.0

    def test_returns_float(self):
        assert isinstance(gnumeric_bytes_per_cell(GNU / "minimal-spreadsheet.gnumeric"), float)

    def test_positive(self):
        assert gnumeric_bytes_per_cell(GNU / "minimal-spreadsheet.gnumeric") > 0


# --- gnumeric_bytes_per_sheet ---

class TestGnumericBytesPerSheet:
    def test_minimal(self):
        assert abs(gnumeric_bytes_per_sheet(GNU / "minimal-spreadsheet.gnumeric") - 307.0) < 0.01

    def test_multi(self):
        assert abs(gnumeric_bytes_per_sheet(GNU / "multi-cell-basic.gnumeric") - 337.0) < 0.01

    def test_empty(self):
        assert abs(gnumeric_bytes_per_sheet(GNU / "empty-sheet.gnumeric") - 264.0) < 0.01

    def test_returns_float(self):
        assert isinstance(gnumeric_bytes_per_sheet(GNU / "minimal-spreadsheet.gnumeric"), float)

    def test_positive(self):
        assert gnumeric_bytes_per_sheet(GNU / "minimal-spreadsheet.gnumeric") > 0
