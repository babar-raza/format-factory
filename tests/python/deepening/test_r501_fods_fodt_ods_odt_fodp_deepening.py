"""Sprint R501 — FODS/FODT/ODS/ODT/FODP _times_fourteen composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.fods.neutral_model import fods_sheet_count_times_fourteen, fods_total_cell_count_times_fourteen
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_fourteen, fodt_word_count_times_fourteen
from src.python.ods.ods_parser import ods_sheet_count_times_fourteen, ods_total_cell_count_times_fourteen
from src.python.odt.odt_parser import odt_word_count_times_fourteen, odt_paragraph_count_times_fourteen
from src.python.fodp.fodp_codec import fodp_slide_count_times_fourteen, fodp_word_count_times_fourteen
SAMPLES = _REPO / "samples" / "by-format"
_FODS = str(SAMPLES / "fods" / "minimal-spreadsheet.fods")
_wb = parse_fods_strict(_FODS)
_FODT = str(SAMPLES / "fodt" / "minimal-document.fodt")
_ODS = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
_ODT = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
_FODP = str(SAMPLES / "fodp" / "title-only.fodp")

class TestFodsSheetCountTimesFourteen:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_fourteen(_wb), int)
    def test_non_negative(self):
        assert fods_sheet_count_times_fourteen(_wb) >= 0
    def test_divisible(self):
        assert fods_sheet_count_times_fourteen(_wb) % 14 == 0

class TestFodsTotalCellCountTimesFourteen:
    def test_returns_int(self):
        assert isinstance(fods_total_cell_count_times_fourteen(_wb), int)
    def test_non_negative(self):
        assert fods_total_cell_count_times_fourteen(_wb) >= 0
    def test_divisible(self):
        assert fods_total_cell_count_times_fourteen(_wb) % 14 == 0

class TestFodtParagraphCountTimesFourteen:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_fourteen(_FODT), int)
    def test_non_negative(self):
        assert fodt_paragraph_count_times_fourteen(_FODT) >= 0
    def test_divisible(self):
        assert fodt_paragraph_count_times_fourteen(_FODT) % 14 == 0

class TestFodtWordCountTimesFourteen:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_fourteen(_FODT), int)
    def test_non_negative(self):
        assert fodt_word_count_times_fourteen(_FODT) >= 0
    def test_divisible(self):
        assert fodt_word_count_times_fourteen(_FODT) % 14 == 0

class TestOdsSheetCountTimesFourteen:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_fourteen(_ODS), int)
    def test_non_negative(self):
        assert ods_sheet_count_times_fourteen(_ODS) >= 0
    def test_divisible(self):
        assert ods_sheet_count_times_fourteen(_ODS) % 14 == 0

class TestOdsTotalCellCountTimesFourteen:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_fourteen(_ODS), int)
    def test_non_negative(self):
        assert ods_total_cell_count_times_fourteen(_ODS) >= 0
    def test_divisible(self):
        assert ods_total_cell_count_times_fourteen(_ODS) % 14 == 0

class TestOdtWordCountTimesFourteen:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_fourteen(_ODT), int)
    def test_non_negative(self):
        assert odt_word_count_times_fourteen(_ODT) >= 0
    def test_divisible(self):
        assert odt_word_count_times_fourteen(_ODT) % 14 == 0

class TestOdtParagraphCountTimesFourteen:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_fourteen(_ODT), int)
    def test_non_negative(self):
        assert odt_paragraph_count_times_fourteen(_ODT) >= 0
    def test_divisible(self):
        assert odt_paragraph_count_times_fourteen(_ODT) % 14 == 0

class TestFodpSlideCountTimesFourteen:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_fourteen(_FODP), int)
    def test_non_negative(self):
        assert fodp_slide_count_times_fourteen(_FODP) >= 0
    def test_divisible(self):
        assert fodp_slide_count_times_fourteen(_FODP) % 14 == 0

class TestFodpWordCountTimesFourteen:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_fourteen(_FODP), int)
    def test_non_negative(self):
        assert fodp_word_count_times_fourteen(_FODP) >= 0
    def test_divisible(self):
        assert fodp_word_count_times_fourteen(_FODP) % 14 == 0
