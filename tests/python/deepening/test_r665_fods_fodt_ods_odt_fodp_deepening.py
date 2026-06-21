"""Sprint R665 — FODS/FODT/ODS/ODT/FODP _times_fifty_five composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.fods.neutral_model import fods_sheet_count_times_fifty_five, fods_total_cell_count_times_fifty_five
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_fifty_five, fodt_word_count_times_fifty_five
from src.python.ods.ods_parser import ods_sheet_count_times_fifty_five, ods_total_cell_count_times_fifty_five
from src.python.odt.odt_parser import odt_word_count_times_fifty_five, odt_paragraph_count_times_fifty_five
from src.python.fodp.fodp_codec import fodp_slide_count_times_fifty_five, fodp_word_count_times_fifty_five
SAMPLES = _REPO / "samples" / "by-format"
_wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
_FODT = str(SAMPLES / "fodt" / "minimal-document.fodt")
_ODS = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
_ODT = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
_FODP = str(SAMPLES / "fodp" / "title-only.fodp")

class TestFodsSheetCountTimesFiftyFive:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_fifty_five(_wb), int)
    def test_non_negative(self):
        assert fods_sheet_count_times_fifty_five(_wb) >= 0
    def test_divisible(self):
        assert fods_sheet_count_times_fifty_five(_wb) % 55 == 0
class TestFodsTotalCellCountTimesFiftyFive:
    def test_returns_int(self):
        assert isinstance(fods_total_cell_count_times_fifty_five(_wb), int)
    def test_non_negative(self):
        assert fods_total_cell_count_times_fifty_five(_wb) >= 0
    def test_divisible(self):
        assert fods_total_cell_count_times_fifty_five(_wb) % 55 == 0
class TestFodtParagraphCountTimesFiftyFive:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_fifty_five(_FODT), int)
    def test_non_negative(self):
        assert fodt_paragraph_count_times_fifty_five(_FODT) >= 0
    def test_divisible(self):
        assert fodt_paragraph_count_times_fifty_five(_FODT) % 55 == 0
class TestFodtWordCountTimesFiftyFive:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_fifty_five(_FODT), int)
    def test_non_negative(self):
        assert fodt_word_count_times_fifty_five(_FODT) >= 0
    def test_divisible(self):
        assert fodt_word_count_times_fifty_five(_FODT) % 55 == 0
class TestOdsSheetCountTimesFiftyFive:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_fifty_five(_ODS), int)
    def test_non_negative(self):
        assert ods_sheet_count_times_fifty_five(_ODS) >= 0
    def test_divisible(self):
        assert ods_sheet_count_times_fifty_five(_ODS) % 55 == 0
class TestOdsTotalCellCountTimesFiftyFive:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_fifty_five(_ODS), int)
    def test_non_negative(self):
        assert ods_total_cell_count_times_fifty_five(_ODS) >= 0
    def test_divisible(self):
        assert ods_total_cell_count_times_fifty_five(_ODS) % 55 == 0
class TestOdtWordCountTimesFiftyFive:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_fifty_five(_ODT), int)
    def test_non_negative(self):
        assert odt_word_count_times_fifty_five(_ODT) >= 0
    def test_divisible(self):
        assert odt_word_count_times_fifty_five(_ODT) % 55 == 0
class TestOdtParagraphCountTimesFiftyFive:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_fifty_five(_ODT), int)
    def test_non_negative(self):
        assert odt_paragraph_count_times_fifty_five(_ODT) >= 0
    def test_divisible(self):
        assert odt_paragraph_count_times_fifty_five(_ODT) % 55 == 0
class TestFodpSlideCountTimesFiftyFive:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_fifty_five(_FODP), int)
    def test_non_negative(self):
        assert fodp_slide_count_times_fifty_five(_FODP) >= 0
    def test_divisible(self):
        assert fodp_slide_count_times_fifty_five(_FODP) % 55 == 0
class TestFodpWordCountTimesFiftyFive:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_fifty_five(_FODP), int)
    def test_non_negative(self):
        assert fodp_word_count_times_fifty_five(_FODP) >= 0
    def test_divisible(self):
        assert fodp_word_count_times_fifty_five(_FODP) % 55 == 0
