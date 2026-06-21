"""Sprint 138 — ODS bytes_per_sheet/cells_per_sheet_avg, ODT bytes_per_word/bytes_per_paragraph."""
import sys, pathlib, pytest
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.ods.ods_parser import ods_bytes_per_sheet, ods_cells_per_sheet_avg
from src.python.odt.odt_parser import odt_bytes_per_word, odt_bytes_per_paragraph

O1 = str(_REPO / "samples/by-format/ods/valid/minimal-spreadsheet.ods")
O2 = str(_REPO / "samples/by-format/ods/valid/numeric-row.ods")
O3 = str(_REPO / "samples/by-format/ods/valid/single-cell.ods")
D1 = str(_REPO / "samples/by-format/odt/valid/minimal-document.odt")
D2 = str(_REPO / "samples/by-format/odt/valid/two-paragraphs.odt")
D3 = str(_REPO / "samples/by-format/odt/valid/unicode-text.odt")

class TestOdsBytesPerSheet:
    def test_minimal(self):
        assert ods_bytes_per_sheet(O1) == 1338.0
    def test_numeric(self):
        assert ods_bytes_per_sheet(O2) == 1314.0
    def test_single(self):
        assert ods_bytes_per_sheet(O3) == 1294.0
    def test_return_type(self):
        assert isinstance(ods_bytes_per_sheet(O1), float)
    def test_positive(self):
        assert ods_bytes_per_sheet(O1) > 0

class TestOdsCellsPerSheetAvg:
    def test_minimal(self):
        assert ods_cells_per_sheet_avg(O1) == 4.0
    def test_numeric(self):
        assert ods_cells_per_sheet_avg(O2) == 3.0
    def test_single(self):
        assert ods_cells_per_sheet_avg(O3) == 1.0
    def test_return_type(self):
        assert isinstance(ods_cells_per_sheet_avg(O1), float)
    def test_positive(self):
        assert ods_cells_per_sheet_avg(O1) > 0

class TestOdtBytesPerWord:
    def test_minimal(self):
        assert odt_bytes_per_word(D1) == 606.0
    def test_two_para(self):
        assert odt_bytes_per_word(D2) == 306.0
    def test_unicode(self):
        assert odt_bytes_per_word(D3) == 409.0
    def test_return_type(self):
        assert isinstance(odt_bytes_per_word(D1), float)
    def test_positive(self):
        assert odt_bytes_per_word(D1) > 0

class TestOdtBytesPerParagraph:
    def test_minimal(self):
        assert odt_bytes_per_paragraph(D1) == 1212.0
    def test_two_para(self):
        assert odt_bytes_per_paragraph(D2) == 612.0
    def test_unicode(self):
        assert odt_bytes_per_paragraph(D3) == 1227.0
    def test_return_type(self):
        assert isinstance(odt_bytes_per_paragraph(D1), float)
    def test_positive(self):
        assert odt_bytes_per_paragraph(D1) > 0
