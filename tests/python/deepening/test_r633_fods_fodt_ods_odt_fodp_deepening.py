"""Sprint R633 — FODS/FODT/ODS/ODT/FODP _times_forty_seven composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.fods.neutral_model import fods_sheet_count_times_forty_seven, fods_total_cell_count_times_forty_seven
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_forty_seven, fodt_word_count_times_forty_seven
from src.python.ods.ods_parser import ods_sheet_count_times_forty_seven, ods_total_cell_count_times_forty_seven
from src.python.odt.odt_parser import odt_word_count_times_forty_seven, odt_paragraph_count_times_forty_seven
from src.python.fodp.fodp_codec import fodp_slide_count_times_forty_seven, fodp_word_count_times_forty_seven
SAMPLES = _REPO / "samples" / "by-format"
_wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
_FODT = str(SAMPLES / "fodt" / "minimal-document.fodt")
_ODS = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
_ODT = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
_FODP = str(SAMPLES / "fodp" / "title-only.fodp")

class TestFodsSheetCountTimesForty_Seven:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_forty_seven(_wb), int)
    def test_non_negative(self):
        assert fods_sheet_count_times_forty_seven(_wb) >= 0
    def test_divisible(self):
        assert fods_sheet_count_times_forty_seven(_wb) % 47 == 0
class TestFodsTotalCellCountTimesForty_Seven:
    def test_returns_int(self):
        assert isinstance(fods_total_cell_count_times_forty_seven(_wb), int)
    def test_non_negative(self):
        assert fods_total_cell_count_times_forty_seven(_wb) >= 0
    def test_divisible(self):
        assert fods_total_cell_count_times_forty_seven(_wb) % 47 == 0
class TestFodtParagraphCountTimesForty_Seven:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_forty_seven(_FODT), int)
    def test_non_negative(self):
        assert fodt_paragraph_count_times_forty_seven(_FODT) >= 0
    def test_divisible(self):
        assert fodt_paragraph_count_times_forty_seven(_FODT) % 47 == 0
class TestFodtWordCountTimesForty_Seven:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_forty_seven(_FODT), int)
    def test_non_negative(self):
        assert fodt_word_count_times_forty_seven(_FODT) >= 0
    def test_divisible(self):
        assert fodt_word_count_times_forty_seven(_FODT) % 47 == 0
class TestOdsSheetCountTimesForty_Seven:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_forty_seven(_ODS), int)
    def test_non_negative(self):
        assert ods_sheet_count_times_forty_seven(_ODS) >= 0
    def test_divisible(self):
        assert ods_sheet_count_times_forty_seven(_ODS) % 47 == 0
class TestOdsTotalCellCountTimesForty_Seven:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_forty_seven(_ODS), int)
    def test_non_negative(self):
        assert ods_total_cell_count_times_forty_seven(_ODS) >= 0
    def test_divisible(self):
        assert ods_total_cell_count_times_forty_seven(_ODS) % 47 == 0
class TestOdtWordCountTimesForty_Seven:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_forty_seven(_ODT), int)
    def test_non_negative(self):
        assert odt_word_count_times_forty_seven(_ODT) >= 0
    def test_divisible(self):
        assert odt_word_count_times_forty_seven(_ODT) % 47 == 0
class TestOdtParagraphCountTimesForty_Seven:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_forty_seven(_ODT), int)
    def test_non_negative(self):
        assert odt_paragraph_count_times_forty_seven(_ODT) >= 0
    def test_divisible(self):
        assert odt_paragraph_count_times_forty_seven(_ODT) % 47 == 0
class TestFodpSlideCountTimesForty_Seven:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_forty_seven(_FODP), int)
    def test_non_negative(self):
        assert fodp_slide_count_times_forty_seven(_FODP) >= 0
    def test_divisible(self):
        assert fodp_slide_count_times_forty_seven(_FODP) % 47 == 0
class TestFodpWordCountTimesForty_Seven:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_forty_seven(_FODP), int)
    def test_non_negative(self):
        assert fodp_word_count_times_forty_seven(_FODP) >= 0
    def test_divisible(self):
        assert fodp_word_count_times_forty_seven(_FODP) % 47 == 0
