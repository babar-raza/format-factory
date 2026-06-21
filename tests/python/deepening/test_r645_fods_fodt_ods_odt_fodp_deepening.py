"""Sprint R645 — FODS/FODT/ODS/ODT/FODP _times_fifty composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.fods.neutral_model import fods_sheet_count_times_fifty, fods_total_cell_count_times_fifty
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_fifty, fodt_word_count_times_fifty
from src.python.ods.ods_parser import ods_sheet_count_times_fifty, ods_total_cell_count_times_fifty
from src.python.odt.odt_parser import odt_word_count_times_fifty, odt_paragraph_count_times_fifty
from src.python.fodp.fodp_codec import fodp_slide_count_times_fifty, fodp_word_count_times_fifty
SAMPLES = _REPO / "samples" / "by-format"
_wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
_FODT = str(SAMPLES / "fodt" / "minimal-document.fodt")
_ODS = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
_ODT = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
_FODP = str(SAMPLES / "fodp" / "title-only.fodp")

class TestFodsSheetCountTimesFifty:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_fifty(_wb), int)
    def test_non_negative(self):
        assert fods_sheet_count_times_fifty(_wb) >= 0
    def test_divisible(self):
        assert fods_sheet_count_times_fifty(_wb) % 50 == 0
class TestFodsTotalCellCountTimesFifty:
    def test_returns_int(self):
        assert isinstance(fods_total_cell_count_times_fifty(_wb), int)
    def test_non_negative(self):
        assert fods_total_cell_count_times_fifty(_wb) >= 0
    def test_divisible(self):
        assert fods_total_cell_count_times_fifty(_wb) % 50 == 0
class TestFodtParagraphCountTimesFifty:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_fifty(_FODT), int)
    def test_non_negative(self):
        assert fodt_paragraph_count_times_fifty(_FODT) >= 0
    def test_divisible(self):
        assert fodt_paragraph_count_times_fifty(_FODT) % 50 == 0
class TestFodtWordCountTimesFifty:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_fifty(_FODT), int)
    def test_non_negative(self):
        assert fodt_word_count_times_fifty(_FODT) >= 0
    def test_divisible(self):
        assert fodt_word_count_times_fifty(_FODT) % 50 == 0
class TestOdsSheetCountTimesFifty:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_fifty(_ODS), int)
    def test_non_negative(self):
        assert ods_sheet_count_times_fifty(_ODS) >= 0
    def test_divisible(self):
        assert ods_sheet_count_times_fifty(_ODS) % 50 == 0
class TestOdsTotalCellCountTimesFifty:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_fifty(_ODS), int)
    def test_non_negative(self):
        assert ods_total_cell_count_times_fifty(_ODS) >= 0
    def test_divisible(self):
        assert ods_total_cell_count_times_fifty(_ODS) % 50 == 0
class TestOdtWordCountTimesFifty:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_fifty(_ODT), int)
    def test_non_negative(self):
        assert odt_word_count_times_fifty(_ODT) >= 0
    def test_divisible(self):
        assert odt_word_count_times_fifty(_ODT) % 50 == 0
class TestOdtParagraphCountTimesFifty:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_fifty(_ODT), int)
    def test_non_negative(self):
        assert odt_paragraph_count_times_fifty(_ODT) >= 0
    def test_divisible(self):
        assert odt_paragraph_count_times_fifty(_ODT) % 50 == 0
class TestFodpSlideCountTimesFifty:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_fifty(_FODP), int)
    def test_non_negative(self):
        assert fodp_slide_count_times_fifty(_FODP) >= 0
    def test_divisible(self):
        assert fodp_slide_count_times_fifty(_FODP) % 50 == 0
class TestFodpWordCountTimesFifty:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_fifty(_FODP), int)
    def test_non_negative(self):
        assert fodp_word_count_times_fifty(_FODP) >= 0
    def test_divisible(self):
        assert fodp_word_count_times_fifty(_FODP) % 50 == 0
