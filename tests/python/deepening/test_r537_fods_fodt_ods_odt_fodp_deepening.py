"""Sprint R537 — FODS/FODT/ODS/ODT/FODP _times_twenty_three composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.fods.neutral_model import fods_sheet_count_times_twenty_three, fods_total_cell_count_times_twenty_three
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_twenty_three, fodt_word_count_times_twenty_three
from src.python.ods.ods_parser import ods_sheet_count_times_twenty_three, ods_total_cell_count_times_twenty_three
from src.python.odt.odt_parser import odt_word_count_times_twenty_three, odt_paragraph_count_times_twenty_three
from src.python.fodp.fodp_codec import fodp_slide_count_times_twenty_three, fodp_word_count_times_twenty_three
SAMPLES = _REPO / "samples" / "by-format"
_wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
_FODT = str(SAMPLES / "fodt" / "minimal-document.fodt")
_ODS = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
_ODT = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
_FODP = str(SAMPLES / "fodp" / "title-only.fodp")

class TestFodsSheetCountTimesTwentyThree:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_twenty_three(_wb), int)
    def test_non_negative(self):
        assert fods_sheet_count_times_twenty_three(_wb) >= 0
    def test_divisible(self):
        assert fods_sheet_count_times_twenty_three(_wb) % 23 == 0
class TestFodsTotalCellCountTimesTwentyThree:
    def test_returns_int(self):
        assert isinstance(fods_total_cell_count_times_twenty_three(_wb), int)
    def test_non_negative(self):
        assert fods_total_cell_count_times_twenty_three(_wb) >= 0
    def test_divisible(self):
        assert fods_total_cell_count_times_twenty_three(_wb) % 23 == 0
class TestFodtParagraphCountTimesTwentyThree:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_twenty_three(_FODT), int)
    def test_non_negative(self):
        assert fodt_paragraph_count_times_twenty_three(_FODT) >= 0
    def test_divisible(self):
        assert fodt_paragraph_count_times_twenty_three(_FODT) % 23 == 0
class TestFodtWordCountTimesTwentyThree:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_twenty_three(_FODT), int)
    def test_non_negative(self):
        assert fodt_word_count_times_twenty_three(_FODT) >= 0
    def test_divisible(self):
        assert fodt_word_count_times_twenty_three(_FODT) % 23 == 0
class TestOdsSheetCountTimesTwentyThree:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_twenty_three(_ODS), int)
    def test_non_negative(self):
        assert ods_sheet_count_times_twenty_three(_ODS) >= 0
    def test_divisible(self):
        assert ods_sheet_count_times_twenty_three(_ODS) % 23 == 0
class TestOdsTotalCellCountTimesTwentyThree:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_twenty_three(_ODS), int)
    def test_non_negative(self):
        assert ods_total_cell_count_times_twenty_three(_ODS) >= 0
    def test_divisible(self):
        assert ods_total_cell_count_times_twenty_three(_ODS) % 23 == 0
class TestOdtWordCountTimesTwentyThree:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_twenty_three(_ODT), int)
    def test_non_negative(self):
        assert odt_word_count_times_twenty_three(_ODT) >= 0
    def test_divisible(self):
        assert odt_word_count_times_twenty_three(_ODT) % 23 == 0
class TestOdtParagraphCountTimesTwentyThree:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_twenty_three(_ODT), int)
    def test_non_negative(self):
        assert odt_paragraph_count_times_twenty_three(_ODT) >= 0
    def test_divisible(self):
        assert odt_paragraph_count_times_twenty_three(_ODT) % 23 == 0
class TestFodpSlideCountTimesTwentyThree:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_twenty_three(_FODP), int)
    def test_non_negative(self):
        assert fodp_slide_count_times_twenty_three(_FODP) >= 0
    def test_divisible(self):
        assert fodp_slide_count_times_twenty_three(_FODP) % 23 == 0
class TestFodpWordCountTimesTwentyThree:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_twenty_three(_FODP), int)
    def test_non_negative(self):
        assert fodp_word_count_times_twenty_three(_FODP) >= 0
    def test_divisible(self):
        assert fodp_word_count_times_twenty_three(_FODP) % 23 == 0
