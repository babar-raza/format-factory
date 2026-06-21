"""Sprint R661 — FODS/FODT/ODS/ODT/FODP _times_fifty_four composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.fods.neutral_model import fods_sheet_count_times_fifty_four, fods_total_cell_count_times_fifty_four
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_fifty_four, fodt_word_count_times_fifty_four
from src.python.ods.ods_parser import ods_sheet_count_times_fifty_four, ods_total_cell_count_times_fifty_four
from src.python.odt.odt_parser import odt_word_count_times_fifty_four, odt_paragraph_count_times_fifty_four
from src.python.fodp.fodp_codec import fodp_slide_count_times_fifty_four, fodp_word_count_times_fifty_four
SAMPLES = _REPO / "samples" / "by-format"
_wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
_FODT = str(SAMPLES / "fodt" / "minimal-document.fodt")
_ODS = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
_ODT = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
_FODP = str(SAMPLES / "fodp" / "title-only.fodp")

class TestFodsSheetCountTimesFiftyFour:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_fifty_four(_wb), int)
    def test_non_negative(self):
        assert fods_sheet_count_times_fifty_four(_wb) >= 0
    def test_divisible(self):
        assert fods_sheet_count_times_fifty_four(_wb) % 54 == 0
class TestFodsTotalCellCountTimesFiftyFour:
    def test_returns_int(self):
        assert isinstance(fods_total_cell_count_times_fifty_four(_wb), int)
    def test_non_negative(self):
        assert fods_total_cell_count_times_fifty_four(_wb) >= 0
    def test_divisible(self):
        assert fods_total_cell_count_times_fifty_four(_wb) % 54 == 0
class TestFodtParagraphCountTimesFiftyFour:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_fifty_four(_FODT), int)
    def test_non_negative(self):
        assert fodt_paragraph_count_times_fifty_four(_FODT) >= 0
    def test_divisible(self):
        assert fodt_paragraph_count_times_fifty_four(_FODT) % 54 == 0
class TestFodtWordCountTimesFiftyFour:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_fifty_four(_FODT), int)
    def test_non_negative(self):
        assert fodt_word_count_times_fifty_four(_FODT) >= 0
    def test_divisible(self):
        assert fodt_word_count_times_fifty_four(_FODT) % 54 == 0
class TestOdsSheetCountTimesFiftyFour:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_fifty_four(_ODS), int)
    def test_non_negative(self):
        assert ods_sheet_count_times_fifty_four(_ODS) >= 0
    def test_divisible(self):
        assert ods_sheet_count_times_fifty_four(_ODS) % 54 == 0
class TestOdsTotalCellCountTimesFiftyFour:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_fifty_four(_ODS), int)
    def test_non_negative(self):
        assert ods_total_cell_count_times_fifty_four(_ODS) >= 0
    def test_divisible(self):
        assert ods_total_cell_count_times_fifty_four(_ODS) % 54 == 0
class TestOdtWordCountTimesFiftyFour:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_fifty_four(_ODT), int)
    def test_non_negative(self):
        assert odt_word_count_times_fifty_four(_ODT) >= 0
    def test_divisible(self):
        assert odt_word_count_times_fifty_four(_ODT) % 54 == 0
class TestOdtParagraphCountTimesFiftyFour:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_fifty_four(_ODT), int)
    def test_non_negative(self):
        assert odt_paragraph_count_times_fifty_four(_ODT) >= 0
    def test_divisible(self):
        assert odt_paragraph_count_times_fifty_four(_ODT) % 54 == 0
class TestFodpSlideCountTimesFiftyFour:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_fifty_four(_FODP), int)
    def test_non_negative(self):
        assert fodp_slide_count_times_fifty_four(_FODP) >= 0
    def test_divisible(self):
        assert fodp_slide_count_times_fifty_four(_FODP) % 54 == 0
class TestFodpWordCountTimesFiftyFour:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_fifty_four(_FODP), int)
    def test_non_negative(self):
        assert fodp_word_count_times_fifty_four(_FODP) >= 0
    def test_divisible(self):
        assert fodp_word_count_times_fifty_four(_FODP) % 54 == 0
